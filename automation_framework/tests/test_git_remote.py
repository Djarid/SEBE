"""
Tests for tools.git_remote — Git remote operations.

All subprocess calls are mocked. Tests cover .env parsing, credential loading,
git operations, and security (token redaction).
"""

import pytest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import subprocess

from tools.git_remote import (
    load_env,
    get_credentials,
    run_git,
    authenticated_url,
    action_status,
    action_add_remote,
    action_push,
    action_pull,
    action_sync,
)


# ═══════════════════════════════════════════════════════════════════════════
# .env Parsing Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestLoadEnv:
    """Test .env file parsing."""

    @patch("tools.git_remote.ENV_FILE")
    def test_load_env_valid_file(self, mock_env_file, tmp_path):
        """Parse valid .env file."""
        env_file = tmp_path / ".env"
        env_file.write_text("""
GITHUB_TOKEN=ghp_test123456
GITHUB_USER=testuser
GITHUB_REPO=github.com/testuser/SEBE.git
""", encoding="utf-8")
        mock_env_file.exists.return_value = True
        
        with patch("tools.git_remote.open", mock_open(read_data=env_file.read_text())):
            result = load_env()
        
        assert result["GITHUB_TOKEN"] == "ghp_test123456"
        assert result["GITHUB_USER"] == "testuser"
        assert result["GITHUB_REPO"] == "github.com/testuser/SEBE.git"

    @patch("tools.git_remote.ENV_FILE")
    def test_load_env_missing_file(self, mock_env_file):
        """Missing .env file returns empty dict."""
        mock_env_file.exists.return_value = False
        result = load_env()
        assert result == {}

    @patch("tools.git_remote.ENV_FILE")
    def test_load_env_ignores_comments(self, mock_env_file, tmp_path):
        """Comments and empty lines are ignored."""
        env_content = """
# This is a comment
GITHUB_TOKEN=token123

# Another comment
GITHUB_USER=user123
"""
        mock_env_file.exists.return_value = True
        with patch("tools.git_remote.open", mock_open(read_data=env_content)):
            result = load_env()
        
        assert len(result) == 2
        assert result["GITHUB_TOKEN"] == "token123"

    @patch("tools.git_remote.ENV_FILE")
    def test_load_env_ignores_malformed_lines(self, mock_env_file):
        """Malformed lines without = are skipped."""
        env_content = "VALID_KEY=value\nINVALID_LINE\nANOTHER_KEY=value2"
        mock_env_file.exists.return_value = True
        
        with patch("tools.git_remote.open", mock_open(read_data=env_content)):
            result = load_env()
        
        assert len(result) == 2
        assert "VALID_KEY" in result
        assert "ANOTHER_KEY" in result


# ═══════════════════════════════════════════════════════════════════════════
# Credential Loading Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestGetCredentials:
    """Test credential validation."""

    @patch("tools.git_remote.load_env")
    def test_get_credentials_all_present(self, mock_load_env):
        """All required credentials present."""
        mock_load_env.return_value = {
            "GITHUB_TOKEN": "token123",
            "GITHUB_USER": "user123",
            "GITHUB_REPO": "github.com/user/repo.git",
        }
        
        result = get_credentials()
        assert result["success"] is True
        assert result["GITHUB_TOKEN"] == "token123"
        assert result["GITHUB_USER"] == "user123"

    @patch("tools.git_remote.load_env")
    def test_get_credentials_missing_token(self, mock_load_env):
        """Missing GITHUB_TOKEN returns error."""
        mock_load_env.return_value = {
            "GITHUB_USER": "user123",
            "GITHUB_REPO": "repo",
        }
        
        result = get_credentials()
        assert result["success"] is False
        assert "GITHUB_TOKEN" in result["error"]

    @patch("tools.git_remote.load_env")
    def test_get_credentials_missing_user(self, mock_load_env):
        """Missing GITHUB_USER returns error."""
        mock_load_env.return_value = {
            "GITHUB_TOKEN": "token123",
            "GITHUB_REPO": "repo",
        }
        
        result = get_credentials()
        assert result["success"] is False
        assert "GITHUB_USER" in result["error"]

    @patch("tools.git_remote.load_env")
    def test_get_credentials_empty_values(self, mock_load_env):
        """Empty string values are treated as missing."""
        mock_load_env.return_value = {
            "GITHUB_TOKEN": "",
            "GITHUB_USER": "user",
            "GITHUB_REPO": "repo",
        }
        
        result = get_credentials()
        assert result["success"] is False


# ═══════════════════════════════════════════════════════════════════════════
# Git Command Execution Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestRunGit:
    """Test git command execution."""

    @patch("tools.git_remote.subprocess.run")
    def test_run_git_success(self, mock_run):
        """Successful git command."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="output here",
            stderr="",
        )
        
        result = run_git("status")
        assert result["success"] is True
        assert result["stdout"] == "output here"
        assert result["returncode"] == 0

    @patch("tools.git_remote.subprocess.run")
    def test_run_git_failure(self, mock_run):
        """Failed git command."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="error: pathspec 'invalid' did not match any file(s)",
        )
        
        result = run_git("add", "invalid")
        assert result["success"] is False
        assert result["returncode"] == 1
        assert "error" in result["stderr"]

    @patch("tools.git_remote.subprocess.run")
    def test_run_git_timeout(self, mock_run):
        """Git command timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired("git", 60)
        
        result = run_git("fetch")
        assert result["success"] is False
        assert "timed out" in result["error"]

    @patch("tools.git_remote.subprocess.run")
    def test_run_git_not_found(self, mock_run):
        """Git binary not found."""
        mock_run.side_effect = FileNotFoundError()
        
        result = run_git("status")
        assert result["success"] is False
        assert "not found" in result["error"]


# ═══════════════════════════════════════════════════════════════════════════
# Authenticated URL Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestAuthenticatedUrl:
    """Test authenticated URL construction."""

    def test_authenticated_url_https(self):
        """HTTPS URL is converted correctly."""
        url = authenticated_url(
            "https://github.com/user/repo.git",
            "token123",
            "user123"
        )
        assert url == "https://user123:token123@github.com/user/repo.git"

    def test_authenticated_url_ssh(self):
        """SSH URL is converted to HTTPS."""
        url = authenticated_url(
            "git@github.com:user/repo.git",
            "token123",
            "user123"
        )
        assert url == "https://user123:token123@github.com/user/repo.git"

    def test_authenticated_url_no_protocol(self):
        """URL without protocol."""
        url = authenticated_url(
            "github.com/user/repo.git",
            "token123",
            "user123"
        )
        assert url == "https://user123:token123@github.com/user/repo.git"

    def test_authenticated_url_adds_git_suffix(self):
        """Adds .git suffix if missing."""
        url = authenticated_url(
            "github.com/user/repo",
            "token123",
            "user123"
        )
        assert url.endswith(".git")


# ═══════════════════════════════════════════════════════════════════════════
# Action: Status Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestActionStatus:
    """Test status action."""

    @patch("tools.git_remote.run_git")
    def test_action_status_with_remote(self, mock_run_git):
        """Status with remote configured."""
        mock_run_git.side_effect = [
            {"success": True, "stdout": "origin\thttps://user:token@github.com/user/repo.git (fetch)"},
            {"success": True, "stdout": "main"},
            {"success": True, "stdout": "abc123 Latest commit"},
            {"success": True, "stdout": ""},
            {"success": True, "stdout": "1\t2"},
        ]
        
        result = action_status()
        assert result["success"] is True
        assert result["remote_configured"] is True
        assert "***@github.com" in result["origin_url"]  # Token redacted
        assert result["branch"] == "main"
        assert result["working_tree_clean"] is True

    @patch("tools.git_remote.run_git")
    def test_action_status_no_remote(self, mock_run_git):
        """Status without remote configured."""
        mock_run_git.side_effect = [
            {"success": True, "stdout": ""},  # No remotes
            {"success": True, "stdout": "main"},
            {"success": True, "stdout": ""},
            {"success": True, "stdout": ""},
        ]
        
        result = action_status()
        assert result["success"] is True
        assert result["remote_configured"] is False

    @patch("tools.git_remote.run_git")
    def test_action_status_dirty_working_tree(self, mock_run_git):
        """Status with uncommitted changes."""
        mock_run_git.side_effect = [
            {"success": True, "stdout": ""},
            {"success": True, "stdout": "main"},
            {"success": True, "stdout": ""},
            {"success": True, "stdout": " M file.txt\n?? newfile.txt"},
        ]
        
        result = action_status()
        assert result["working_tree_clean"] is False
        assert len(result["dirty_files"]) == 2


# ═══════════════════════════════════════════════════════════════════════════
# Action: Add Remote Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestActionAddRemote:
    """Test add-remote action."""

    @patch("tools.git_remote.get_credentials")
    @patch("tools.git_remote.run_git")
    def test_action_add_remote_new(self, mock_run_git, mock_creds):
        """Add remote when none exists."""
        mock_creds.return_value = {
            "success": True,
            "GITHUB_TOKEN": "token123",
            "GITHUB_USER": "user123",
            "GITHUB_REPO": "github.com/user/repo.git",
        }
        mock_run_git.side_effect = [
            {"success": False},  # get-url fails (no remote)
            {"success": True},   # add succeeds
        ]
        
        result = action_add_remote()
        assert result["success"] is True
        assert result["action"] == "added"

    @patch("tools.git_remote.get_credentials")
    @patch("tools.git_remote.run_git")
    def test_action_add_remote_update(self, mock_run_git, mock_creds):
        """Update existing remote."""
        mock_creds.return_value = {
            "success": True,
            "GITHUB_TOKEN": "token123",
            "GITHUB_USER": "user123",
            "GITHUB_REPO": "github.com/user/repo.git",
        }
        mock_run_git.side_effect = [
            {"success": True, "stdout": "https://old-url"},  # get-url succeeds
            {"success": True},   # set-url succeeds
        ]
        
        result = action_add_remote()
        assert result["success"] is True
        assert result["action"] == "updated"

    @patch("tools.git_remote.get_credentials")
    def test_action_add_remote_no_credentials(self, mock_creds):
        """Error if credentials missing."""
        mock_creds.return_value = {"success": False, "error": "Missing token"}
        
        result = action_add_remote()
        assert result["success"] is False


# ═══════════════════════════════════════════════════════════════════════════
# Action: Push/Pull Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestActionPushPull:
    """Test push and pull actions."""

    @patch("tools.git_remote.get_credentials")
    @patch("tools.git_remote.run_git")
    def test_action_push_success(self, mock_run_git, mock_creds):
        """Successful push."""
        mock_creds.return_value = {
            "success": True,
            "GITHUB_TOKEN": "token",
            "GITHUB_USER": "user",
            "GITHUB_REPO": "repo",
        }
        mock_run_git.side_effect = [
            {"success": True},  # get-url
            {"success": True, "stdout": "main"},  # branch
            {"success": True, "stderr": "To github.com\n * [new branch]"},  # push
        ]
        
        result = action_push()
        assert result["success"] is True
        assert "Pushed" in result["message"]

    @patch("tools.git_remote.get_credentials")
    @patch("tools.git_remote.run_git")
    def test_action_pull_success(self, mock_run_git, mock_creds):
        """Successful pull."""
        mock_creds.return_value = {
            "success": True,
            "GITHUB_TOKEN": "token",
            "GITHUB_USER": "user",
            "GITHUB_REPO": "repo",
        }
        mock_run_git.side_effect = [
            {"success": True},  # get-url
            {"success": True, "stdout": "main"},  # branch
            {"success": True, "stdout": "Already up to date"},  # pull
        ]
        
        result = action_pull()
        assert result["success"] is True
        assert "Pulled" in result["message"]


# ═══════════════════════════════════════════════════════════════════════════
# Action: Sync Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestActionSync:
    """Test sync (push + pull) action."""

    @patch("tools.git_remote.action_push")
    @patch("tools.git_remote.action_pull")
    def test_action_sync_success(self, mock_pull, mock_push):
        """Successful sync."""
        mock_push.return_value = {"success": True, "message": "Pushed"}
        mock_pull.return_value = {"success": True, "message": "Pulled"}
        
        result = action_sync()
        assert result["success"] is True
        assert "Sync complete" in result["message"]

    @patch("tools.git_remote.action_push")
    def test_action_sync_push_fails(self, mock_push):
        """Sync fails if push fails."""
        mock_push.return_value = {"success": False, "error": "Push failed"}
        
        result = action_sync()
        assert result["success"] is False
        assert result["phase"] == "push"

    @patch("tools.git_remote.action_push")
    @patch("tools.git_remote.action_pull")
    def test_action_sync_pull_fails(self, mock_pull, mock_push):
        """Sync fails if pull fails."""
        mock_push.return_value = {"success": True}
        mock_pull.return_value = {"success": False, "error": "Pull failed"}
        
        result = action_sync()
        assert result["success"] is False
        assert result["phase"] == "pull"


# ═══════════════════════════════════════════════════════════════════════════
# Security Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestSecurity:
    """Test that tokens are never exposed."""

    @patch("tools.git_remote.run_git")
    def test_status_redacts_token(self, mock_run_git):
        """Status action redacts token from URL."""
        mock_run_git.side_effect = [
            {"success": True, "stdout": "origin\thttps://user:ghp_secret123@github.com/repo.git (fetch)"},
            {"success": True, "stdout": "main"},
            {"success": True, "stdout": ""},
            {"success": True, "stdout": ""},
            {"success": True, "stdout": "0\t0"},  # rev-list ahead/behind
        ]
        
        result = action_status()
        assert "ghp_secret123" not in result["origin_url"]
        assert "***@github.com" in result["origin_url"]

    def test_authenticated_url_contains_token(self):
        """Authenticated URL intentionally contains token (for git use)."""
        url = authenticated_url("github.com/user/repo.git", "secret_token", "user")
        # This is correct behavior — git needs the token in the URL
        assert "secret_token" in url
        # But in production, this URL should never be printed/logged

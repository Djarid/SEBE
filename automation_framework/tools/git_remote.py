"""
Git remote operations for the SEBE automation framework.

Reads GitHub credentials from .env at the repository root and provides
CLI actions for remote management: add, push, pull, status.

Stdlib only. Run from automation_framework/:
    python -m tools.git_remote --action <action> [options]

Actions:
    status      Show remote config and sync state
    add-remote  Configure origin from .env credentials
    push        Push current branch to origin
    pull        Pull from origin into current branch
    sync        Push then pull (convenience)
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────

FRAMEWORK_ROOT = Path(__file__).parent.parent  # automation_framework/
REPO_ROOT = FRAMEWORK_ROOT.parent              # SEBE/
ENV_FILE = REPO_ROOT / ".env"


# ── .env reader ────────────────────────────────────────────────────────

def load_env() -> dict:
    """Parse .env file into a dict. Simple KEY=VALUE, no interpolation."""
    env = {}
    if not ENV_FILE.exists():
        return env
    with open(ENV_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip()
    return env


def get_credentials() -> dict:
    """Load and validate required GitHub credentials from .env."""
    env = load_env()
    required = ["GITHUB_TOKEN", "GITHUB_USER", "GITHUB_REPO"]
    missing = [k for k in required if k not in env or not env[k]]
    if missing:
        return {
            "success": False,
            "error": f"Missing .env keys: {', '.join(missing)}",
            "hint": f"Expected in {ENV_FILE}",
        }
    return {"success": True, **{k: env[k] for k in required}}


# ── Git helpers ────────────────────────────────────────────────────────

def run_git(*args, capture: bool = True) -> dict:
    """Run a git command from the repo root. Returns dict with output/error."""
    cmd = ["git"] + list(args)
    try:
        result = subprocess.run(
            cmd,
            cwd=REPO_ROOT,
            capture_output=capture,
            text=True,
            timeout=60,
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip() if capture else "",
            "stderr": result.stderr.strip() if capture else "",
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Git command timed out (60s)"}
    except FileNotFoundError:
        return {"success": False, "error": "git not found on PATH"}


def authenticated_url(repo_url: str, token: str, user: str) -> str:
    """Build an authenticated HTTPS URL for git push/pull.

    Accepts:
        https://github.com/User/Repo.git
        git@github.com:User/Repo.git
        github.com/User/Repo.git
    """
    # Normalise to path component
    url = repo_url.strip()
    if url.startswith("git@github.com:"):
        path = url.replace("git@github.com:", "")
    elif "github.com/" in url:
        path = url.split("github.com/", 1)[1]
    else:
        path = url

    # Ensure .git suffix
    if not path.endswith(".git"):
        path += ".git"

    return f"https://{user}:{token}@github.com/{path}"


# ── Actions ────────────────────────────────────────────────────────────

def action_status() -> dict:
    """Show remote configuration and sync state."""
    remotes = run_git("remote", "-v")
    branch = run_git("branch", "--show-current")
    log = run_git("log", "--oneline", "-5")
    status = run_git("status", "--porcelain")

    # Check if we have a remote configured
    has_origin = False
    origin_url = None
    if remotes["success"] and remotes["stdout"]:
        for line in remotes["stdout"].splitlines():
            if line.startswith("origin"):
                has_origin = True
                # Redact token from displayed URL
                parts = line.split()
                if len(parts) >= 2:
                    url = parts[1]
                    if "@" in url:
                        # Redact: https://user:token@github.com/... -> https://***@github.com/...
                        pre, at, post = url.partition("@")
                        origin_url = f"https://***@{post}"
                    else:
                        origin_url = url
                break

    # Check ahead/behind if remote exists
    ahead_behind = None
    if has_origin:
        ab = run_git("rev-list", "--left-right", "--count", "HEAD...origin/main")
        if ab["success"] and ab["stdout"]:
            parts = ab["stdout"].split()
            if len(parts) == 2:
                ahead_behind = {"ahead": int(parts[0]), "behind": int(parts[1])}

    return {
        "success": True,
        "remote_configured": has_origin,
        "origin_url": origin_url,
        "branch": branch.get("stdout", "unknown"),
        "recent_commits": log.get("stdout", "").splitlines() if log["success"] else [],
        "working_tree_clean": status["success"] and not status["stdout"],
        "dirty_files": status.get("stdout", "").splitlines() if status["success"] and status["stdout"] else [],
        "ahead_behind": ahead_behind,
    }


def action_add_remote() -> dict:
    """Configure origin remote from .env credentials."""
    creds = get_credentials()
    if not creds["success"]:
        return creds

    # Check if origin already exists
    check = run_git("remote", "get-url", "origin")
    if check["success"]:
        # Origin exists — update it
        auth_url = authenticated_url(
            creds["GITHUB_REPO"], creds["GITHUB_TOKEN"], creds["GITHUB_USER"]
        )
        result = run_git("remote", "set-url", "origin", auth_url)
        if result["success"]:
            return {
                "success": True,
                "action": "updated",
                "message": "Origin remote URL updated from .env credentials",
            }
        return {"success": False, "error": result.get("stderr", "Failed to update remote")}

    # Origin doesn't exist — add it
    auth_url = authenticated_url(
        creds["GITHUB_REPO"], creds["GITHUB_TOKEN"], creds["GITHUB_USER"]
    )
    result = run_git("remote", "add", "origin", auth_url)
    if result["success"]:
        return {
            "success": True,
            "action": "added",
            "message": "Origin remote added from .env credentials",
        }
    return {"success": False, "error": result.get("stderr", "Failed to add remote")}


def action_push(branch: str | None = None, force: bool = False) -> dict:
    """Push current branch to origin."""
    creds = get_credentials()
    if not creds["success"]:
        return creds

    # Ensure remote is configured
    check = run_git("remote", "get-url", "origin")
    if not check["success"]:
        add_result = action_add_remote()
        if not add_result["success"]:
            return add_result

    # Determine branch
    if not branch:
        br = run_git("branch", "--show-current")
        branch = br["stdout"] if br["success"] else "main"

    # Build push command
    args = ["push", "-u", "origin", branch]
    if force:
        args.insert(1, "--force")

    result = run_git(*args)
    if result["success"]:
        return {
            "success": True,
            "message": f"Pushed {branch} to origin",
            "branch": branch,
            "output": result.get("stderr", result.get("stdout", "")),
        }
    return {
        "success": False,
        "error": result.get("stderr", "Push failed"),
        "hint": "Check that the remote repo exists and token has push access",
    }


def action_pull(branch: str | None = None) -> dict:
    """Pull from origin into current branch."""
    creds = get_credentials()
    if not creds["success"]:
        return creds

    # Ensure remote is configured
    check = run_git("remote", "get-url", "origin")
    if not check["success"]:
        add_result = action_add_remote()
        if not add_result["success"]:
            return add_result

    # Determine branch
    if not branch:
        br = run_git("branch", "--show-current")
        branch = br["stdout"] if br["success"] else "main"

    result = run_git("pull", "origin", branch)
    if result["success"]:
        return {
            "success": True,
            "message": f"Pulled {branch} from origin",
            "branch": branch,
            "output": result.get("stdout", ""),
        }
    return {
        "success": False,
        "error": result.get("stderr", "Pull failed"),
    }


def action_sync(branch: str | None = None) -> dict:
    """Push then pull — convenience for full sync."""
    push_result = action_push(branch)
    if not push_result["success"]:
        return {"success": False, "phase": "push", **push_result}

    pull_result = action_pull(branch)
    if not pull_result["success"]:
        return {"success": False, "phase": "pull", "push": push_result, **pull_result}

    return {
        "success": True,
        "message": "Sync complete (push + pull)",
        "push": push_result,
        "pull": pull_result,
    }


# ── CLI ────────────────────────────────────────────────────────────────

ACTIONS = {
    "status": action_status,
    "add-remote": action_add_remote,
    "push": action_push,
    "pull": action_pull,
    "sync": action_sync,
}


def main():
    parser = argparse.ArgumentParser(
        description="Git remote operations for SEBE",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Actions:
  status        Show remote config and sync state
  add-remote    Configure origin from .env credentials
  push          Push current branch to origin
  pull          Pull from origin into current branch
  sync          Push then pull
        """,
    )
    parser.add_argument(
        "--action", required=True, choices=ACTIONS.keys(),
        help="Operation to perform",
    )
    parser.add_argument(
        "--branch", default=None,
        help="Branch name (default: current branch)",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Force push (use with caution)",
    )
    args = parser.parse_args()

    # Dispatch
    if args.action in ("push", "sync"):
        if args.action == "push":
            result = action_push(branch=args.branch, force=args.force)
        else:
            result = action_sync(branch=args.branch)
    elif args.action == "pull":
        result = action_pull(branch=args.branch)
    else:
        result = ACTIONS[args.action]()

    # Output
    status = "OK" if result.get("success") else "ERROR"
    msg = result.get("message", result.get("error", args.action))
    print(f"{status} {msg}", file=sys.stderr)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

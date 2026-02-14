"""
Tests for services/config.py.

Tests configuration dataclasses, .env loading, environment-based configuration.
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch

from services.config import (
    DaemonConfig,
    EmailConfig,
    LLMConfig,
    LLMModel,
    SignalConfig,
    _load_dotenv,
    get_config,
)


def test_llm_model_defaults():
    """Test LLMModel default values."""
    model = LLMModel(name="x", systemd_unit="y", role="default")
    assert model.startup_wait == 5.0


def test_llm_config_defaults():
    """Test LLMConfig default values."""
    config = LLMConfig()
    assert config.base_url == "http://localhost:8080/v1"
    assert config.api_key == "sk-local-no-auth"
    assert config.default_model == "qwen3"
    assert "qwen3" in config.models
    assert "oss120" in config.models
    assert config.models["qwen3"].role == "default"
    assert config.models["oss120"].role == "batch"
    assert config.swap_timeout == 120.0


def test_signal_config_defaults():
    """Test SignalConfig default values."""
    config = SignalConfig()
    assert config.account == ""
    assert config.api_port == 8082
    assert config.owner_number == ""


def test_email_config_defaults():
    """Test EmailConfig default values."""
    config = EmailConfig()
    assert config.imap_port == 1143
    assert config.smtp_port == 1025
    assert config.sender_address == ""
    assert config.watch_folders == ["INBOX"]


def test_daemon_config_defaults():
    """Test DaemonConfig default values."""
    config = DaemonConfig()
    assert config.poll_interval == 30
    assert config.approval_timeout == 3600
    assert config.log_level == "INFO"


def test_load_dotenv_parses_file(tmp_path):
    """Test that _load_dotenv parses .env file correctly."""
    env_file = tmp_path / ".env"
    env_file.write_text("""FOO=bar
QUOTED="baz"
# comment line
SPACED = qux
EMPTY=

""")
    
    with patch("services.config.DOTENV_PATH", env_file):
        result = _load_dotenv()
    
    assert result["FOO"] == "bar"
    assert result["QUOTED"] == "baz"
    assert result["SPACED"] == "qux"
    # Empty values should be included
    assert "EMPTY" in result


def test_load_dotenv_missing_file(tmp_path):
    """Test that _load_dotenv returns empty dict when file missing."""
    nonexistent = tmp_path / "nonexistent.env"
    
    with patch("services.config.DOTENV_PATH", nonexistent):
        result = _load_dotenv()
    
    assert result == {}


def test_from_env_reads_environ(monkeypatch):
    """Test that DaemonConfig.from_env reads environment variables."""
    monkeypatch.setenv("SIGNAL_ACCOUNT", "+447000000000")
    monkeypatch.setenv("SIGNAL_OWNER_NUMBER", "+447000000001")
    monkeypatch.setenv("PROTON_USERNAME", "test@pm.me")
    monkeypatch.setenv("PROTON_PASSWORD", "secret")
    monkeypatch.setenv("EMAIL_SENDER", "test@example.com")
    monkeypatch.setenv("LLM_BASE_URL", "http://remote:9090/v1")
    
    config = DaemonConfig.from_env()
    
    assert config.signal.account == "+447000000000"
    assert config.signal.owner_number == "+447000000001"
    assert config.email.username == "test@pm.me"
    assert config.email.password == "secret"
    assert config.email.sender_address == "test@example.com"
    assert config.llm.base_url == "http://remote:9090/v1"


def test_get_config_returns_daemon_config():
    """Test that get_config returns DaemonConfig instance."""
    config = get_config()
    assert isinstance(config, DaemonConfig)

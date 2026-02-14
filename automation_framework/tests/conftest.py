"""
Shared fixtures for the SEBE daemon test suite.
"""

import os
import pytest
from pathlib import Path
from unittest.mock import MagicMock

from services.config import (
    DaemonConfig,
    LLMConfig,
    LLMModel,
    SignalConfig,
    EmailConfig,
)
from services.llm_client import LLMClient, ModelManager
from services.channels.base import (
    ChannelType,
    InboundMessage,
    OutboundMessage,
    PendingAction,
    Urgency,
)
from services.channels.email_channel import EmailChannel
from services.channels.signal_channel import SignalChannel


@pytest.fixture
def llm_config():
    """Standard LLM config for testing."""
    return LLMConfig(
        base_url="http://localhost:9999/v1",
        api_key="sk-test-key",
        models={
            "qwen3": LLMModel(
                name="test-qwen3",
                systemd_unit="llama-qwen3",
                role="default",
                startup_wait=0.1,
            ),
            "oss120": LLMModel(
                name="test-oss120",
                systemd_unit="llama-oss120",
                role="batch",
                startup_wait=0.1,
            ),
        },
        swap_timeout=2.0,
    )


@pytest.fixture
def signal_config():
    """Standard Signal config for testing."""
    return SignalConfig(
        binary="/usr/bin/true",
        account="+447000000000",
        api_port=8082,
        owner_number="+447000000001",
    )


@pytest.fixture
def email_config():
    """Standard email config for testing."""
    return EmailConfig(
        imap_host="127.0.0.1",
        imap_port=1143,
        smtp_host="127.0.0.1",
        smtp_port=1025,
        username="test@example.com",
        password="testpass",
        sender_address="test@example.com",
        watch_folders=["INBOX"],
        poll_interval=5,
    )


@pytest.fixture
def daemon_config(llm_config, signal_config, email_config):
    """Full daemon config for testing."""
    return DaemonConfig(
        llm=llm_config,
        signal=signal_config,
        email=email_config,
        poll_interval=1,
        approval_timeout=60,
    )


@pytest.fixture
def sample_inbound_email():
    """A sample inbound email message."""
    from datetime import datetime
    return InboundMessage(
        channel=ChannelType.EMAIL,
        sender="pdc@greenparty.org.uk",
        subject="Re: SEBE - Policy Proposal",
        body="Thank you for your submission. We suggest the Economy PWG.",
        timestamp=datetime(2026, 2, 14, 12, 0, 0),
        message_id="<abc123@greenparty.org.uk>",
        reply_to="<original@example.com>",
        thread_id="<original@example.com>",
    )


@pytest.fixture
def sample_inbound_signal():
    """A sample inbound Signal message from the owner."""
    from datetime import datetime
    return InboundMessage(
        channel=ChannelType.SIGNAL,
        sender="+447000000001",
        subject="",
        body="APPROVE abc123",
        timestamp=datetime(2026, 2, 14, 12, 0, 0),
        message_id="signal-1234567890",
    )


@pytest.fixture
def sample_outbound_email():
    """A sample outbound email message."""
    return OutboundMessage(
        channel=ChannelType.EMAIL,
        recipient="pdc@greenparty.org.uk",
        subject="Re: SEBE - Policy Proposal",
        body="Thank you for directing me to the Economy PWG.",
        reply_to="<abc123@greenparty.org.uk>",
    )


@pytest.fixture
def sample_pending_action(sample_outbound_email):
    """A sample pending action."""
    from datetime import datetime
    return PendingAction(
        action_id="abc123",
        action_type="reply_email",
        description="Reply to pdc@greenparty.org.uk: Re: SEBE",
        outbound=sample_outbound_email,
        created_at=datetime(2026, 2, 14, 12, 0, 0),
    )


# ── Tools/ fixtures ────────────────────────────────────────────────────────

@pytest.fixture
def tmp_memory_db(tmp_path, monkeypatch):
    """In-memory SQLite database for memory system tests."""
    import sqlite3
    from tools.memory import config
    
    # Use in-memory database
    monkeypatch.setattr(config, "DB_PATH", ":memory:")
    monkeypatch.setattr(config, "DATA_DIR", tmp_path / "data")
    
    # Create connection and tables
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    
    yield conn
    
    conn.close()


@pytest.fixture
def tmp_memory_dirs(tmp_path, monkeypatch):
    """Temporary directory structure for memory file operations."""
    from tools.memory import config
    
    memory_dir = tmp_path / "memory"
    logs_dir = memory_dir / "logs"
    data_dir = tmp_path / "data"
    context_dir = tmp_path / "context"
    
    memory_dir.mkdir()
    logs_dir.mkdir()
    data_dir.mkdir()
    context_dir.mkdir()
    
    # Patch config paths in config module
    monkeypatch.setattr(config, "MEMORY_DIR", memory_dir)
    monkeypatch.setattr(config, "MEMORY_FILE", memory_dir / "MEMORY.md")
    monkeypatch.setattr(config, "LOGS_DIR", logs_dir)
    monkeypatch.setattr(config, "DATA_DIR", data_dir)
    monkeypatch.setattr(config, "DB_PATH", data_dir / "memory.db")
    monkeypatch.setattr(config, "CONTEXT_DIR", context_dir)
    monkeypatch.setattr(config, "PROJECT_CONTEXT", context_dir / "project_context.md")
    monkeypatch.setattr(config, "AUTHOR_CONTEXT", context_dir / "author_context.md")
    
    # Patch paths where they're imported and used (reader.py, writer.py, export.py)
    monkeypatch.setattr("tools.memory.reader.MEMORY_FILE", memory_dir / "MEMORY.md")
    monkeypatch.setattr("tools.memory.reader.LOGS_DIR", logs_dir)
    
    monkeypatch.setattr("tools.memory.writer.MEMORY_FILE", memory_dir / "MEMORY.md")
    monkeypatch.setattr("tools.memory.writer.MEMORY_DIR", memory_dir)
    monkeypatch.setattr("tools.memory.writer.LOGS_DIR", logs_dir)
    
    monkeypatch.setattr("tools.memory.export.DATA_DIR", data_dir)
    monkeypatch.setattr("tools.memory.export.EXPORT_DIR", data_dir / "exports")
    
    return {
        "memory_dir": memory_dir,
        "logs_dir": logs_dir,
        "data_dir": data_dir,
        "context_dir": context_dir,
    }

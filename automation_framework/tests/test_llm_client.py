"""
Tests for services/llm_client.py.

Tests LLMClient HTTP operations and ModelManager systemd model swapping.
"""

import json
import pytest
import time
from io import BytesIO
from unittest.mock import MagicMock, Mock, patch, call
from urllib.error import HTTPError, URLError

from services.llm_client import LLMClient, ModelManager, _ModelContext


def test_detect_model_id_success(llm_config):
    """Test successful model ID detection."""
    mock_response = Mock()
    mock_response.read.return_value = json.dumps({
        "data": [{"id": "test-model-id"}]
    }).encode()
    mock_response.__enter__ = Mock(return_value=mock_response)
    mock_response.__exit__ = Mock(return_value=False)
    
    with patch("urllib.request.urlopen", return_value=mock_response):
        client = LLMClient(llm_config)
        model_id = client._detect_model_id()
    
    assert model_id == "test-model-id"


def test_detect_model_id_failure(llm_config):
    """Test model ID detection failure."""
    with patch("urllib.request.urlopen", side_effect=URLError("connection refused")):
        client = LLMClient(llm_config)
        model_id = client._detect_model_id()
    
    assert model_id == "unknown"


def test_chat_sends_correct_payload(llm_config):
    """Test that chat() sends correct HTTP request."""
    mock_response = Mock()
    mock_response.read.return_value = json.dumps({
        "choices": [{"message": {"content": "hello"}}]
    }).encode()
    mock_response.__enter__ = Mock(return_value=mock_response)
    mock_response.__exit__ = Mock(return_value=False)
    
    captured_request = None
    
    def capture_urlopen(req, timeout=None):
        nonlocal captured_request
        captured_request = req
        return mock_response
    
    with patch("urllib.request.urlopen", side_effect=capture_urlopen):
        client = LLMClient(llm_config)
        response = client.chat([{"role": "user", "content": "test"}])
    
    assert captured_request is not None
    assert captured_request.get_header("Content-type") == "application/json"
    assert captured_request.get_header("Authorization") == f"Bearer {llm_config.api_key}"
    
    # Parse the payload
    payload = json.loads(captured_request.data)
    assert "model" in payload
    assert payload["messages"] == [{"role": "user", "content": "test"}]
    assert "temperature" in payload
    assert "max_tokens" in payload
    
    assert response["choices"][0]["message"]["content"] == "hello"


def test_chat_with_system_prompt(llm_config):
    """Test that system prompt is prepended to messages."""
    mock_response = Mock()
    mock_response.read.return_value = json.dumps({
        "choices": [{"message": {"content": "response"}}]
    }).encode()
    mock_response.__enter__ = Mock(return_value=mock_response)
    mock_response.__exit__ = Mock(return_value=False)
    
    captured_request = None
    
    def capture_urlopen(req, timeout=None):
        nonlocal captured_request
        captured_request = req
        return mock_response
    
    with patch("urllib.request.urlopen", side_effect=capture_urlopen):
        client = LLMClient(llm_config)
        client.chat([{"role": "user", "content": "test"}], system_prompt="you are a bot")
    
    payload = json.loads(captured_request.data)
    assert payload["messages"][0] == {"role": "system", "content": "you are a bot"}
    assert payload["messages"][1] == {"role": "user", "content": "test"}


def test_chat_simple_returns_text(llm_config):
    """Test chat_simple returns assistant text."""
    mock_response = Mock()
    mock_response.read.return_value = json.dumps({
        "choices": [{"message": {"content": "response text"}}]
    }).encode()
    mock_response.__enter__ = Mock(return_value=mock_response)
    mock_response.__exit__ = Mock(return_value=False)
    
    with patch("urllib.request.urlopen", return_value=mock_response):
        client = LLMClient(llm_config)
        result = client.chat_simple("hi")
    
    assert result == "response text"


def test_chat_simple_empty_choices(llm_config):
    """Test chat_simple with empty choices."""
    mock_response = Mock()
    mock_response.read.return_value = json.dumps({"choices": []}).encode()
    mock_response.__enter__ = Mock(return_value=mock_response)
    mock_response.__exit__ = Mock(return_value=False)
    
    with patch("urllib.request.urlopen", return_value=mock_response):
        client = LLMClient(llm_config)
        result = client.chat_simple("hi")
    
    assert result == ""


def test_chat_http_error(llm_config):
    """Test chat raises HTTPError on HTTP failure."""
    error = HTTPError("url", 500, "Internal", {}, BytesIO(b"error"))
    
    with patch("urllib.request.urlopen", side_effect=error):
        client = LLMClient(llm_config)
        with pytest.raises(HTTPError):
            client.chat([{"role": "user", "content": "test"}])


def test_chat_url_error(llm_config):
    """Test chat raises URLError on connection failure."""
    with patch("urllib.request.urlopen", side_effect=URLError("connection refused")):
        client = LLMClient(llm_config)
        with pytest.raises(URLError):
            client.chat([{"role": "user", "content": "test"}])


def test_is_available_true(llm_config):
    """Test is_available returns True when API responds."""
    mock_response = Mock()
    mock_response.status = 200
    mock_response.read.return_value = json.dumps({"data": []}).encode()
    mock_response.__enter__ = Mock(return_value=mock_response)
    mock_response.__exit__ = Mock(return_value=False)
    
    with patch("urllib.request.urlopen", return_value=mock_response):
        client = LLMClient(llm_config)
        assert client.is_available() is True


def test_is_available_false(llm_config):
    """Test is_available returns False on exception."""
    with patch("urllib.request.urlopen", side_effect=URLError("error")):
        client = LLMClient(llm_config)
        assert client.is_available() is False


def test_model_manager_systemctl(llm_config):
    """Test ModelManager._systemctl calls systemctl correctly."""
    mock_client = Mock()
    manager = ModelManager(llm_config, mock_client)
    
    mock_result = Mock()
    mock_result.returncode = 0
    
    with patch("subprocess.run", return_value=mock_result) as mock_run:
        result = manager._systemctl("start", "llama-qwen3")
    
    assert result is True
    mock_run.assert_called_once_with(
        ["systemctl", "--user", "start", "llama-qwen3"],
        capture_output=True,
        text=True,
        timeout=30
    )


def test_model_manager_systemctl_failure(llm_config):
    """Test _systemctl returns False on non-zero exit code."""
    mock_client = Mock()
    manager = ModelManager(llm_config, mock_client)
    
    mock_result = Mock()
    mock_result.returncode = 1
    mock_result.stderr = "failed"
    
    with patch("subprocess.run", return_value=mock_result):
        result = manager._systemctl("stop", "llama-qwen3")
    
    assert result is False


def test_model_manager_ensure_model(llm_config):
    """Test ensure_model starts model and waits for ready."""
    mock_client = Mock()
    mock_client.is_available.side_effect = [False, True]  # Ready after 1 check
    
    manager = ModelManager(llm_config, mock_client)
    
    mock_result = Mock()
    mock_result.returncode = 0
    
    with patch("subprocess.run", return_value=mock_result), \
         patch("time.sleep"), \
         patch("time.monotonic", return_value=0):
        result = manager.ensure_model("qwen3")
    
    assert result is True
    assert manager._active_model == "qwen3"


def test_model_manager_ensure_model_already_active(llm_config):
    """Test ensure_model skips swap when already active."""
    mock_client = Mock()
    mock_client.is_available.return_value = True
    
    manager = ModelManager(llm_config, mock_client)
    manager._active_model = "qwen3"
    
    with patch("subprocess.run") as mock_run:
        result = manager.ensure_model("qwen3")
    
    assert result is True
    mock_run.assert_not_called()


def test_model_manager_ensure_model_swap(llm_config):
    """Test ensure_model swaps from one model to another."""
    mock_client = Mock()
    mock_client.is_available.side_effect = [
        False,  # After stop
        False,  # First wait_for_ready check
        True,   # Second wait_for_ready check
    ]
    
    manager = ModelManager(llm_config, mock_client)
    manager._active_model = "qwen3"
    
    mock_result = Mock()
    mock_result.returncode = 0
    
    with patch("subprocess.run", return_value=mock_result) as mock_run, \
         patch("time.sleep"), \
         patch("time.monotonic", return_value=0):
        result = manager.ensure_model("oss120")
    
    assert result is True
    assert manager._active_model == "oss120"
    
    # Verify stop called for qwen3, start called for oss120
    calls = mock_run.call_args_list
    assert any("stop" in str(c) and "llama-qwen3" in str(c) for c in calls)
    assert any("start" in str(c) and "llama-oss120" in str(c) for c in calls)


def test_model_manager_ensure_default(llm_config):
    """Test ensure_default starts default model."""
    mock_client = Mock()
    # _active_model is None so ensure_model hits the else branch:
    #   1. Stops all known models -> _wait_for_stopped needs is_available=False
    #   2. Starts the default model -> time.sleep(startup_wait), then
    #      _wait_for_ready needs is_available=True
    mock_client.is_available.side_effect = [
        False,  # _wait_for_stopped check -> not available = stopped
        True,   # _wait_for_ready check -> available = ready
    ]
    
    manager = ModelManager(llm_config, mock_client)
    
    mock_result = Mock()
    mock_result.returncode = 0
    
    with patch("subprocess.run", return_value=mock_result), \
         patch("time.sleep"), \
         patch("time.monotonic", side_effect=range(100)):
        result = manager.ensure_default()
    
    assert result is True
    assert manager._active_model == "qwen3"


def test_model_manager_unknown_model(llm_config):
    """Test ensure_model fails for unknown model."""
    mock_client = Mock()
    manager = ModelManager(llm_config, mock_client)
    
    result = manager.ensure_model("nonexistent")
    assert result is False


def test_model_context_manager(llm_config):
    """Test context manager swaps model and restores."""
    mock_client = Mock()
    mock_client.is_available.return_value = True
    
    manager = ModelManager(llm_config, mock_client)
    manager._active_model = "qwen3"
    
    mock_result = Mock()
    mock_result.returncode = 0
    
    with patch("subprocess.run", return_value=mock_result), \
         patch("time.sleep"), \
         patch("time.monotonic", side_effect=range(100)):
        with manager.use("oss120"):
            assert manager._active_model == "oss120"
        
        # After exit, should restore qwen3
        assert manager._active_model == "qwen3"


def test_model_context_manager_failure(llm_config):
    """Test context manager raises on model start failure."""
    mock_client = Mock()
    mock_client.is_available.return_value = False
    
    manager = ModelManager(llm_config, mock_client)
    
    mock_result = Mock()
    mock_result.returncode = 0
    
    with patch("subprocess.run", return_value=mock_result), \
         patch("time.sleep"), \
         patch("time.monotonic", side_effect=range(100)):
        with pytest.raises(RuntimeError):
            with manager.use("oss120"):
                pass


def test_model_manager_status(llm_config):
    """Test status returns correct information."""
    mock_client = Mock()
    mock_client.is_available.return_value = True
    
    manager = ModelManager(llm_config, mock_client)
    manager._active_model = "qwen3"
    
    status = manager.status()
    
    assert status["active_model"] == "qwen3"
    assert status["api_available"] is True
    assert status["default_model"] == "qwen3"

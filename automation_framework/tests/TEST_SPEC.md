# SEBE Daemon Test Specification

Target: ~80% coverage across `services/` package.
Framework: pytest + pytest-cov (installed in .venv)
Run from: `automation_framework/`
Command: `source .venv/bin/activate && pytest tests/ -v --cov=services --cov-report=term-missing`

All tests use `unittest.mock` (stdlib). No external services needed.

---

## pytest configuration

Create `automation_framework/pytest.ini`:
```ini
[pytest]
testpaths = tests
pythonpath = .
```

## Shared fixtures: `tests/conftest.py`

Already written. Provides: `llm_config`, `signal_config`, `email_config`,
`daemon_config`, `sample_inbound_email`, `sample_inbound_signal`,
`sample_outbound_email`, `sample_pending_action`.

---

## 1. tests/test_config.py

Test `services/config.py`. Key classes: `LLMModel`, `LLMConfig`,
`SignalConfig`, `EmailConfig`, `DaemonConfig`, `_load_dotenv`, `get_config`.

### Tests to write:

**test_llm_model_defaults**
- Create `LLMModel(name="x", systemd_unit="y", role="default")`
- Assert `startup_wait == 5.0`

**test_llm_config_defaults**
- Create `LLMConfig()`
- Assert `base_url == "http://localhost:8080/v1"`
- Assert `api_key == "sk-local-no-auth"`
- Assert `default_model == "qwen3"`
- Assert `"qwen3" in models and "oss120" in models`
- Assert `models["qwen3"].role == "default"`
- Assert `models["oss120"].role == "batch"`
- Assert `swap_timeout == 120.0`

**test_signal_config_defaults**
- Create `SignalConfig()`
- Assert `account == ""`, `api_port == 8082`, `owner_number == ""`

**test_email_config_defaults**
- Create `EmailConfig()`
- Assert `imap_port == 1143`, `smtp_port == 1025`
- Assert `sender_address == ""`
- Assert `watch_folders == ["INBOX"]`

**test_daemon_config_defaults**
- Create `DaemonConfig()`
- Assert `poll_interval == 30`, `approval_timeout == 3600`
- Assert `log_level == "INFO"`

**test_load_dotenv_parses_file**
- Use `tmp_path` fixture to create a temp .env file with:
  ```
  FOO=bar
  QUOTED="baz"
  # comment
  SPACED = qux
  ```
- Monkey-patch `services.config.DOTENV_PATH` to point at the temp file
- Call `_load_dotenv()`, assert `{"FOO": "bar", "QUOTED": "baz", "SPACED": "qux"}`

**test_load_dotenv_missing_file**
- Monkey-patch `DOTENV_PATH` to a nonexistent path
- Call `_load_dotenv()`, assert returns `{}`

**test_from_env_reads_environ**
- Use `monkeypatch.setenv` to set:
  - `SIGNAL_ACCOUNT=+447000000000`
  - `SIGNAL_OWNER_NUMBER=+447000000001`
  - `PROTON_USERNAME=test@pm.me`
  - `PROTON_PASSWORD=secret`
  - `EMAIL_SENDER=test@example.com`
  - `LLM_BASE_URL=http://remote:9090/v1`
- Call `DaemonConfig.from_env()`
- Assert all values propagated correctly

**test_get_config_returns_daemon_config**
- Call `get_config()`, assert `isinstance(result, DaemonConfig)`

---

## 2. tests/test_llm_client.py

Test `services/llm_client.py`. Key classes: `LLMClient`, `ModelManager`,
`_ModelContext`.

### Mock boundaries:
- `urllib.request.urlopen` — mock all HTTP calls
- `subprocess.run` — mock all systemctl calls
- `time.sleep` — mock to avoid real waits
- `time.monotonic` — mock for timeout testing

### Tests to write:

**test_detect_model_id_success**
- Mock `urlopen` to return `{"data": [{"id": "test-model-id"}]}`
- Create `LLMClient(llm_config)`, access `client.model_id`
- Assert returns `"test-model-id"`

**test_detect_model_id_failure**
- Mock `urlopen` to raise `URLError`
- Assert `model_id` returns `"unknown"`

**test_chat_sends_correct_payload**
- Mock `urlopen` to return a valid chat completion response:
  `{"choices": [{"message": {"content": "hello"}}]}`
- Call `client.chat([{"role": "user", "content": "test"}])`
- Capture the Request object passed to urlopen
- Assert payload contains `model`, `messages`, `temperature`, `max_tokens`
- Assert Content-Type and Authorization headers set

**test_chat_with_system_prompt**
- Mock `urlopen` as above
- Call `client.chat(messages, system_prompt="you are a bot")`
- Assert first message in payload is `{"role": "system", "content": "you are a bot"}`

**test_chat_simple_returns_text**
- Mock `urlopen` to return `{"choices": [{"message": {"content": "response text"}}]}`
- Assert `client.chat_simple("hi")` returns `"response text"`

**test_chat_simple_empty_choices**
- Mock `urlopen` to return `{"choices": []}`
- Assert returns `""`

**test_chat_http_error**
- Mock `urlopen` to raise `HTTPError(url, 500, "Internal", {}, BytesIO(b"err"))`
- Assert `client.chat(...)` raises `HTTPError`

**test_chat_url_error**
- Mock `urlopen` to raise `URLError("connection refused")`
- Assert `client.chat(...)` raises `URLError`

**test_is_available_true**
- Mock `urlopen` to return response with `status == 200`
- Assert `client.is_available()` returns `True`

**test_is_available_false**
- Mock `urlopen` to raise exception
- Assert returns `False`

**test_model_manager_systemctl**
- Create `ModelManager(llm_config, mock_client)`
- Mock `subprocess.run` to return `returncode=0`
- Call `manager._systemctl("start", "llama-qwen3")`
- Assert `subprocess.run` called with `["systemctl", "--user", "start", "llama-qwen3"]`

**test_model_manager_systemctl_failure**
- Mock `subprocess.run` to return `returncode=1, stderr="failed"`
- Assert `_systemctl()` returns `False`

**test_model_manager_ensure_model**
- Mock `subprocess.run` (returncode=0) and `client.is_available()` (True after 1 call)
- Mock `time.sleep` and `time.monotonic`
- Call `manager.ensure_model("qwen3")`
- Assert returns `True`, `active_model == "qwen3"`

**test_model_manager_ensure_model_already_active**
- Set `manager._active_model = "qwen3"`
- Mock `client.is_available()` returns `True`
- Call `manager.ensure_model("qwen3")`
- Assert `subprocess.run` NOT called (no swap needed)

**test_model_manager_ensure_model_swap**
- Set `manager._active_model = "qwen3"`
- Mock everything
- Call `manager.ensure_model("oss120")`
- Assert stop called for qwen3, start called for oss120

**test_model_manager_ensure_default**
- Mock everything, call `manager.ensure_default()`
- Assert `ensure_model("qwen3")` effectively called

**test_model_manager_unknown_model**
- Call `manager.ensure_model("nonexistent")`
- Assert returns `False`

**test_model_context_manager**
- Set `manager._active_model = "qwen3"`, mock everything
- Use `with manager.use("oss120"): pass`
- Assert oss120 started, then qwen3 restored after exit

**test_model_context_manager_failure**
- Mock `ensure_model` to return `False`
- Assert `with manager.use("oss120")` raises `RuntimeError`

**test_model_manager_status**
- Mock `client.is_available()` returns `True`
- Set `manager._active_model = "qwen3"`
- Assert `manager.status()` returns correct dict

---

## 3. tests/test_channels_base.py

Test `services/channels/base.py`. Mostly dataclass and enum tests.

### Tests to write:

**test_channel_type_values**
- Assert `ChannelType.EMAIL.value == "email"`, etc. for all 4

**test_urgency_values**
- Assert all 4 urgency levels have correct string values

**test_inbound_message_defaults**
- Create `InboundMessage(...)` with required fields only
- Assert `urgency == Urgency.NORMAL`, `classification is None`
- Assert `attachments == []`, `raw is None`

**test_outbound_message_creation**
- Create `OutboundMessage(...)`, assert all fields

**test_pending_action_defaults**
- Create `PendingAction(...)`, assert `status == "pending"`
- Assert `approved_at is None`

**test_base_channel_is_abstract**
- Assert `BaseChannel()` raises `TypeError` (can't instantiate ABC)

---

## 4. tests/test_email_channel.py

Test `services/channels/email_channel.py`.

### Mock boundaries:
- `imaplib.IMAP4` — mock the IMAP connection entirely
- `smtplib.SMTP` — mock SMTP sending
- `ssl.create_default_context` — mock SSL context

### Tests to write:

**test_email_channel_type**
- Assert `EmailChannel(config).channel_type == ChannelType.EMAIL`

**test_poll_no_unseen**
- Mock IMAP: `select` returns OK, `search(None, "UNSEEN")` returns `(OK, [b""])`
- Assert `poll()` returns `[]`

**test_poll_with_messages**
- Mock IMAP: search returns `(OK, [b"1 2"])`
- Mock `fetch` to return a valid RFC822 email bytes for each
- Build a minimal email: `From: test@example.com\r\nSubject: Test\r\n\r\nBody text`
- Assert `poll()` returns 2 `InboundMessage` objects
- Assert `sender == "test@example.com"`, `subject == "Test"`, `body == "Body text"`

**test_poll_multipart_email**
- Build a multipart MIME email with text/plain and text/html parts
- Assert `poll()` extracts the text/plain part

**test_poll_html_only_email**
- Build a multipart MIME email with only text/html
- Assert body contains the HTML content

**test_poll_connection_failure**
- Mock IMAP constructor to raise `Exception`
- Assert `poll()` returns `[]` (doesn't crash)

**test_poll_fetch_error**
- Mock search returns messages, but fetch raises for one
- Assert partial results returned (other messages still processed)

**test_send_success**
- Mock SMTP context manager, `send_message` succeeds
- Call `channel.send(outbound_message)`
- Assert returns `True`
- Assert `send_message` called with correct From/To/Subject

**test_send_with_reply_headers**
- Create outbound with `reply_to` set
- Assert email has `In-Reply-To` and `References` headers

**test_send_failure**
- Mock SMTP to raise `smtplib.SMTPException`
- Assert `send()` returns `False`

**test_is_available_true**
- Mock IMAP connects and `noop()` succeeds
- Assert `is_available()` returns `True`

**test_is_available_false**
- Mock IMAP raises on connect
- Assert returns `False`

---

## 5. tests/test_signal_channel.py

Test `services/channels/signal_channel.py`.

### Mock boundary:
- `subprocess.run` — mock all signal-cli calls

### Tests to write:

**test_signal_channel_type**
- Assert `channel_type == ChannelType.SIGNAL`

**test_run_signal_cli_success**
- Mock `subprocess.run` returns `(returncode=0, stdout='{"ok":true}')`
- Assert `_run_signal_cli("receive")` returns the stdout string

**test_run_signal_cli_failure**
- Mock `subprocess.run` returns `returncode=1`
- Assert returns `None`

**test_run_signal_cli_not_found**
- Mock `subprocess.run` raises `FileNotFoundError`
- Assert returns `None`

**test_run_signal_cli_timeout**
- Mock `subprocess.run` raises `subprocess.TimeoutExpired`
- Assert returns `None`

**test_poll_parses_messages**
- Mock `_run_signal_cli` to return JSON lines with valid envelope+dataMessage
- Assert `poll()` returns list of `InboundMessage`
- Assert sender, body, timestamp parsed correctly

**test_poll_skips_receipts**
- Return JSON with envelope but no `dataMessage` (e.g. receipt)
- Assert `poll()` returns `[]`

**test_poll_empty**
- Mock returns empty string
- Assert returns `[]`

**test_send_success**
- Mock `_run_signal_cli` returns non-None
- Assert `send(outbound)` returns `True`

**test_send_failure**
- Mock returns `None`
- Assert returns `False`

**test_send_to_owner**
- Mock `send`, call `send_to_owner("hello")`
- Assert `send` called with owner_number as recipient

**test_send_to_owner_no_number**
- Set `config.owner_number = ""`
- Assert `send_to_owner(...)` returns `False`

**test_notify_with_action_id**
- Mock `send_to_owner`
- Call `notify("summary", action_id="abc123")`
- Assert message contains "APPROVE abc123" and "DENY abc123"

**test_notify_without_action_id**
- Call `notify("summary")`
- Assert message is just the summary, no APPROVE/DENY

**test_is_owner_message**
- Create `InboundMessage` with `sender=config.owner_number`
- Assert `is_owner_message()` returns `True`
- Change sender, assert `False`

**test_parse_command**
- `parse_command("APPROVE abc123")` -> `("APPROVE", ["abc123"])`
- `parse_command("status")` -> `("STATUS", [])`
- `parse_command("  deny  xyz  ")` -> `("DENY", ["xyz"])`
- `parse_command("")` -> `("", [])`

**test_is_available_no_account**
- Set `config.account = ""`
- Assert `is_available()` returns `False`

---

## 6. tests/test_orchestrator.py

Test `services/orchestrator.py`. This is the most complex module.

### Mock boundaries:
- All channel adapters (mock `poll()`, `send()`, `is_available()`)
- `LLMClient` (mock `chat_simple()`, `is_available()`)
- `ModelManager` (mock `ensure_default()`, `ensure_model()`, `status()`)
- `signal.signal` — mock to avoid registering real signal handlers
- `time.sleep` — mock to avoid real waits

### Tests to write:

**test_orchestrator_init_with_credentials**
- Create `Orchestrator(daemon_config)` where email and signal have credentials
- Assert both channels present in `self.channels`

**test_orchestrator_init_no_credentials**
- Create config with empty username/password/account
- Assert channels dict is empty

**test_handle_owner_command_approve**
- Setup: put a `PendingAction` in `orchestrator.pending`
- Mock the email channel's `send()` returns `True`
- Mock signal's `send_to_owner()`
- Create inbound signal message with body "APPROVE abc123"
- Call `_handle_owner_command(msg)`
- Assert action.status == "approved"
- Assert channel.send() called with the outbound message

**test_handle_owner_command_approve_nonexistent**
- Call with "APPROVE nonexistent"
- Assert signal notified "No pending action"

**test_handle_owner_command_deny**
- Put action in pending, call "DENY abc123"
- Assert action.status == "denied"

**test_handle_owner_command_status**
- Mock `model_manager.status()`, channel `is_available()`
- Call "STATUS"
- Assert signal.send_to_owner called with status text

**test_handle_owner_command_tasks_empty**
- Call "TASKS" with no pending
- Assert "No pending actions"

**test_handle_owner_command_tasks_with_pending**
- Add 2 pending actions
- Call "TASKS"
- Assert both action IDs in the message

**test_handle_owner_command_swap**
- Mock `model_manager.ensure_model()` returns `True`
- Call "SWAP oss120"
- Assert ensure_model called with "oss120"

**test_handle_owner_command_help**
- Call "HELP"
- Assert response contains all command names

**test_handle_owner_command_unknown**
- Call "FOOBAR"
- Assert "Unknown command" in response

**test_classify_message**
- Mock `llm_client.chat_simple()` to return valid JSON:
  `'{"urgency":"high","classification":"green_party","needs_response":true,"summary":"PDC reply","suggested_action":"respond"}'`
- Call `_classify_message(sample_inbound_email)`
- Assert `msg.urgency == Urgency.HIGH`
- Assert `msg.classification == "green_party"`
- Assert returns dict with expected keys

**test_classify_message_with_code_fence**
- Mock returns response wrapped in ```json ... ```
- Assert still parses correctly

**test_classify_message_failure**
- Mock `chat_simple` raises exception
- Assert returns `None`

**test_draft_response**
- Mock `chat_simple` returns "Dear PDC, thank you..."
- Call `_draft_response(sample_inbound_email)`
- Assert returns the draft text

**test_draft_response_failure**
- Mock raises exception
- Assert returns `None`

**test_queue_action**
- Call `_queue_action(sample_inbound_email, "draft text")`
- Assert returns an action_id string
- Assert action in `orchestrator.pending`
- Assert outbound has correct recipient, subject, reply_to

**test_expire_actions**
- Add action with `created_at` in the distant past
- Set `config.approval_timeout = 1`
- Call `_expire_actions()`
- Assert action.status == "expired"

**test_expire_actions_leaves_recent**
- Add action with `created_at = datetime.now()`
- Call `_expire_actions()`
- Assert action.status still "pending"

**test_handle_message_signal_owner**
- Create inbound from owner number on Signal channel
- Mock `_handle_owner_command`
- Call `_handle_message(msg)`
- Assert `_handle_owner_command` called, NOT `_classify_message`

**test_handle_message_email_needs_response**
- Mock classify returns `{"needs_response": true, "summary": "test"}`
- Mock draft returns "draft text"
- Mock signal.notify
- Call `_handle_message(sample_inbound_email)`
- Assert action queued, signal notified with action_id

**test_handle_message_email_no_response**
- Mock classify returns `{"needs_response": false, "summary": "newsletter"}`
- Call `_handle_message(sample_inbound_email)`
- Assert NO action queued, signal still notified (informational)

---

## Running

```bash
cd automation_framework
source .venv/bin/activate
pytest tests/ -v --cov=services --cov-report=term-missing
```

Target: 80%+ on each module.

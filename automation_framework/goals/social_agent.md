# Goal: Social Agent

## Objective

Provide a sandboxed interface for social network operations (post, read
notifications, check metrics) that prevents the orchestrating LLM from
accessing credentials or being exposed to raw untrusted social content.

## Security Model

The social agent runs as a **separate subprocess**. The orchestrator
communicates via JSON on stdin/stdout. This provides:

- **Credential isolation:** Credentials are loaded from `services/.env`
  inside the subprocess. They never appear in stdout, error messages,
  or any return value.
- **Content sanitisation:** All text from external users is truncated,
  stripped of control characters, and flagged if it matches prompt
  injection patterns.
- **Least privilege:** The agent has network access to social APIs only.
  No filesystem access beyond `services/.env` (read). No memory DB
  access. No access to SEBE documents.
- **No persistent state:** The agent is stateless. Each invocation
  authenticates fresh and discards the session.

## Invocation

```bash
# From CLI
echo '{"command":"auth_test","platform":"bsky"}' | python -m tools.social

# From Python (orchestrator/daemon)
import subprocess, json
result = subprocess.run(
    ["python", "-m", "tools.social"],
    input=json.dumps({"command": "post", "platform": "bsky", "text": "Hello"}),
    capture_output=True, text=True,
    cwd="automation_framework/"
)
response = json.loads(result.stdout)
```

## Commands

| Command | Platforms | Required Fields | Optional Fields |
|---------|-----------|----------------|-----------------|
| `auth_test` | all | | |
| `post` | all | `text` | `url`, `reply_to`, `subreddit`, `title` (Reddit) |
| `get_profile` | all | | |
| `get_notifications` | all | | `limit` |
| `get_post_metrics` | all | `post_id` | |
| `delete_post` | all | `post_id` | |

## Platforms

| Platform | Key | Credentials Required |
|----------|-----|---------------------|
| Bluesky | `bsky` | `BSKY_HANDLE`, `BSKY_PASSWORD` |
| Mastodon | `mastodon` | `MASTODON_INSTANCE`, `MASTODON_TOKEN` |
| Reddit | `reddit` | `REDDIT_CLIENT_ID`, `REDDIT_SECRET`, `REDDIT_USERNAME`, `REDDIT_PASSWORD` |

## Error Handling

All errors return `{"success": false, "error": "error_type"}`. Error
types: `auth_failed`, `no_credentials`, `unknown_command`,
`unknown_platform`, `invalid_json`, `empty_input`, `rate_limited`,
`request_failed`, `internal_error`.

Credentials are never echoed in error messages. Raw API error bodies
are sanitised before return.

## Edge Cases

- Empty input → `empty_input`
- Malformed JSON → `invalid_json`
- Unknown command → `unknown_command`
- Unknown platform → `unknown_platform`
- Missing credentials → `no_credentials`
- Post text too long → silently truncated to platform limit
- Notification text contains injection patterns → `flagged: true` in item

## Files

```
tools/social/
├── __init__.py     # Package marker
├── __main__.py     # python -m entry point
├── agent.py        # Command dispatcher
├── config.py       # Credential loader (services/.env)
├── sanitise.py     # Output sanitisation
├── bluesky.py      # Bluesky AT Protocol adapter
├── mastodon.py     # Mastodon API adapter
└── reddit.py       # Reddit API adapter
```

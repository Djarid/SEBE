# Goal: Social Agent

## Objective

Provide a sandboxed interface for social network operations (post, read
notifications, check metrics) that prevents the orchestrating LLM from
accessing credentials or being exposed to raw untrusted social content.

## Security Model

The social agent runs as a **containerised MCP server** (`services/social_mcp/`).
The `@social` subagent in opencode connects to it over SSE (port 8090) and
can ONLY call the defined MCP tools. This provides:

- **Credential isolation:** Credentials are loaded from environment variables
  inside the container. They never appear in tool responses, error messages,
  or provenance blocks.
- **Content sanitisation:** All text from external users is truncated,
  stripped of control characters, and flagged if it matches prompt
  injection patterns.
- **Response validation:** Every tool response is validated against per-command
  schemas before returning. Invalid data is dropped with a count reported.
- **Provenance tracking:** Every response includes a `_provenance` block
  (tool name, platform, timestamp, source, item counts) so consumers can
  distinguish real API data from LLM fabrication.
- **Least privilege:** The server has network access to social APIs only.
  No filesystem access beyond credential environment variables. No memory
  DB access. No access to SEBE documents.
- **No persistent state:** Each API call authenticates fresh (Bluesky session
  tokens are per-request).

## Invocation

```bash
# Containerised (default, SSE on port 8090)
python -m services.social_mcp

# Dev/test (stdio transport)
SOCIAL_MCP_TRANSPORT=stdio python -m services.social_mcp
```

The `@social` subagent is configured in `opencode.json` under the `mcp`
section as a remote SSE server. Use `@social` for all social media tasks.

## MCP Tools

| Tool | Platforms | Required Args | Optional Args |
|------|-----------|---------------|---------------|
| `social_auth_test` | all | `platform` | |
| `social_post` | all | `platform`, `text` | `url`, `reply_to`, `subreddit`, `title` (Reddit) |
| `social_get_profile` | all | `platform` | |
| `social_get_feed` | all | `platform` | `limit` |
| `social_get_notifications` | all | `platform` | `limit` |
| `social_get_post_metrics` | all | `platform`, `post_id` | |
| `social_delete_post` | all | `platform`, `post_id` | |
| `social_verify_url` | n/a | `url` | |

## Platforms

| Platform | Key | Credentials Required |
|----------|-----|---------------------|
| Bluesky | `bsky` | `BSKY_HANDLE`, `BSKY_PASSWORD` |
| Mastodon | `mastodon` | `MASTODON_INSTANCE`, `MASTODON_TOKEN` |
| Reddit | `reddit` | `REDDIT_CLIENT_ID`, `REDDIT_SECRET`, `REDDIT_USERNAME`, `REDDIT_PASSWORD` |

## Error Handling

All errors return `{"success": false, "error": "..."}` with a `_provenance`
block. Common errors: `Unknown platform`, `No credentials configured`,
`auth_failed`, `invalid_profile_data`, `invalid_metrics_data`,
`timeout_or_network_error`.

Credentials are never echoed in error messages. Raw API error bodies
are sanitised before return.

## Files

```
services/social_mcp/
├── __init__.py     # Package marker
├── __main__.py     # python -m entry point
├── server.py       # FastMCP SSE server (tool definitions)
├── config.py       # Credential loader (env vars)
├── validate.py     # Response schema validation
├── sanitise.py     # Output sanitisation
├── bluesky.py      # Bluesky AT Protocol adapter
├── mastodon.py     # Mastodon API adapter
└── reddit.py       # Reddit API adapter
```

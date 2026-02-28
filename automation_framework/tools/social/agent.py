"""
SEBE Social Agent — sandboxed entry point.

Reads a single JSON command from stdin, dispatches to the appropriate
platform adapter, and writes a JSON result to stdout.

This is designed to run as a subprocess. The calling process (orchestrator,
daemon, or CLI) never has access to social network credentials.

Usage:
    echo '{"command":"auth_test","platform":"bsky"}' | python -m tools.social.agent
    echo '{"command":"post","platform":"bsky","text":"Hello"}' | python -m tools.social.agent
    echo '{"command":"get_profile","platform":"bsky"}' | python -m tools.social.agent
    echo '{"command":"get_notifications","platform":"bsky"}' | python -m tools.social.agent
    echo '{"command":"get_post_metrics","platform":"bsky","post_id":"at://..."}' | python -m tools.social.agent
    echo '{"command":"delete_post","platform":"bsky","post_id":"at://..."}' | python -m tools.social.agent

All output is JSON on stdout. Errors are also JSON: {"success": false, "error": "..."}.
Nothing is ever printed to stderr except Python tracebacks (which the caller should discard).
"""

import json
import sys

from . import bluesky, mastodon, reddit, config


ADAPTERS = {
    "bsky": bluesky,
    "mastodon": mastodon,
    "reddit": reddit,
}

COMMANDS = {
    "auth_test",
    "post",
    "get_profile",
    "get_notifications",
    "get_post_metrics",
    "delete_post",
}


def _error(msg: str) -> dict:
    return {"success": False, "error": msg}


def dispatch(cmd: dict) -> dict:
    """Dispatch a command to the appropriate adapter."""
    command = cmd.get("command", "")
    platform = cmd.get("platform", "")

    if command not in COMMANDS:
        return _error(f"unknown_command: {command}")

    if platform not in ADAPTERS:
        return _error(f"unknown_platform: {platform}")

    if not config.has_platform(platform):
        return _error(f"no_credentials: {platform}")

    adapter = ADAPTERS[platform]
    fn = getattr(adapter, command, None)
    if fn is None:
        return _error(f"unsupported: {platform}/{command}")

    # Build kwargs from command, excluding meta fields
    kwargs = {k: v for k, v in cmd.items() if k not in ("command", "platform")}

    try:
        return fn(**kwargs)
    except TypeError as e:
        return _error(f"invalid_args: {e}")
    except Exception as e:
        # Never expose internal error details
        return _error("internal_error")


def main():
    """Read JSON from stdin, dispatch, write JSON to stdout."""
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            print(json.dumps(_error("empty_input")))
            sys.exit(1)

        cmd = json.loads(raw)
    except json.JSONDecodeError:
        print(json.dumps(_error("invalid_json")))
        sys.exit(1)

    result = dispatch(cmd)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()

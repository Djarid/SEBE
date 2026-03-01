"""
Credential loader for the social MCP server.

Loads credentials from services/.env and exposes them ONLY within
this process. Credentials are never included in any return value,
log output, or error message.
"""

import os
from pathlib import Path


def _load_env() -> dict[str, str]:
    """Load key=value pairs from services/.env."""
    # Walk up from this file to find services/.env
    # social_mcp/ is inside services/, so .env is ../.
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return {}
    result = {}
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                result[k.strip()] = v.strip()
    return result


_ENV = _load_env()


def get(key: str, default: str = "") -> str:
    """Get a credential by key. Falls back to os.environ, then default."""
    return _ENV.get(key, os.environ.get(key, default))


def has_platform(platform: str) -> bool:
    """Check if credentials exist for a platform."""
    required = {
        "bsky": ["BSKY_HANDLE", "BSKY_PASSWORD"],
        "mastodon": ["MASTODON_INSTANCE", "MASTODON_TOKEN"],
        "reddit": [
            "REDDIT_CLIENT_ID",
            "REDDIT_SECRET",
            "REDDIT_USERNAME",
            "REDDIT_PASSWORD",
        ],
        "reddit_personal": [
            "REDDIT_PERSONAL_CLIENT_ID",
            "REDDIT_PERSONAL_SECRET",
            "REDDIT_PERSONAL_USERNAME",
            "REDDIT_PERSONAL_PASSWORD",
        ],
    }
    keys = required.get(platform, [])
    return all(get(k) for k in keys)


# Reddit credential key mapping by account type
REDDIT_KEYS = {
    "official": {
        "client_id": "REDDIT_CLIENT_ID",
        "secret": "REDDIT_SECRET",
        "username": "REDDIT_USERNAME",
        "password": "REDDIT_PASSWORD",
    },
    "personal": {
        "client_id": "REDDIT_PERSONAL_CLIENT_ID",
        "secret": "REDDIT_PERSONAL_SECRET",
        "username": "REDDIT_PERSONAL_USERNAME",
        "password": "REDDIT_PERSONAL_PASSWORD",
    },
}


def reddit_creds(account: str = "official") -> dict[str, str]:
    """Get Reddit credentials for a given account type.

    Args:
        account: 'official' (default) or 'personal'

    Returns:
        Dict with client_id, secret, username, password values.
        Values may be empty if not configured.
    """
    keys = REDDIT_KEYS.get(account, REDDIT_KEYS["official"])
    return {field: get(env_key) for field, env_key in keys.items()}

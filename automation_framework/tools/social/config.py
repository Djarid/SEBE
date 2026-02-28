"""
Credential loader for the social agent.

Loads credentials from services/.env and exposes them ONLY to the
adapter modules within this process. Credentials are never included
in any return value, log output, or error message.
"""

import os
from pathlib import Path


def _load_env() -> dict[str, str]:
    """Load key=value pairs from services/.env."""
    env_path = Path(__file__).resolve().parent.parent.parent / "services" / ".env"
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
    }
    keys = required.get(platform, [])
    return all(get(k) for k in keys)

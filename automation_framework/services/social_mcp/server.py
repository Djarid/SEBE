"""
SEBE Social MCP Server — containerised tool interface.

Exposes social network operations as MCP tools via FastMCP over SSE.
The social subagent connects to this server and can ONLY call these
defined tools. It has no filesystem access, no code editing ability.

Each platform adapter (bluesky, mastodon, reddit) is self-contained
within this package.

Every response includes a _provenance block (tool name, platform,
timestamp, item counts) so that consumers can distinguish real API
data from LLM fabrication. Responses are validated against per-command
schemas before returning.

Usage (containerised, default):
    python -m services.social_mcp

Usage (dev/test, stdio fallback):
    SOCIAL_MCP_TRANSPORT=stdio python -m services.social_mcp

Runs as an SSE MCP server on port 8090 by default.
Configured in opencode.json under "mcp" as a remote server.
"""

from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP

from . import bluesky, mastodon, reddit, config, validate, sanitise

MCP_PORT = int(os.environ.get("SOCIAL_MCP_PORT", "8090"))

mcp = FastMCP(
    "sebe-social",
    instructions=(
        "Social network tools for the SEBE project. "
        "Use these to post, read feeds, check notifications, "
        "and manage posts on Bluesky, Mastodon, and Reddit. "
        "Available platforms: bsky, mastodon, reddit. "
        "Every response includes a _provenance block with source, "
        "timestamp, and item counts. Only report data that appears "
        "in tool responses. If a tool returns an empty list, report "
        "'no activity found'. Never fabricate data."
    ),
    host="0.0.0.0",
    port=MCP_PORT,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ADAPTERS = {
    "bsky": bluesky,
    "mastodon": mastodon,
    "reddit": reddit,
}

# Platforms that support multi-account via the 'account' kwarg
_MULTI_ACCOUNT_PLATFORMS = {"reddit"}


def _check_platform(platform: str, account: str = "official") -> str | None:
    """Validate platform and credentials. Returns error string or None."""
    if platform not in ADAPTERS:
        return f"Unknown platform: {platform}. Use: bsky, mastodon, reddit"
    check_key = platform
    if platform in _MULTI_ACCOUNT_PLATFORMS and account == "personal":
        check_key = f"{platform}_personal"
    if not config.has_platform(check_key):
        return f"No credentials configured for {check_key}"
    return None


def _call(platform: str, method: str, account: str = "official", **kwargs):
    """Call an adapter method, passing account only to multi-account platforms."""
    fn = getattr(ADAPTERS[platform], method)
    if platform in _MULTI_ACCOUNT_PLATFORMS:
        return fn(account=account, **kwargs)
    return fn(**kwargs)


def _provenance(
    tool: str,
    platform: str,
    result: dict,
    raw_count: int | None = None,
    filtered_count: int | None = None,
) -> dict:
    """Attach provenance metadata to a result dict."""
    source = "api" if result.get("success") else "error"
    if platform and platform not in ADAPTERS:
        source = "unknown_platform"
    elif platform and not config.has_platform(platform):
        source = "no_credentials"

    prov: dict = {
        "tool": tool,
        "platform": platform,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": source,
    }
    if raw_count is not None:
        prov["raw_count"] = raw_count
    if filtered_count is not None:
        prov["filtered_count"] = filtered_count

    result["_provenance"] = prov
    return result


def _fmt(result: dict) -> str:
    """Format result as readable JSON for MCP response."""
    return json.dumps(result, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def social_auth_test(platform: str, account: str = "official") -> str:
    """Test authentication for a social platform.

    Args:
        platform: Platform to test. One of: bsky, mastodon, reddit
        account: For Reddit only. 'official' (default SEBE account) or 'personal'
    """
    err = _check_platform(platform, account)
    if err:
        return _fmt(
            _provenance("social_auth_test", platform, {"success": False, "error": err})
        )
    result = _call(platform, "auth_test", account)
    return _fmt(_provenance("social_auth_test", platform, result))


@mcp.tool()
def social_post(
    platform: str,
    text: str,
    url: str | None = None,
    reply_to: str | None = None,
    subreddit: str | None = None,
    title: str | None = None,
    account: str = "official",
) -> str:
    """Create a post on a social platform.

    Args:
        platform: Platform to post to. One of: bsky, mastodon, reddit
        text: The post text content
        url: Optional URL to attach
        reply_to: Optional post ID to reply to (format varies by platform)
        subreddit: Required for Reddit. The subreddit name (without r/)
        title: Required for Reddit. The post title
        account: For Reddit only. 'official' (default SEBE account) or 'personal'
    """
    err = _check_platform(platform, account)
    if err:
        return _fmt(
            _provenance("social_post", platform, {"success": False, "error": err})
        )

    kwargs: dict = {"text": text}
    if url is not None:
        kwargs["url"] = url
    if reply_to is not None:
        kwargs["reply_to"] = reply_to
    if subreddit is not None:
        kwargs["subreddit"] = subreddit
    if title is not None:
        kwargs["title"] = title

    result = _call(platform, "post", account, **kwargs)
    return _fmt(_provenance("social_post", platform, result))


@mcp.tool()
def social_get_profile(platform: str, account: str = "official") -> str:
    """Get the authenticated user's profile information.

    Args:
        platform: Platform to query. One of: bsky, mastodon, reddit
        account: For Reddit only. 'official' (default SEBE account) or 'personal'
    """
    err = _check_platform(platform, account)
    if err:
        return _fmt(
            _provenance(
                "social_get_profile", platform, {"success": False, "error": err}
            )
        )

    result = _call(platform, "get_profile", account)

    # Validate profile data
    if result.get("success") and not validate.validate_profile(result, platform):
        result = {"success": False, "error": "invalid_profile_data"}

    return _fmt(_provenance("social_get_profile", platform, result))


@mcp.tool()
def social_get_feed(platform: str, limit: int = 50, account: str = "official") -> str:
    """Get the authenticated user's own posts/feed.

    Args:
        platform: Platform to query. One of: bsky, mastodon, reddit
        limit: Maximum number of posts to return (default 50, max 100)
        account: For Reddit only. 'official' (default SEBE account) or 'personal'
    """
    err = _check_platform(platform, account)
    if err:
        return _fmt(
            _provenance("social_get_feed", platform, {"success": False, "error": err})
        )

    adapter = ADAPTERS[platform]
    if not hasattr(adapter, "get_feed"):
        return _fmt(
            _provenance(
                "social_get_feed",
                platform,
                {"success": False, "error": f"get_feed not supported on {platform}"},
            )
        )

    result = _call(platform, "get_feed", account, limit=limit)

    # Validate and filter feed items
    raw_count = 0
    filtered_count = 0
    if result.get("success") and "posts" in result:
        raw_count = len(result["posts"])
        # Sanitise each item
        result["posts"] = [sanitise.sanitise_feed_item(p) for p in result["posts"]]
        # Validate
        result["posts"], dropped = validate.filter_items(
            result["posts"],
            validate.validate_feed_item,
            platform,
            "get_feed",
        )
        filtered_count = len(result["posts"])
        result["count"] = filtered_count
        if dropped:
            result["_validation_dropped"] = dropped

    return _fmt(
        _provenance(
            "social_get_feed",
            platform,
            result,
            raw_count=raw_count,
            filtered_count=filtered_count,
        )
    )


@mcp.tool()
def social_get_notifications(
    platform: str, limit: int = 20, account: str = "official"
) -> str:
    """Get recent notifications from a social platform.

    Args:
        platform: Platform to query. One of: bsky, mastodon, reddit
        limit: Maximum number of notifications to return (default 20)
        account: For Reddit only. 'official' (default SEBE account) or 'personal'
    """
    err = _check_platform(platform, account)
    if err:
        return _fmt(
            _provenance(
                "social_get_notifications",
                platform,
                {"success": False, "error": err},
            )
        )

    result = _call(platform, "get_notifications", account, limit=limit)

    # Validate and filter notification items
    raw_count = 0
    filtered_count = 0
    if result.get("success") and "items" in result:
        raw_count = len(result["items"])
        result["items"], dropped = validate.filter_items(
            result["items"],
            validate.validate_notification,
            platform,
            "get_notifications",
        )
        filtered_count = len(result["items"])
        if dropped:
            result["_validation_dropped"] = dropped

    return _fmt(
        _provenance(
            "social_get_notifications",
            platform,
            result,
            raw_count=raw_count,
            filtered_count=filtered_count,
        )
    )


@mcp.tool()
def social_get_post_metrics(
    platform: str, post_id: str, account: str = "official"
) -> str:
    """Get engagement metrics (likes, reposts, replies) for a specific post.

    Args:
        platform: Platform to query. One of: bsky, mastodon, reddit
        post_id: The post identifier (AT URI for Bluesky, status ID for Mastodon, fullname for Reddit)
        account: For Reddit only. 'official' (default SEBE account) or 'personal'
    """
    err = _check_platform(platform, account)
    if err:
        return _fmt(
            _provenance(
                "social_get_post_metrics",
                platform,
                {"success": False, "error": err},
            )
        )

    result = _call(platform, "get_post_metrics", account, post_id=post_id)

    # Validate metrics
    if result.get("success") and not validate.validate_metrics(result, platform):
        result = {"success": False, "error": "invalid_metrics_data"}

    return _fmt(_provenance("social_get_post_metrics", platform, result))


@mcp.tool()
def social_delete_post(platform: str, post_id: str, account: str = "official") -> str:
    """Delete a post from a social platform.

    Args:
        platform: Platform to query. One of: bsky, mastodon, reddit
        post_id: The post identifier to delete
        account: For Reddit only. 'official' (default SEBE account) or 'personal'
    """
    err = _check_platform(platform, account)
    if err:
        return _fmt(
            _provenance(
                "social_delete_post",
                platform,
                {"success": False, "error": err},
            )
        )

    result = _call(platform, "delete_post", account, post_id=post_id)
    return _fmt(_provenance("social_delete_post", platform, result))


@mcp.tool()
def social_verify_url(url: str) -> str:
    """Verify that a social media URL exists by fetching it.

    Use this to confirm a post or profile exists before including
    it in a summary. Returns verified status and HTTP status code.

    Args:
        url: The URL to verify (must be a public social media URL)
    """
    if not url or not url.startswith(("https://", "http://")):
        return _fmt(
            {
                "verified": False,
                "url": url,
                "error": "invalid_url",
                "_provenance": {
                    "tool": "social_verify_url",
                    "platform": "",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "source": "validation",
                },
            }
        )

    try:
        req = urllib.request.Request(
            url,
            method="HEAD",
            headers={"User-Agent": "SEBE-Social-Verify/1.0"},
        )
        resp = urllib.request.urlopen(req, timeout=10)
        status_code = resp.getcode()
        return _fmt(
            {
                "verified": status_code == 200,
                "url": url,
                "status_code": status_code,
                "_provenance": {
                    "tool": "social_verify_url",
                    "platform": "",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "source": "api",
                },
            }
        )
    except urllib.error.HTTPError as e:
        return _fmt(
            {
                "verified": False,
                "url": url,
                "status_code": e.code,
                "_provenance": {
                    "tool": "social_verify_url",
                    "platform": "",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "source": "api",
                },
            }
        )
    except Exception:
        return _fmt(
            {
                "verified": False,
                "url": url,
                "error": "timeout_or_network_error",
                "_provenance": {
                    "tool": "social_verify_url",
                    "platform": "",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "source": "error",
                },
            }
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    """Run the MCP server. SSE by default, stdio for dev/test."""
    transport = os.environ.get("SOCIAL_MCP_TRANSPORT", "sse")
    if transport == "stdio":
        mcp.run(transport="stdio")
    else:
        mcp.run(transport="sse")


if __name__ == "__main__":
    main()

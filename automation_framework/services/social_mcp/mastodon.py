"""
Mastodon API adapter for the social MCP server.

Handles posting, profile retrieval, notifications, and post metrics.
Credentials loaded from config.py, never exposed in return values.

Requires MASTODON_INSTANCE and MASTODON_TOKEN in services/.env.
"""

from __future__ import annotations

import json
import urllib.request
import urllib.error
import urllib.parse

from . import config, sanitise


def _base_url() -> str:
    instance = config.get("MASTODON_INSTANCE")
    if not instance:
        raise ValueError("auth_failed")
    return instance.rstrip("/")


def _headers() -> dict:
    token = config.get("MASTODON_TOKEN")
    if not token:
        raise ValueError("auth_failed")
    return {"Authorization": f"Bearer {token}"}


def auth_test() -> dict:
    """Test authentication."""
    try:
        url = f"{_base_url()}/api/v1/accounts/verify_credentials"
        req = urllib.request.Request(url, headers=_headers())
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        return {
            "success": True,
            "handle": sanitise.clean_handle(data.get("acct", "")),
        }
    except Exception:
        return {"success": False, "error": "auth_failed"}


def post(text: str, url: str | None = None, reply_to: str | None = None) -> dict:
    """Create a status."""
    try:
        base = _base_url()
        headers = _headers()
    except Exception:
        return {"success": False, "error": "auth_failed"}

    full_text = text
    if url:
        full_text = f"{text}\n\n{url}"

    params = urllib.parse.urlencode({"status": full_text[:500]})
    if reply_to:
        params += f"&in_reply_to_id={urllib.parse.quote(reply_to)}"

    try:
        req = urllib.request.Request(
            f"{base}/api/v1/statuses",
            data=params.encode(),
            headers={
                **headers,
                "Content-Type": "application/x-www-form-urlencoded",
            },
            method="POST",
        )
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        return {
            "success": True,
            "post_id": str(data.get("id", "")),
            "url": data.get("url", ""),
        }
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read().decode())
            msg = err.get("error", "unknown_error")
        except Exception:
            msg = "unknown_error"
        return {"success": False, "error": sanitise.clean_string(msg, 200)}


def get_profile() -> dict:
    """Get own profile info."""
    try:
        url = f"{_base_url()}/api/v1/accounts/verify_credentials"
        req = urllib.request.Request(url, headers=_headers())
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        return {
            "success": True,
            "handle": sanitise.clean_handle(data.get("acct", "")),
            "display_name": sanitise.clean_string(data.get("display_name", ""), 100),
            "followers": data.get("followers_count", 0),
            "following": data.get("following_count", 0),
            "posts": data.get("statuses_count", 0),
        }
    except Exception:
        return {"success": False, "error": "auth_failed"}


def get_feed(limit: int = 50) -> dict:
    """Get own statuses."""
    try:
        base = _base_url()
        headers = _headers()
    except Exception:
        return {"success": False, "error": "auth_failed"}

    try:
        # First get own account ID
        req = urllib.request.Request(
            f"{base}/api/v1/accounts/verify_credentials",
            headers=headers,
        )
        resp = urllib.request.urlopen(req, timeout=15)
        me = json.loads(resp.read())
        account_id = me.get("id", "")

        # Then fetch statuses
        req = urllib.request.Request(
            f"{base}/api/v1/accounts/{account_id}/statuses?limit={min(limit, 40)}",
            headers=headers,
        )
        resp = urllib.request.urlopen(req, timeout=15)
        statuses = json.loads(resp.read())

        posts = []
        for s in statuses:
            post_data = {
                "post_id": str(s.get("id", "")),
                "text": sanitise.clean_string(s.get("content", ""), 1000),
                "created_at": s.get("created_at", ""),
                "likes": s.get("favourites_count", 0),
                "reposts": s.get("reblogs_count", 0),
                "replies": s.get("replies_count", 0),
                "url": s.get("url", ""),
            }
            posts.append(post_data)

        return {"success": True, "posts": posts, "count": len(posts)}
    except Exception:
        return {"success": False, "error": "request_failed"}


def get_notifications(limit: int = 20) -> dict:
    """Get recent notifications."""
    try:
        url = f"{_base_url()}/api/v1/notifications?limit={min(limit, 40)}"
        req = urllib.request.Request(url, headers=_headers())
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())

        items = []
        for n in data:
            status = n.get("status") or {}
            item = {
                "type": n.get("type", ""),
                "author": n.get("account", {}).get("acct", ""),
                "text_preview": status.get("content", ""),
                "post_id": str(status.get("id", "")),
            }
            items.append(sanitise.sanitise_notification(item))

        return {"success": True, "items": items}
    except Exception:
        return {"success": False, "error": "request_failed"}


def get_post_metrics(post_id: str) -> dict:
    """Get engagement metrics for a status."""
    try:
        url = f"{_base_url()}/api/v1/statuses/{urllib.parse.quote(post_id)}"
        req = urllib.request.Request(url, headers=_headers())
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        return {
            "success": True,
            "likes": data.get("favourites_count", 0),
            "reposts": data.get("reblogs_count", 0),
            "replies": data.get("replies_count", 0),
        }
    except Exception:
        return {"success": False, "error": "request_failed"}


def delete_post(post_id: str) -> dict:
    """Delete a status."""
    try:
        url = f"{_base_url()}/api/v1/statuses/{urllib.parse.quote(post_id)}"
        req = urllib.request.Request(url, headers=_headers(), method="DELETE")
        urllib.request.urlopen(req, timeout=15)
        return {"success": True}
    except Exception:
        return {"success": False, "error": "delete_failed"}

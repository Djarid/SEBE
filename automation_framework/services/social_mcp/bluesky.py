"""
Bluesky (AT Protocol) adapter for the social MCP server.

Handles authentication, posting, profile retrieval, feed listing,
notifications, and post metrics via the Bluesky API. Credentials
are loaded from config.py and never exposed in return values.
"""

from __future__ import annotations

import json
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timezone
from typing import Any

from . import config, sanitise


API = "https://bsky.social/xrpc"


def _auth() -> tuple[str, str]:
    """Authenticate and return (access_token, did). Raises on failure."""
    handle = config.get("BSKY_HANDLE")
    password = config.get("BSKY_PASSWORD")
    if not handle or not password:
        raise ValueError("auth_failed")

    data = json.dumps({"identifier": handle, "password": password}).encode()
    req = urllib.request.Request(
        f"{API}/com.atproto.server.createSession",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    resp = urllib.request.urlopen(req, timeout=15)
    session = json.loads(resp.read())
    return session["accessJwt"], session["did"]


def _authed_get(endpoint: str, token: str) -> dict:
    """Make an authenticated GET request."""
    req = urllib.request.Request(
        f"{API}/{endpoint}",
        headers={"Authorization": f"Bearer {token}"},
    )
    resp = urllib.request.urlopen(req, timeout=15)
    return json.loads(resp.read())


def auth_test() -> dict:
    """Test authentication. Returns handle on success."""
    try:
        _auth()
        return {"success": True, "handle": config.get("BSKY_HANDLE")}
    except Exception:
        return {"success": False, "error": "auth_failed"}


def post(text: str, url: str | None = None, reply_to: str | None = None) -> dict:
    """Create a post. Optionally attach a link card or reply to a post."""
    try:
        token, did = _auth()
    except Exception:
        return {"success": False, "error": "auth_failed"}

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")

    record: dict[str, Any] = {
        "$type": "app.bsky.feed.post",
        "text": text[:300],
        "createdAt": now,
    }

    if url:
        record["embed"] = {
            "$type": "app.bsky.embed.external",
            "external": {
                "uri": url,
                "title": "",
                "description": "",
            },
        }

    if reply_to:
        # reply_to should be "uri|cid" format
        parts = reply_to.split("|", 1)
        if len(parts) == 2:
            record["reply"] = {
                "root": {"uri": parts[0], "cid": parts[1]},
                "parent": {"uri": parts[0], "cid": parts[1]},
            }

    body = {
        "repo": did,
        "collection": "app.bsky.feed.post",
        "record": record,
    }

    try:
        data = json.dumps(body).encode()
        req = urllib.request.Request(
            f"{API}/com.atproto.repo.createRecord",
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
        )
        resp = urllib.request.urlopen(req, timeout=15)
        result = json.loads(resp.read())
        uri = result.get("uri", "")
        rkey = uri.split("/")[-1] if "/" in uri else ""
        handle = config.get("BSKY_HANDLE")
        return {
            "success": True,
            "post_id": uri,
            "cid": result.get("cid", ""),
            "url": f"https://bsky.app/profile/{handle}/post/{rkey}",
        }
    except urllib.error.HTTPError as e:
        body_bytes = e.read().decode()
        try:
            err = json.loads(body_bytes)
            msg = err.get("message", "unknown_error")
        except Exception:
            msg = "unknown_error"
        return {"success": False, "error": sanitise.clean_string(msg, 200)}


def get_profile() -> dict:
    """Get own profile info."""
    try:
        token, did = _auth()
    except Exception:
        return {"success": False, "error": "auth_failed"}

    handle = config.get("BSKY_HANDLE")
    try:
        data = _authed_get(
            f"app.bsky.actor.getProfile?actor={urllib.parse.quote(handle)}",
            token,
        )
        return {
            "success": True,
            "handle": sanitise.clean_handle(data.get("handle", "")),
            "display_name": sanitise.clean_string(data.get("displayName", ""), 100),
            "followers": data.get("followersCount", 0),
            "following": data.get("followsCount", 0),
            "posts": data.get("postsCount", 0),
        }
    except Exception:
        return {"success": False, "error": "request_failed"}


def get_feed(limit: int = 50) -> dict:
    """Get own posts/feed."""
    try:
        token, did = _auth()
    except Exception:
        return {"success": False, "error": "auth_failed"}

    handle = config.get("BSKY_HANDLE")
    try:
        data = _authed_get(
            f"app.bsky.feed.getAuthorFeed"
            f"?actor={urllib.parse.quote(handle)}"
            f"&limit={min(limit, 100)}",
            token,
        )

        posts = []
        for item in data.get("feed", []):
            p = item.get("post", {})
            record = p.get("record", {})
            uri = p.get("uri", "")
            rkey = uri.split("/")[-1] if "/" in uri else ""

            post_data = {
                "post_id": uri,
                "cid": p.get("cid", ""),
                "text": sanitise.clean_string(record.get("text", ""), 1000),
                "created_at": record.get("createdAt", ""),
                "likes": p.get("likeCount", 0),
                "reposts": p.get("repostCount", 0),
                "replies": p.get("replyCount", 0),
                "url": f"https://bsky.app/profile/{handle}/post/{rkey}",
            }
            posts.append(post_data)

        return {"success": True, "posts": posts, "count": len(posts)}
    except Exception:
        return {"success": False, "error": "request_failed"}


def get_notifications(limit: int = 20) -> dict:
    """Get recent notifications."""
    try:
        token, did = _auth()
    except Exception:
        return {"success": False, "error": "auth_failed"}

    try:
        data = _authed_get(
            f"app.bsky.notification.listNotifications?limit={min(limit, 50)}",
            token,
        )

        items = []
        for n in data.get("notifications", []):
            item = {
                "type": n.get("reason", ""),
                "author": n.get("author", {}).get("handle", ""),
                "text_preview": n.get("record", {}).get("text", ""),
                "post_id": n.get("uri", ""),
            }
            items.append(sanitise.sanitise_notification(item))

        return {"success": True, "items": items}
    except Exception:
        return {"success": False, "error": "request_failed"}


def get_post_metrics(post_id: str) -> dict:
    """Get engagement metrics for a specific post."""
    try:
        token, did = _auth()
    except Exception:
        return {"success": False, "error": "auth_failed"}

    try:
        encoded = urllib.parse.quote(post_id, safe="")
        data = _authed_get(
            f"app.bsky.feed.getPosts?uris={encoded}",
            token,
        )

        posts = data.get("posts", [])
        if not posts:
            return {"success": False, "error": "post_not_found"}

        p = posts[0]
        return {
            "success": True,
            "likes": p.get("likeCount", 0),
            "reposts": p.get("repostCount", 0),
            "replies": p.get("replyCount", 0),
        }
    except Exception:
        return {"success": False, "error": "request_failed"}


def delete_post(post_id: str) -> dict:
    """Delete a post by URI."""
    try:
        token, did = _auth()
    except Exception:
        return {"success": False, "error": "auth_failed"}

    parts = post_id.split("/")
    if len(parts) < 5:
        return {"success": False, "error": "invalid_post_id"}
    rkey = parts[-1]
    collection = parts[-2]

    try:
        data = json.dumps(
            {
                "repo": did,
                "collection": collection,
                "rkey": rkey,
            }
        ).encode()
        req = urllib.request.Request(
            f"{API}/com.atproto.repo.deleteRecord",
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
        )
        urllib.request.urlopen(req, timeout=15)
        return {"success": True}
    except Exception:
        return {"success": False, "error": "delete_failed"}

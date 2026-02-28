"""
Bluesky (AT Protocol) adapter for the social agent.

Handles authentication, posting, profile retrieval, notifications
and post metrics via the Bluesky API. Credentials are loaded from
config.py and never exposed in return values.
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


def _request(method: str, endpoint: str, token: str, data: dict | None = None) -> dict:
    """Make an authenticated API request."""
    url = f"{API}/{endpoint}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method=method,
    )
    resp = urllib.request.urlopen(req, timeout=15)
    return json.loads(resp.read()) if resp.read else {}


def auth_test() -> dict:
    """Test authentication. Returns handle on success."""
    try:
        token, did = _auth()
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
        # Extract rkey for URL construction
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
        body = e.read().decode()
        # Never echo raw error body (may contain auth details)
        try:
            err = json.loads(body)
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
        req = urllib.request.Request(
            f"{API}/app.bsky.actor.getProfile?actor={urllib.parse.quote(handle)}",
            headers={"Authorization": f"Bearer {token}"},
        )
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
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


def get_notifications(limit: int = 20) -> dict:
    """Get recent notifications."""
    try:
        token, did = _auth()
    except Exception:
        return {"success": False, "error": "auth_failed"}

    try:
        req = urllib.request.Request(
            f"{API}/app.bsky.notification.listNotifications?limit={min(limit, 50)}",
            headers={"Authorization": f"Bearer {token}"},
        )
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())

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
        req = urllib.request.Request(
            f"{API}/app.bsky.feed.getPosts?uris={encoded}",
            headers={"Authorization": f"Bearer {token}"},
        )
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())

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

    # Extract rkey from URI: at://did/collection/rkey
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

"""
Reddit API adapter for the social MCP server.

Handles OAuth authentication, posting to subreddits, profile retrieval,
inbox notifications, and post metrics. Credentials loaded from config.py,
never exposed in return values.

Requires REDDIT_CLIENT_ID, REDDIT_SECRET, REDDIT_USERNAME,
REDDIT_PASSWORD in services/.env.
"""

from __future__ import annotations

import json
import urllib.request
import urllib.error
import urllib.parse
import base64

from . import config, sanitise


TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
API = "https://oauth.reddit.com"
USER_AGENT = "SEBE-Social-Agent/1.0"


def _auth(account: str = "official") -> str:
    """Get an OAuth bearer token. Returns token string.

    Args:
        account: 'official' (default) or 'personal'
    """
    creds = config.reddit_creds(account)
    client_id = creds["client_id"]
    client_secret = creds["secret"]
    username = creds["username"]
    password = creds["password"]

    if not all([client_id, client_secret, username, password]):
        raise ValueError("auth_failed")

    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

    data = urllib.parse.urlencode(
        {
            "grant_type": "password",
            "username": username,
            "password": password,
        }
    ).encode()

    req = urllib.request.Request(
        TOKEN_URL,
        data=data,
        headers={
            "Authorization": f"Basic {credentials}",
            "User-Agent": USER_AGENT,
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    resp = urllib.request.urlopen(req, timeout=15)
    token_data = json.loads(resp.read())
    token = token_data.get("access_token")
    if not token:
        raise ValueError("auth_failed")
    return token


def _authed_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "User-Agent": USER_AGENT,
    }


def auth_test(account: str = "official") -> dict:
    """Test authentication."""
    try:
        token = _auth(account)
        req = urllib.request.Request(
            f"{API}/api/v1/me",
            headers=_authed_headers(token),
        )
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        return {
            "success": True,
            "handle": sanitise.clean_handle(data.get("name", "")),
        }
    except Exception:
        return {"success": False, "error": "auth_failed"}


def post(
    text: str,
    url: str | None = None,
    subreddit: str | None = None,
    title: str | None = None,
    reply_to: str | None = None,
    account: str = "official",
) -> dict:
    """Submit a post to a subreddit.

    If url is provided without text, submits as a link post.
    Otherwise submits as a self post.
    subreddit and title are required.
    """
    if not subreddit or not title:
        return {"success": False, "error": "subreddit and title required"}

    try:
        token = _auth(account)
    except Exception:
        return {"success": False, "error": "auth_failed"}

    params = {
        "sr": subreddit,
        "title": title[:300],
        "kind": "link" if url and not text else "self",
    }

    if url and not text:
        params["url"] = url
    else:
        full_text = text
        if url:
            full_text = f"{text}\n\n{url}"
        params["text"] = full_text[:40000]

    try:
        data = urllib.parse.urlencode(params).encode()
        req = urllib.request.Request(
            f"{API}/api/submit",
            data=data,
            headers={
                **_authed_headers(token),
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        resp = urllib.request.urlopen(req, timeout=15)
        result = json.loads(resp.read())

        post_url = ""
        post_id = ""
        if "json" in result:
            json_data = result["json"].get("data", {})
            post_url = json_data.get("url", "")
            post_id = json_data.get("name", "")

        return {
            "success": True,
            "post_id": post_id,
            "url": post_url,
        }
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read().decode())
            msg = str(err.get("message", "unknown_error"))
        except Exception:
            msg = "unknown_error"
        return {"success": False, "error": sanitise.clean_string(msg, 200)}


def get_profile(account: str = "official") -> dict:
    """Get own profile info."""
    try:
        token = _auth(account)
        req = urllib.request.Request(
            f"{API}/api/v1/me",
            headers=_authed_headers(token),
        )
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        return {
            "success": True,
            "handle": sanitise.clean_handle(data.get("name", "")),
            "display_name": sanitise.clean_string(
                data.get("subreddit", {}).get("title", ""), 100
            ),
            "karma": data.get("total_karma", 0),
        }
    except Exception:
        return {"success": False, "error": "auth_failed"}


def get_feed(limit: int = 50, account: str = "official") -> dict:
    """Get own submitted posts."""
    try:
        token = _auth(account)
    except Exception:
        return {"success": False, "error": "auth_failed"}

    creds = config.reddit_creds(account)
    username = creds["username"]
    try:
        req = urllib.request.Request(
            f"{API}/user/{urllib.parse.quote(username)}/submitted"
            f"?limit={min(limit, 25)}",
            headers=_authed_headers(token),
        )
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())

        posts = []
        for child in data.get("data", {}).get("children", []):
            d = child.get("data", {})
            post_data = {
                "post_id": d.get("name", ""),
                "title": sanitise.clean_string(d.get("title", ""), 300),
                "text": sanitise.clean_string(d.get("selftext", ""), 1000),
                "created_at": str(d.get("created_utc", "")),
                "subreddit": d.get("subreddit", ""),
                "likes": d.get("ups", 0),
                "reposts": 0,
                "replies": d.get("num_comments", 0),
                "url": d.get("url", ""),
            }
            posts.append(post_data)

        return {"success": True, "posts": posts, "count": len(posts)}
    except Exception:
        return {"success": False, "error": "request_failed"}


def delete_post(post_id: str, account: str = "official") -> dict:
    """Delete a post by fullname (e.g. t3_xxxxx)."""
    try:
        token = _auth(account)
        data = urllib.parse.urlencode({"id": post_id}).encode()
        req = urllib.request.Request(
            f"{API}/api/del",
            data=data,
            headers={
                **_authed_headers(token),
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        urllib.request.urlopen(req, timeout=15)
        return {"success": True}
    except Exception:
        return {"success": False, "error": "delete_failed"}


def get_notifications(limit: int = 20, account: str = "official") -> dict:
    """Get inbox messages (Reddit's notification equivalent)."""
    try:
        token = _auth(account)
        req = urllib.request.Request(
            f"{API}/message/inbox?limit={min(limit, 25)}",
            headers=_authed_headers(token),
        )
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())

        items = []
        for child in data.get("data", {}).get("children", []):
            d = child.get("data", {})
            item = {
                "type": d.get("type", "message"),
                "author": d.get("author", ""),
                "text_preview": d.get("body", ""),
                "post_id": d.get("name", ""),
            }
            items.append(sanitise.sanitise_notification(item))

        return {"success": True, "items": items}
    except Exception:
        return {"success": False, "error": "request_failed"}


def get_post_metrics(post_id: str, account: str = "official") -> dict:
    """Get metrics for a post by fullname."""
    try:
        token = _auth(account)
        req = urllib.request.Request(
            f"{API}/api/info?id={urllib.parse.quote(post_id)}",
            headers=_authed_headers(token),
        )
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())

        children = data.get("data", {}).get("children", [])
        if not children:
            return {"success": False, "error": "post_not_found"}

        p = children[0].get("data", {})
        return {
            "success": True,
            "likes": p.get("ups", 0),
            "reposts": 0,
            "replies": p.get("num_comments", 0),
        }
    except Exception:
        return {"success": False, "error": "request_failed"}

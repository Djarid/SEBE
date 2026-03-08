"""
URL defanging and refanging utilities.

Defence-in-depth measure: URLs extracted from untrusted sources (email,
web scrapes) are defanged before entering LLM context. This prevents
accidental navigation via browser automation tools (CDP, etc.).

Defanged format:
    https://example.com/path  →  hxxps://example[.]com/path
    http://sub.example.co.uk  →  hxxp://sub[.]example[.]co[.]uk

Downstream tools that need to follow a URL must explicitly call
refang_url() first, creating a deliberate access point.
"""

from __future__ import annotations

import re
from urllib.parse import urlparse, urlunparse


def defang_url(url: str) -> str:
    """Defang a single URL by mangling scheme and domain dots.

    Scheme:  https:// → hxxps://  |  http:// → hxxp://
    Domain:  dots in the hostname are replaced with [.]

    Path, query, and fragment are left intact for readability.
    Non-HTTP(S) URLs are returned unchanged.
    """
    url = url.strip()
    if not re.match(r"https?://", url, re.IGNORECASE):
        return url

    try:
        parsed = urlparse(url)
    except Exception:
        return url

    # Mangle scheme
    scheme = parsed.scheme.lower()
    if scheme == "https":
        scheme = "hxxps"
    elif scheme == "http":
        scheme = "hxxp"

    # Mangle dots in hostname only
    hostname = (parsed.hostname or "").replace(".", "[.]")

    # Reconstruct netloc (preserve port if present)
    if parsed.port:
        netloc = f"{hostname}:{parsed.port}"
    else:
        netloc = hostname

    # Preserve userinfo if present (rare but possible)
    if parsed.username:
        userinfo = parsed.username
        if parsed.password:
            userinfo += f":{parsed.password}"
        netloc = f"{userinfo}@{netloc}"

    return urlunparse(
        (scheme, netloc, parsed.path, parsed.params, parsed.query, parsed.fragment)
    )


def refang_url(url: str) -> str:
    """Reverse defanging: restore a defanged URL to a followable form.

    hxxps:// → https://  |  hxxp:// → http://
    [.] → .
    """
    url = url.strip()
    url = re.sub(r"^hxxps://", "https://", url, flags=re.IGNORECASE)
    url = re.sub(r"^hxxp://", "http://", url, flags=re.IGNORECASE)
    url = url.replace("[.]", ".")
    return url


# Pattern matches http(s) URLs in free text. Stops at whitespace,
# angle brackets, quotes, and common sentence-ending punctuation
# that is unlikely to be part of the URL.
_URL_RE = re.compile(
    r"https?://[^\s<>\"'\)\]]+",
    re.IGNORECASE,
)


def defang_urls(text: str) -> str:
    """Find and defang all bare HTTP(S) URLs in a block of text."""
    return _URL_RE.sub(lambda m: defang_url(m.group(0)), text)

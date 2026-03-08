"""
Tests for tools/url_sanitise.py.

Covers defanging, refanging, and round-trip integrity.
"""

import pytest

from tools.url_sanitise import defang_url, defang_urls, refang_url


# --- defang_url ---


class TestDefangUrl:
    """Tests for single-URL defanging."""

    def test_https_scheme(self):
        assert defang_url("https://example.com") == "hxxps://example[.]com"

    def test_http_scheme(self):
        assert defang_url("http://example.com") == "hxxp://example[.]com"

    def test_preserves_path(self):
        result = defang_url("https://example.com/path/to/page")
        assert result == "hxxps://example[.]com/path/to/page"

    def test_preserves_query(self):
        result = defang_url("https://example.com/search?q=test&page=1")
        assert result == "hxxps://example[.]com/search?q=test&page=1"

    def test_preserves_fragment(self):
        result = defang_url("https://example.com/page#section")
        assert result == "hxxps://example[.]com/page#section"

    def test_preserves_port(self):
        result = defang_url("https://example.com:8443/api")
        assert result == "hxxps://example[.]com:8443/api"

    def test_subdomain_dots(self):
        result = defang_url("https://sub.domain.example.co.uk/path")
        assert result == "hxxps://sub[.]domain[.]example[.]co[.]uk/path"

    def test_zoom_url(self):
        url = "https://zoom.us/j/97155298601?pwd=hVGXcdhVoNlgBaMfVcGoX21gt7xOjb.1"
        result = defang_url(url)
        assert result.startswith("hxxps://zoom[.]us/j/")
        assert "pwd=hVGXcdhVoNlgBaMfVcGoX21gt7xOjb.1" in result

    def test_non_http_unchanged(self):
        assert defang_url("ftp://files.example.com") == "ftp://files.example.com"

    def test_mailto_unchanged(self):
        assert defang_url("mailto:user@example.com") == "mailto:user@example.com"

    def test_empty_string(self):
        assert defang_url("") == ""

    def test_plain_text_unchanged(self):
        assert defang_url("not a url") == "not a url"

    def test_whitespace_stripped(self):
        result = defang_url("  https://example.com  ")
        assert result == "hxxps://example[.]com"

    def test_case_insensitive_scheme(self):
        result = defang_url("HTTPS://Example.COM/Path")
        assert result.startswith("hxxps://")


# --- refang_url ---


class TestRefangUrl:
    """Tests for URL refanging (restoring to followable form)."""

    def test_hxxps_to_https(self):
        assert refang_url("hxxps://example[.]com") == "https://example.com"

    def test_hxxp_to_http(self):
        assert refang_url("hxxp://example[.]com") == "http://example.com"

    def test_with_path_and_query(self):
        defanged = "hxxps://zoom[.]us/j/12345?pwd=abc"
        assert refang_url(defanged) == "https://zoom.us/j/12345?pwd=abc"

    def test_with_port(self):
        assert (
            refang_url("hxxps://example[.]com:8443/api")
            == "https://example.com:8443/api"
        )

    def test_multiple_subdomain_dots(self):
        defanged = "hxxps://sub[.]domain[.]example[.]co[.]uk/path"
        assert refang_url(defanged) == "https://sub.domain.example.co.uk/path"

    def test_already_normal_url(self):
        """Refanging an already-normal URL should be harmless."""
        assert refang_url("https://example.com") == "https://example.com"

    def test_empty_string(self):
        assert refang_url("") == ""

    def test_case_insensitive(self):
        assert refang_url("HXXPS://example[.]com").startswith("https://")


# --- round-trip ---


class TestRoundTrip:
    """Defang then refang should yield the original URL."""

    @pytest.mark.parametrize(
        "url",
        [
            "https://example.com",
            "http://example.com/path?key=value#frag",
            "https://sub.domain.example.co.uk:8443/api/v2",
            "https://zoom.us/j/97155298601?pwd=hVGXcdhVoNlgBaMfVcGoX21gt7xOjb.1",
            "http://192.168.1.10:8082/v1/accounts",
        ],
    )
    def test_round_trip(self, url):
        assert refang_url(defang_url(url)) == url


# --- defang_urls (bulk text) ---


class TestDefangUrls:
    """Tests for defanging all URLs in a text block."""

    def test_single_url_in_text(self):
        text = "Visit https://evil.com/phish for details"
        result = defang_urls(text)
        assert "hxxps://evil[.]com/phish" in result
        assert "https://evil.com" not in result

    def test_multiple_urls(self):
        text = "Go to https://a.com and http://b.org/page"
        result = defang_urls(text)
        assert "hxxps://a[.]com" in result
        assert "hxxp://b[.]org/page" in result
        assert "https://" not in result
        assert "http://" not in result

    def test_no_urls(self):
        text = "No links here, just plain text."
        assert defang_urls(text) == text

    def test_preserves_surrounding_text(self):
        text = "Before https://example.com after"
        result = defang_urls(text)
        assert result.startswith("Before ")
        assert result.endswith(" after")

    def test_url_at_end_of_line(self):
        text = "Link: https://example.com/path\nNext line"
        result = defang_urls(text)
        assert "hxxps://example[.]com/path" in result
        assert "Next line" in result

    def test_already_defanged_unchanged(self):
        """Already-defanged URLs should not be double-mangled."""
        text = "Link: hxxps://example[.]com/path"
        assert defang_urls(text) == text

    def test_empty_string(self):
        assert defang_urls("") == ""

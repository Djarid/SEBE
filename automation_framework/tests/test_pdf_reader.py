"""
Tests for tools.pdf_reader — PDF text extraction.

All PDF operations and network requests are mocked.
Tests cover local files, URLs, metadata, text extraction, and search.
"""

import pytest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import tempfile

from tools.pdf_reader import (
    fetch_pdf,
    open_pdf,
    cleanup,
    action_info,
    action_text,
    action_pages,
    action_search,
)


# ═══════════════════════════════════════════════════════════════════════════
# Helper Function Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestFetchPdf:
    """Test PDF fetching from URLs."""

    @patch("tools.pdf_reader.urllib.request.urlopen")
    @patch("tools.pdf_reader.tempfile.NamedTemporaryFile")
    def test_fetch_pdf_success(self, mock_tempfile, mock_urlopen):
        """Successful PDF download."""
        # Mock response
        mock_response = MagicMock()
        mock_response.read.return_value = b"PDF content here"
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        # Mock temp file
        mock_temp = MagicMock()
        mock_temp.name = "/tmp/test.pdf"
        mock_tempfile.return_value = mock_temp
        
        result = fetch_pdf("https://example.com/report.pdf")
        
        assert isinstance(result, Path)
        assert str(result) == "/tmp/test.pdf"
        mock_temp.write.assert_called_once_with(b"PDF content here")

    @patch("tools.pdf_reader.urllib.request.urlopen")
    @patch("tools.pdf_reader.tempfile.NamedTemporaryFile")
    def test_fetch_pdf_network_error(self, mock_tempfile, mock_urlopen):
        """Network error during download."""
        mock_urlopen.side_effect = Exception("Network timeout")
        mock_temp = MagicMock()
        mock_tempfile.return_value = mock_temp
        
        with pytest.raises(RuntimeError, match="Failed to download"):
            fetch_pdf("https://example.com/report.pdf")


class TestOpenPdf:
    """Test PDF opening (local and URL)."""

    @patch("tools.pdf_reader.pymupdf.open")
    def test_open_pdf_local_file(self, mock_pymupdf_open, tmp_path):
        """Open local PDF file."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"PDF content")
        
        mock_doc = MagicMock()
        mock_pymupdf_open.return_value = mock_doc
        
        doc, temp = open_pdf(str(pdf_file))
        
        assert doc == mock_doc
        assert temp is None
        mock_pymupdf_open.assert_called_once_with(str(pdf_file))

    @patch("tools.pdf_reader.pymupdf.open")
    def test_open_pdf_local_missing(self, mock_pymupdf_open, tmp_path):
        """Error opening non-existent local file."""
        with pytest.raises(FileNotFoundError):
            open_pdf(str(tmp_path / "missing.pdf"))

    @patch("tools.pdf_reader.pymupdf.open")
    @patch("tools.pdf_reader.fetch_pdf")
    def test_open_pdf_url(self, mock_fetch, mock_pymupdf_open, tmp_path):
        """Open PDF from URL."""
        temp_file = tmp_path / "downloaded.pdf"
        mock_fetch.return_value = temp_file
        
        mock_doc = MagicMock()
        mock_pymupdf_open.return_value = mock_doc
        
        doc, temp = open_pdf("https://example.com/report.pdf")
        
        assert doc == mock_doc
        assert temp == temp_file
        mock_fetch.assert_called_once()


class TestCleanup:
    """Test temp file cleanup."""

    def test_cleanup_removes_file(self, tmp_path):
        """Cleanup removes temp file."""
        temp_file = tmp_path / "temp.pdf"
        temp_file.write_bytes(b"content")
        
        cleanup(temp_file)
        
        assert not temp_file.exists()

    def test_cleanup_missing_file(self, tmp_path):
        """Cleanup handles missing file gracefully."""
        temp_file = tmp_path / "nonexistent.pdf"
        cleanup(temp_file)  # Should not raise

    def test_cleanup_none(self):
        """Cleanup handles None gracefully."""
        cleanup(None)  # Should not raise


# ═══════════════════════════════════════════════════════════════════════════
# Action: Info Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestActionInfo:
    """Test PDF metadata extraction."""

    @patch("tools.pdf_reader.open_pdf")
    def test_action_info_basic(self, mock_open_pdf):
        """Extract basic PDF metadata."""
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 42
        mock_doc.metadata = {
            "title": "SEBE Policy Document",
            "author": "Jason Huxley",
            "subject": "Economic policy",
            "creator": "LibreOffice",
            "producer": "PDF Export",
            "creationDate": "2026-02-14",
        }
        mock_open_pdf.return_value = (mock_doc, None)
        
        result = action_info("test.pdf")
        
        assert result["success"] is True
        assert result["pages"] == 42
        assert result["title"] == "SEBE Policy Document"
        assert result["author"] == "Jason Huxley"
        mock_doc.close.assert_called_once()

    @patch("tools.pdf_reader.open_pdf")
    def test_action_info_empty_metadata(self, mock_open_pdf):
        """PDF with empty metadata."""
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 5
        mock_doc.metadata = {}
        mock_open_pdf.return_value = (mock_doc, None)
        
        result = action_info("test.pdf")
        
        assert result["success"] is True
        assert result["pages"] == 5
        assert result["title"] == ""


# ═══════════════════════════════════════════════════════════════════════════
# Action: Text Extraction Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestActionText:
    """Test full text extraction."""

    @patch("tools.pdf_reader.open_pdf")
    def test_action_text_full_extraction(self, mock_open_pdf):
        """Extract all text from PDF."""
        mock_page1 = MagicMock()
        mock_page1.get_text.return_value = "Page 1 content\nSEBE revenue model"
        mock_page2 = MagicMock()
        mock_page2.get_text.return_value = "Page 2 content\nDistribution costs"
        
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 2
        mock_doc.__getitem__.side_effect = [mock_page1, mock_page2]
        mock_open_pdf.return_value = (mock_doc, None)
        
        result = action_text("test.pdf")
        
        assert result["success"] is True
        assert result["total_pages"] == 2
        assert result["extracted_pages"] == 2
        assert len(result["pages"]) == 2
        assert "SEBE revenue model" in result["pages"][0]["text"]
        assert "Distribution costs" in result["pages"][1]["text"]

    @patch("tools.pdf_reader.open_pdf")
    def test_action_text_max_pages_limit(self, mock_open_pdf):
        """Extract limited number of pages."""
        mock_pages = []
        for i in range(10):
            page = MagicMock()
            page.get_text.return_value = f"Page {i+1} content"
            mock_pages.append(page)
        
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 10
        mock_doc.__getitem__.side_effect = lambda i: mock_pages[i]
        mock_open_pdf.return_value = (mock_doc, None)
        
        result = action_text("test.pdf", max_pages=3)
        
        assert result["success"] is True
        assert result["total_pages"] == 10
        assert result["extracted_pages"] == 3

    @patch("tools.pdf_reader.open_pdf")
    def test_action_text_empty_pages_skipped(self, mock_open_pdf):
        """Empty pages are skipped."""
        mock_page1 = MagicMock()
        mock_page1.get_text.return_value = "Content here"
        mock_page2 = MagicMock()
        mock_page2.get_text.return_value = "   \n\n  "  # Whitespace only
        
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 2
        mock_doc.__getitem__.side_effect = [mock_page1, mock_page2]
        mock_open_pdf.return_value = (mock_doc, None)
        
        result = action_text("test.pdf")
        
        assert result["extracted_pages"] == 1


# ═══════════════════════════════════════════════════════════════════════════
# Action: Specific Pages Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestActionPages:
    """Test specific page extraction."""

    @patch("tools.pdf_reader.open_pdf")
    def test_action_pages_valid_pages(self, mock_open_pdf):
        """Extract specific valid pages."""
        mock_page1 = MagicMock()
        mock_page1.get_text.return_value = "Page 1 content"
        mock_page3 = MagicMock()
        mock_page3.get_text.return_value = "Page 3 content"
        
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 5
        mock_doc.__getitem__.side_effect = lambda i: [mock_page1, None, mock_page3][i]
        mock_open_pdf.return_value = (mock_doc, None)
        
        result = action_pages("test.pdf", [1, 3])
        
        assert result["success"] is True
        assert len(result["pages"]) == 2
        assert result["pages"][0]["page"] == 1
        assert result["pages"][1]["page"] == 3

    @patch("tools.pdf_reader.open_pdf")
    def test_action_pages_invalid_page_numbers(self, mock_open_pdf):
        """Invalid page numbers return errors."""
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 3
        mock_open_pdf.return_value = (mock_doc, None)
        
        result = action_pages("test.pdf", [1, 10])
        
        assert result["success"] is True
        assert len(result["pages"]) == 2
        # Page 1 should succeed, page 10 should have error
        valid = [p for p in result["pages"] if "error" not in p]
        invalid = [p for p in result["pages"] if "error" in p]
        assert len(valid) == 1
        assert len(invalid) == 1
        assert "out of range" in invalid[0]["error"]


# ═══════════════════════════════════════════════════════════════════════════
# Action: Search Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestActionSearch:
    """Test PDF text search."""

    @patch("tools.pdf_reader.open_pdf")
    def test_action_search_matches_found(self, mock_open_pdf):
        """Search finds matches."""
        mock_page1 = MagicMock()
        mock_page1.get_text.return_value = "SEBE revenue model\ntargets £200-500B"
        mock_page2 = MagicMock()
        mock_page2.get_text.return_value = "No match here"
        mock_page3 = MagicMock()
        mock_page3.get_text.return_value = "Another SEBE mention\nwith context"
        
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 3
        mock_doc.__getitem__.side_effect = [mock_page1, mock_page2, mock_page3]
        mock_open_pdf.return_value = (mock_doc, None)
        
        result = action_search("test.pdf", "SEBE")
        
        assert result["success"] is True
        assert result["query"] == "SEBE"
        assert result["matches"] == 2
        assert len(result["results"]) == 2
        assert result["results"][0]["page"] == 1
        assert result["results"][1]["page"] == 3

    @patch("tools.pdf_reader.open_pdf")
    def test_action_search_no_matches(self, mock_open_pdf):
        """Search with no matches."""
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Some unrelated content"
        
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 1
        mock_doc.__getitem__.return_value = mock_page
        mock_open_pdf.return_value = (mock_doc, None)
        
        result = action_search("test.pdf", "nonexistent")
        
        assert result["success"] is True
        assert result["matches"] == 0
        assert result["results"] == []

    @patch("tools.pdf_reader.open_pdf")
    def test_action_search_case_insensitive(self, mock_open_pdf):
        """Search is case-insensitive."""
        mock_page = MagicMock()
        mock_page.get_text.return_value = "SEBE Revenue Model"
        
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 1
        mock_doc.__getitem__.return_value = mock_page
        mock_open_pdf.return_value = (mock_doc, None)
        
        result = action_search("test.pdf", "sebe")
        
        assert result["matches"] == 1

    @patch("tools.pdf_reader.open_pdf")
    def test_action_search_context_lines(self, mock_open_pdf):
        """Search returns context around matches."""
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Line 1\nLine 2 SEBE here\nLine 3\nLine 4"
        
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 1
        mock_doc.__getitem__.return_value = mock_page
        mock_open_pdf.return_value = (mock_doc, None)
        
        result = action_search("test.pdf", "SEBE")
        
        assert len(result["results"]) == 1
        context = result["results"][0]["context"]
        # Should include line before and after
        assert "Line 1" in context or "Line 2" in context
        assert "Line 3" in context

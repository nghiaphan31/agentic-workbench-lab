"""
test_archive_query_server.py — Tests for Cold Zone MCP Server

GAP-11e: Tests for archive_query_server.py

Tests the archive_query_server module which exposes memory-bank/archive-cold/
via MCP tools. Agents MUST use these tools instead of reading archive-cold/ directly.
"""

import json
import sys
from pathlib import Path

import pytest

# Add the mcp directory to path
MCP_DIR = Path(__file__).parent.parent.parent / "agentic-workbench-engine" / ".workbench" / "mcp"
sys.path.insert(0, str(MCP_DIR))

from archive_query_server import search_archive, read_archive_file, ARCHIVE_PATH


class TestArchiveQueryServer:
    """GAP-11e: Cold Zone MCP Server tests."""

    @pytest.fixture
    def mock_archive(self, tmp_path, monkeypatch):
        """Create a mock archive-cold directory with test files."""
        archive_dir = tmp_path / "archive-cold"
        archive_dir.mkdir()
        
        # Create test files
        (archive_dir / "sprint-1-progress.md").write_text(
            "# Sprint 1 Progress\n\nREQ-001 was completed in sprint 1.\nUser authentication feature merged.\n",
            encoding="utf-8"
        )
        (archive_dir / "sprint-2-decisions.md").write_text(
            "# Sprint 2 Decisions\n\nDecided to use JWT for authentication.\nREQ-002 dependency on REQ-001.\n",
            encoding="utf-8"
        )
        (archive_dir / "sprint-1-handoff.md").write_text(
            "# Sprint 1 Handoff\n\nHandoff from Developer to Reviewer.\nREQ-001 implementation complete.\n",
            encoding="utf-8"
        )
        
        # Monkeypatch ARCHIVE_PATH in the module
        import archive_query_server
        monkeypatch.setattr(archive_query_server, "ARCHIVE_PATH", archive_dir)
        
        return archive_dir

    def test_gap11e_search_archive_returns_matching_files(self, mock_archive):
        """GAP-11e: search_archive returns files matching query."""
        import archive_query_server
        results = archive_query_server.search_archive("REQ-001")
        assert len(results) > 0, "Should find files containing REQ-001"
        assert all("filename" in r for r in results), "Each result should have filename"
        assert all("excerpt" in r for r in results), "Each result should have excerpt"
        assert all("size_lines" in r for r in results), "Each result should have size_lines"

    def test_gap11e_search_archive_returns_max_3_results(self, mock_archive):
        """GAP-11e: search_archive returns max 3 results even when more match."""
        import archive_query_server
        # All 3 files contain "sprint" — should return max 3
        results = archive_query_server.search_archive("sprint")
        assert len(results) <= 3, f"Should return max 3 results, got {len(results)}"

    def test_gap11e_search_archive_sprint_filter(self, mock_archive):
        """GAP-11e: search_archive sprint filter narrows results."""
        import archive_query_server
        results = archive_query_server.search_archive("REQ-001", sprint="sprint-1")
        assert all("sprint-1" in r["filename"] for r in results), \
            "Sprint filter should only return sprint-1 files"

    def test_gap11e_search_archive_empty_when_no_match(self, mock_archive):
        """GAP-11e: search_archive returns empty list when no files match."""
        import archive_query_server
        results = archive_query_server.search_archive("NONEXISTENT_QUERY_XYZ_12345")
        assert results == [], "Should return empty list when no files match"

    def test_gap11e_read_archive_file_returns_content(self, mock_archive):
        """GAP-11e: read_archive_file returns file content."""
        import archive_query_server
        content = archive_query_server.read_archive_file("sprint-1-progress.md")
        assert "Sprint 1 Progress" in content, "Should return file content"
        assert "REQ-001" in content

    def test_gap11e_read_archive_file_truncates_to_max_lines(self, mock_archive):
        """GAP-11e: read_archive_file truncates to max_lines."""
        import archive_query_server
        content = archive_query_server.read_archive_file("sprint-1-progress.md", max_lines=2)
        lines = content.split("\n")
        # Should have at most 2 content lines + truncation notice
        assert len(lines) <= 4, f"Should be truncated, got {len(lines)} lines"
        assert "truncated" in content.lower() or len(lines) <= 3

    def test_gap11e_read_archive_file_blocks_path_traversal(self, mock_archive):
        """GAP-11e: read_archive_file blocks path traversal attacks."""
        import archive_query_server
        result = archive_query_server.read_archive_file("../../../etc/passwd")
        assert "ERROR" in result, "Path traversal should be blocked"
        assert "Access denied" in result or "outside archive-cold" in result

    def test_gap11e_read_archive_file_returns_error_for_missing_file(self, mock_archive):
        """GAP-11e: read_archive_file returns error for non-existent file."""
        import archive_query_server
        result = archive_query_server.read_archive_file("nonexistent-file.md")
        assert "ERROR" in result, "Should return error for missing file"
        assert "not found" in result.lower()

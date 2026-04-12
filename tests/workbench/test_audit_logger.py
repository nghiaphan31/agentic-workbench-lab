"""
test_audit_logger.py — UC-033 to UC-036
Tests for audit_logger.py — Immutable audit trail
"""

import json

import pytest
from .helpers import read_state


class TestAuditLogger:
    """UC-033 through UC-036: Audit logger use cases."""

    def test_uc033_save_session_creates_immutable_file(self, temp_workbench, state_factory, run_script):
        """UC-033: Save session — creates immutable file in docs/conversations/"""
        state_factory(active_req_id="REQ-001", state="RED")
        exit_code, stdout, stderr = run_script("audit_logger", "save", "--session-id", "abc123", "--branch", "feature/REQ-001")
        assert exit_code == 0
        conversations_dir = temp_workbench / "docs" / "conversations"
        files = list(conversations_dir.glob("*.md"))
        assert len(files) == 1
        content = files[0].read_text(encoding="utf-8")
        assert "abc123" in content
        assert "feature/REQ-001" in content

    def test_uc034_save_session_filename_format(self, temp_workbench, state_factory, run_script):
        """UC-034: Save session — filename matches YYYYMMDD_HHMMSS_sessionid.md"""
        state_factory()
        exit_code, stdout, stderr = run_script("audit_logger", "save", "--session-id", "xyz789", "--branch", "main")
        assert exit_code == 0
        conversations_dir = temp_workbench / "docs" / "conversations"
        files = list(conversations_dir.glob("*_xyz789.md"))
        assert len(files) == 1
        name = files[0].name
        # Should start with timestamp pattern (8 digits for date+time)
        parts = name.split("_")
        assert len(parts) >= 2
        assert parts[0].isdigit() and len(parts[0]) >= 8

    def test_uc035_list_sessions(self, temp_workbench, state_factory, run_script):
        """UC-035: List sessions — shows all audit log files reverse chronological"""
        state_factory()
        # Create 3 audit files manually
        conv = temp_workbench / "docs" / "conversations"
        conv.mkdir(parents=True, exist_ok=True)
        (conv / "20260101_120000_session1.md").write_text("# Session 1", encoding="utf-8")
        (conv / "20260102_130000_session2.md").write_text("# Session 2", encoding="utf-8")
        (conv / "20260103_140000_session3.md").write_text("# Session 3", encoding="utf-8")
        
        exit_code, stdout, stderr = run_script("audit_logger", "list")
        assert exit_code == 0
        assert "session1" in stdout
        assert "session2" in stdout
        assert "session3" in stdout

    def test_uc036_conversations_directory_auto_created(self, temp_workbench, state_factory, run_script):
        """UC-036: Save session — docs/conversations/ auto-created if missing"""
        state_factory()
        conv_dir = temp_workbench / "docs" / "conversations"
        # Ensure directory does not exist
        import shutil
        if conv_dir.exists():
            shutil.rmtree(conv_dir)
        
        exit_code, stdout, stderr = run_script("audit_logger", "save", "--session-id", "auto_created", "--branch", "main")
        assert exit_code == 0
        assert conv_dir.exists()
        files = list(conv_dir.glob("*.md"))
        assert len(files) == 1
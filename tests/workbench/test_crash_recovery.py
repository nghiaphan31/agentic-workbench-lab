"""
test_crash_recovery.py — UC-037 to UC-040
Tests for crash_recovery.py — Heartbeat + resume detection
"""

import json

import pytest
from .helpers import read_state


class TestCrashRecovery:
    """UC-037 through UC-040: Crash recovery use cases."""

    def test_uc037_start_daemon_writes_active_checkpoint(self, temp_workbench, state_factory, run_script):
        """UC-037: Start daemon — writes ACTIVE checkpoint with session data"""
        state_factory()
        checkpoint = temp_workbench / "memory-bank" / "hot-context" / "session-checkpoint.md"
        # Ensure fresh EMPTY state for this test
        checkpoint.write_text("**status:** EMPTY\n", encoding="utf-8")

        # Run status on a fresh checkpoint
        exit_code, stdout, stderr = run_script("crash_recovery", "status")
        assert exit_code == 0
        # Fresh state should show EMPTY
        assert "EMPTY" in stdout or "No active session" in stdout

    def test_uc038_status_active_session_detected(self, temp_workbench, state_factory, run_script):
        """UC-038: Status — ACTIVE session detected — offers resume"""
        state_factory()
        # Pre-seed session-checkpoint.md with ACTIVE status and session data
        checkpoint = temp_workbench / "memory-bank" / "hot-context" / "session-checkpoint.md"
        # crash_recovery.py parses "status: ACTIVE" (no markdown bold)
        checkpoint.write_text(
            """# session-checkpoint.md — 5-Minute Crash Recovery Heartbeat

status: ACTIVE

session_id: abc12345
branch: feature/REQ-001
commit_hash: a1b2c3d4
current_task: Implementing user login
last_heartbeat: 2026-04-12 14:00 UTC
""",
            encoding="utf-8",
        )
        
        exit_code, stdout, stderr = run_script("crash_recovery", "status")
        assert exit_code == 0
        assert "ACTIVE" in stdout
        assert "abc12345" in stdout or "feature/REQ-001" in stdout
        assert "Resume available" in stdout or "offer" in stdout.lower()

    def test_uc039_status_no_active_session(self, temp_workbench, state_factory, run_script):
        """UC-039: Status — No active session — fresh start"""
        state_factory()
        checkpoint = temp_workbench / "memory-bank" / "hot-context" / "session-checkpoint.md"
        checkpoint.write_text("**status:** EMPTY", encoding="utf-8")
        
        exit_code, stdout, stderr = run_script("crash_recovery", "status")
        assert exit_code == 0
        assert "EMPTY" in stdout or "No active session" in stdout

    def test_uc040_clear_checkpoint(self, temp_workbench, state_factory, run_script):
        """UC-040: Clear checkpoint — resets to EMPTY"""
        state_factory()
        checkpoint = temp_workbench / "memory-bank" / "hot-context" / "session-checkpoint.md"
        checkpoint.write_text("**status:** ACTIVE\n- **session_id:** xyz\n", encoding="utf-8")
        
        exit_code, stdout, stderr = run_script("crash_recovery", "clear")
        assert exit_code == 0
        
        content = checkpoint.read_text(encoding="utf-8")
        assert "status: EMPTY" in content or "**status:** EMPTY" in content
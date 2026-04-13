"""
test_arbiter_check.py — Tests for Arbiter Compliance Health Scanner

GAP-15u: 11 test cases covering all observable proxy check functions

Tests the arbiter_check.py module which runs observable proxy checks for
.clinerules rules. Each test focuses on the observable behavior of the check
functions without mocking git internals heavily.
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent.parent.parent / "agentic-workbench-engine" / ".workbench" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import arbiter_check
from arbiter_check import (
    CheckResult,
    check_startup_protocol,
    check_audit_log_immutability,
    check_handoff_read,
    check_handoff_freshness,
    check_cold_zone_access,
    check_decision_log_updated,
    check_crash_checkpoint,
    check_dependency_blocked_mode,
    check_file_access_constraints,
    check_live_imports_from_non_merged,
    check_regression_failures_populated,
    check_arbiter_capabilities_registered,
    check_forbidden_self_declaration,
    run_checks,
    SESSION_CHECKS,
    CHECK_REGISTRY,
)


class TestArbiterCheckFunctions:
    """GAP-15u: Tests for arbiter_check.py observable proxy check functions."""

    @pytest.fixture
    def mock_repo(self, tmp_path, monkeypatch):
        """Set up a mock repo structure for arbiter_check tests."""
        # Create directory structure
        hot_context = tmp_path / "memory-bank" / "hot-context"
        hot_context.mkdir(parents=True)
        archive_cold = tmp_path / "memory-bank" / "archive-cold"
        archive_cold.mkdir(parents=True)
        docs_conversations = tmp_path / "docs" / "conversations"
        docs_conversations.mkdir(parents=True)
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        
        # Create default hot-context files
        (hot_context / "activeContext.md").write_text(
            "# Active Context\n\nCurrent task: testing\n", encoding="utf-8"
        )
        (hot_context / "handoff-state.md").write_text(
            "# Handoff State\n\nNo active handoff.\n", encoding="utf-8"
        )
        (hot_context / "decisionLog.md").write_text(
            "# Decision Log\n\n## Decisions\n\nNo decisions yet.\n", encoding="utf-8"
        )
        (hot_context / "session-checkpoint.md").write_text(
            "status: IDLE\n", encoding="utf-8"
        )
        (hot_context / "progress.md").write_text(
            "# Progress\n\n## Sprint Goals\n- [ ] Goal 1\n", encoding="utf-8"
        )
        
        # Create default state.json
        state = {
            "version": "2.1",
            "state": "INIT",
            "stage": None,
            "active_req_id": None,
            "regression_state": "NOT_RUN",
            "regression_failures": [],
            "integration_state": "NOT_RUN",
            "feature_registry": {},
            "file_ownership": {},
            "arbiter_capabilities": {
                "test_orchestrator": False,
                "gherkin_validator": False,
                "memory_rotator": False,
                "audit_logger": False,
                "crash_recovery": False,
                "dependency_monitor": False,
                "integration_test_runner": False,
                "git_hooks": False,
            },
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "last_updated_by": "workbench-cli",
        }
        (tmp_path / "state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
        
        # Monkeypatch module-level paths
        monkeypatch.setattr(arbiter_check, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(arbiter_check, "STATE_JSON", tmp_path / "state.json")
        monkeypatch.setattr(arbiter_check, "HOT_CONTEXT", hot_context)
        monkeypatch.setattr(arbiter_check, "ARCHIVE_COLD", archive_cold)
        monkeypatch.setattr(arbiter_check, "DOCS_CONVERSATIONS", docs_conversations)
        monkeypatch.setattr(arbiter_check, "SRC_DIR", src_dir)
        
        return {
            "root": tmp_path,
            "hot_context": hot_context,
            "archive_cold": archive_cold,
            "docs_conversations": docs_conversations,
            "src_dir": src_dir,
            "state": state,
        }

    def test_gap15u_check_registry_has_13_rules(self):
        """GAP-15u: CHECK_REGISTRY contains 13 rules."""
        assert len(CHECK_REGISTRY) == 13, f"Expected 13 rules, got {len(CHECK_REGISTRY)}"

    def test_gap15u_session_checks_contains_5_critical_rules(self):
        """GAP-15u: SESSION_CHECKS contains exactly 5 rules for lightweight scan."""
        assert len(SESSION_CHECKS) == 5, f"Expected 5 session checks, got {len(SESSION_CHECKS)}"
        expected_session = {"SLC-2", "MEM-1", "DEP-3", "FAC-1", "CR-1"}
        assert set(SESSION_CHECKS) == expected_session

    def test_gap15u_check_startup_protocol_active_context_missing(
        self, mock_repo, monkeypatch
    ):
        """GAP-15u: check_startup_protocol returns WARNING when activeContext.md missing."""
        # Remove activeContext.md
        (mock_repo["hot_context"] / "activeContext.md").unlink()
        
        result = check_startup_protocol()
        
        assert result.status == "WARNING"
        assert "SLC-1" in result.rule
        assert "activeContext.md" in result.message

    def test_gap15u_check_audit_log_immutability_no_logs(
        self, mock_repo
    ):
        """GAP-15u: check_audit_log_immutability returns OK when no logs exist."""
        result = check_audit_log_immutability()
        
        assert result.status == "OK"
        assert "SLC-2" in result.rule

    def test_gap15u_check_handoff_read_no_handoff(
        self, mock_repo
    ):
        """GAP-15u: check_handoff_read returns OK when no handoff exists."""
        # Remove handoff
        handoff_file = mock_repo["hot_context"] / "handoff-state.md"
        if handoff_file.exists():
            handoff_file.unlink()
        
        result = check_handoff_read()
        
        assert result.status == "OK"
        assert "HND-1" in result.rule

    def test_gap15u_check_handoff_freshness_no_stale_markers(
        self, mock_repo
    ):
        """GAP-15u: check_handoff_freshness returns OK when no stale sprint markers."""
        result = check_handoff_freshness()
        
        assert result.status == "OK"
        assert "HND-2" in result.rule

    def test_gap15u_check_decision_log_updated_empty_log(
        self, mock_repo
    ):
        """GAP-15u: check_decision_log_updated returns WARNING when no decisions logged."""
        # Write an empty decision log (no actual decisions)
        decision_log = mock_repo["hot_context"] / "decisionLog.md"
        decision_log.write_text(
            "# Decision Log\n\n## Decisions\n\n(TODO: Add ADR entries here)\n",
            encoding="utf-8"
        )
        # Set mtime to 10 days ago
        old_time = datetime.now(timezone.utc) - timedelta(days=10)
        old_timestamp = old_time.timestamp()
        os.utime(decision_log, (old_timestamp, old_timestamp))
        
        result = check_decision_log_updated()
        
        assert result.status == "WARNING"
        assert "MEM-2" in result.rule

    def test_gap15u_check_crash_checkpoint_no_checkpoint(
        self, mock_repo
    ):
        """GAP-15u: check_crash_checkpoint returns INFO when no checkpoint exists."""
        result = check_crash_checkpoint()
        
        assert result.status == "INFO"
        assert "CR-1" in result.rule

    def test_gap15u_check_dependency_blocked_mode_not_blocked(
        self, mock_repo
    ):
        """GAP-15u: check_dependency_blocked_mode returns OK when not in blocked state."""
        result = check_dependency_blocked_mode()
        
        assert result.status == "OK"
        assert "DEP-3" in result.rule

    def test_gap15u_check_file_access_constraints_no_staged_files(
        self, mock_repo, monkeypatch
    ):
        """GAP-15u: check_file_access_constraints returns OK when no staged files."""
        # Mock git diff to return empty
        monkeypatch.setattr(arbiter_check, "run_git", lambda *args, **kwargs: ("", 0))
        
        result = check_file_access_constraints()
        
        assert result.status == "OK"
        assert "FAC-1" in result.rule

    def test_gap15u_check_live_imports_no_non_merged_features(
        self, mock_repo
    ):
        """GAP-15u: check_live_imports_from_non_merged returns OK when all merged."""
        result = check_live_imports_from_non_merged()
        
        assert result.status == "OK"
        assert "TRC-2" in result.rule

    def test_gap15u_check_regression_failures_populated_not_red(
        self, mock_repo
    ):
        """GAP-15u: check_regression_failures_populated returns OK when not REGRESSION_RED."""
        result = check_regression_failures_populated()
        
        assert result.status == "OK"
        assert "REG-1" in result.rule

    def test_gap15u_check_arbiter_capabilities_all_false(
        self, mock_repo
    ):
        """GAP-15u: check_arbiter_capabilities_registered returns WARNING when all false."""
        result = check_arbiter_capabilities_registered()
        
        assert result.status == "WARNING"
        assert "CMD-TRANSITION" in result.rule

    def test_gap15u_check_forbidden_self_declaration_clean_state(
        self, mock_repo
    ):
        """GAP-15u: check_forbidden_self_declaration returns OK in INIT state."""
        result = check_forbidden_self_declaration()
        
        assert result.status == "OK"
        assert "FOR-1" in result.rule

    def test_gap15u_run_checks_returns_list_of_results(
        self, mock_repo, monkeypatch
    ):
        """GAP-15u: run_checks() returns a list of CheckResult objects."""
        # Mock git commands to avoid actual git dependency
        def mock_git(*args, **kwargs):
            return ("", 0)
        monkeypatch.setattr(arbiter_check, "run_git", mock_git)
        
        results = run_checks(rules=["SLC-1", "SLC-2"])
        
        assert isinstance(results, list)
        assert len(results) == 2
        assert all(isinstance(r, CheckResult) for r in results)

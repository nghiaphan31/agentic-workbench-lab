"""
test_test_orchestrator.py — UC-015 to UC-021
Tests for test_orchestrator.py — Two-phase test execution
"""

import json

import pytest
from .helpers import read_state


class TestTestOrchestrator:
    """UC-015 through UC-021: Test orchestrator use cases."""

    def test_uc015_no_tests_found_skipped(self, temp_workbench, state_factory, run_script):
        """UC-015: Phase 1 — No tests found for REQ-ID — exit 0, pass_ratio=1.0"""
        state_factory(state="RED", active_req_id="REQ-001")
        exit_code, stdout, stderr = run_script("test_orchestrator", "run", "--scope", "feature", "--req-id", "REQ-001", "--set-state")
        assert exit_code == 0
        assert "Pass Ratio: 100.0%" in stdout

    def test_uc016_phase1_all_pass(self, temp_workbench, state_factory, run_script, mock_runner_pass):
        """UC-016: Phase 1 — Tests found, all pass — state becomes FEATURE_GREEN"""
        state_factory(state="RED", active_req_id="REQ-001")
        (temp_workbench / "tests" / "unit" / "REQ-001-user-login.spec.ts").write_text("describe('test', () => {});", encoding="utf-8")
        exit_code, stdout, stderr = run_script("test_orchestrator", "run", "--scope", "feature", "--req-id", "REQ-001", "--set-state")
        assert exit_code == 0
        state = read_state(temp_workbench)
        assert state["state"] == "FEATURE_GREEN"

    def test_uc017_phase1_some_fail(self, temp_workbench, state_factory, run_script, mock_runner_fail):
        """UC-017: Phase 1 — Tests found, some fail — state stays RED"""
        state_factory(state="RED", active_req_id="REQ-001")
        (temp_workbench / "tests" / "unit" / "REQ-001-user-login.spec.ts").write_text("describe('test', () => {});", encoding="utf-8")
        exit_code, stdout, stderr = run_script("test_orchestrator", "run", "--scope", "feature", "--req-id", "REQ-001", "--set-state")
        assert exit_code == 1
        state = read_state(temp_workbench)
        assert state["state"] == "RED"

    def test_uc018_phase2_full_regression_all_pass(self, temp_workbench, state_factory, run_script, mock_runner_pass):
        """UC-018: Phase 2 — Full regression, all pass — state becomes GREEN"""
        state_factory(state="FEATURE_GREEN", active_req_id="REQ-001")
        (temp_workbench / "tests" / "unit" / "REQ-001-user-login.spec.ts").write_text("describe('test', () => {});", encoding="utf-8")
        exit_code, stdout, stderr = run_script("test_orchestrator", "run", "--scope", "full", "--set-state")
        assert exit_code == 0
        state = read_state(temp_workbench)
        assert state["state"] == "GREEN"
        assert state["regression_state"] == "CLEAN"

    def test_uc019_phase2_full_regression_some_fail(self, temp_workbench, state_factory, run_script, mock_runner_fail):
        """UC-019: Phase 2 — Full regression, some fail — state becomes REGRESSION_RED"""
        state_factory(state="FEATURE_GREEN", active_req_id="REQ-001")
        (temp_workbench / "tests" / "unit" / "REQ-001-user-login.spec.ts").write_text("describe('test', () => {});", encoding="utf-8")
        exit_code, stdout, stderr = run_script("test_orchestrator", "run", "--scope", "full", "--set-state")
        assert exit_code == 1
        state = read_state(temp_workbench)
        assert state["state"] == "REGRESSION_RED"

    def test_uc020_missing_req_id_for_feature_scope(self, temp_workbench, state_factory, run_script):
        """UC-020: Missing --req-id for feature scope — exit 2"""
        state_factory()
        exit_code, stdout, stderr = run_script("test_orchestrator", "run", "--scope", "feature")
        assert exit_code == 2
        assert "--req-id required" in stderr or "--req-id required" in stdout

    def test_uc021_missing_state_json(self, temp_workbench, run_script, tmp_path):
        """UC-021: Missing state.json — exit 2"""
        # Don't create state.json
        exit_code, stdout, stderr = run_script("test_orchestrator", "run", "--scope", "full")
        assert exit_code == 2
        assert "state.json not found" in stderr or "state.json not found" in stdout

    # =============================================================================
    # GAP-6: Regression failures population tests
    # =============================================================================

    def test_gap6_regression_failures_populated_on_test_failure(self, temp_workbench, state_factory, run_script, mock_runner_fail):
        """
        GAP-6: When tests fail, regression_failures array is populated with actual failure details.
        
        Verify that when Phase 2 full regression tests fail, the state.json
        regression_failures array contains the actual failure details, not just an empty array.
        """
        state_factory(state="FEATURE_GREEN", active_req_id="REQ-001")
        (temp_workbench / "tests" / "unit" / "REQ-001-user-login.spec.ts").write_text(
            "describe('test', () => { it('fail', () => { expect(true).toBe(false); }); });",
            encoding="utf-8"
        )
        exit_code, stdout, stderr = run_script("test_orchestrator", "run", "--scope", "full", "--set-state")
        
        # Test should fail
        assert exit_code == 1
        
        state = read_state(temp_workbench)
        
        # regression_failures should be populated with failure details
        assert "regression_failures" in state, "state.json should have regression_failures field"
        assert isinstance(state["regression_failures"], list), "regression_failures should be an array"
        assert len(state["regression_failures"]) > 0, "regression_failures should not be empty when tests fail"

    def test_gap6_regression_failures_empty_on_success(self, temp_workbench, state_factory, run_script, mock_runner_pass):
        """
        GAP-6: When tests pass, regression_failures array remains empty.
        
        Verify that when Phase 2 full regression tests pass, the state.json
        regression_failures array remains empty.
        """
        state_factory(state="FEATURE_GREEN", active_req_id="REQ-001")
        (temp_workbench / "tests" / "unit" / "REQ-001-user-login.spec.ts").write_text(
            "describe('test', () => { it('pass', () => { expect(true).toBe(true); }); });",
            encoding="utf-8"
        )
        exit_code, stdout, stderr = run_script("test_orchestrator", "run", "--scope", "full", "--set-state")
        
        # Test should pass
        assert exit_code == 0
        
        state = read_state(temp_workbench)
        
        # regression_failures should remain empty when tests pass
        assert "regression_failures" in state
        assert state["regression_failures"] == [], "regression_failures should be empty when tests pass"
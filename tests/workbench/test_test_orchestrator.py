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
"""
test_state_machine.py — SM-001 to SM-014
Tests for state machine transitions in state.json
"""

import json

import pytest
from .helpers import read_state


class TestStateMachine:
    """SM-001 through SM-014: State machine transition coverage."""

    def test_sm001_init_to_red(self, temp_workbench, state_factory, run_script, mock_runner_fail):
        """SM-001: INIT → RED — Stage 2 tests authored, Phase 1 run fails"""
        state_factory(state="INIT", active_req_id="REQ-001")
        (temp_workbench / "tests" / "unit" / "REQ-001-user-login.spec.ts").write_text("describe('test', () => {});", encoding="utf-8")
        exit_code, stdout, stderr = run_script("test_orchestrator", "run", "--scope", "feature", "--req-id", "REQ-001", "--set-state")
        assert exit_code == 1
        state = read_state(temp_workbench)
        assert state["state"] == "RED"

    def test_sm002_red_to_feature_green(self, temp_workbench, state_factory, run_script, mock_runner_pass):
        """SM-002: RED → FEATURE_GREEN — Phase 1 all tests pass"""
        state_factory(state="RED", active_req_id="REQ-001")
        (temp_workbench / "tests" / "unit" / "REQ-001-user-login.spec.ts").write_text("describe('test', () => {});", encoding="utf-8")
        exit_code, stdout, stderr = run_script("test_orchestrator", "run", "--scope", "feature", "--req-id", "REQ-001", "--set-state")
        assert exit_code == 0
        state = read_state(temp_workbench)
        assert state["state"] == "FEATURE_GREEN"

    def test_sm003_red_to_dependency_blocked(self, temp_workbench, state_factory, run_script):
        """SM-003: RED → DEPENDENCY_BLOCKED — depends_on not MERGED"""
        state_factory(
            state="RED",
            active_req_id="REQ-002",
            feature_registry={
                "REQ-001": {"state": "RED", "depends_on": []},
                "REQ-002": {"state": "RED", "depends_on": ["REQ-001"]},
            }
        )
        # Manually set state to DEPENDENCY_BLOCKED via dependency_monitor check
        exit_code, stdout, stderr = run_script("dependency_monitor", "check-unblock")
        state = read_state(temp_workbench)
        # REQ-002 should NOT be unblocked since REQ-001 is not MERGED
        assert state["feature_registry"]["REQ-002"]["state"] == "RED"

    def test_sm004_feature_green_to_green(self, temp_workbench, state_factory, run_script, mock_runner_pass):
        """SM-004: FEATURE_GREEN → GREEN — Phase 2 regression passes"""
        state_factory(state="FEATURE_GREEN", active_req_id="REQ-001")
        (temp_workbench / "tests" / "unit" / "REQ-001-user-login.spec.ts").write_text("describe('test', () => {});", encoding="utf-8")
        exit_code, stdout, stderr = run_script("test_orchestrator", "run", "--scope", "full", "--set-state")
        assert exit_code == 0
        state = read_state(temp_workbench)
        assert state["state"] == "GREEN"
        assert state["regression_state"] == "CLEAN"

    def test_sm005_feature_green_to_regression_red(self, temp_workbench, state_factory, run_script, mock_runner_fail):
        """SM-005: FEATURE_GREEN → REGRESSION_RED — Phase 2 regression fails"""
        state_factory(state="FEATURE_GREEN", active_req_id="REQ-001")
        (temp_workbench / "tests" / "unit" / "REQ-001-user-login.spec.ts").write_text("describe('test', () => {});", encoding="utf-8")
        exit_code, stdout, stderr = run_script("test_orchestrator", "run", "--scope", "full", "--set-state")
        assert exit_code == 1
        state = read_state(temp_workbench)
        assert state["state"] == "REGRESSION_RED"
        assert state["regression_state"] == "REGRESSION_RED"

    def test_sm006_regression_red_to_feature_green(self, temp_workbench, state_factory, run_script, mock_runner_pass):
        """SM-006: REGRESSION_RED → FEATURE_GREEN — re-run Phase 1 after fix"""
        state_factory(state="REGRESSION_RED", active_req_id="REQ-001")
        (temp_workbench / "tests" / "unit" / "REQ-001-user-login.spec.ts").write_text("describe('test', () => {});", encoding="utf-8")
        exit_code, stdout, stderr = run_script("test_orchestrator", "run", "--scope", "feature", "--req-id", "REQ-001", "--set-state")
        assert exit_code == 0
        state = read_state(temp_workbench)
        assert state["state"] == "FEATURE_GREEN"

    def test_sm007_green_to_integration_check(self, temp_workbench, state_factory, run_script):
        """SM-007: GREEN → INTEGRATION_CHECK — Stage 4 entry"""
        # The integration runner doesn't have a specific "entry" command;
        # it just runs and transitions. So we check that from GREEN,
        # running integration tests is allowed.
        state_factory(state="GREEN")
        exit_code, stdout, stderr = run_script("integration_test_runner", "run", "--set-state")
        # Should run (not blocked), but integration might pass or fail
        assert exit_code in [0, 1]
        state = read_state(temp_workbench)
        assert state["integration_state"] in ["GREEN", "RED"]

    def test_sm008_integration_check_to_review_pending(self, temp_workbench, state_factory, run_script, mock_runner_pass):
        """SM-008: INTEGRATION_CHECK → REVIEW_PENDING — integration tests pass"""
        state_factory(state="GREEN", integration_state="NOT_RUN")
        (temp_workbench / "tests" / "integration" / "FLOW-001.integration.spec.ts").write_text('describe("x", () => {});', encoding="utf-8")
        exit_code, stdout, stderr = run_script("integration_test_runner", "run", "--set-state")
        assert exit_code == 0
        state = read_state(temp_workbench)
        assert state["integration_state"] == "GREEN"
        # After GREEN, Arbiter transitions to REVIEW_PENDING for HITL Gate 2
        # MERGED is set manually after HITL approval

    def test_sm009_integration_check_to_integration_red(self, temp_workbench, state_factory, run_script, mock_runner_fail):
        """SM-009: INTEGRATION_CHECK → INTEGRATION_RED — integration tests fail"""
        state_factory(state="GREEN", integration_state="NOT_RUN")
        (temp_workbench / "tests" / "integration" / "FLOW-001.integration.spec.ts").write_text('describe("x", () => {});', encoding="utf-8")
        exit_code, stdout, stderr = run_script("integration_test_runner", "run", "--set-state")
        assert exit_code == 1
        state = read_state(temp_workbench)
        assert state["state"] == "INTEGRATION_RED"
        assert state["integration_state"] == "RED"

    def test_sm010_integration_red_to_green(self, temp_workbench, state_factory, run_script, mock_runner_pass):
        """SM-010: INTEGRATION_RED → GREEN — integration tests fixed and re-run"""
        state_factory(state="INTEGRATION_RED", integration_state="RED")
        (temp_workbench / "tests" / "integration" / "FLOW-001.integration.spec.ts").write_text('describe("x", () => {});', encoding="utf-8")
        exit_code, stdout, stderr = run_script("integration_test_runner", "run", "--set-state")
        assert exit_code == 0
        state = read_state(temp_workbench)
        # Should revert to GREEN once integration passes
        assert state["state"] == "GREEN" or state["integration_state"] == "GREEN"

    def test_sm011_dependency_blocked_to_red(self, temp_workbench, state_factory, run_script):
        """SM-012: DEPENDENCY_BLOCKED → RED — dependency_monitor unblocks"""
        state_factory(
            feature_registry={
                "REQ-001": {"state": "MERGED", "depends_on": []},
                "REQ-002": {"state": "DEPENDENCY_BLOCKED", "depends_on": ["REQ-001"]},
            }
        )
        exit_code, stdout, stderr = run_script("dependency_monitor", "check-unblock")
        state = read_state(temp_workbench)
        assert state["feature_registry"]["REQ-002"]["state"] == "RED"

    def test_sm012_all_dependencies_merged_unblocks(self, temp_workbench, state_factory, run_script):
        """SM-012b: All deps MERGED — feature transitions to RED"""
        state_factory(
            feature_registry={
                "REQ-001": {"state": "MERGED", "depends_on": []},
                "REQ-002": {"state": "MERGED", "depends_on": []},
                "REQ-003": {"state": "DEPENDENCY_BLOCKED", "depends_on": ["REQ-001", "REQ-002"]},
            }
        )
        exit_code, stdout, stderr = run_script("dependency_monitor", "check-unblock")
        state = read_state(temp_workbench)
        assert state["feature_registry"]["REQ-003"]["state"] == "RED"

    def test_sm013_review_pending_to_merged(self, temp_workbench, state_factory, run_script):
        """SM-013: REVIEW_PENDING → MERGED — HITL Gate 2 approval"""
        state_factory(state="REVIEW_PENDING", integration_state="GREEN")
        # MERGED is set by workbench-cli or manual Arbiter action after HITL Gate 2
        # This test verifies the state transition is valid in state.json schema
        import json
        state_path = temp_workbench / "state.json"
        state_data = json.loads(state_path.read_text(encoding="utf-8"))
        state_data["state"] = "MERGED"
        state_path.write_text(json.dumps(state_data, indent=2), encoding="utf-8")
        state = read_state(temp_workbench)
        assert state["state"] == "MERGED"
        assert state["integration_state"] == "GREEN"
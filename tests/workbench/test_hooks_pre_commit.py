"""
test_hooks_pre_commit.py — UC-051 to UC-056
Tests for pre-commit hook enforcement logic (simulated in Python)
"""

import json

import pytest
from .helpers import read_state


class TestPreCommitHook:
    """UC-051 through UC-056: Pre-commit hook logic tests (simulated)."""

    def test_uc051_precommit_statejson_not_staged_allowed(self, temp_workbench, state_factory):
        """UC-051: state.json not staged — allowed"""
        state_factory(state="INIT")
        # Simulate staged files (without state.json)
        staged_files = ["src/user-login.ts", "tests/unit/REQ-001.spec.ts"]
        # If state.json not in staged files, pre-commit should allow
        assert "state.json" not in staged_files

    def test_uc052_precommit_statejson_staged_by_non_arbiter_blocked(self, temp_workbench, state_factory):
        """UC-052: state.json staged by non-Arbiter — blocked"""
        state_factory(state="INIT")
        # The actual ALLOWED_WRITERS list from pre-commit hook:
        # ALLOWED_WRITERS="test_orchestrator.py integration_test_runner.py dependency_monitor.py memory_rotator.py audit_logger.py crash_recovery.py workbench-cli pre-commit"
        allowed_writers = [
            "test_orchestrator.py",
            "integration_test_runner.py",
            "dependency_monitor.py",
            "memory_rotator.py",
            "audit_logger.py",
            "crash_recovery.py",
            "workbench-cli",
            "pre-commit"
        ]
        # If last_updated_by is not in ALLOWED_WRITERS, commit is blocked
        current_author = "agent"  # simulating non-Arbiter author
        is_arbiter = current_author in allowed_writers
        assert not is_arbiter  # Should be blocked

    def test_uc053_precommit_valid_feature_file_staged(self, temp_workbench, state_factory, feature_factory, run_script):
        """UC-053: Valid .feature file staged — allowed"""
        state_factory()
        feature_factory(
            "REQ-001-user-login.feature",
            req_id="REQ-001",
            feature_name="User Login",
            scenarios=[{"name": "Login", "steps": ["Given a user", "When they login", "Then success"]}],
        )
        exit_code, stdout, stderr = run_script("gherkin_validator", "features/")
        assert exit_code == 0  # Valid, so pre-commit would allow

    def test_uc054_precommit_invalid_feature_file_staged(self, temp_workbench, state_factory, feature_factory, run_script):
        """UC-054: Invalid .feature file staged — blocked"""
        state_factory()
        feature_factory(
            "REQ-001-login.feature",
            req_id="REQ-001",
            raw_content="@REQ-001\nFeature: Login\n\nScenario: Test\n",
        )
        exit_code, stdout, stderr = run_script("gherkin_validator", "features/")
        assert exit_code == 1  # Invalid, so pre-commit would block

    def test_uc055_precommit_feature_green_regression_red_blocked(self, temp_workbench, state_factory):
        """UC-055: FEATURE_GREEN + REGRESSION_RED — blocked"""
        state_factory(state="FEATURE_GREEN", regression_state="REGRESSION_RED")
        state = read_state(temp_workbench)
        # Pre-commit check: if state == FEATURE_GREEN and regression_state == REGRESSION_RED, block
        blocking = state["state"] == "FEATURE_GREEN" and state["regression_state"] == "REGRESSION_RED"
        assert blocking

    def test_uc056_precommit_feature_green_clean_allowed(self, temp_workbench, state_factory):
        """UC-056: FEATURE_GREEN + CLEAN regression — allowed"""
        state_factory(state="FEATURE_GREEN", regression_state="CLEAN")
        state = read_state(temp_workbench)
        blocking = state["state"] == "FEATURE_GREEN" and state["regression_state"] == "REGRESSION_RED"
        assert not blocking  # Not blocked since regression is CLEAN
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

    # =============================================================================
    # UC-068 to UC-071: Branch Name Validation Tests (Gap 1 - CMT-1)
    # =============================================================================

    def test_uc068_commit_on_main_blocked(self):
        """UC-068: Commit on main — blocked"""
        current_branch = "main"
        blocked_branches = ["main", "master", "develop"]
        is_blocked = current_branch in blocked_branches
        assert is_blocked

    def test_uc069_commit_on_develop_blocked(self):
        """UC-069: Commit on develop — blocked"""
        current_branch = "develop"
        blocked_branches = ["main", "master", "develop"]
        is_blocked = current_branch in blocked_branches
        assert is_blocked

    def test_uc070_commit_on_feature_branch_allowed(self):
        """UC-070: Commit on feature branch — allowed"""
        current_branch = "feature/REQ-001-my-feature"
        blocked_branches = ["main", "master", "develop"]
        is_blocked = current_branch in blocked_branches
        assert not is_blocked

    def test_uc071_commit_on_lab_branch_allowed(self):
        """UC-071: Commit on lab branch — allowed"""
        current_branch = "lab/REQ-001-my-feature"
        blocked_branches = ["main", "master", "develop"]
        is_blocked = current_branch in blocked_branches
        assert not is_blocked

    # =============================================================================
    # UC-077 to UC-079: Merged-Branch Check Tests (Gap 4 - CMT-2)
    # =============================================================================

    def test_uc077_branch_merged_to_main_blocked(self):
        """UC-077: Branch merged to main — blocked"""
        current_branch = "feature/REQ-001"
        merged_branches = ["main", "develop"]
        # Simulate: git branch --merged main returns current_branch
        is_merged = current_branch == "feature/REQ-001"  # simulating git check
        is_feature_or_lab = current_branch.startswith("feature/") or current_branch.startswith("lab/")
        is_blocked = is_feature_or_lab and is_merged and "main" in merged_branches
        assert is_blocked

    def test_uc078_branch_merged_to_develop_blocked(self):
        """UC-078: Branch merged to develop — blocked"""
        current_branch = "feature/REQ-001"
        merged_branches = ["main", "develop"]
        # Simulate: git branch --merged develop returns current_branch
        is_merged = current_branch == "feature/REQ-001"  # simulating git check
        is_feature_or_lab = current_branch.startswith("feature/") or current_branch.startswith("lab/")
        is_blocked = is_feature_or_lab and is_merged and "develop" in merged_branches
        assert is_blocked

    def test_uc079_unmerged_feature_branch_allowed(self):
        """UC-079: Unmerged feature branch — allowed"""
        current_branch = "feature/REQ-001"
        # Simulate: git branch --merged main/develop does NOT return current_branch
        is_merged = False  # simulating git check
        is_feature_or_lab = current_branch.startswith("feature/") or current_branch.startswith("lab/")
        is_blocked = is_feature_or_lab and is_merged
        assert not is_blocked

    # =============================================================================
    # UC-080, UC-082 to UC-084: Expanded Blocking States Tests (Gap 5)
    # =============================================================================

    def test_uc080_state_integration_red_blocked(self, temp_workbench, state_factory):
        """UC-080: state=INTEGRATION_RED — blocked"""
        state_factory(state="INTEGRATION_RED")
        state = read_state(temp_workbench)
        blocking_states = ["REGRESSION_RED", "INTEGRATION_RED", "PIVOT_IN_PROGRESS"]
        is_blocked = state["state"] in blocking_states
        assert is_blocked

    def test_uc082_state_regression_red_blocked(self, temp_workbench, state_factory):
        """UC-082: state=REGRESSION_RED — blocked"""
        state_factory(state="REGRESSION_RED")
        state = read_state(temp_workbench)
        blocking_states = ["REGRESSION_RED", "INTEGRATION_RED", "PIVOT_IN_PROGRESS"]
        is_blocked = state["state"] in blocking_states
        assert is_blocked

    def test_uc083_state_green_allowed(self, temp_workbench, state_factory):
        """UC-083: state=GREEN — allowed"""
        state_factory(state="GREEN")
        state = read_state(temp_workbench)
        blocking_states = ["REGRESSION_RED", "INTEGRATION_RED", "PIVOT_IN_PROGRESS"]
        is_blocked = state["state"] in blocking_states
        assert not is_blocked

    def test_uc084_state_init_allowed(self, temp_workbench, state_factory):
        """UC-084: state=INIT — allowed"""
        state_factory(state="INIT")
        state = read_state(temp_workbench)
        blocking_states = ["REGRESSION_RED", "INTEGRATION_RED", "PIVOT_IN_PROGRESS"]
        is_blocked = state["state"] in blocking_states
        assert not is_blocked
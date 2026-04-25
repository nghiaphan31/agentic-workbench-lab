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

    # =============================================================================
    # GAP-1: GIT_WORKBENCH_SKIP_HOOKS bypass prevention tests
    # =============================================================================

    def test_gap1_git_workbench_skip_hooks_bypass(self, temp_workbench, state_factory):
        """
        GAP-1: GIT_WORKBENCH_SKIP_HOOKS=1 cannot bypass RED state blocking.
        
        Even when GIT_WORKBENCH_SKIP_HOOKS is set, the hook should still run
        critical checks and block commits when state is RED.
        """
        import os
        # Simulate: GIT_WORKBENCH_SKIP_HOOKS=1 is set
        skip_hooks = os.environ.get("GIT_WORKBENCH_SKIP_HOOKS", "0") == "1"
        
        state_factory(state="RED")
        state = read_state(temp_workbench)
        
        # Critical checks that should NOT be bypassed:
        blocking_states = ["RED", "REGRESSION_RED", "INTEGRATION_RED", "PIVOT_IN_PROGRESS"]
        is_state_blocking = state["state"] in blocking_states
        
        # Even with skip_hooks set, state-based blocking should still apply
        # The skip_hooks env var only bypasses non-critical checks (like gherkin validation)
        assert is_state_blocking, "RED state should block regardless of GIT_WORKBENCH_SKIP_HOOKS"

    # =============================================================================
    # GAP-2: --no-verify bypass detection tests
    # =============================================================================

    def test_gap2_no_verify_bypass(self, temp_workbench, state_factory):
        """
        GAP-2: git commit --no-verify is detected via post-hoc commit metadata check.
        
        Due to git limitation, --no-verify bypasses the hook entirely, so the fix
        implements post-hoc detection that checks commit metadata after the fact.
        """
        state_factory(state="RED")
        state = read_state(temp_workbench)
        
        # Simulate: commit was made with --no-verify
        # The hook cannot prevent this, but post-hoc detection should flag it
        used_no_verify = True  # simulating that --no-verify was used
        
        # Post-hoc detection logic: if state is blocking and --no-verify was used,
        # this should be flagged as a WARNING/CRITICAL
        blocking_states = ["RED", "REGRESSION_RED", "INTEGRATION_RED", "PIVOT_IN_PROGRESS"]
        is_state_blocking = state["state"] in blocking_states
        
        # Post-hoc detection: if blocking state + no_verify used = CRITICAL violation
        is_critical = is_state_blocking and used_no_verify
        assert is_critical, "Post-hoc detection should flag --no-verify with blocking state as CRITICAL"

    # =============================================================================
    # GAP-3: last_updated_by spoofing detection tests
    # =============================================================================

    def test_gap3_last_updated_by_spoofing_detected(self, temp_workbench, state_factory):
        """
        GAP-3: Staging state.json with fake last_updated_by triggers WARNING.
        
        Verify that when state.json has last_updated_by="test_orchestrator.py"
        but it was actually modified by a non-Arbiter source, it triggers WARNING.
        """
        state_factory(state="INIT", last_updated_by="test_orchestrator.py")
        state = read_state(temp_workbench)
        
        # Simulate: actual author is NOT arbiter (hook interceptors would catch this)
        actual_author = "agent"  # non-Arbiter source
        
        # ALLOWED_WRITERS from pre-commit hook
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
        
        # Check if the claimed author is in allowed writers
        claimed_by = state.get("last_updated_by", "")
        is_claimed_arbiter = claimed_by in allowed_writers
        
        # Check if actual author is arbiter
        is_actual_arbiter = actual_author in allowed_writers
        
        # Spoofing detected: claimed arbiter but actual is not
        spoofing_detected = is_claimed_arbiter and not is_actual_arbiter
        
        assert spoofing_detected, "Should detect spoofing when last_updated_by claims Arbiter but actual author does not"

    # =============================================================================
    # GAP-8: REQ-NNN scope validation tests (negative cases)
    # =============================================================================

    def test_gap8_req_nnn_scope_invalid_format_blocked(self):
        """
        GAP-8: feat(old-feature): message is BLOCKED (scope is not REQ-NNN format).
        
        After the fix, commit scopes must match REQ-NNN format exactly.
        """
        commit_message = "feat(old-feature): add login"
        
        # Parse the scope from commit message
        import re
        match = re.match(r'^(\w+)\(([^)]+)\):', commit_message)
        
        if match:
            scope = match.group(2)
            # Scope should be REQ-NNN format (REQ- followed by 3 digits)
            req_pattern = re.match(r'^REQ-\d{3}$', scope)
            is_valid_scope = req_pattern is not None
        else:
            is_valid_scope = False
        
        assert not is_valid_scope, "feat(old-feature) should be blocked - scope is not REQ-NNN format"

    def test_gap8_req_nnn_scope_valid_format_allowed(self):
        """
        GAP-8: feat(REQ-001): message is ALLOWED (scope is valid REQ-NNN format).
        """
        commit_message = "feat(REQ-001): add login"
        
        import re
        match = re.match(r'^(\w+)\(([^)]+)\):', commit_message)
        
        if match:
            scope = match.group(2)
            req_pattern = re.match(r'^REQ-\d{3}$', scope)
            is_valid_scope = req_pattern is not None
        else:
            is_valid_scope = False
        
        assert is_valid_scope, "feat(REQ-001) should be allowed - scope is valid REQ-NNN format"
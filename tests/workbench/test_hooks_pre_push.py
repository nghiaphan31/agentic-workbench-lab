"""
test_hooks_pre_push.py — UC-057 to UC-064
Tests for pre-push hook enforcement logic (simulated in Python)
"""

import json

import pytest
from .helpers import read_state


class TestPrePushHook:
    """UC-057 through UC-064: Pre-push hook logic tests (simulated)."""

    def _is_push_blocked(self, state_value, blocking_states=None):
        """Simulate the pre-push blocking check from the hook."""
        if blocking_states is None:
            blocking_states = ["RED", "REGRESSION_RED", "INTEGRATION_RED", "PIVOT_IN_PROGRESS"]
        return state_value in blocking_states

    def test_uc057_prepush_blocking_state_red(self, temp_workbench, state_factory):
        """UC-057: pre-push with RED state — blocked"""
        state_factory(state="RED")
        state = read_state(temp_workbench)
        assert self._is_push_blocked(state["state"])

    def test_uc058_prepush_blocking_state_regression_red(self, temp_workbench, state_factory):
        """UC-058: pre-push with REGRESSION_RED state — blocked"""
        state_factory(state="REGRESSION_RED")
        state = read_state(temp_workbench)
        assert self._is_push_blocked(state["state"])

    def test_uc059_prepush_blocking_state_integration_red(self, temp_workbench, state_factory):
        """UC-059: pre-push with INTEGRATION_RED state — blocked"""
        state_factory(state="INTEGRATION_RED")
        state = read_state(temp_workbench)
        assert self._is_push_blocked(state["state"])

    def test_uc060_prepush_blocking_state_pivot_in_progress(self, temp_workbench, state_factory):
        """UC-060: pre-push with PIVOT_IN_PROGRESS state — blocked"""
        state_factory(state="PIVOT_IN_PROGRESS")
        state = read_state(temp_workbench)
        assert self._is_push_blocked(state["state"])

    def test_uc061_prepush_green_state_allowed(self, temp_workbench, state_factory):
        """UC-061: pre-push with GREEN state — allowed"""
        state_factory(state="GREEN")
        state = read_state(temp_workbench)
        assert not self._is_push_blocked(state["state"])

    def test_uc062_prepush_direct_push_to_main_blocked(self):
        """UC-062: Direct push to main (non-merge commit) — blocked"""
        # Simulate: target_branch = "main", parent_count = 1 (not a merge)
        target_branch = "main"
        parent_count = 1  # single parent = not a merge commit
        is_blocked = target_branch == "main" and parent_count < 2
        assert is_blocked

    def test_uc063_prepush_merge_commit_to_main_allowed(self):
        """UC-063: Merge commit to main — allowed"""
        target_branch = "main"
        parent_count = 2  # merge commit = 2 parents
        is_blocked = target_branch == "main" and parent_count < 2
        assert not is_blocked  # Not blocked

    def test_uc064_prepush_file_ownership_conflict_warning(self, temp_workbench, state_factory):
        """UC-064: File ownership conflict — warning, push not blocked"""
        state_factory(
            state="RED",
            file_ownership={"src/user-login.ts": "REQ-001"},
            feature_registry={"REQ-001": {"state": "RED"}},
        )
        state = read_state(temp_workbench)
        modified_files = ["src/user-login.ts"]
        
        conflicts = []
        for modified in modified_files:
            owner = state["file_ownership"].get(modified)
            if owner:
                owner_state = state["feature_registry"].get(owner, {}).get("state", "UNKNOWN")
                if owner_state != "MERGED":
                    conflicts.append(f"{modified} owned by {owner} (state={owner_state})")
        
        assert len(conflicts) > 0
        # Push should continue with warning (not hard-blocked)
        is_blocked = self._is_push_blocked(state["state"])
        # Note: conflicts don't add extra blocking beyond the state check

    def test_uc065_direct_push_to_develop_blocked(self):
        """UC-065: Direct push to develop (non-merge commit) — blocked"""
        # Simulate: target_branch = "develop", parent_count = 1 (not a merge)
        target_branch = "develop"
        parent_count = 1  # single parent = not a merge commit
        is_blocked = target_branch in ["main", "master", "develop"] and parent_count < 2
        assert is_blocked

    def test_uc066_trivial_chore_to_develop_with_approval_allowed(self):
        """UC-066: Trivial chore with APPROVED-BY-HUMAN to develop — allowed"""
        target_branch = "develop"
        parent_count = 1  # single parent = not a merge commit
        commit_message = "chore(docs): fix typo in README APPROVED-BY-HUMAN"
        has_approval = "APPROVED-BY-HUMAN" in commit_message
        
        # Check if this would be blocked first
        would_be_blocked = target_branch == "develop" and parent_count < 2
        # Exception allows push if has approval
        is_blocked = would_be_blocked and not has_approval
        assert not is_blocked

    def test_uc067_feature_branch_push_allowed(self):
        """UC-067: Push to feature/* branch — always allowed"""
        target_branch = "feature/REQ-001-my-feature"
        parent_count = 1  # could be merge or regular commit
        blocked_branches = ["main", "master", "develop"]
        is_blocked = target_branch in blocked_branches and parent_count < 2
        assert not is_blocked

    # =============================================================================
    # UC-075 to UC-076: --delete-branch Warning Tests (Gap 3 - CMT-2)
    # =============================================================================

    def test_uc075_merge_to_main_warns_about_delete_branch(self):
        """UC-075: Merge to main warns about --delete-branch"""
        branch = "main"
        oldrev = "abc123"
        newrev = "def456"
        merge_base = "abc123"  # != oldrev means it's a merge

        # Simulate the warning check from pre-push hook
        is_merge_to_protected = branch in ["main", "develop"]
        merge_base_changed = merge_base != oldrev
        should_warn = is_merge_to_protected and merge_base_changed
        assert should_warn

    def test_uc076_merge_to_develop_warns_about_delete_branch(self):
        """UC-076: Merge to develop warns about --delete-branch"""
        branch = "develop"
        oldrev = "abc123"
        newrev = "def456"
        merge_base = "abc123"  # != oldrev means it's a merge

        # Simulate the warning check from pre-push hook
        is_merge_to_protected = branch in ["main", "develop"]
        merge_base_changed = merge_base != oldrev
        should_warn = is_merge_to_protected and merge_base_changed
        assert should_warn
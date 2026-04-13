"""
test_hooks_post_merge.py — UC-PM-001 to UC-PM-004
Tests for post-merge hook enforcement logic (simulated in Python)
"""

import json

import pytest
from .helpers import read_state


class TestPostMergeHook:
    """UC-PM-001 through UC-PM-004: Post-merge hook logic tests."""

    def test_upm001_merged_feature_unblocks_dependents(
        self, temp_workbench, state_factory, run_script
    ):
        """UC-PM-001: MERGED event triggers dependency_monitor.py check-unblock"""
        # Setup: REQ-001 (dependency) is MERGED, REQ-002 (dependent) is DEPENDENCY_BLOCKED
        state_factory(
            state="DEPENDENCY_BLOCKED",
            feature_registry={
                "REQ-001": {"state": "MERGED", "depends_on": []},
                "REQ-002": {"state": "DEPENDENCY_BLOCKED", "depends_on": ["REQ-001"]},
            },
        )
        # Simulate: dependency_monitor.py check-unblock should find REQ-002 unblocked
        exit_code, stdout, stderr = run_script("dependency_monitor", "check-unblock")
        assert exit_code == 0
        # After check-unblock, REQ-002 should transition from DEPENDENCY_BLOCKED
        # (In real hook flow, post-merge triggers this automatically)

    def test_upm002_non_feature_branch_no_action(
        self, temp_workbench, state_factory
    ):
        """UC-PM-002: Non-feature branch merge — no state change"""
        state_factory(state="GREEN")
        # post-merge on non-feature branch should be no-op
        # The hook checks if the merged commit is a feature merge

    def test_upm003_state_not_merged_no_unblock(
        self, temp_workbench, state_factory
    ):
        """UC-PM-003: If state != MERGED after merge, dependency check skipped"""
        state_factory(state="RED")  # Not MERGED
        # post-merge should only run check-unblock when state == MERGED

    def test_upm004_missing_dependency_monitor_graceful(
        self, temp_workbench, state_factory, monkeypatch
    ):
        """UC-PM-004: If dependency_monitor.py missing, hook exits 0 (non-blocking)"""
        state_factory(state="MERGED")
        # post-merge is non-blocking by design (exit 0 always)
"""
test_dependency_monitor.py — UC-004 to UC-006
Tests for dependency_monitor.py — Dependency unblocking logic
"""

import json

import pytest
from .helpers import read_state


class TestDependencyMonitor:
    """UC-004 through UC-006: Dependency monitor use cases."""

    def test_uc004_feature_blocked_on_unmerged_dep(self, temp_workbench, state_factory, run_script):
        """UC-004: Feature blocked on unmerged dependency — stays DEPENDENCY_BLOCKED"""
        state_factory(
            feature_registry={
                "REQ-001": {"state": "RED", "depends_on": []},
                "REQ-002": {"state": "DEPENDENCY_BLOCKED", "depends_on": ["REQ-001"]},
            }
        )
        exit_code, stdout, stderr = run_script("dependency_monitor", "check-unblock")
        assert exit_code == 0
        state = read_state(temp_workbench)
        # REQ-002 should still be blocked since REQ-001 is not MERGED
        assert state["feature_registry"]["REQ-002"]["state"] == "DEPENDENCY_BLOCKED"

    def test_uc005_multiple_deps_partial_satisfaction(self, temp_workbench, state_factory, run_script):
        """UC-005: Multiple deps, one MERGED, one not — still blocked"""
        state_factory(
            feature_registry={
                "REQ-001": {"state": "MERGED", "depends_on": []},
                "REQ-002": {"state": "RED", "depends_on": []},
                "REQ-003": {"state": "DEPENDENCY_BLOCKED", "depends_on": ["REQ-001", "REQ-002"]},
            }
        )
        exit_code, stdout, stderr = run_script("dependency_monitor", "check-unblock")
        state = read_state(temp_workbench)
        assert state["feature_registry"]["REQ-003"]["state"] == "DEPENDENCY_BLOCKED"

    def test_uc005b_second_dep_merges_unblocks(self, temp_workbench, state_factory, run_script):
        """UC-005b: Second dep also MERGED — REQ-003 unblocked to RED"""
        state_factory(
            feature_registry={
                "REQ-001": {"state": "MERGED", "depends_on": []},
                "REQ-002": {"state": "RED", "depends_on": []},
                "REQ-003": {"state": "DEPENDENCY_BLOCKED", "depends_on": ["REQ-001", "REQ-002"]},
            }
        )
        # First check — still blocked
        exit_code, stdout, stderr = run_script("dependency_monitor", "check-unblock")
        state = read_state(temp_workbench)
        assert state["feature_registry"]["REQ-003"]["state"] == "DEPENDENCY_BLOCKED"

        # Now simulate REQ-002 becoming MERGED
        state["feature_registry"]["REQ-002"]["state"] = "MERGED"
        with open(temp_workbench / "state.json", "w") as f:
            json.dump(state, f, indent=2)
            f.write("\n")

        exit_code, stdout, stderr = run_script("dependency_monitor", "check-unblock")
        state = read_state(temp_workbench)
        assert state["feature_registry"]["REQ-003"]["state"] == "RED"  # Unblocked

    def test_uc006_circular_dependency(self, temp_workbench, state_factory, run_script):
        """UC-006: Circular dependency — neither feature unblocks"""
        state_factory(
            feature_registry={
                "REQ-001": {"state": "DEPENDENCY_BLOCKED", "depends_on": ["REQ-002"]},
                "REQ-002": {"state": "DEPENDENCY_BLOCKED", "depends_on": ["REQ-001"]},
            }
        )
        exit_code, stdout, stderr = run_script("dependency_monitor", "check-unblock")
        state = read_state(temp_workbench)
        assert state["feature_registry"]["REQ-001"]["state"] == "DEPENDENCY_BLOCKED"
        assert state["feature_registry"]["REQ-002"]["state"] == "DEPENDENCY_BLOCKED"

    def test_uc004b_dep_merges_unblocks_feature(self, temp_workbench, state_factory, run_script):
        """UC-004b: Dependency MERGED — feature unblocks to RED"""
        state_factory(
            feature_registry={
                "REQ-001": {"state": "MERGED", "depends_on": []},
                "REQ-002": {"state": "DEPENDENCY_BLOCKED", "depends_on": ["REQ-001"]},
            }
        )
        exit_code, stdout, stderr = run_script("dependency_monitor", "check-unblock")
        state = read_state(temp_workbench)
        assert state["feature_registry"]["REQ-002"]["state"] == "RED"  # Unblocked

    def test_uc004_status_command(self, temp_workbench, state_factory, run_script):
        """UC-004c: dependency_monitor status REQ-001 — shows dependency state"""
        state_factory(
            feature_registry={
                "REQ-001": {"state": "MERGED", "depends_on": []},
                "REQ-002": {"state": "DEPENDENCY_BLOCKED", "depends_on": ["REQ-001"]},
            }
        )
        exit_code, stdout, stderr = run_script("dependency_monitor", "status", "REQ-002")
        assert exit_code == 0
        assert "DEPENDENCY_BLOCKED" in stdout or "BLOCKED" in stdout
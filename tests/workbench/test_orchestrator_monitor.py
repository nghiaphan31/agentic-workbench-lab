"""
test_orchestrator_monitor.py — Tests for Orchestrator Agent Status Monitor

Phase 3: Orchestrator Monitoring Tests

Tests the orchestrator_monitor.py module which provides comprehensive
monitoring for the Orchestrator Agent — gates, dependencies, blocking states.
"""

import json
import sys
from pathlib import Path

import pytest

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent.parent.parent / "agentic-workbench-engine" / ".workbench" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import orchestrator_monitor
from orchestrator_monitor import (
    generate_orchestrator_report,
    check_blocking_states,
    check_dependency_blocks,
    format_status_table,
    load_state,
)


class TestOrchestratorMonitor:
    """Tests for orchestrator_monitor.py orchestrator status monitoring."""

    @pytest.fixture
    def state_init(self):
        """INIT state — no features."""
        return {
            "version": "2.1",
            "state": "INIT",
            "active_req_id": None,
            "feature_registry": {},
        }

    @pytest.fixture
    def state_with_gates(self):
        """State with pending gates."""
        return {
            "version": "2.1",
            "state": "REVIEW_PENDING",
            "active_req_id": "REQ-001",
            "feature_registry": {
                "REQ-001": {
                    "state": "REVIEW_PENDING",
                    "slug": "feature-one",
                    "depends_on": [],
                }
            },
        }

    @pytest.fixture
    def state_dependency_blocked(self):
        """State with dependency blocks."""
        return {
            "version": "2.1",
            "state": "DEPENDENCY_BLOCKED",
            "active_req_id": "REQ-002",
            "feature_registry": {
                "REQ-001": {
                    "state": "MERGED",
                    "slug": "merged-feature",
                    "depends_on": [],
                },
                "REQ-002": {
                    "state": "DEPENDENCY_BLOCKED",
                    "slug": "blocked-feature",
                    "depends_on": ["REQ-001"],
                },
            },
        }

    @pytest.fixture
    def state_red(self):
        """State with RED blocking state."""
        return {
            "version": "2.1",
            "state": "RED",
            "active_req_id": "REQ-003",
            "feature_registry": {
                "REQ-003": {
                    "state": "RED",
                    "slug": "red-feature",
                    "depends_on": [],
                }
            },
        }

    @pytest.fixture
    def state_comprehensive(self):
        """State with multiple issues."""
        return {
            "version": "2.1",
            "state": "RED",  # Changed from REVIEW_PENDING to avoid double-counting gates
            "active_req_id": "REQ-003",
            "feature_registry": {
                "REQ-001": {
                    "state": "REQUIREMENTS_LOCKED",  # Gate state, not active
                    "slug": "feature-one",
                    "depends_on": [],
                },
                "REQ-002": {
                    "state": "MERGED",
                    "slug": "merged-feature",
                    "depends_on": [],
                },
                "REQ-003": {
                    "state": "RED",
                    "slug": "red-feature",
                    "depends_on": [],
                },
            },
        }

    def test_init_state_report(self, state_init):
        """OM-01: INIT state generates clean report"""
        report = generate_orchestrator_report(state_init)
        assert report["current_state"] == "INIT"
        assert report["summary"]["total_pending_gates"] == 0
        assert report["summary"]["human_blocking_gates"] == 0

    def test_review_pending_has_pending_gate(self, state_with_gates):
        """OM-02: REVIEW_PENDING state has pending HITL 2 gate"""
        report = generate_orchestrator_report(state_with_gates)
        assert report["summary"]["total_pending_gates"] == 1
        assert report["pending_gates"][0]["gate"] == "HITL 2"
        assert report["pending_gates"][0]["is_human_blocking"] == True

    def test_dependency_block_detected(self, state_dependency_blocked):
        """OM-03: DEPENDENCY_BLOCKED feature detected"""
        report = generate_orchestrator_report(state_dependency_blocked)
        assert report["summary"]["total_dependency_blocks"] == 1
        assert report["dependency_blocks"][0]["req_id"] == "REQ-002"

    def test_red_state_blocking(self, state_red):
        """OM-04: RED state is blocking"""
        report = generate_orchestrator_report(state_red)
        assert report["summary"]["total_blocking_states"] == 1
        assert report["blocking_states"][0]["state"] == "RED"

    def test_comprehensive_report_multiple_issues(self, state_comprehensive):
        """OM-05: Comprehensive state with multiple issues"""
        report = generate_orchestrator_report(state_comprehensive)
        # REQUIREMENTS_LOCKED (HITL 1) from feature_registry
        assert report["summary"]["total_pending_gates"] == 1
        # DEPENDENCY_BLOCKED not in this state
        assert report["summary"]["total_dependency_blocks"] == 0
        # RED is a blocking state
        assert report["summary"]["total_blocking_states"] == 1

    def test_enrollment_blocking_in_report(self, state_init):
        """OM-06: Enrollment CRITICAL reflected in report"""
        report = generate_orchestrator_report(state_init)
        assert report["enrollment"]["is_blocking"] == True
        assert report["enrollment"]["level"] == "CRITICAL"

    def test_check_blocking_states_red(self, state_red):
        """OM-07: check_blocking_states detects RED"""
        states = check_blocking_states(state_red)
        assert len(states) == 1
        assert states[0]["state"] == "RED"

    def test_check_blocking_states_no_blocking(self, state_init):
        """OM-08: check_blocking_states returns empty for INIT"""
        states = check_blocking_states(state_init)
        assert len(states) == 0

    def test_check_dependency_blocks_detected(self, state_dependency_blocked):
        """OM-09: check_dependency_blocks detects blocked features"""
        blocks = check_dependency_blocks(state_dependency_blocked)
        assert len(blocks) == 1
        assert blocks[0]["req_id"] == "REQ-002"

    def test_check_dependency_blocks_none(self, state_init):
        """OM-10: check_dependency_blocks returns empty when none"""
        blocks = check_dependency_blocks(state_init)
        assert len(blocks) == 0


class TestOrchestratorMonitorFormat:
    """Tests for orchestrator monitor output formatting."""

    @pytest.fixture
    def state_init(self):
        return {
            "version": "2.1",
            "state": "INIT",
            "active_req_id": None,
            "feature_registry": {},
        }

    @pytest.fixture
    def state_with_gates(self):
        return {
            "version": "2.1",
            "state": "REVIEW_PENDING",
            "active_req_id": "REQ-001",
            "feature_registry": {
                "REQ-001": {
                    "state": "REVIEW_PENDING",
                    "slug": "feature-one",
                    "depends_on": [],
                }
            },
        }

    def test_format_status_table_contains_report_header(self, state_init):
        """OM-11: Status table contains report header"""
        report = generate_orchestrator_report(state_init)
        formatted = format_status_table(report)
        assert "## Orchestrator Status Report" in formatted

    def test_format_status_table_no_gates(self, state_init):
        """OM-12: Status table shows no pending gates"""
        report = generate_orchestrator_report(state_init)
        formatted = format_status_table(report)
        assert "✅ No Pending Human Actions" in formatted

    def test_format_status_table_gates(self, state_with_gates):
        """OM-13: Status table shows pending gates"""
        report = generate_orchestrator_report(state_with_gates)
        formatted = format_status_table(report)
        assert "### ⚠️ Pending Human Actions" in formatted
        assert "HITL 2" in formatted

    def test_format_status_table_enrollment_blocking(self, state_init):
        """OM-14: Status table shows enrollment blocking"""
        report = generate_orchestrator_report(state_init)
        formatted = format_status_table(report)
        assert "🚨 **ENROLLMENT BLOCKING" in formatted
"""
test_gate_notification.py — Tests for Proactive HITL Gate Notification

Phase 2: Gate Notification Tests

Tests the gate_notification.py module which monitors state.json for
gate-blocking states and surfaces pending human actions.
"""

import json
import sys
from pathlib import Path

import pytest

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent.parent.parent / "agentic-workbench-engine" / ".workbench" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from gate_notification import check_gates, GateReport, GateInfo, GATE_STATES


class TestGateNotification:
    """Tests for gate_notification.py gate detection."""

    @pytest.fixture
    def mock_state_init(self):
        """INIT state — no gates pending."""
        return {
            "version": "2.1",
            "state": "INIT",
            "active_req_id": None,
            "feature_registry": {},
        }

    @pytest.fixture
    def mock_state_requirements_locked(self):
        """REQUIREMENTS_LOCKED — HITL 1 pending."""
        return {
            "version": "2.1",
            "state": "REQUIREMENTS_LOCKED",
            "active_req_id": "REQ-001",
            "feature_registry": {
                "REQ-001": {
                    "state": "REQUIREMENTS_LOCKED",
                    "slug": "example-feature",
                    "depends_on": [],
                }
            },
        }

    @pytest.fixture
    def mock_state_review_pending(self):
        """REVIEW_PENDING — HITL 2 pending."""
        return {
            "version": "2.1",
            "state": "REVIEW_PENDING",
            "active_req_id": "REQ-002",
            "feature_registry": {
                "REQ-002": {
                    "state": "REVIEW_PENDING",
                    "slug": "another-feature",
                    "depends_on": [],
                }
            },
        }

    @pytest.fixture
    def mock_state_dependency_blocked(self):
        """DEPENDENCY_BLOCKED — Orchestrator monitoring."""
        return {
            "version": "2.1",
            "state": "DEPENDENCY_BLOCKED",
            "active_req_id": "REQ-003",
            "feature_registry": {
                "REQ-003": {
                    "state": "DEPENDENCY_BLOCKED",
                    "slug": "blocked-feature",
                    "depends_on": ["REQ-001"],
                }
            },
        }

    @pytest.fixture
    def mock_state_red(self):
        """RED — no gate, implementation in progress."""
        return {
            "version": "2.1",
            "state": "RED",
            "active_req_id": "REQ-004",
            "feature_registry": {
                "REQ-004": {
                    "state": "RED",
                    "slug": "active-feature",
                    "depends_on": [],
                }
            },
        }

    @pytest.fixture
    def mock_state_multiple_gates(self):
        """Multiple features in gate states."""
        return {
            "version": "2.1",
            "state": "RED",
            "active_req_id": "REQ-004",
            "feature_registry": {
                "REQ-001": {
                    "state": "REQUIREMENTS_LOCKED",
                    "slug": "feature-one",
                    "depends_on": [],
                },
                "REQ-002": {
                    "state": "REVIEW_PENDING",
                    "slug": "feature-two",
                    "depends_on": [],
                },
                "REQ-004": {
                    "state": "RED",
                    "slug": "active-feature",
                    "depends_on": [],
                },
            },
        }

    def test_no_gates_in_init_state(self, mock_state_init):
        """GN-01: INIT state → no pending gates"""
        report = check_gates(mock_state_init)
        assert not report.has_pending_gates()
        assert report.get_summary()["total_pending"] == 0

    def test_requirements_locked_triggers_hitl_1(self, mock_state_requirements_locked):
        """GN-02: REQUIREMENTS_LOCKED → HITL 1 pending"""
        report = check_gates(mock_state_requirements_locked)
        assert report.has_pending_gates()
        assert len(report.gates) == 1
        assert report.gates[0].gate == "HITL 1"
        assert report.gates[0].req_id == "REQ-001"
        assert "Product Owner must approve" in report.gates[0].action_required

    def test_review_pending_triggers_hitl_2(self, mock_state_review_pending):
        """GN-03: REVIEW_PENDING → HITL 2 pending"""
        report = check_gates(mock_state_review_pending)
        assert report.has_pending_gates()
        assert len(report.gates) == 1
        assert report.gates[0].gate == "HITL 2"
        assert report.gates[0].req_id == "REQ-002"
        assert "Lead Engineer must approve" in report.gates[0].action_required

    def test_dependency_blocked_triggers_orchestrator_alert(self, mock_state_dependency_blocked):
        """GN-04: DEPENDENCY_BLOCKED → Orchestrator monitoring (not human blocking)"""
        report = check_gates(mock_state_dependency_blocked)
        assert report.has_pending_gates()
        assert len(report.gates) == 1
        assert report.gates[0].gate == "DEPENDENCY_BLOCKED"
        assert report.gates[0].req_id == "REQ-003"

    def test_red_state_has_no_gates(self, mock_state_red):
        """GN-05: RED state → no pending gates (implementation in progress)"""
        report = check_gates(mock_state_red)
        assert not report.has_pending_gates()

    def test_multiple_features_in_gate_states(self, mock_state_multiple_gates):
        """GN-06: Multiple features in gate states → all detected"""
        report = check_gates(mock_state_multiple_gates)
        # Current state is RED so only non-active features in gate states are added
        # REQ-001 (REQUIREMENTS_LOCKED) and REQ-002 (REVIEW_PENDING) should be detected
        assert len(report.gates) >= 2
        gates_by_gate = {g.gate for g in report.gates}
        assert "HITL 1" in gates_by_gate
        assert "HITL 2" in gates_by_gate

    def test_gate_states_mapping_complete(self):
        """GN-07: GATE_STATES contains all expected states"""
        expected_states = [
            "REQUIREMENTS_LOCKED",
            "REVIEW_PENDING",
            "PIVOT_IN_PROGRESS",
            "DEPENDENCY_BLOCKED",
        ]
        for state in expected_states:
            assert state in GATE_STATES
            assert "gate" in GATE_STATES[state]
            assert "action" in GATE_STATES[state]

    def test_gate_report_summary(self, mock_state_requirements_locked):
        """GN-08: GateReport summary counts are correct"""
        report = check_gates(mock_state_requirements_locked)
        summary = report.get_summary()
        assert summary["total_pending"] == 1
        assert summary["hitl_1_pending"] == 1
        assert summary["hitl_2_pending"] == 0
        assert summary["hitl_1_5_pending"] == 0


class TestGateNotificationFormat:
    """Tests for gate notification output formatting."""

    def test_format_gates_table_empty(self):
        """GN-09: Empty gates table formatted correctly"""
        from gate_notification import format_gates_table
        table = format_gates_table([])
        assert "| REQ-ID |" in table
        assert "_(empty)_" in table

    def test_format_gates_table_with_data(self):
        """GN-10: Gates table formatted with data"""
        from gate_notification import format_gates_table, GateInfo

        gates = [
            GateInfo(
                req_id="REQ-001",
                gate="HITL 1",
                feature_slug="example-feature",
                state="REQUIREMENTS_LOCKED",
                action_required="Product Owner must approve",
            )
        ]
        table = format_gates_table(gates)
        assert "REQ-001" in table
        assert "HITL 1" in table
        assert "example-feature" in table
        assert "Product Owner must approve" in table
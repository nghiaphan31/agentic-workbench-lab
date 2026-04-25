"""
test_gatekeeper.py — Tests for Pipeline Enrollment Validator

Phase 1: Gatekeeper Tests

Tests the gatekeeper.py module which validates that any active work is
properly enrolled in the pipeline (has valid active_req_id in state.json,
exists in feature_registry, not in terminal state).
"""

import json
import sys
from pathlib import Path

import pytest

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent.parent.parent / "agentic-workbench-engine" / ".workbench" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from gatekeeper import check_enrollment, EnrollmentResult, TERMINAL_STATES


class TestGatekeeperEnrollment:
    """Tests for gatekeeper.py pipeline enrollment validation."""

    @pytest.fixture
    def mock_state_empty(self):
        """Empty state dict — INIT bootstrap state."""
        return {
            "version": "2.1",
            "state": "INIT",
            "active_req_id": None,
            "feature_registry": {},
        }

    @pytest.fixture
    def mock_state_with_feature(self):
        """State with an active feature properly enrolled."""
        return {
            "version": "2.1",
            "state": "RED",
            "active_req_id": "REQ-001",
            "feature_registry": {
                "REQ-001": {
                    "state": "RED",
                    "depends_on": [],
                    "created_at": "2026-04-25T10:00:00Z",
                }
            },
        }

    @pytest.fixture
    def mock_state_requirements_locked(self):
        """State where feature is REQUIREMENTS_LOCKED (HITL 1 pending)."""
        return {
            "version": "2.1",
            "state": "REQUIREMENTS_LOCKED",
            "active_req_id": "REQ-002",
            "feature_registry": {
                "REQ-002": {
                    "state": "REQUIREMENTS_LOCKED",
                    "depends_on": [],
                    "created_at": "2026-04-25T11:00:00Z",
                }
            },
        }

    @pytest.fixture
    def mock_state_merged(self):
        """State where feature is MERGED (terminal state)."""
        return {
            "version": "2.1",
            "state": "INIT",
            "active_req_id": "REQ-001",
            "feature_registry": {
                "REQ-001": {
                    "state": "MERGED",
                    "depends_on": [],
                    "created_at": "2026-04-20T10:00:00Z",
                }
            },
        }

    @pytest.fixture
    def mock_state_abandoned(self):
        """State where feature is ABANDONED (terminal state)."""
        return {
            "version": "2.1",
            "state": "INIT",
            "active_req_id": "REQ-003",
            "feature_registry": {
                "REQ-003": {
                    "state": "ABANDONED",
                    "depends_on": [],
                    "created_at": "2026-04-21T10:00:00Z",
                }
            },
        }

    @pytest.fixture
    def mock_state_no_req_in_registry(self):
        """State where active_req_id is set but feature not in registry."""
        return {
            "version": "2.1",
            "state": "STAGE_1_ACTIVE",
            "active_req_id": "REQ-999",
            "feature_registry": {
                "REQ-001": {
                    "state": "RED",
                    "depends_on": [],
                    "created_at": "2026-04-25T10:00:00Z",
                }
            },
        }

    @pytest.fixture
    def mock_state_empty_registry(self):
        """State where active_req_id is set but feature_registry is empty."""
        return {
            "version": "2.1",
            "state": "STAGE_1_ACTIVE",
            "active_req_id": "REQ-001",
            "feature_registry": {},
        }

    def test_no_active_req_id_returns_critical(self, mock_state_empty):
        """GK-01: No active_req_id → CRITICAL"""
        result = check_enrollment(mock_state_empty)
        assert result.level == "CRITICAL"
        assert "No active feature" in result.message
        assert "Stage 1" in result.suggestion

    def test_properly_enrolled_feature_returns_ok(self, mock_state_with_feature):
        """GK-02: Properly enrolled feature in active state → OK"""
        result = check_enrollment(mock_state_with_feature)
        assert result.level == "OK"
        assert "REQ-001" in result.message
        assert result.req_id == "REQ-001"

    def test_requirements_locked_returns_ok(self, mock_state_requirements_locked):
        """GK-03: REQUIREMENTS_LOCKED is valid active state → OK"""
        result = check_enrollment(mock_state_requirements_locked)
        assert result.level == "OK"
        assert "REQUIREMENTS_LOCKED" in result.message

    def test_merged_feature_returns_warning(self, mock_state_merged):
        """GK-04: MERGED feature → WARNING (terminal state)"""
        result = check_enrollment(mock_state_merged)
        assert result.level == "WARNING"
        assert "MERGED" in result.message

    def test_abandoned_feature_returns_warning(self, mock_state_abandoned):
        """GK-05: ABANDONED feature → WARNING (terminal state)"""
        result = check_enrollment(mock_state_abandoned)
        assert result.level == "WARNING"
        assert "ABANDONED" in result.message

    def test_req_not_in_registry_returns_critical(self, mock_state_no_req_in_registry):
        """GK-06: active_req_id not in feature_registry → CRITICAL"""
        result = check_enrollment(mock_state_no_req_in_registry)
        assert result.level == "CRITICAL"
        assert "REQ-999" in result.message
        assert "not in state.json.feature_registry" in result.message

    def test_empty_registry_returns_critical(self, mock_state_empty_registry):
        """GK-07: feature_registry is empty → CRITICAL"""
        result = check_enrollment(mock_state_empty_registry)
        assert result.level == "CRITICAL"
        assert "feature_registry is empty" in result.message

    def test_terminal_states_list_defined(self):
        """GK-08: TERMINAL_STATES contains expected values"""
        assert "MERGED" in TERMINAL_STATES
        assert "ABANDONED" in TERMINAL_STATES
        assert "DELETED" in TERMINAL_STATES


class TestGatekeeperArbiterIntegration:
    """Tests for GATEKEEPER check in arbiter_check.py."""

    @pytest.fixture
    def mock_arbiter_check(self, monkeypatch, tmp_path):
        """Set up arbiter_check with mock repo for GATEKEEPER test."""
        # Create directory structure
        hot_context = tmp_path / "memory-bank" / "hot-context"
        hot_context.mkdir(parents=True)
        (hot_context / "activeContext.md").write_text("# Active Context\n", encoding="utf-8")
        (hot_context / "handoff-state.md").write_text("# Handoff State\n", encoding="utf-8")

        # Create state.json
        state = {
            "version": "2.1",
            "state": "INIT",
            "active_req_id": None,
            "feature_registry": {},
            "arbiter_capabilities": {},
        }
        (tmp_path / "state.json").write_text(json.dumps(state), encoding="utf-8")

        # Monkeypatch REPO_ROOT to tmp_path
        import arbiter_check as ac
        monkeypatch.setattr(ac, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(ac, "STATE_JSON", tmp_path / "state.json")
        monkeypatch.setattr(ac, "HOT_CONTEXT", hot_context)

        return tmp_path

    def test_gatekeeper_check_in_session_checks(self):
        """GK-09: GATEKEEPER is included in SESSION_CHECKS"""
        from arbiter_check import SESSION_CHECKS
        assert "GATEKEEPER" in SESSION_CHECKS

    def test_gatekeeper_check_in_registry(self):
        """GK-10: GATEKEEPER is in CHECK_REGISTRY"""
        from arbiter_check import CHECK_REGISTRY
        assert "GATEKEEPER" in CHECK_REGISTRY

    def test_check_pipeline_enrollment_no_req_id(self, mock_arbiter_check):
        """GK-11: check_pipeline_enrollment returns CRITICAL when no active_req_id"""
        from arbiter_check import check_pipeline_enrollment

        result = check_pipeline_enrollment()
        assert result.status == "CRITICAL"
        assert result.rule == "GATEKEEPER"
        assert "No active feature" in result.message

    def test_check_pipeline_enrollment_with_valid_feature(self, mock_arbiter_check):
        """GK-12: check_pipeline_enrollment returns OK for valid enrolled feature"""
        import arbiter_check as ac

        state = {
            "version": "2.1",
            "state": "RED",
            "active_req_id": "REQ-001",
            "feature_registry": {
                "REQ-001": {"state": "RED", "depends_on": []}
            },
        }
        (mock_arbiter_check / "state.json").write_text(json.dumps(state), encoding="utf-8")

        result = ac.check_pipeline_enrollment()
        assert result.status == "OK"
        assert result.rule == "GATEKEEPER"
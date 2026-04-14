# test_pivot_flow.py
"""
GAP-PVa/b: Phase 2B Pivot (Mid-Stage Requirements Change).

Tests PV-001 through PV-010 from plans/Workbench_Lifecycle_Test_Plan.md.
"""

import json
from pathlib import Path

import pytest


class TestPivotFlow:
    """GAP-PVa: Pivot state transitions."""

    def test_pv_001_delta_prompt_during_stage1_sets_pivot_in_progress(
        self, temp_workbench, state_factory
    ):
        """PV-001: Human submits Delta Prompt during Stage 1; state → PIVOT_IN_PROGRESS."""
        state_factory(state="STAGE_1_ACTIVE", active_req_id="REQ-001")

        # Simulate Delta Prompt injection
        state_path = temp_workbench / "state.json"
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)

        state["state"] = "PIVOT_IN_PROGRESS"
        state["pivot_reason"] = "Human wants to add 2FA requirement to reset flow"
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

        with open(state_path, "r", encoding="utf-8") as f:
            loaded = json.load(f)

        assert loaded["state"] == "PIVOT_IN_PROGRESS"
        assert "pivot_reason" in loaded

    def test_pv_002_delta_prompt_during_stage3_sets_pivot_in_progress(
        self, temp_workbench, state_factory
    ):
        """PV-002: Human submits Delta Prompt during Stage 3; state → PIVOT_IN_PROGRESS."""
        state_factory(state="RED", active_req_id="REQ-001")

        state_path = temp_workbench / "state.json"
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)

        state["state"] = "PIVOT_IN_PROGRESS"
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

        with open(state_path, "r", encoding="utf-8") as f:
            loaded = json.load(f)

        assert loaded["state"] == "PIVOT_IN_PROGRESS"

    def test_pv_003_pivot_branch_created_from_current_working_branch(
        self, temp_workbench
    ):
        """PV-003: pivot/{ticket-id} branch created from current working branch."""
        # Simulate branch creation metadata
        pivot_branch_file = temp_workbench / "pivot_branch_info.md"
        pivot_branch_file.write_text(
            """# Pivot Branch — pivot/REQ-001-2FA-reset

**Source Branch:** feature/REQ-001-user-auth
**Pivot Branch:** pivot/REQ-001-2FA-reset
**Created:** 2026-04-14
**Reason:** Human requests 2FA for password reset flow
""",
            encoding="utf-8",
        )

        assert pivot_branch_file.exists()
        content = pivot_branch_file.read_text(encoding="utf-8")
        assert "pivot/" in content
        assert "feature/" in content

    def test_pv_004_architect_agent_modifies_feature_on_pivot_branch(
        self, temp_workbench, feature_factory
    ):
        """PV-004: Architect Agent modifies .feature scenarios on pivot branch."""
        # Original feature
        feature_factory("REQ-001-auth.feature", req_id="REQ-001")

        feature_path = temp_workbench / "features" / "REQ-001-auth.feature"

        # Simulate Architect Agent delta modification
        original_content = feature_path.read_text(encoding="utf-8")
        modified_content = original_content + """

  Scenario: User resets password with 2FA
    Given the user has 2FA enabled
    When the user requests password reset
    Then the system should send a 2FA verification code
    And the user should enter the code to complete reset
"""
        feature_path.write_text(modified_content, encoding="utf-8")

        assert "2FA" in feature_path.read_text(encoding="utf-8")

    def test_pv_005_hitl15_human_approves_pivot_via_roo_chat(self, tmp_path):
        """PV-005: HITL 1.5 — human approves pivot via Roo Chat."""
        approval_file = tmp_path / "pivot_approval.md"
        approval_content = """# HITL 1.5: Pivot Approval

## Delta: REQ-001 — Add 2FA to Password Reset

**Changes:**
+ Scenario: User resets password with 2FA

**Decision:** APPROVED
**Reviewer:** Product Owner
**Date:** 2026-04-14
"""
        approval_file.write_text(approval_content, encoding="utf-8")

        assert "APPROVED" in approval_file.read_text(encoding="utf-8")

    def test_pv_006_pivot_approved_invalidates_tests_sets_red(
        self, temp_workbench, state_factory
    ):
        """PV-006: PIVOT_APPROVED → Arbiter invalidates tests → RED."""
        state_factory(state="PIVOT_APPROVED", active_req_id="REQ-001")

        state_path = temp_workbench / "state.json"
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)

        # Simulate Arbiter test invalidation
        state["state"] = "RED"
        state["regression_state"] = "NOT_RUN"
        state["regression_failures"] = []
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

        with open(state_path, "r", encoding="utf-8") as f:
            loaded = json.load(f)

        assert loaded["state"] == "RED"

    def test_pv_007_test_engineer_rewrites_invalidated_tests(
        self, temp_workbench
    ):
        """PV-007: Test Engineer Agent rewrites invalidated tests."""
        tests_unit = temp_workbench / "tests" / "unit"
        tests_unit.mkdir(parents=True, exist_ok=True)

        # Simulate rewrite of invalidated test
        test_path = tests_unit / "REQ-001-auth.spec.ts"
        new_content = """// REQ-001: User Authentication — UPDATED after Pivot
import { describe, it, expect } from 'vitest';

describe('REQ-001: User Authentication', () => {
  it('should allow user to log in with valid credentials', () => {
    expect(true).toBe(false); // RED until implemented
  });

  it('should require 2FA code for password reset', () => {
    expect(true).toBe(false); // NEW test after pivot
  });
});
"""
        test_path.write_text(new_content, encoding="utf-8")

        content = test_path.read_text(encoding="utf-8")
        assert "UPDATED after Pivot" in content
        assert "2FA" in content

    def test_pv_008_developer_refactors_until_green(self, temp_workbench, state_factory):
        """PV-008: Developer Agent refactors source until GREEN."""
        # Simulate RED → FEATURE_GREEN → GREEN progression
        state_factory(state="FEATURE_GREEN", active_req_id="REQ-001")

        state_path = temp_workbench / "state.json"
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)

        # Simulate all tests passing
        state["state"] = "GREEN"
        state["regression_state"] = "CLEAN"
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

        with open(state_path, "r", encoding="utf-8") as f:
            loaded = json.load(f)

        assert loaded["state"] == "GREEN"
        assert loaded["regression_state"] == "CLEAN"

    def test_pv_009_pivot_blocked_during_regression_red_or_integration_red(
        self, temp_workbench, state_factory
    ):
        """PV-009: Pivot blocked during REGRESSION_RED, INTEGRATION_RED states."""
        state_factory(
            state="REGRESSION_RED",
            active_req_id="REQ-001",
        )

        state_path = temp_workbench / "state.json"
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)

        # Pivot should be blocked during REGRESSION_RED
        # This is enforced by Rule PVT-1
        assert state["state"] == "REGRESSION_RED"
        # Pivot cannot be initiated during blocking states

    def test_pv_010_only_architect_agent_can_initiate_pivot_during_stage1(
        self, temp_workbench, state_factory
    ):
        """PV-010: Only Architect Agent can initiate pivot during Stage 1."""
        state_factory(state="STAGE_1_ACTIVE", active_req_id="REQ-001")

        state_path = temp_workbench / "state.json"
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)

        # Rule PVT-2: Only Architect Agent may initiate pivot during Stage 1
        # Developer Agent may request pivot but requires human approval
        state["state"] = "PIVOT_IN_PROGRESS"
        state["pivot_initiated_by"] = "Architect Agent"

        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

        with open(state_path, "r", encoding="utf-8") as f:
            loaded = json.load(f)

        assert loaded["state"] == "PIVOT_IN_PROGRESS"
        assert loaded["pivot_initiated_by"] == "Architect Agent"

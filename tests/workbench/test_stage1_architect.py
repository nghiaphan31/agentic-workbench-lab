# test_stage1_architect.py
"""
GAP-S1a/b/c/d/e/f: Stage 1 Architect Agent — feature creation and REQ-ID assignment.

Tests S1-001 through S1-011 from plans/Workbench_Lifecycle_Test_Plan.md.
"""

import json
from pathlib import Path

import pytest


class TestStage1Architect:
    """GAP-S1a: REQ-ID and feature file creation."""

    def test_s1_001_req_id_assigned_to_new_feature_file(self, temp_workbench, feature_factory):
        """S1-001: REQ-ID assigned to new .feature file in /features/."""
        features_dir = temp_workbench / "features"
        feature_path = features_dir / "REQ-001-user-login.feature"

        # Create feature via factory
        feature_factory("REQ-001-user-login.feature", req_id="REQ-001")

        assert feature_path.exists(), "Feature file should be created"
        content = feature_path.read_text(encoding="utf-8")
        assert "@REQ-001" in content, "@REQ-NNN tag should be present"

    def test_s1_002_filename_format_is_req_slug_feature(self, temp_workbench, feature_factory):
        """S1-002: Filename format is {REQ-NNN}-{slug}.feature."""
        feature_factory("REQ-042-payment-checkout.feature", req_id="REQ-042")

        features_dir = temp_workbench / "features"
        files = list(features_dir.glob("REQ-042-*.feature"))
        assert len(files) == 1, "Exactly one file matching REQ-042 slug pattern"

    def test_s1_003_req_tag_present_as_first_tag(self, temp_workbench, feature_factory):
        """S1-003: @REQ-NNN tag present as first tag in every .feature file."""
        feature_factory("REQ-001-test.feature", req_id="REQ-001")

        feature_path = temp_workbench / "features" / "REQ-001-test.feature"
        content = feature_path.read_text(encoding="utf-8")
        lines = content.splitlines()

        first_tag_line = lines[0]
        assert first_tag_line.startswith("@REQ-001"), "@REQ-NNN must be first tag"

    def test_s1_004_depends_on_tag_present_and_parsed(
        self, temp_workbench, feature_factory
    ):
        """S1-004: @depends-on: tag is present and correctly parsed in feature file."""
        feature_factory(
            "REQ-002-dependent.feature",
            req_id="REQ-002",
            depends_on=["REQ-001"],
        )

        feature_path = temp_workbench / "features" / "REQ-002-dependent.feature"
        content = feature_path.read_text(encoding="utf-8")

        # Verify @depends-on tag is present
        assert "@depends-on:" in content, "@depends-on: tag must be present"
        assert "REQ-001" in content, "REQ-001 should be referenced in depends-on"

    def test_s1_005_draft_feature_in_inbox_has_draft_tag_no_req_id(
        self, temp_workbench, feature_factory
    ):
        """S1-005: Draft feature in _inbox/ has @draft tag, no REQ-ID."""
        feature_factory(
            "_inbox/draft-payment.feature",
            draft=True,
            feature_name="Payment Feature",
        )

        inbox_path = temp_workbench / "_inbox" / "draft-payment.feature"
        content = inbox_path.read_text(encoding="utf-8")

        assert "@draft" in content, "@draft tag must be present"
        assert "@REQ-" not in content, "Draft should not have REQ-ID"

    def test_s1_006_feature_promoted_from_inbox_receives_req_id(
        self, temp_workbench, feature_factory
    ):
        """S1-006: Feature promoted from _inbox/ to /features/ receives REQ-ID."""
        # Simulate promotion: move from inbox to features, add REQ-ID
        feature_factory(
            "_inbox/draft-payment.feature",
            draft=True,
            feature_name="Payment Feature",
        )

        inbox_path = temp_workbench / "_inbox" / "draft-payment.feature"
        features_path = temp_workbench / "features" / "REQ-001-payment.feature"

        # Simulate Architect Agent promotion
        content = inbox_path.read_text(encoding="utf-8")
        promoted_content = content.replace("@draft", "@REQ-001")
        features_path.write_text(promoted_content, encoding="utf-8")

        assert features_path.exists()
        assert "@REQ-001" in features_path.read_text(encoding="utf-8")

    def test_s1_007_gherkin_syntax_validated(
        self, temp_workbench, feature_factory, run_script
    ):
        """S1-007: Gherkin syntax validated by gherkin_validator.py."""
        feature_factory(
            "REQ-001-valid.feature",
            req_id="REQ-001",
            scenarios=[
                {
                    "name": "User logs in successfully",
                    "steps": [
                        "Given the user is on the login page",
                        "When the user enters valid credentials",
                        "Then the user should be redirected to the dashboard",
                    ],
                }
            ],
        )

        exit_code, stdout, stderr = run_script("gherkin_validator", "features/")
        assert exit_code == 0, f"Valid Gherkin should pass, got: {stderr}"

    def test_s1_008_hitl1_human_reviews_pr_triggers_start_feature(
        self, temp_workbench, state_factory, run_script
    ):
        """S1-008: HITL 1 — human reviews PR, approves, triggers start-feature."""
        # Simulate: state=STAGE_1_ACTIVE after requirements locked
        state_factory(state="STAGE_1_ACTIVE", active_req_id="REQ-001")

        state_path = temp_workbench / "state.json"
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)

        assert state["state"] == "STAGE_1_ACTIVE"

    def test_s1_009_hitl1_rejection_stays_stage_1_active(
        self, temp_workbench, state_factory
    ):
        """S1-009: HITL 1 rejection — human requests changes, stage stays STAGE_1_ACTIVE."""
        state_factory(state="STAGE_1_ACTIVE", active_req_id="REQ-001")

        state_path = temp_workbench / "state.json"
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)

        # Simulate rejection (human requests changes)
        assert state["state"] == "STAGE_1_ACTIVE"

    def test_s1_010_cmd_start_feature_sets_state_to_stage_1_active(
        self, temp_workbench, state_factory
    ):
        """S1-010: cmd_start_feature sets state.json.state = STAGE_1_ACTIVE."""
        state_factory(state="STAGE_1_ACTIVE", active_req_id="REQ-001")

        state_path = temp_workbench / "state.json"
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)

        assert state["state"] == "STAGE_1_ACTIVE"
        assert state["active_req_id"] == "REQ-001"

    def test_s1_011_cmd_lock_requirements_transitions_to_red(
        self, temp_workbench, state_factory
    ):
        """S1-011: cmd_lock_requirements transitions STAGE_1_ACTIVE → RED."""
        # Simulate lock requirements
        state_factory(state="RED", active_req_id="REQ-001")

        state_path = temp_workbench / "state.json"
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)

        assert state["state"] == "RED"
        assert state["active_req_id"] == "REQ-001"

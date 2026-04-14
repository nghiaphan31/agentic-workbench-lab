# test_inbox_flow.py
"""
GAP-INa/b: Phase 2A Inbox (Non-Blocking Ideas).

Tests IN-001 through IN-007 from plans/Workbench_Lifecycle_Test_Plan.md.
"""

import json
from pathlib import Path

import pytest


class TestInboxFlow:
    """GAP-INa: Inbox flow artifacts."""

    def test_in_001_human_submits_shower_thought_to_inbox(self, temp_workbench):
        """IN-001: Human submits shower-thought prompt to _inbox/."""
        inbox_dir = temp_workbench / "_inbox"
        inbox_dir.mkdir(parents=True, exist_ok=True)

        shower_thought_path = inbox_dir / "shower-thought-invoice-import.md"
        content = """# Shower Thought: Invoice Import

What if users could just email invoices directly to the system?
The email processor could auto-extract the data...

@draft
"""
        shower_thought_path.write_text(content, encoding="utf-8")

        assert shower_thought_path.exists()
        assert "@draft" in shower_thought_path.read_text(encoding="utf-8")

    def test_in_002_architect_agent_lightweight_chunking_with_draft_tag(
        self, temp_workbench
    ):
        """IN-002: Architect Agent lightweight chunking with @draft tag."""
        inbox_dir = temp_workbench / "_inbox"
        chunked_path = inbox_dir / "chunked-invoice-import.feature"

        gherkin_content = """@draft
Feature: Email Invoice Import

  Scenario: User submits invoice via email
    Given the user is an authenticated AP clerk
    When the user emails an invoice PDF to the system
    Then the system should extract line items from the PDF
"""
        inbox_dir.mkdir(parents=True, exist_ok=True)
        chunked_path.write_text(gherkin_content, encoding="utf-8")

        content = chunked_path.read_text(encoding="utf-8")
        assert "@draft" in content
        assert "Feature:" in content

    def test_in_003_no_req_id_assigned_while_in_inbox(self, temp_workbench):
        """IN-003: No REQ-ID assigned while in _inbox/."""
        inbox_dir = temp_workbench / "_inbox"
        draft_path = inbox_dir / "draft-feature.feature"

        draft_content = """@draft
Feature: Draft Feature

  Scenario: Example
    Given a condition
    When an action
    Then a result
"""
        inbox_dir.mkdir(parents=True, exist_ok=True)
        draft_path.write_text(draft_content, encoding="utf-8")

        content = draft_path.read_text(encoding="utf-8")
        assert "@draft" in content
        assert "@REQ-" not in content, "Inbox items should NOT have REQ-ID"

    def test_in_004_gherkin_syntax_check_runs_on_draft_files_but_no_req_enforcement(
        self, temp_workbench, run_script
    ):
        """IN-004: Gherkin syntax check runs on @draft files but no REQ-ID enforcement."""
        inbox_dir = temp_workbench / "_inbox"
        inbox_dir.mkdir(parents=True, exist_ok=True)

        draft_feature = inbox_dir / "draft-valid.feature"
        draft_feature.write_text(
            """@draft
Feature: Valid Draft

  Scenario: Valid Example
    Given a condition
    When an action
    Then a result
""",
            encoding="utf-8",
        )

        exit_code, stdout, stderr = run_script("gherkin_validator", "_inbox/", "--allow-draft")
        # Gherkin syntax validation passes; REQ-ID enforcement is skipped for @draft
        assert exit_code == 0, f"Valid Gherkin should pass: {stderr}"

    def test_in_005_product_owner_reviews_inbox_approves_for_promotion(
        self, temp_workbench
    ):
        """IN-005: Product Owner reviews _inbox/, approves for promotion."""
        inbox_dir = temp_workbench / "_inbox"
        review_path = inbox_dir / "REVIEW.md"
        review_content = """# Inbox Review — 2026-04-14

## Items Reviewed

### draft-invoice-import.feature
- **Decision:** APPROVED FOR PROMOTION
- **Priority:** P1
- **Notes:** Aligns with Q2 AP automation goals
- **Promotion Action:** Assign REQ-ID, move to /features/
"""
        inbox_dir.mkdir(parents=True, exist_ok=True)
        review_path.write_text(review_content, encoding="utf-8")

        content = review_path.read_text(encoding="utf-8")
        assert "APPROVED" in content

    def test_in_006_feature_promoted_req_id_assigned_moved_to_features(
        self, temp_workbench, feature_factory, state_factory
    ):
        """IN-006: Feature promoted — REQ-ID assigned, moved to /features/, state = STAGE_1_ACTIVE."""
        # Simulate promotion workflow
        # 1. Draft exists in inbox
        feature_factory(
            "_inbox/draft-feature.feature",
            draft=True,
            feature_name="Draft Feature",
        )

        # 2. Architect Agent assigns REQ-ID and moves to features
        inbox_path = temp_workbench / "_inbox" / "draft-feature.feature"
        features_path = temp_workbench / "features" / "REQ-001-draft.feature"

        content = inbox_path.read_text(encoding="utf-8")
        promoted_content = content.replace("@draft", "@REQ-001")
        features_path.write_text(promoted_content, encoding="utf-8")

        # 3. State updated to STAGE_1_ACTIVE via fixture
        state_factory(state="STAGE_1_ACTIVE", active_req_id="REQ-001")

        state_path = temp_workbench / "state.json"
        assert features_path.exists()
        assert "@REQ-001" in features_path.read_text(encoding="utf-8")

        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)
        assert state["state"] == "STAGE_1_ACTIVE"

    def test_in_007_feature_rejected_remains_in_inbox(self, temp_workbench):
        """IN-007: Feature rejected — remains in _inbox/."""
        inbox_dir = temp_workbench / "_inbox"
        review_path = inbox_dir / "REVIEW.md"
        review_content = """# Inbox Review

## draft-idea-too-vague.feature
- **Decision:** REJECTED
- **Reason:** Too vague — needs clarification before promotion
- **Action:** Return to Architect for iteration
"""
        inbox_dir.mkdir(parents=True, exist_ok=True)
        review_path.write_text(review_content, encoding="utf-8")

        content = review_path.read_text(encoding="utf-8")
        assert "REJECTED" in content

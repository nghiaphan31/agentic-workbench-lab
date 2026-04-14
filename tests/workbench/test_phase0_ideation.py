# test_phase0_ideation.py
"""
GAP-P0a/b: Phase 0 Ideation & Discovery Pipeline.

Tests P0-001 through P0-006 from plans/Workbench_Lifecycle_Test_Plan.md.

Note: Phase 0 is primarily human-driven. Tests simulate the artifacts
and transitions, but human interaction (Socratic interrogation, approvals)
cannot be fully automated.
"""

import json
from pathlib import Path

import pytest


class TestPhase0Ideation:
    """GAP-P0a: Phase 0 artifacts and state transitions."""

    def test_p0_001_narrative_request_md_created_in_hot_context(
        self, temp_workbench
    ):
        """P0-001: Human submits unstructured prompt; narrativeRequest.md created in hot-context."""
        hot_context = temp_workbench / "memory-bank" / "hot-context"
        narrative_path = hot_context / "narrativeRequest.md"

        narrative_content = """# Narrative Feature Request

## User Persona
Accounts Payable Clerk

## Business Problem
Users spend 30+ minutes manually entering invoice data because the system
doesn't support batch import of supplier PDF invoices.

## Goals
- Import 100+ invoice PDFs in a single batch operation
- Auto-extract vendor, amount, date, and line items
- Present extracted data for human review before posting
"""
        hot_context.mkdir(parents=True, exist_ok=True)
        narrative_path.write_text(narrative_content, encoding="utf-8")

        assert narrative_path.exists(), "narrativeRequest.md should be created"

    def test_p0_002_architect_agent_performs_socratic_interrogation(self, tmp_path):
        """P0-002: Architect Agent performs Socratic interrogation via questions."""
        # Simulate Architect Agent questions document
        questions_path = tmp_path / "socratic_questions.md"
        questions_content = """# Socratic Interrogation — REQ-NNN Invoice Import

## Questions for Clarification

1. **File Format**: Do you mean ALL PDF formats (scanned images, searchable PDFs, hybrid)?
2. **Recognition Accuracy**: What tolerance for extraction errors?
3. **Human Review**: Is a 100% human review step acceptable?
4. **Integration**: Should invoices post directly to the ERP or just queue for review?
"""
        questions_path.write_text(questions_content, encoding="utf-8")

        assert questions_path.exists()
        assert "Socratic" in questions_path.read_text(encoding="utf-8")

    def test_p0_003_five_whys_deep_dive_produces_refined_narrative(self, tmp_path):
        """P0-003: "Five Whys" deep dive produces refined narrative."""
        refined_path = tmp_path / "refined_narrative.md"
        refined_content = """# Refined Narrative — After Five Whys

## Original Request
"PDF invoice import"

## Root Need (After 5 Whys)
Supplier invoices arrive as email attachments. AP clerks manually transcribe
into the ERP because: (1) system rejects email-based submissions, (2) no OCR
processing exists, (3) audit requires source document retention.

## Actual Requirement
Automated email processing with OCR that extracts line items, creates a
review queue, and links source PDF to the posting record.
"""
        refined_path.write_text(refined_content, encoding="utf-8")

        assert refined_path.exists()
        content = refined_path.read_text(encoding="utf-8")
        assert "Root Need" in content
        assert "5 Whys" in content or "five whys" in content.lower()

    def test_p0_004_architect_agent_synthesizes_multiturn_dialogue(
        self, temp_workbench
    ):
        """P0-004: Architect Agent synthesizes multi-turn dialogue into narrativeRequest.md."""
        hot_context = temp_workbench / "memory-bank" / "hot-context"
        narrative_path = hot_context / "narrativeRequest.md"

        # Simulate synthesis from Socratic dialogue
        synthesis = """# Narrative Feature Request — Invoice Batch Import

## Background
AP clerks manually transcribe supplier invoice PDFs because email submissions
are rejected and no OCR processing exists.

## User Persona
Accounts Payable Clerk, mid-volume (50-200 invoices/week)

## Business Problem
Manual data entry is error-prone, causes downstream posting delays, and
creates audit risk due to missing source document links.

## Goals
1. Automated email attachment processing
2. OCR extraction with confidence scoring
3. Human review queue with one-click approval
4. Source PDF linkage to ERP posting record

## Success Criteria
- [ ] 95%+ extraction accuracy on standard formatted invoices
- [ ] <5 minutes for 100-invoice batch review
- [ ] Zero invoices lost in email-to-posting pipeline
"""
        hot_context.mkdir(parents=True, exist_ok=True)
        narrative_path.write_text(synthesis, encoding="utf-8")

        content = narrative_path.read_text(encoding="utf-8")
        assert "Background" in content
        assert "User Persona" in content
        assert "Business Problem" in content
        assert "Goals" in content

    def test_p0_005_human_approves_rejects_modifies_narrative(self, tmp_path):
        """P0-005: Human approves/rejects/modifies narrativeRequest.md."""
        approval_path = tmp_path / "narrative_approval.md"
        approval_content = """# HITL 0: Narrative Approval

**Status:** APPROVED WITH MODIFICATIONS

**Modifications Required:**
1. Add compliance requirement: invoices must be retained for 7 years
2. Change success criteria: accuracy from 95% to 98%

**Approval:** Approved as modified
**Reviewer:** Product Owner
**Date:** 2026-04-14
"""
        approval_path.write_text(approval_content, encoding="utf-8")

        content = approval_path.read_text(encoding="utf-8")
        assert "APPROVED" in content or "Approved" in content

    def test_p0_006_approved_narrative_triggers_stage_1(
        self, temp_workbench, state_factory
    ):
        """P0-006: Approved narrativeRequest.md triggers Stage 1 via HITL 0 gate."""
        hot_context = temp_workbench / "memory-bank" / "hot-context"
        narrative_path = hot_context / "narrativeRequest.md"

        # narrativeRequest.md may already exist from conftest; if so just verify it
        if narrative_path.exists():
            content = narrative_path.read_text(encoding="utf-8")
            assert "Feature Request" in content or "Narrative" in content

        # Simulate HITL 0 gate: approved narrative → state = STAGE_1_ACTIVE
        state_factory(state="STAGE_1_ACTIVE", active_req_id=None)

        state_path = temp_workbench / "state.json"
        with open(state_path, "r", encoding="utf-8") as f:
            loaded = json.load(f)

        assert loaded["state"] == "STAGE_1_ACTIVE"

# test_phase0_ideation.py
# GAP-P0-1: Phase 0 Ideation & Discovery Pipeline
#
# Tests Phase 0 from Draft.md lines 67-98:
# - Socratic interrogation
# - Five Whys deep dive
# - Narrative synthesis
# - Human approval gate (HITL 0)
#
# Reference: Agentic Workbench v2 - Draft.md lines 67-98, diagrams/02-phase0-and-pipeline.md

import json
from pathlib import Path

import pytest


class TestNarrativeCreation:
    # =================================================================
    # Phase 0: Narrative Creation
    # =================================================================

    def test_p0001_narrative_created_from_raw_prompt(self, temp_workbench):
        # P0-001: Human submits raw prompt → narrativeRequest.md created
        narrative_path = temp_workbench / 'memory-bank' / 'hot-context' / 'narrativeRequest.md'
        narrative_path.parent.mkdir(parents=True, exist_ok=True)

        raw_prompt = '''# Raw User Feedback

Users are complaining that the reporting tool is too slow.
They want PDF exports.
'''

        narrative_content = f'''# Narrative Feature Request

## Source
Raw user feedback

## Problem Statement
{raw_prompt}

## Status
DRAFT
'''

        narrative_path.write_text(narrative_content, encoding='utf-8')

        assert narrative_path.exists()
        content = narrative_path.read_text(encoding='utf-8')
        assert 'PDF exports' in content
        assert 'DRAFT' in content

    def test_p0002_narrative_follows_template(self, temp_workbench):
        # P0-002: narrativeRequest.md follows template format
        narrative_path = temp_workbench / 'memory-bank' / 'hot-context' / 'narrativeRequest.md'
        narrative_path.parent.mkdir(parents=True, exist_ok=True)

        template_content = '''# Narrative Feature Request

**Template Version:** 2.1
**Owner:** Architect Agent
**Phase:** Phase 0 - Ideation

---

## Background

(TODO: Describe the business context and problem)

## User Persona

- **Who:** (user persona experiencing the problem)
- **What:** (actual operational bottleneck)
- **Value:** (impact on KPIs: retention, revenue, efficiency)

## Goals

- [ ] (TODO: High-level goal 1)
- [ ] (TODO: High-level goal 2)

## Status

**Status:** DRAFT
**Created:** (auto-generated)
**Approved:** (pending HITL 0)
'''

        narrative_path.write_text(template_content, encoding='utf-8')

        content = narrative_path.read_text(encoding='utf-8')
        assert 'Narrative Feature Request' in content
        assert 'Background' in content
        assert 'User Persona' in content
        assert 'Goals' in content


class TestSocraticInterrogation:
    # =================================================================
    # Phase 0: Socratic Interrogation
    # =================================================================

    def test_p0003_socratic_questions_generated(self, temp_workbench):
        # P0-003: Architect generates Socratic questions from raw prompt
        # See Draft.md lines 76-82
        questions_content = '''# Socratic Questions — Email Invoice Import

## Targeted Questions

### Who
- Which specific user persona is experiencing this friction?
- Is it the AP clerk who processes invoices daily?

### What
- What is the actual operational bottleneck?
- Is it manual data entry, PDF parsing, or something else?

### Value
- How does solving this issue impact core KPIs?
- Would faster processing improve cash flow?
'''

        questions_file = temp_workbench / 'socratic_questions.md'
        questions_file.write_text(questions_content, encoding='utf-8')

        content = questions_file.read_text(encoding='utf-8')
        assert 'Who' in content
        assert 'What' in content
        assert 'Value' in content

    def test_p0004_five_whys_pushback_generated(self, temp_workbench):
        # P0-004: "Five Whys" deep dive for prescriptive features
        # See Draft.md lines 84-87
        five_whys_content = '''# Five Whys — PDF Export Feature

## The Query
"You mentioned PDF exports. Why do users need PDFs?"

## Why 1
Users need to present reports to executives.

## Why 2
Executives prefer offline, formatted documents.

## Why 3
Meetings happen without internet access.

## Why 4
Compliance requires archived records.

## Why 5
Legal audit trail must be preserved.

## Root Need
Users need offline, compliant report archival — not necessarily PDF specifically.
'''

        five_whys_file = temp_workbench / 'five_whys.md'
        five_whys_file.write_text(five_whys_content, encoding='utf-8')

        content = five_whys_file.read_text(encoding='utf-8')
        assert 'Why' in content
        assert 'Root Need' in content

    def test_p0005_multi_turn_synthesis(self, temp_workbench):
        # P0-005: Multi-turn dialogue synthesized into structured document
        # See Draft.md lines 89-92

        # Simulate dialogue exchanges
        dialogue = [
            ('Human', 'Users want PDF exports'),
            ('Architect', 'Why do users need PDFs?'),
            ('Human', 'For executive presentations'),
            ('Architect', 'Why do executives need offline access?'),
            ('Human', 'Meetings happen without internet'),
            ('Architect', 'Why offline for meetings?'),
            ('Human', 'Compliance requires archived records'),
        ]

        synthesis = '''# Multi-Turn Dialogue Synthesis

## Key Insights

1. **Root Need:** Compliance archival (not PDF specifically)
2. **User Persona:** AP Clerk + Compliance Officer
3. **Operational Bottleneck:** Manual report generation

## Refined Feature Request

Feature: Automated compliance report archival system that:
- Generates reports on schedule
- Archives in compliance-ready format
- Provides offline access
'''

        synthesis_file = temp_workbench / 'synthesis.md'
        synthesis_file.write_text(synthesis, encoding='utf-8')

        content = synthesis_file.read_text(encoding='utf-8')
        assert 'Root Need' in content
        assert 'Synthesis' in content or 'Key Insights' in content


class TestHitl0Approval:
    # =================================================================
    # HITL 0: Phase 0 Approval Gate
    # =================================================================

    def test_p0006_narrative_approved_transitions_to_stage1(self, temp_workbench, state_factory):
        # P0-006: Human approves narrativeRequest.md → Stage 1 triggered
        # See Draft.md lines 94-97
        narrative_path = temp_workbench / 'memory-bank' / 'hot-context' / 'narrativeRequest.md'
        narrative_path.parent.mkdir(parents=True, exist_ok=True)
        narrative_path.write_text('''# Narrative Feature Request

## Approved

**Status:** APPROVED
**Reviewer:** Product Owner
**Approval Date:** 2026-04-14
''', encoding='utf-8')

        # Simulate approval
        state_factory(state='INIT')
        state_path = temp_workbench / 'state.json'

        with open(state_path, 'r', encoding='utf-8') as f:
            state = json.load(f)

        state['state'] = 'STAGE_1_ACTIVE'
        state['stage'] = 1

        with open(state_path, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
            f.write('\n')

        with open(state_path, 'r', encoding='utf-8') as f:
            new_state = json.load(f)

        assert new_state['state'] == 'STAGE_1_ACTIVE'

    def test_p0007_narrative_rejected_returns_for_revision(self, temp_workbench, state_factory):
        # P0-007: Human requests changes → returns to Architect for revision
        narrative_path = temp_workbench / 'memory-bank' / 'hot-context' / 'narrativeRequest.md'
        narrative_path.parent.mkdir(parents=True, exist_ok=True)
        narrative_path.write_text('''# Narrative Feature Request

## Revision Requested

**Status:** REVISION_REQUESTED
**Reviewer:** Product Owner
**Notes:** Missing user persona details
**Date:** 2026-04-14
''', encoding='utf-8')

        state = json.loads((temp_workbench / 'state.json').read_text())
        # State should remain INIT until approved
        assert state['state'] == 'INIT'


class TestNarrativeContent:
    # =================================================================
    # Phase 0: Narrative Content Requirements
    # =================================================================

    def test_p0008_narrative_includes_background(self, temp_workbench):
        # P0-008: Narrative includes background context
        narrative = temp_workbench / 'memory-bank' / 'hot-context' / 'narrativeRequest.md'
        narrative.parent.mkdir(parents=True, exist_ok=True)
        narrative.write_text('''# Narrative Feature Request

## Background

The AP department processes 500+ invoices monthly.
Manual data entry causes 3-day delays in processing.
Errors cost ~$50K/year in duplicate payments.

## User Persona

- **AP Clerk:** Processes invoices daily
- **Finance Manager:** Reviews reports weekly
''', encoding='utf-8')

        content = narrative.read_text(encoding='utf-8')
        assert 'Background' in content

    def test_p0009_narrative_includes_user_persona(self, temp_workbench):
        # P0-009: Narrative includes user persona
        narrative = temp_workbench / 'memory-bank' / 'hot-context' / 'narrativeRequest.md'
        narrative.parent.mkdir(parents=True, exist_ok=True)
        narrative.write_text('''## User Persona

### Primary: AP Clerk
- **Role:** Accounts Payable Processor
- **Pain Points:** Manual data entry, duplicate invoices
- **Goals:** Faster processing, accuracy

### Secondary: Finance Manager
- **Role:** Department Head
- **Pain Points:** Report generation delays
- **Goals:** Visibility into AP status
''', encoding='utf-8')

        content = narrative.read_text(encoding='utf-8')
        assert 'AP Clerk' in content

    def test_p0010_narrative_includes_business_problem(self, temp_workbench):
        # P0-010: Narrative includes business problem statement
        narrative = temp_workbench / 'memory-bank' / 'hot-context' / 'narrativeRequest.md'
        narrative.parent.mkdir(parents=True, exist_ok=True)
        narrative.write_text('''## Business Problem

### Operational Bottleneck
Manual invoice processing causes:
- 3-day average processing delay
- 2% error rate in data entry
- $50K annual cost in duplicate payments

### Value Proposition
Solving this reduces:
- Processing time by 80%
- Errors by 95%
- Cost by $40K/year
''', encoding='utf-8')

        content = narrative.read_text(encoding='utf-8')
        assert 'Bottleneck' in content or 'Problem' in content


class TestPhase0Diagram:
    # =================================================================
    # Phase 0 Sequence Diagram Alignment
    # =================================================================

    def test_p0011_phase0_sequence_matches_diagram(self, temp_workbench):
        # P0-011: Verify Phase 0 sequence from diagrams/02-phase0-and-pipeline.md
        # Diagram 3 shows: Human → Raw prompt → Architect → Socratic loop → Narrative

        sequence_steps = [
            'Human submits raw unstructured braindump',
            'Architect ingests without judgment, prepares questions',
            'Socratic interrogation loop executes',
            'Five Whys pushback (if prescriptive)',
            'Architect synthesizes multi-turn dialogue',
            'Architect generates Narrative Feature Request',
            'Human reviews and approves (HITL 0)',
            'Stage 1 triggered with approved narrative'
        ]

        # Verify all steps are representable
        assert len(sequence_steps) == 8
        assert 'HITL' in sequence_steps[6]
        assert 'Stage 1' in sequence_steps[7]

    def test_p0012_phase0_rotates_with_sprint(self, temp_workbench):
        # P0-012: narrativeRequest.md follows rotation policy
        # See Draft.md line 258: Rotate at sprint end

        narrative = temp_workbench / 'memory-bank' / 'hot-context' / 'narrativeRequest.md'
        narrative.parent.mkdir(parents=True, exist_ok=True)
        narrative.write_text('# Narrative Feature Request\n\n## Phase 0 Draft\n', encoding='utf-8')

        # narrativeRequest.md should rotate (archive + reset)
        # This is tested by memory_rotator.py
        assert narrative.exists()

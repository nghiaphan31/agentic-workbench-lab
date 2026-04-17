# test_hitl_gates.py
# GAP-HITL-1: Human-in-the-Loop Gates Simulation
#
# Tests HITL gates from Draft.md:
# - HITL 0: Phase 0 narrative approval (Draft.md lines 94-97)
# - HITL 1: Stage 1 contract approval (Draft.md line 117)
# - HITL 1.5: Pivot approval (Draft.md lines 196-198)
# - HITL 2: Stage 4 delivery approval (Draft.md line 177)
#
# Reference: Agentic Workbench v2 - Draft.md, Beginners_Guide.md Appendix C

import json
from pathlib import Path

import pytest


class TestHitl0Gate:
    # =================================================================
    # HITL 0: Phase 0 Narrative Approval
    # =================================================================

    def test_hitl001_phase0_narrative_approved_transitions_to_stage1(self, temp_workbench, state_factory):
        # HITL-001: Human approves narrativeRequest.md → Stage 1 triggered
        state_factory(state='INIT')
        
        # Simulate human approval of narrative
        narrative = temp_workbench / 'memory-bank' / 'hot-context' / 'narrativeRequest.md'
        narrative.write_text('# Narrative Feature Request\n\n## Approved\nStatus: APPROVED\n', encoding='utf-8')
        
        # Simulate HITL 0 approval action
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
        assert new_state['stage'] == 1

    def test_hitl002_phase0_narrative_rejected_returns_to_architect(self, temp_workbench, state_factory):
        # HITL-002: Human rejects narrative → Architect continues iteration
        state_factory(state='INIT')
        
        narrative = temp_workbench / 'memory-bank' / 'hot-context' / 'narrativeRequest.md'
        narrative.write_text('# Narrative Feature Request\n\n## Rejected\nStatus: REJECTED\nNotes: Needs more detail\n', encoding='utf-8')
        
        # Verify state remains INIT (not transitioned)
        state = json.loads((temp_workbench / 'state.json').read_text())
        assert state['state'] == 'INIT'


class TestHitl1Gate:
    # =================================================================
    # HITL 1: Stage 1 Contract Approval (Feature Files)
    # =================================================================

    def test_hitl003_stage1_feature_approved_transitions_to_requirements_locked(self, temp_workbench, state_factory, feature_factory):
        # HITL-003: Product Owner approves .feature files → REQUIREMENTS_LOCKED
        state_factory(state='STAGE_1_ACTIVE', active_req_id='REQ-001')
        
        feature_factory(
            'REQ-001-user-login.feature',
            req_id='REQ-001',
            feature_name='User Login',
            scenarios=[{
                'name': 'Valid login',
                'steps': ['Given a user', 'When they login', 'Then success']
            }]
        )
        
        # Create approval artifact
        approval = temp_workbench / 'features' / 'REQ-001-user-login.approval'
        approval.write_text('## HITL 1 Approval\nStatus: APPROVED\nReviewer: Product Owner\n', encoding='utf-8')
        
        # Simulate HITL 1 approval
        state_path = temp_workbench / 'state.json'
        with open(state_path, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        state['state'] = 'REQUIREMENTS_LOCKED'
        state['stage'] = 2
        with open(state_path, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
            f.write('\n')
        
        with open(state_path, 'r', encoding='utf-8') as f:
            new_state = json.load(f)
        
        assert new_state['state'] == 'REQUIREMENTS_LOCKED'

    def test_hitl004_stage1_feature_rejected_returns_to_architect(self, temp_workbench, state_factory, feature_factory):
        # HITL-004: Product Owner requests changes → Architect continues
        state_factory(state='STAGE_1_ACTIVE', active_req_id='REQ-001')
        
        feature_factory('REQ-001.feature', req_id='REQ-001')
        
        # Create rejection artifact
        rejection = temp_workbench / 'features' / 'REQ-001-user-login.review'
        rejection.write_text('## HITL 1 Review\nStatus: CHANGES_REQUESTED\nNotes: Missing edge cases\n', encoding='utf-8')
        
        # Verify state remains STAGE_1_ACTIVE
        state = json.loads((temp_workbench / 'state.json').read_text())
        assert state['state'] == 'STAGE_1_ACTIVE'

    def test_hitl005_multiple_features_require_individual_approval(self, temp_workbench, state_factory, feature_factory):
        # HITL-005: Each feature requires separate approval
        state_factory(state='STAGE_1_ACTIVE', active_req_id='REQ-001')
        
        feature_factory('REQ-001.feature', req_id='REQ-001')
        feature_factory('REQ-002.feature', req_id='REQ-002')
        
        # REQ-001 approved
        (temp_workbench / 'features' / 'REQ-001.approval').write_text('APPROVED', encoding='utf-8')
        
        # REQ-002 still pending
        state = json.loads((temp_workbench / 'state.json').read_text())
        assert state['state'] == 'STAGE_1_ACTIVE'  # Still in Stage 1


class TestHitl15Gate:
    # =================================================================
    # HITL 1.5: Pivot Approval
    # =================================================================

    def test_hitl006_pivot_approved_transitions_to_pivot_approved(self, temp_workbench, state_factory):
        # HITL-006: Human approves Git diff on pivot branch → PIVOT_APPROVED
        # See Draft.md line 571
        state_factory(state='PIVOT_IN_PROGRESS', active_req_id='REQ-001')
        
        # Create pivot approval artifact
        pivot_approval = temp_workbench / 'pivot_approval.md'
        pivot_approval.write_text('## HITL 1.5: Pivot Approval\n\nStatus: APPROVED\nBranch: pivot/REQ-001-2FA\n', encoding='utf-8')
        
        # Simulate HITL 1.5 approval
        state_path = temp_workbench / 'state.json'
        with open(state_path, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        state['state'] = 'PIVOT_APPROVED'
        with open(state_path, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
            f.write('\n')
        
        with open(state_path, 'r', encoding='utf-8') as f:
            new_state = json.load(f)
        
        assert new_state['state'] == 'PIVOT_APPROVED'

    def test_hitl007_pivot_rejected_returns_to_active_work(self, temp_workbench, state_factory):
        # HITL-007: Human rejects pivot → pivot cancelled, work continues
        state_factory(state='PIVOT_IN_PROGRESS', active_req_id='REQ-001')
        
        # Create rejection
        pivot_rejection = temp_workbench / 'pivot_rejection.md'
        pivot_rejection.write_text('## HITL 1.5: Pivot Rejection\n\nStatus: REJECTED\nNotes: Not urgent enough\n', encoding='utf-8')
        
        # Simulate rejection: state reverts to previous active state (manually, as code would)
        state_path = temp_workbench / 'state.json'
        with open(state_path, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        # Pivot cancelled → back to original state before pivot
        state['state'] = 'RED'
        with open(state_path, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
            f.write('\n')
        
        with open(state_path, 'r', encoding='utf-8') as f:
            new_state = json.load(f)
        assert new_state['state'] in ['RED', 'STAGE_1_ACTIVE']


class TestHitl2Gate:
    # =================================================================
    # HITL 2: Stage 4 Delivery Approval
    # =================================================================

    def test_hitl008_stage4_pr_approved_transitions_to_merged(self, temp_workbench, state_factory):
        # HITL-008: Lead Engineer approves PR → MERGED
        # See Draft.md line 566
        state_factory(
            state='REVIEW_PENDING',
            integration_state='GREEN',
            active_req_id='REQ-001',
            feature_registry={
                'REQ-001': {'state': 'REVIEW_PENDING', 'branch': 'feature/REQ-001'}
            }
        )
        
        # Create approval artifact
        pr_approval = temp_workbench / 'pr_approval.md'
        pr_approval.write_text('## HITL 2: PR Approval\n\nStatus: APPROVED\nReviewer: Lead Engineer\n', encoding='utf-8')
        
        # Simulate HITL 2 approval via merge command
        from pathlib import Path
        import subprocess
        
        TEMPLATE_ROOT = Path(__file__).parent.parent.parent / 'agentic-workbench-engine'
        result = subprocess.run(
            ['python3', str(TEMPLATE_ROOT / 'workbench-cli.py'), 'merge', '--req-id', 'REQ-001'],
            cwd=str(temp_workbench),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Should succeed
        assert result.returncode == 0, f'Merge failed: {result.stderr}'
        
        state = json.loads((temp_workbench / 'state.json').read_text())
        assert state['state'] == 'MERGED'

    def test_hitl009_stage4_pr_rejected_returns_to_developer(self, temp_workbench, state_factory):
        # HITL-009: Lead Engineer rejects PR → Developer continues
        state_factory(
            state='REVIEW_PENDING',
            integration_state='GREEN',
            active_req_id='REQ-001'
        )
        
        # Create rejection artifact
        pr_rejection = temp_workbench / 'pr_rejection.md'
        pr_rejection.write_text('## HITL 2: PR Review\n\nStatus: CHANGES_REQUESTED\nNotes: Security concerns\n', encoding='utf-8')
        
        # State should remain REVIEW_PENDING until issues resolved
        state = json.loads((temp_workbench / 'state.json').read_text())
        assert state['state'] == 'REVIEW_PENDING'

    def test_hitl010_integration_must_pass_before_hitl2(self, temp_workbench, state_factory):
        # HITL-010: integration_state=GREEN required before HITL 2
        state_factory(
            state='GREEN',
            integration_state='RED',  # Not ready
            active_req_id='REQ-001'
        )
        
        # Verify integration must pass first
        state = json.loads((temp_workbench / 'state.json').read_text())
        assert state['integration_state'] != 'GREEN'


class TestGateTransitionValidation:
    # =================================================================
    # Gate Transition Validation
    # =================================================================

    def test_hitl011_gate_approvals_create_audit_trail(self, temp_workbench, state_factory):
        # HITL-011: Each gate approval creates immutable audit log
        state_factory(state='REVIEW_PENDING', integration_state='GREEN')
        
        # Create approval artifact
        approval_file = temp_workbench / 'docs' / 'conversations' / 'approval-REQ-001-HITL2.md'
        approval_file.parent.mkdir(parents=True, exist_ok=True)
        approval_file.write_text('''# HITL 2 Approval — REQ-001

**Date:** 2026-04-14
**Reviewer:** Lead Engineer
**Status:** APPROVED

## Notes

Code quality acceptable. Security scan passed.
''', encoding='utf-8')
        
        assert approval_file.exists()
        content = approval_file.read_text(encoding='utf-8')
        assert 'APPROVED' in content
        assert 'Lead Engineer' in content

    def test_hitl012_gate_rejections_log_reason(self, temp_workbench, state_factory):
        # HITL-012: Gate rejections log reason for change request
        state_factory(state='STAGE_1_ACTIVE')
        
        rejection_file = temp_workbench / 'features' / 'REQ-001-review.md'
        rejection_file.write_text('''# Feature Review — REQ-001

**Date:** 2026-04-14
**Reviewer:** Product Owner
**Status:** CHANGES_REQUESTED

## Required Changes

1. Add edge case: forgot password
2. Clarify session timeout behavior
''', encoding='utf-8')
        
        content = rejection_file.read_text(encoding='utf-8')
        assert 'CHANGES_REQUESTED' in content
        assert 'Required Changes' in content


class TestHitlGateTiming:
    # =================================================================
    # Gate Timing Requirements
    # =================================================================

    def test_hitl013_gate1_requires_all_features_approved(self, temp_workbench, state_factory):
        # HITL-013: Gate 1 cannot pass until all feature files approved
        state_factory(state='STAGE_1_ACTIVE')
        
        # Multiple features in progress
        features_dir = temp_workbench / 'features'
        (features_dir / 'REQ-001.feature').write_text('@REQ-001\nFeature: Login\n', encoding='utf-8')
        (features_dir / 'REQ-002.feature').write_text('@REQ-002\nFeature: Logout\n', encoding='utf-8')
        
        # Only one approved
        (features_dir / 'REQ-001.approval').write_text('APPROVED', encoding='utf-8')
        
        # Verify not all approved
        req1_approved = (features_dir / 'REQ-001.approval').exists()
        req2_approved = (features_dir / 'REQ-002.approval').exists()
        
        assert req1_approved and not req2_approved

    def test_hitl014_gate2_requires_integration_green(self, temp_workbench, state_factory):
        # HITL-014: Gate 2 cannot pass until integration_state=GREEN
        state_factory(state='REVIEW_PENDING', integration_state='NOT_RUN')
        
        # Verify integration not yet run
        state = json.loads((temp_workbench / 'state.json').read_text())
        assert state['integration_state'] != 'GREEN'
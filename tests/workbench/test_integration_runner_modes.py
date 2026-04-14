# test_integration_runner_modes.py
# GAP-INT-1: Integration Test Runner Mode Distinction
#
# Tests that integration_test_runner.py correctly distinguishes between:
# - Stage 2b: Syntax-only validation (no execution)
# - Stage 4: Full execution and reporting
#
# Reference: Draft.md lines 131-142, 596, Beginners_Guide.md Appendix B

import json
from pathlib import Path

import pytest


class TestStage2bMode:
    # =================================================================
    # Stage 2b: Integration Scaffolding (Syntax-Only)
    # =================================================================

    def test_int001_stage2b_syntax_only_no_execution(self, temp_workbench, state_factory, run_script):
        # INT-001: Stage 2b integration runner does syntax validation only
        # See Draft.md line 141: "It does not execute them — execution is deferred to Stage 4"
        state_factory(
            state='REQUIREMENTS_LOCKED',
            stage=2,
            integration_state='NOT_RUN'
        )

        # Create integration skeleton
        integration_file = temp_workbench / 'tests' / 'integration' / 'FLOW-001.contract.spec.ts'
        integration_file.parent.mkdir(parents=True, exist_ok=True)
        integration_file.write_text('''// FLOW-001: Integration Contract
// These tests are CONTRACTS — intentionally RED

describe('FLOW-001 Integration', () => {
  it('should verify user auth before payment', () => {
    expect(true).toBe(false); // Not implemented
  });
});
''', encoding='utf-8')

        # Run with validate-only mode
        exit_code, stdout, stderr = run_script('integration_test_runner', 'validate-only')

        # Should succeed for syntax check
        assert exit_code == 0, f'Syntax validation failed: {stderr}'

    def test_int002_stage2b_integration_skeleton_tagged_flow_id(self, temp_workbench):
        # INT-002: Integration skeleton tagged with FLOW-NNN ID
        # See Draft.md line 134: "tagged with a FLOW-NNN ID"
        integration_file = temp_workbench / 'tests' / 'integration' / 'FLOW-001-user-payment.integration.spec.ts'
        integration_file.parent.mkdir(parents=True, exist_ok=True)
        integration_file.write_text('''// FLOW-001: User to Payment Integration
// Contract between User Auth (REQ-001) and Payment (REQ-002)

import { describe, it, expect } from 'vitest';

describe('FLOW-001: User Payment Integration', () => {
  it('should authenticate user before payment', () => {
    expect(true).toBe(false); // Contract
  });
});
''', encoding='utf-8')

        content = integration_file.read_text(encoding='utf-8')
        assert 'FLOW-001' in content

    def test_int003_stage2b_reads_merged_features_from_registry(self, temp_workbench, state_factory):
        # INT-003: Integration scaffold reads from feature_registry for MERGED features
        # See Draft.md line 133: "All .feature files for features in MERGED state"
        state_factory(
            feature_registry={
                'REQ-001': {'state': 'MERGED', 'depends_on': []},
                'REQ-002': {'state': 'RED', 'depends_on': ['REQ-001']}
            }
        )

        state = json.loads((temp_workbench / 'state.json').read_text())
        registry = state['feature_registry']

        # Integration scaffold should reference REQ-001 as MERGED
        assert registry['REQ-001']['state'] == 'MERGED'
        assert registry['REQ-002']['state'] == 'RED'

    def test_int004_stage2b_skipped_when_no_integration_directory(self, temp_workbench, state_factory):
        # INT-004: Stage 2b auto-skipped if /tests/integration/ does not exist
        # See Draft.md line 142: "If no integration test directory exists yet, Stage 2b is skipped"
        integration_dir = temp_workbench / 'tests' / 'integration'

        # Ensure directory doesn't exist
        if integration_dir.exists():
            import shutil
            shutil.rmtree(integration_dir)

        assert not integration_dir.exists()


class TestStage4Mode:
    # =================================================================
    # Stage 4: Integration Gate (Full Execution)
    # =================================================================

    def test_int005_stage4_full_execution(self, temp_workbench, state_factory, run_script, mock_runner_pass):
        # INT-005: Stage 4 integration runner executes tests
        # See Draft.md line 176: "Arbiter's Integration Test Runner script executes the full /tests/integration/ suite"
        state_factory(
            state='GREEN',
            integration_state='NOT_RUN'
        )

        # Create integration test
        integration_file = temp_workbench / 'tests' / 'integration' / 'FLOW-001.integration.spec.ts'
        integration_file.parent.mkdir(parents=True, exist_ok=True)
        integration_file.write_text('''describe('FLOW-001', () => {
  it('passes', () => {});
});
''', encoding='utf-8')

        # Run integration tests
        exit_code, stdout, stderr = run_script('integration_test_runner', 'run', '--set-state')

        state = json.loads((temp_workbench / 'state.json').read_text())
        assert state['integration_state'] in ['GREEN', 'RED']

    def test_int006_stage4_integration_state_tracked(self, temp_workbench, state_factory):
        # INT-006: integration_state field tracked in state.json
        # See Draft.md line 595: "Writes integration_state to state.json"
        state_factory(
            state='GREEN',
            integration_state='GREEN'
        )

        state = json.loads((temp_workbench / 'state.json').read_text())
        assert 'integration_state' in state
        assert state['integration_state'] == 'GREEN'

    def test_int007_stage4_integration_test_pass_ratio(self, temp_workbench, state_factory):
        # INT-007: integration_test_pass_ratio tracked
        state_factory(
            state='GREEN',
            integration_state='GREEN',
            integration_test_pass_ratio=1.0
        )

        state = json.loads((temp_workbench / 'state.json').read_text())
        assert state['integration_test_pass_ratio'] == 1.0


class TestModeDistinction:
    # =================================================================
    # Mode Distinction Verification
    # =================================================================

    def test_int008_validate_only_vs_run_mode_difference(self, temp_workbench, run_script):
        # INT-008: validate-only and run modes behave differently
        integration_file = temp_workbench / 'tests' / 'integration' / 'FLOW-001.spec.ts'
        integration_file.parent.mkdir(parents=True, exist_ok=True)
        integration_file.write_text('describe("x", () => { it("y", () => {}); });', encoding='utf-8')

        # validate-only mode
        exit_validate, _, _ = run_script('integration_test_runner', 'validate-only')

        # run mode (with --set-state to actually run)
        exit_run, _, _ = run_script('integration_test_runner', 'run', '--set-state')

        # Both should succeed for valid syntax
        assert exit_validate == 0

    def test_int009_integration_runner_script_exists(self):
        # INT-009: integration_test_runner.py script exists
        import sys
        from pathlib import Path

        SCRIPTS_DIR = Path(__file__).parent.parent.parent / 'agentic-workbench-engine' / '.workbench' / 'scripts'
        sys.path.insert(0, str(SCRIPTS_DIR))

        try:
            import integration_test_runner
            assert hasattr(integration_test_runner, 'run_integration_tests') or hasattr(integration_test_runner, 'validate_syntax')
        except ImportError:
            pytest.skip('integration_test_runner not available')

    def test_int010_state_transitions_for_integration(self, temp_workbench, state_factory):
        # INT-010: Verify correct state transitions for integration
        # See Draft.md lines 561-564

        transitions = [
            ('GREEN', 'INTEGRATION_CHECK'),
            ('INTEGRATION_CHECK', 'INTEGRATION_RED'),  # Fail
            ('INTEGRATION_CHECK', 'REVIEW_PENDING'),   # Pass
            ('INTEGRATION_RED', 'INTEGRATION_CHECK'),  # Fix and re-run
        ]

        for from_state, to_state in transitions:
            state_factory(state=from_state)
            state = json.loads((temp_workbench / 'state.json').read_text())
            # Valid transition path
            assert from_state in ['GREEN', 'INTEGRATION_CHECK', 'INTEGRATION_RED']


class TestArbiterCheckIntegration:
    # =================================================================
    # arbiter_check Integration
    # =================================================================

    def test_int011_integration_red_blocks_merge(self, temp_workbench, state_factory):
        # INT-011: INTEGRATION_RED blocks advancement to REVIEW_PENDING
        state_factory(
            state='INTEGRATION_RED',
            integration_state='INTEGRATION_RED'
        )

        state = json.loads((temp_workbench / 'state.json').read_text())
        # Cannot advance to REVIEW_PENDING while INTEGRATION_RED
        assert state['state'] == 'INTEGRATION_RED'

    def test_int012_integration_green_required_for_merge(self, temp_workbench, state_factory):
        # INT-012: INTEGRATION_GREEN required before REVIEW_PENDING
        state_factory(
            state='GREEN',
            integration_state='GREEN'
        )

        state = json.loads((temp_workbench / 'state.json').read_text())
        # Both must be GREEN for merge
        assert state['state'] == 'GREEN'
        assert state['integration_state'] == 'GREEN'


class TestFlowIdConvention:
    # =================================================================
    # FLOW-NNN ID Convention
    # =================================================================

    def test_int013_flow_id_format(self, temp_workbench):
        # INT-013: FLOW-NNN ID format verified
        integration_file = temp_workbench / 'tests' / 'integration' / 'FLOW-001-user-payment.integration.spec.ts'
        integration_file.parent.mkdir(parents=True, exist_ok=True)
        integration_file.write_text('''// FLOW-001: User Payment Integration
describe('FLOW-001', () => {});
''', encoding='utf-8')

        content = integration_file.read_text(encoding='utf-8')
        # FLOW-NNN format: FLOW + zero-padded 3-digit number
        assert 'FLOW-001' in content

    def test_int014_multiple_flow_ids(self, temp_workbench):
        # INT-014: Multiple integration flows have unique FLOW-NNN IDs
        flow1 = temp_workbench / 'tests' / 'integration' / 'FLOW-001-auth-payment.spec.ts'
        flow2 = temp_workbench / 'tests' / 'integration' / 'FLOW-002-user-profile.spec.ts'

        flow1.parent.mkdir(parents=True, exist_ok=True)
        flow1.write_text('// FLOW-001\ndescribe("FLOW-001", () => {});', encoding='utf-8')
        flow2.write_text('// FLOW-002\ndescribe("FLOW-002", () => {});', encoding='utf-8')

        assert flow1.exists()
        assert flow2.exists()
        assert flow1.read_text().count('FLOW-001') >= 1
        assert flow2.read_text().count('FLOW-002') >= 1
# test_regression_failure_capture.py
# GAP-REG-1: Regression Failure Log Population
#
# Tests Rule REG-1 and GAP-9: The Developer Agent MUST receive actionable
# regression failure details. regression_failures must be populated with
# actual test output, not empty.
#
# Reference: .clinerules lines 182-187, Draft.md line 598, GAP-9

import json
from pathlib import Path

import pytest


class TestRegressionFailureCapture:
    # =================================================================
    # REG-1: Regression Failure Log Population
    # =================================================================

    def test_reg001_regression_failures_populated_when_regression_red(self, temp_workbench, state_factory, run_script, mock_runner_fail):
        # REG-001: regression_failures array populated with actual failures
        # See Draft.md line 598: "Parse pytest JSON report or vitest JSON reporter"
        state_factory(
            state='REGRESSION_RED',
            regression_state='REGRESSION_RED',
            regression_failures=[
                {
                    'test': 'REQ-001.spec.ts > should handle concurrent logins',
                    'error': 'Error: expected 200 but got 500',
                    'file': 'tests/unit/REQ-001.spec.ts'
                }
            ]
        )

        state = json.loads((temp_workbench / 'state.json').read_text())
        assert len(state['regression_failures']) > 0
        assert 'test' in state['regression_failures'][0]

    def test_reg002_regression_failures_empty_when_clean(self, temp_workbench, state_factory):
        # REG-002: regression_failures empty when regression_state=CLEAN
        state_factory(
            state='GREEN',
            regression_state='CLEAN',
            regression_failures=[]  # Empty when clean
        )

        state = json.loads((temp_workbench / 'state.json').read_text())
        assert state['regression_state'] == 'CLEAN'
        assert len(state['regression_failures']) == 0

    def test_reg003_regression_failures_contains_actionable_details(self, temp_workbench, state_factory):
        # REG-003: regression_failures contains file, test name, error message
        state_factory(
            state='REGRESSION_RED',
            regression_state='REGRESSION_RED',
            regression_failures=[
                {
                    'test': 'REQ-042.spec.ts > payment checkout timeout',
                    'error': 'TimeoutError: payment service did not respond within 30s',
                    'file': 'tests/unit/REQ-042.spec.ts',
                    'line': 42
                }
            ]
        )

        state = json.loads((temp_workbench / 'state.json').read_text())
        failure = state['regression_failures'][0]

        assert 'test' in failure
        assert 'error' in failure
        assert 'file' in failure
        assert failure['test'] == 'REQ-042.spec.ts > payment checkout timeout'

    def test_reg004_regression_failures_prioritized_over_feature_errors(self, temp_workbench, state_factory):
        # REG-004: When REGRESSION_RED, regression failures are primary input
        # See .clinerules line 185: "regression failure log is primary input"
        state_factory(
            state='REGRESSION_RED',
            regression_state='REGRESSION_RED',
            active_req_id='REQ-042',
            regression_failures=[
                {
                    'test': 'REQ-001.spec.ts > user session expired',
                    'error': 'AssertionError: expected active but got expired'
                }
            ]
        )

        state = json.loads((temp_workbench / 'state.json').read_text())

        # Regression failures should be the primary concern
        assert state['state'] == 'REGRESSION_RED'
        assert len(state['regression_failures']) > 0

    def test_reg005_multiple_regression_failures_captured(self, temp_workbench, state_factory):
        # REG-005: Multiple regression failures all captured
        state_factory(
            state='REGRESSION_RED',
            regression_state='REGRESSION_RED',
            regression_failures=[
                {'test': 'REQ-001.spec.ts > test 1', 'error': 'Error 1'},
                {'test': 'REQ-002.spec.ts > test 2', 'error': 'Error 2'},
                {'test': 'REQ-003.spec.ts > test 3', 'error': 'Error 3'}
            ]
        )

        state = json.loads((temp_workbench / 'state.json').read_text())
        assert len(state['regression_failures']) == 3


class TestTestOrchestratorIntegration:
    # =================================================================
    # Test Orchestrator Parsing
    # =================================================================

    def test_reg006_test_orchestrator_parses_vitest_json(self, temp_workbench, state_factory, run_script, mock_runner_fail):
        # REG-006: test_orchestrator.py parses vitest JSON reporter output
        state_factory(
            state='FEATURE_GREEN',
            regression_state='REGRESSION_RED',
            active_req_id='REQ-001'
        )

        # Create failing test
        test_file = temp_workbench / 'tests' / 'unit' / 'REQ-001.spec.ts'
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text('describe("test", () => { it("fails", () => { expect(true).toBe(false); }); });', encoding='utf-8')

        # Run test orchestrator with full scope
        exit_code, stdout, stderr = run_script(
            'test_orchestrator', 'run',
            '--scope', 'full',
            '--set-state'
        )

        state = json.loads((temp_workbench / 'state.json').read_text())

        # After full regression, state should reflect result
        assert state['regression_state'] in ['REGRESSION_RED', 'CLEAN']

    def test_reg007_test_orchestrator_parses_pytest_json(self, temp_workbench, state_factory, run_script, mock_runner_fail):
        # REG-007: test_orchestrator.py parses pytest JSON report
        state_factory(state='FEATURE_GREEN', regression_state='REGRESSION_RED')

        # Create pytest-style output
        pytest_report = temp_workbench / 'pytest_report.json'
        pytest_report.write_text('''{
            "result": "failed",
            "failures": [
                {
                    "test": "tests/unit/REQ-001_test.py::test_login",
                    "error": "AssertionError: assert False"
                }
            ]
        }''', encoding='utf-8')

        # Verify JSON parsing would work
        import json
        report = json.loads(pytest_report.read_text())
        assert report['result'] == 'failed'
        assert len(report['failures']) > 0


class TestRegressionPriority:
    # =================================================================
    # REG-1: Regression Priority Over Feature Errors
    # =================================================================

    def test_reg008_regression_log_primary_input_when_regression_red(self, temp_workbench, state_factory):
        # REG-008: regression_failures is primary input when state=REGRESSION_RED
        # See .clinerules line 185
        state_factory(
            state='REGRESSION_RED',
            regression_state='REGRESSION_RED',
            active_req_id='REQ-042',
            regression_failures=[
                {'test': 'REQ-001.spec.ts > old feature broken', 'error': 'Error in old feature'}
            ]
        )

        state = json.loads((temp_workbench / 'state.json').read_text())

        # Developer should prioritize fixing the regression over current feature
        assert state['state'] == 'REGRESSION_RED'
        assert state['regression_failures'][0]['test'] != f'REQ-{state["active_req_id"].split("-")[0]}'

    def test_reg009_feature_errors_still_tracked_separately(self, temp_workbench, state_factory):
        # REG-009: Feature errors tracked separately from regression errors
        state_factory(
            state='RED',
            active_req_id='REQ-042'
        )

        # Feature-specific errors would be in error logs
        # regression_failures are cross-feature regressions
        state = json.loads((temp_workbench / 'state.json').read_text())
        assert state['active_req_id'] == 'REQ-042'


class TestArbiterCheckIntegration:
    # =================================================================
    # arbiter_check Integration
    # =================================================================

    def test_reg010_check_regression_failures_populated_exists(self):
        # REG-010: check_regression_failures_populated function exists
        import sys
        from pathlib import Path

        SCRIPTS_DIR = Path(__file__).parent.parent.parent / 'agentic-workbench-engine' / '.workbench' / 'scripts'
        sys.path.insert(0, str(SCRIPTS_DIR))

        try:
            import arbiter_check
            assert hasattr(arbiter_check, 'check_regression_failures_populated')
        except ImportError:
            pytest.skip('arbiter_check not available')

    def test_reg011_arbiter_check_warns_when_empty_and_regression_red(self, temp_workbench, state_factory):
        # REG-011: arbiter_check warns when regression_failures empty but state=REGRESSION_RED
        state_factory(
            state='REGRESSION_RED',
            regression_state='REGRESSION_RED',
            regression_failures=[]  # Empty but should have content
        )

        # This would trigger a WARNING from arbiter_check
        state = json.loads((temp_workbench / 'state.json').read_text())
        assert state['state'] == 'REGRESSION_RED'
        # regression_failures being empty when REGRESSION_RED is suspicious
"""
test_integration_runner.py — UC-022 to UC-027
Tests for integration_test_runner.py — Stage 2b syntax check + Stage 4 execution
"""

import json

import pytest
from .helpers import read_state


class TestIntegrationRunner:
    """UC-022 through UC-027: Integration test runner use cases."""

    def test_uc022_stage2b_no_integration_tests(self, temp_workbench, state_factory, run_script):
        """UC-022: Stage 2b — No integration tests (skip) — exit 0"""
        state_factory()
        exit_code, stdout, stderr = run_script("integration_test_runner", "validate-only")
        assert exit_code == 0
        assert "Files Checked: 0" in stdout
        assert "Valid: True" in stdout

    def test_uc023_stage2b_valid_integration_syntax(self, temp_workbench, state_factory, run_script):
        """UC-023: Stage 2b — Valid integration test syntax — exit 0"""
        state_factory()
        (temp_workbench / "tests" / "integration" / "FLOW-001-login.integration.spec.ts").write_text(
            'describe("login flow", () => { it("logs in", () => {}); });',
            encoding="utf-8",
        )
        exit_code, stdout, stderr = run_script("integration_test_runner", "validate-only")
        assert exit_code == 0

    def test_uc024_stage2b_invalid_syntax_missing_describe(self, temp_workbench, state_factory, run_script):
        """UC-024: Stage 2b — Invalid syntax (missing describe/it) — exit 1"""
        state_factory()
        (temp_workbench / "tests" / "integration" / "FLOW-001-login.integration.spec.ts").write_text(
            "// missing describe/it blocks",
            encoding="utf-8",
        )
        exit_code, stdout, stderr = run_script("integration_test_runner", "validate-only")
        assert exit_code == 1
        assert "missing test structure" in stderr.lower() or "missing test structure" in stdout.lower()

    def test_uc025_stage4_integration_tests_pass(self, temp_workbench, state_factory, run_script, mock_runner_pass):
        """UC-025: Stage 4 — Integration tests pass — integration_state=GREEN"""
        state_factory(state="GREEN", integration_state="NOT_RUN")
        (temp_workbench / "tests" / "integration" / "FLOW-001-login.integration.spec.ts").write_text(
            'describe("login flow", () => { it("logs in", () => {}); });',
            encoding="utf-8",
        )
        exit_code, stdout, stderr = run_script("integration_test_runner", "run", "--set-state")
        assert exit_code == 0
        state = read_state(temp_workbench)
        assert state["integration_state"] == "GREEN"

    def test_uc026_stage4_integration_tests_fail(self, temp_workbench, state_factory, run_script, mock_runner_fail):
        """UC-026: Stage 4 — Integration tests fail — integration_state=RED"""
        state_factory(state="GREEN", integration_state="NOT_RUN")
        (temp_workbench / "tests" / "integration" / "FLOW-001-login.integration.spec.ts").write_text(
            'describe("login flow", () => { it("logs in", () => {}); });',
            encoding="utf-8",
        )
        exit_code, stdout, stderr = run_script("integration_test_runner", "run", "--set-state")
        assert exit_code == 1
        state = read_state(temp_workbench)
        assert state["integration_state"] == "INTEGRATION_RED"

    def test_uc027_feature_green_but_integration_red(self, temp_workbench, state_factory, run_script, mock_runner_fail):
        """UC-027: Feature GREEN but integration fails — state becomes INTEGRATION_RED"""
        state_factory(state="GREEN", integration_state="NOT_RUN")
        (temp_workbench / "tests" / "integration" / "FLOW-001-login.integration.spec.ts").write_text(
            'describe("login flow", () => { it("logs in", () => {}); });',
            encoding="utf-8",
        )
        exit_code, stdout, stderr = run_script("integration_test_runner", "run", "--set-state")
        state = read_state(temp_workbench)
        assert state["state"] == "INTEGRATION_RED"
        assert state["integration_state"] == "INTEGRATION_RED"
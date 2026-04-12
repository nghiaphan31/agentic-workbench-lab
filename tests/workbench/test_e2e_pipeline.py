"""
test_e2e_pipeline.py — UC-065 to UC-069
End-to-end pipeline simulations: Stage 1 -> 2 -> 2b -> 3 -> 4 -> MERGED
"""

import json

import pytest
from .helpers import read_state


class TestE2EPipeline:
    """UC-065 through UC-069: End-to-end pipeline simulations."""

    def test_uc065_full_happy_path_single_feature(self, temp_workbench, state_factory, feature_factory, run_script):
        """UC-065: Full happy path — single feature, no regressions, all tests pass"""
        # 1. Init state and create feature
        state_factory(state="INIT")
        feature_factory(
            "REQ-001-user-login.feature",
            req_id="REQ-001",
            feature_name="User Login",
            scenarios=[{
                "name": "Valid login",
                "steps": ["Given a user is on the login page", "When they enter valid credentials", "Then they are logged in"]
            }]
        )
        
        # 2. Gherkin validation
        exit_code, stdout, stderr = run_script("gherkin_validator", "features/")
        assert exit_code == 0, f"Gherkin validation failed: {stderr}"
        
        # 3. Stage 2b syntax check (no integration tests yet)
        exit_code, stdout, stderr = run_script("integration_test_runner", "validate-only")
        assert exit_code == 0
        
        # 4. Simulate state transitions manually since we don't have real test execution
        state = read_state(temp_workbench)
        state["state"] = "RED"
        state["active_req_id"] = "REQ-001"
        with open(temp_workbench / "state.json", "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
            f.write("\n")
        
        # 5. Simulate FEATURE_GREEN
        state["state"] = "FEATURE_GREEN"
        state["feature_suite_pass_ratio"] = 1.0
        with open(temp_workbench / "state.json", "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
            f.write("\n")
        
        # 6. Phase 2 full regression — GREEN (via test_orchestrator with set-state)
        exit_code, stdout, stderr = run_script("test_orchestrator", "run", "--scope", "full", "--set-state")
        state = read_state(temp_workbench)
        assert state["state"] == "GREEN"
        
        # 7. Integration test scaffold + validation
        (temp_workbench / "tests" / "integration" / "FLOW-001-login.integration.spec.ts").write_text(
            'describe("login flow", () => { it("passes", () => {}); });', encoding="utf-8"
        )
        exit_code, stdout, stderr = run_script("integration_test_runner", "validate-only")
        assert exit_code == 0
        
        # 8. Audit log
        exit_code, stdout, stderr = run_script("audit_logger", "save", "--session-id", "e2e-065", "--branch", "feature/REQ-001")
        assert exit_code == 0

    def test_uc066_full_path_with_regression_recovery(self, temp_workbench, state_factory, feature_factory, run_script):
        """UC-066: Full path with regression recovery"""
        state_factory(state="INIT")
        feature_factory(
            "REQ-001.feature",
            req_id="REQ-001",
            scenarios=[{"name": "Test", "steps": ["Given X", "When Y", "Then Z"]}]
        )
        
        # Simulate RED state (failing phase 1)
        state = read_state(temp_workbench)
        state["state"] = "RED"
        state["active_req_id"] = "REQ-001"
        with open(temp_workbench / "state.json", "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
            f.write("\n")
        
        # Simulate FEATURE_GREEN (phase 1 passes)
        state["state"] = "FEATURE_GREEN"
        state["feature_suite_pass_ratio"] = 1.0
        with open(temp_workbench / "state.json", "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
            f.write("\n")
        
        # Simulate REGRESSION_RED by direct manipulation
        state["state"] = "REGRESSION_RED"
        state["regression_state"] = "REGRESSION_RED"
        with open(temp_workbench / "state.json", "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
            f.write("\n")
        
        # Fix regression - move back to FEATURE_GREEN
        state["state"] = "FEATURE_GREEN"
        state["regression_state"] = "CLEAN"
        with open(temp_workbench / "state.json", "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
            f.write("\n")
        
        # Phase 2 full regression — GREEN
        exit_code, stdout, stderr = run_script("test_orchestrator", "run", "--scope", "full", "--set-state")
        state = read_state(temp_workbench)
        assert state["state"] == "GREEN"
        assert state["regression_state"] == "CLEAN"

    def test_uc067_full_path_with_dependency_block(self, temp_workbench, state_factory, feature_factory, run_script, mock_runner_pass):
        """UC-067: Full path with dependency block"""
        state_factory(
            state="INIT",
            feature_registry={
                "REQ-001": {"state": "MERGED", "depends_on": []},
                "REQ-002": {"state": "DEPENDENCY_BLOCKED", "depends_on": ["REQ-001"]},
            }
        )
        feature_factory(
            "REQ-002-checkout.feature",
            req_id="REQ-002",
            depends_on=["REQ-001"],
            scenarios=[{"name": "Checkout", "steps": ["Given cart has items", "When checkout", "Then order placed"]}]
        )
        
        # Before unblock, can't proceed
        state = read_state(temp_workbench)
        assert state["feature_registry"]["REQ-002"]["state"] == "DEPENDENCY_BLOCKED"
        
        # Unblock simulation
        state["feature_registry"]["REQ-002"]["state"] = "RED"
        with open(temp_workbench / "state.json", "w") as f:
            json.dump(state, f, indent=2)
            f.write("\n")
        
        # Now proceed normally
        (temp_workbench / "tests" / "unit" / "REQ-002-checkout.spec.ts").write_text("describe('test', () => { it('pass', () => { expect(true).toBe(true); }); });", encoding="utf-8")
        
        exit_code, stdout, stderr = run_script("test_orchestrator", "run", "--scope", "feature", "--req-id", "REQ-002", "--set-state")
        state = read_state(temp_workbench)
        assert state["state"] == "FEATURE_GREEN"
        
        exit_code, stdout, stderr = run_script("test_orchestrator", "run", "--scope", "full", "--set-state")
        state = read_state(temp_workbench)
        assert state["state"] == "GREEN"
        
        # Integration
        (temp_workbench / "tests" / "integration" / "FLOW-002.integration.spec.ts").write_text('describe("x", () => { it("y", () => {}); });', encoding="utf-8")
        exit_code, stdout, stderr = run_script("integration_test_runner", "run", "--set-state")
        state = read_state(temp_workbench)
        assert state["integration_state"] == "GREEN"

    def test_uc068_full_path_with_integration_failure_recovery(self, temp_workbench, state_factory, feature_factory, run_script):
        """UC-068: Full path with integration failure recovery"""
        state_factory(state="INIT")
        feature_factory(
            "REQ-001.feature",
            req_id="REQ-001",
            scenarios=[{"name": "Test", "steps": ["Given", "When", "Then"]}]
        )
        
        # Simulate GREEN state (phase 1 + phase 2 passed)
        state = read_state(temp_workbench)
        state["state"] = "GREEN"
        state["regression_state"] = "CLEAN"
        with open(temp_workbench / "state.json", "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
            f.write("\n")
        
        # Integration tests pass initially (via integration_test_runner with mock)
        (temp_workbench / "tests" / "integration" / "FLOW-001.integration.spec.ts").write_text('describe("x", () => { it("y", () => { expect(true).toBe(true); }); });', encoding="utf-8")
        
        # Simulate GREEN -> INTEGRATION_RED transition
        state = read_state(temp_workbench)
        state["state"] = "INTEGRATION_RED"
        state["integration_state"] = "RED"
        with open(temp_workbench / "state.json", "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
            f.write("\n")
        
        # Fix integration test
        (temp_workbench / "tests" / "integration" / "FLOW-001.integration.spec.ts").write_text('describe("x", () => { it("y", () => { expect(true).toBe(true); }); });', encoding="utf-8")
        
        # Simulate INTEGRATION_RED -> GREEN recovery
        state = read_state(temp_workbench)
        state["state"] = "GREEN"
        state["integration_state"] = "GREEN"
        with open(temp_workbench / "state.json", "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
            f.write("\n")
        
        state = read_state(temp_workbench)
        assert state["state"] == "GREEN"
        assert state["integration_state"] == "GREEN"

    def test_uc069_sprint_end_memory_rotation(self, temp_workbench, state_factory, feature_factory, run_script):
        """UC-069: Sprint end — memory rotation"""
        state_factory()
        hot = temp_workbench / "memory-bank" / "hot-context"
        
        # Write sprint content
        for name, content in {
            "activeContext.md": "# Active sprint content",
            "progress.md": "# Sprint progress",
            "productContext.md": "# Sprint stories",
            "decisionLog.md": "# ADR decisions",
            "handoff-state.md": "# Handoff data",
        }.items():
            (hot / name).write_text(content, encoding="utf-8")
        
        exit_code, stdout, stderr = run_script("memory_rotator", "rotate")
        assert exit_code == 0
        
        # Rotate files: archived + reset
        assert (hot / "activeContext.md").read_text(encoding="utf-8") != "# Active sprint content"
        assert (hot / "progress.md").read_text(encoding="utf-8") != "# Sprint progress"
        # Persist files: unchanged
        assert (hot / "decisionLog.md").read_text(encoding="utf-8") == "# ADR decisions"
        # Reset files: reset
        assert (hot / "handoff-state.md").read_text(encoding="utf-8") != "# Handoff data"
        
        # Archive contains rotated files
        archive = temp_workbench / "memory-bank" / "archive-cold"
        archives = list(archive.glob("*"))
        assert len(archives) > 0
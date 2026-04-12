"""
test_gherkin_validator.py — UC-007 to UC-014
Tests for gherkin_validator.py
"""

import pytest
from .helpers import read_state


class TestGherkinValidator:
    """UC-007 through UC-014: Gherkin validation use cases."""

    def test_uc007_valid_feature_file(self, temp_workbench, state_factory, feature_factory, run_script):
        """UC-007: Valid Feature File — exit 0"""
        state_factory()
        feature_factory(
            "REQ-001-user-login.feature",
            req_id="REQ-001",
            feature_name="User Login",
            scenarios=[
                {
                    "name": "Valid credentials",
                    "steps": ["Given a user is on the login page", "When they enter valid credentials", "Then they are logged in"],
                }
            ],
        )
        exit_code, stdout, stderr = run_script("gherkin_validator", "features/")
        assert exit_code == 0

    def test_uc008_missing_req_id_tag(self, temp_workbench, state_factory, feature_factory, run_script):
        """UC-008: Missing @REQ-NNN tag — exit 1"""
        state_factory()
        feature_factory(
            "login.feature",
            feature_name="User Login",
            scenarios=[
                {
                    "name": "Valid credentials",
                    "steps": ["Given a user is on the login page", "When they enter valid credentials", "Then they are logged in"],
                }
            ],
        )
        exit_code, stdout, stderr = run_script("gherkin_validator", "features/")
        assert exit_code == 1
        assert "Missing @REQ-NNN tag" in stderr or "Missing @REQ-NNN tag" in stdout

    def test_uc009_missing_scenario_block(self, temp_workbench, state_factory, feature_factory, run_script):
        """UC-009: Missing Scenario: block — exit 1"""
        state_factory()
        feature_factory(
            "REQ-001-user-login.feature",
            req_id="REQ-001",
            raw_content="@REQ-001\nFeature: User Login\n\nGiven a user is on the login page\n",
        )
        exit_code, stdout, stderr = run_script("gherkin_validator", "features/")
        assert exit_code == 1
        assert "Missing Scenario" in stderr or "Missing Scenario" in stdout

    def test_uc010_missing_given_when_then_steps(self, temp_workbench, state_factory, feature_factory, run_script):
        """UC-010: Missing Given/When/Then steps — exit 1"""
        state_factory()
        feature_factory(
            "REQ-001-user-login.feature",
            req_id="REQ-001",
            raw_content="@REQ-001\nFeature: User Login\n\nScenario: Valid login\n\n  This scenario has no steps\n",
        )
        exit_code, stdout, stderr = run_script("gherkin_validator", "features/")
        assert exit_code == 1

    def test_uc011_draft_file_no_req_id_required(self, temp_workbench, state_factory, feature_factory, run_script):
        """UC-011: Draft file in _inbox/ with @draft — exit 0"""
        state_factory()
        feature_factory(
            "_inbox/draft-login.feature",
            draft=True,
            feature_name="User Login Draft",
            scenarios=[
                {
                    "name": "Valid credentials",
                    "steps": ["Given a user is on the login page", "When they enter valid credentials", "Then they are logged in"],
                }
            ],
        )
        exit_code, stdout, stderr = run_script("gherkin_validator", "_inbox/", "--allow-draft")
        assert exit_code == 0

    def test_uc012_depends_on_unknown_req_id_warning(self, temp_workbench, state_factory, feature_factory, run_script):
        """UC-012: @depends-on references unknown REQ-ID — exit 0 with warning"""
        state_factory()
        feature_factory(
            "REQ-002-checkout.feature",
            req_id="REQ-002",
            feature_name="Checkout Flow",
            scenarios=[
                {
                    "name": "Checkout",
                    "steps": ["Given a user has items in cart", "When they checkout", "Then order is placed"],
                }
            ],
            depends_on=["REQ-999"],
        )
        exit_code, stdout, stderr = run_script("gherkin_validator", "features/")
        # Should pass but with a warning about unknown dep
        assert exit_code == 0
        assert "REQ-999" in stdout or "REQ-999" in stderr

    def test_uc013_empty_features_directory(self, temp_workbench, state_factory, run_script):
        """UC-013: Empty features/ directory — exit 0, no files found"""
        state_factory()
        exit_code, stdout, stderr = run_script("gherkin_validator", "features/")
        assert exit_code == 0
        assert "No .feature files found" in stdout or "No .feature files found" in stderr

    def test_uc014_nonexistent_directory(self, temp_workbench, state_factory, run_script):
        """UC-014: Non-existent directory — exit 1"""
        state_factory()
        exit_code, stdout, stderr = run_script("gherkin_validator", "/nonexistent/path/")
        assert exit_code == 1
        assert "Directory not found" in stderr or "Directory not found" in stdout
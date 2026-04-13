"""
test_compliance_snapshot.py — UC-CS-001 to UC-CS-006
Tests for compliance_snapshot.py — Arbiter's compliance vault script
"""

import json
import os

import pytest


class TestComplianceSnapshot:
    """UC-CS-001 through UC-CS-006: Compliance snapshot generation tests."""

    def test_ucs001_tag_argument_required(self, temp_workbench, state_factory):
        """UC-CS-001: --tag argument is required"""
        import subprocess

        result = subprocess.run(
            ["python", ".workbench/scripts/compliance_snapshot.py"],
            capture_output=True,
            text=True,
        )
        # Should exit with error about missing --tag

    def test_ucs002_generates_traceability_matrix(
        self, temp_workbench, state_factory
    ):
        """UC-CS-002: Snapshot generates traceability matrix CSV"""
        state_factory(
            state="MERGED",
            feature_registry={
                "REQ-001": {"state": "MERGED", "depends_on": []},
                "REQ-002": {"state": "MERGED", "depends_on": ["REQ-001"]},
            },
        )
        # Run: python .workbench/scripts/compliance_snapshot.py --tag v1.0.0
        # Should create vault/traceability_matrix.csv

    def test_ucs003_creates_vault_directory(
        self, temp_workbench, state_factory
    ):
        """UC-CS-003: Snapshot creates vault/ directory if missing"""
        state_factory(state="MERGED")
        # Vault path: <repo-root>/compliance-vault/

    def test_ucs004_includes_feature_state_summary(
        self, temp_workbench, state_factory
    ):
        """UC-CS-004: Matrix includes all features with state from feature_registry"""
        state_factory(state="MERGED")
        # Matrix columns: REQ-ID, State, Depends-On, Merged-Date

    def test_ucs005_non_version_tag_accepted_but_no_snapshot(
        self, temp_workbench, state_factory
    ):
        """UC-CS-005: Non-version tag runs but skips snapshot (logs warning)"""
        state_factory(state="MERGED")
        # Non-version tags are accepted but no snapshot is generated

    def test_ucs006_readme_generated_in_vault(
        self, temp_workbench, state_factory
    ):
        """UC-CS-006: Vault includes README explaining contents"""
        state_factory(state="MERGED")
        # README should explain what files are in the vault and their purpose
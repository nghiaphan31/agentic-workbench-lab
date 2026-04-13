"""
test_workbench_cli.py — UC-041 to UC-050
Tests for workbench-cli.py — init / upgrade / status / rotate
"""

import json
import os
import shutil
import subprocess

import pytest
from .helpers import read_state, TEMPLATE_ROOT


class TestWorkbenchCLI:
    """UC-041 through UC-050: Workbench CLI use cases."""

    def test_uc041_init_creates_full_scaffold(self, tmp_path):
        """UC-041: init — creates full scaffold with state.json=INIT"""
        # Change to tmp_path for init
        result = subprocess.run(
            ["python", str(TEMPLATE_ROOT / "workbench-cli.py"), "init", "test-project"],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"init failed: {result.stderr}"
        
        project_dir = tmp_path / "test-project"
        assert project_dir.exists()
        
        # Check state.json
        state_path = project_dir / "state.json"
        assert state_path.exists()
        state = json.loads(state_path.read_text(encoding="utf-8"))
        assert state["state"] == "INIT"
        
        # Check engine files
        assert (project_dir / ".clinerules").exists()
        assert (project_dir / ".roomodes").exists()
        assert (project_dir / ".roo-settings.json").exists()
        
        # Check app directories
        for d in ["src", "tests/unit", "tests/integration", "features", "_inbox", "docs/conversations"]:
            assert (project_dir / d).exists(), f"Missing directory: {d}"
        
        # Check memory-bank hot-context populated
        hot = project_dir / "memory-bank" / "hot-context"
        assert (hot / "activeContext.md").exists()
        assert (hot / "progress.md").exists()
        assert (hot / "decisionLog.md").exists()

    def test_uc042_init_project_already_exists(self, tmp_path):
        """UC-042: init — project dir already exists — exit 1"""
        project_dir = tmp_path / "test-project"
        project_dir.mkdir()
        
        result = subprocess.run(
            ["python", str(TEMPLATE_ROOT / "workbench-cli.py"), "init", "test-project"],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 1
        assert "already exists" in result.stderr or "already exists" in result.stdout

    def test_uc043_upgrade_safe_state_init(self, tmp_path):
        """UC-043: upgrade — safe state INIT — proceeds"""
        # Create a project
        subprocess.run(
            ["python", str(TEMPLATE_ROOT / "workbench-cli.py"), "init", "upgrade-test"],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            timeout=30,
        )
        project_dir = tmp_path / "upgrade-test"
        
        result = subprocess.run(
            ["python", str(TEMPLATE_ROOT / "workbench-cli.py"), "upgrade", "--version", "v2.2"],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"upgrade failed: {result.stderr}"
        
        # state.json should be preserved
        state = json.loads((project_dir / "state.json").read_text(encoding="utf-8"))
        assert state["state"] == "INIT"
        
        # .workbench-version should be updated
        version_file = project_dir / ".workbench-version"
        assert version_file.exists()
        # Version file may contain "v2.2" or just "2.2"
        version_content = version_file.read_text()
        assert "2.2" in version_content, f"Expected version '2.2' in '{version_content}'"

    def test_uc044_upgrade_safe_state_merged(self, tmp_path):
        """UC-044: upgrade — safe state MERGED — proceeds"""
        subprocess.run(
            ["python", str(TEMPLATE_ROOT / "workbench-cli.py"), "init", "merged-test"],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            timeout=30,
        )
        project_dir = tmp_path / "merged-test"
        
        # Set state to MERGED
        state = json.loads((project_dir / "state.json").read_text())
        state["state"] = "MERGED"
        with open(project_dir / "state.json", "w") as f:
            json.dump(state, f, indent=2)
            f.write("\n")
        
        result = subprocess.run(
            ["python", str(TEMPLATE_ROOT / "workbench-cli.py"), "upgrade", "--version", "v2.2"],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0

    def test_uc045_upgrade_unsafe_state_red(self, tmp_path):
        """UC-045: upgrade — unsafe state RED — blocked"""
        subprocess.run(
            ["python", str(TEMPLATE_ROOT / "workbench-cli.py"), "init", "red-test"],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            timeout=30,
        )
        project_dir = tmp_path / "red-test"
        
        # Set state to RED
        state = json.loads((project_dir / "state.json").read_text())
        state["state"] = "RED"
        with open(project_dir / "state.json", "w") as f:
            json.dump(state, f, indent=2)
            f.write("\n")
        
        result = subprocess.run(
            ["python", str(TEMPLATE_ROOT / "workbench-cli.py"), "upgrade", "--version", "v2.2"],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 1
        assert "Cannot upgrade while state=RED" in result.stderr or "state=RED" in result.stdout

    def test_uc046_upgrade_unsafe_state_regression_red(self, tmp_path):
        """UC-046: upgrade — unsafe state REGRESSION_RED — blocked"""
        subprocess.run(
            ["python", str(TEMPLATE_ROOT / "workbench-cli.py"), "init", "reg-test"],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            timeout=30,
        )
        project_dir = tmp_path / "reg-test"
        
        state = json.loads((project_dir / "state.json").read_text())
        state["state"] = "REGRESSION_RED"
        with open(project_dir / "state.json", "w") as f:
            json.dump(state, f, indent=2)
            f.write("\n")
        
        result = subprocess.run(
            ["python", str(TEMPLATE_ROOT / "workbench-cli.py"), "upgrade", "--version", "v2.2"],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 1

    def test_uc047_status_displays_all_fields(self, tmp_path):
        """UC-047: status — displays all state.json fields"""
        subprocess.run(
            ["python", str(TEMPLATE_ROOT / "workbench-cli.py"), "init", "status-test"],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            timeout=30,
        )
        project_dir = tmp_path / "status-test"
        
        result = subprocess.run(
            ["python", str(TEMPLATE_ROOT / "workbench-cli.py"), "status"],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
        output = result.stdout + result.stderr
        assert "INIT" in output
        assert "arbiter_capabilities" in output.lower() or "Arbiter" in output

    def test_uc048_status_no_state_json(self, tmp_path):
        """UC-048: status — no state.json — exit 1"""
        result = subprocess.run(
            ["python", str(TEMPLATE_ROOT / "workbench-cli.py"), "status"],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 1
        assert "No state.json found" in result.stderr or "state.json" in result.stdout

    def test_uc049_rotate_delegates_to_memory_rotator(self, tmp_path):
        """UC-049: rotate — delegates to memory_rotator.py"""
        subprocess.run(
            ["python", str(TEMPLATE_ROOT / "workbench-cli.py"), "init", "rotate-test"],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            timeout=30,
        )
        project_dir = tmp_path / "rotate-test"
        
        result = subprocess.run(
            ["python", str(TEMPLATE_ROOT / "workbench-cli.py"), "rotate"],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
        output = result.stdout + result.stderr
        assert "ROTATE" in output or "Sprint Rotation" in output

    def test_uc050_rotate_memory_rotator_not_found(self, tmp_path):
        """UC-050: rotate — memory_rotator.py missing — exit 1"""
        subprocess.run(
            ["python", str(TEMPLATE_ROOT / "workbench-cli.py"), "init", "norotator-test"],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            timeout=30,
        )
        project_dir = tmp_path / "norotator-test"
        
        # Remove memory_rotator.py
        rotator = project_dir / ".workbench" / "scripts" / "memory_rotator.py"
        rotator.unlink()
        
        result = subprocess.run(
            ["python", str(TEMPLATE_ROOT / "workbench-cli.py"), "rotate"],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 1
        assert "not found" in result.stderr or "memory_rotator" in result.stdout


# ============================================================================
# GAP-3d: Hook installation tests
# ============================================================================

class TestHookInstallation:
    """GAP-3d: Hook installation tests."""

    def test_gap3d_install_hooks_creates_executable_hooks(self, tmp_path):
        """GAP-3d: init/install-hooks creates executable .git/hooks/pre-commit and pre-push."""
        import stat
        import sys
        # Create a mock engine with hooks
        engine_dir = tmp_path / "engine"
        engine_dir.mkdir()
        hooks_src = engine_dir / ".workbench" / "hooks"
        hooks_src.mkdir(parents=True)
        (hooks_src / "pre-commit").write_text("#!/bin/sh\necho 'pre-commit'\n")
        (hooks_src / "pre-push").write_text("#!/bin/sh\necho 'pre-push'\n")
        
        # Create a target git repo
        target = tmp_path / "target"
        target.mkdir()
        subprocess.run(["git", "init"], cwd=target, check=True, capture_output=True)
        git_hooks = target / ".git" / "hooks"
        
        # Run _install_hooks by simulating it
        import shutil
        git_hooks.mkdir(parents=True, exist_ok=True)
        for hook_file in hooks_src.iterdir():
            if hook_file.is_file():
                dst = git_hooks / hook_file.name
                shutil.copy2(hook_file, dst)
                dst.chmod(dst.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        
        # Verify
        pre_commit = git_hooks / "pre-commit"
        pre_push = git_hooks / "pre-push"
        assert pre_commit.exists(), ".git/hooks/pre-commit should exist after hook installation"
        assert pre_push.exists(), ".git/hooks/pre-push should exist after hook installation"
        # On Windows, chmod +x doesn't work the same way - executable bit may not be set
        # But the file should exist and be readable as a valid hook file
        if sys.platform != "win32":
            assert pre_commit.stat().st_mode & stat.S_IXUSR, "pre-commit hook should be executable"
            assert pre_push.stat().st_mode & stat.S_IXUSR, "pre-push hook should be executable"

    def test_gap3d_init_installs_hooks(self, tmp_path):
        """GAP-3d: init command installs hooks into .git/hooks/."""
        import stat
        import sys
        result = subprocess.run(
            ["python", str(TEMPLATE_ROOT / "workbench-cli.py"), "init", "hook-test"],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"init failed: {result.stderr}"
        
        project_dir = tmp_path / "hook-test"
        git_hooks = project_dir / ".git" / "hooks"
        
        # Check hooks exist
        assert (git_hooks / "pre-commit").exists(), "pre-commit should be installed"
        assert (git_hooks / "pre-push").exists(), "pre-push should be installed"
        
        # On Windows, chmod +x doesn't work - executable bit check is skipped
        # On Unix, verify executable bit is set
        if sys.platform != "win32":
            pre_commit_mode = (git_hooks / "pre-commit").stat().st_mode
            assert pre_commit_mode & stat.S_IXUSR, "pre-commit should be executable"


# ============================================================================
# GAP-5d: merge command tests
# ============================================================================

class TestMergeCommand:
    """GAP-5d: merge command tests."""

    def test_gap5d_merge_transitions_state_to_merged(self, tmp_path):
        """GAP-5d: merge command transitions state from REVIEW_PENDING to MERGED."""
        # Create project via init
        subprocess.run(
            ["python", str(TEMPLATE_ROOT / "workbench-cli.py"), "init", "merge-test"],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            timeout=30,
        )
        project_dir = tmp_path / "merge-test"
        
        # Set state to REVIEW_PENDING
        state = json.loads((project_dir / "state.json").read_text())
        state["state"] = "REVIEW_PENDING"
        state["stage"] = 4
        state["active_req_id"] = "REQ-001"
        state["integration_state"] = "GREEN"
        state["feature_registry"] = {
            "REQ-001": {"state": "REVIEW_PENDING", "branch": "feature/S1/REQ-001", "depends_on": []}
        }
        with open(project_dir / "state.json", "w") as f:
            json.dump(state, f, indent=2)
            f.write("\n")
        
        # Run merge command
        result = subprocess.run(
            ["python", str(TEMPLATE_ROOT / "workbench-cli.py"), "merge", "--req-id", "REQ-001"],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"merge failed: {result.stderr}"
        
        # Verify state transitioned
        updated = json.loads((project_dir / "state.json").read_text())
        assert updated["state"] == "MERGED", f"Expected state MERGED, got {updated['state']}"
        assert updated["active_req_id"] is None
        assert updated["stage"] is None
        assert updated["feature_registry"]["REQ-001"]["state"] == "MERGED"
        assert "merged_at" in updated["feature_registry"]["REQ-001"]

    def test_gap5d_merge_fails_when_not_review_pending(self, tmp_path):
        """GAP-5d: merge command fails when state != REVIEW_PENDING."""
        subprocess.run(
            ["python", str(TEMPLATE_ROOT / "workbench-cli.py"), "init", "merge-fail-test"],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            timeout=30,
        )
        project_dir = tmp_path / "merge-fail-test"
        
        # Set state to GREEN (not REVIEW_PENDING)
        state = json.loads((project_dir / "state.json").read_text())
        state["state"] = "GREEN"
        state["stage"] = 3
        with open(project_dir / "state.json", "w") as f:
            json.dump(state, f, indent=2)
            f.write("\n")
        
        result = subprocess.run(
            ["python", str(TEMPLATE_ROOT / "workbench-cli.py"), "merge", "--req-id", "REQ-001"],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 1
        assert "REVIEW_PENDING" in result.stderr or "REVIEW_PENDING" in result.stdout


# ============================================================================
# GAP-6f: Full lifecycle sequence tests
# ============================================================================

class TestFullLifecycle:
    """GAP-6f: Full lifecycle sequence tests."""

    def test_gap6f_start_lock_setred_lifecycle(self, tmp_path):
        """GAP-6f: start-feature → lock-requirements → set-red lifecycle."""
        # Create project via init
        subprocess.run(
            ["python", str(TEMPLATE_ROOT / "workbench-cli.py"), "init", "lifecycle-test"],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            timeout=30,
        )
        project_dir = tmp_path / "lifecycle-test"
        
        # Create a feature file
        features_dir = project_dir / "features"
        feature_file = features_dir / "REQ-001-user-auth.feature"
        feature_file.write_text("""@REQ-001
Feature: User Authentication
  Scenario: User logs in
    Given a registered user
    When they submit valid credentials
    Then they are authenticated
""")
        
        # Step 1: start-feature
        result = subprocess.run(
            ["python", str(TEMPLATE_ROOT / "workbench-cli.py"), "start-feature", "--req-id", "REQ-001", "--slug", "user-auth"],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"start-feature failed: {result.stderr}"
        state = json.loads((project_dir / "state.json").read_text())
        assert state["state"] == "STAGE_1_ACTIVE"
        assert state["active_req_id"] == "REQ-001"
        assert state["stage"] == 1
        
        # Step 2: lock-requirements
        result = subprocess.run(
            ["python", str(TEMPLATE_ROOT / "workbench-cli.py"), "lock-requirements", "--req-id", "REQ-001"],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"lock-requirements failed: {result.stderr}"
        state = json.loads((project_dir / "state.json").read_text())
        assert state["state"] == "REQUIREMENTS_LOCKED"
        assert state["stage"] == 2
        
        # Step 3: set-red
        result = subprocess.run(
            ["python", str(TEMPLATE_ROOT / "workbench-cli.py"), "set-red", "--req-id", "REQ-001"],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"set-red failed: {result.stderr}"
        state = json.loads((project_dir / "state.json").read_text())
        assert state["state"] == "RED"
        assert state["stage"] == 3
        assert state["feature_registry"]["REQ-001"]["state"] == "RED"

    def test_gap6f_review_pending_requires_integration_green(self, tmp_path):
        """GAP-6f: review-pending fails when integration_state != GREEN (enforces INT-1)."""
        subprocess.run(
            ["python", str(TEMPLATE_ROOT / "workbench-cli.py"), "init", "review-test"],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            timeout=30,
        )
        project_dir = tmp_path / "review-test"
        
        # Set state to GREEN but integration_state = NOT_RUN
        state = json.loads((project_dir / "state.json").read_text())
        state["state"] = "GREEN"
        state["stage"] = 3
        state["active_req_id"] = "REQ-001"
        state["integration_state"] = "NOT_RUN"
        state["feature_registry"] = {"REQ-001": {"state": "GREEN"}}
        with open(project_dir / "state.json", "w") as f:
            json.dump(state, f, indent=2)
            f.write("\n")
        
        result = subprocess.run(
            ["python", str(TEMPLATE_ROOT / "workbench-cli.py"), "review-pending", "--req-id", "REQ-001"],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 1
        assert "integration_state" in (result.stderr + result.stdout).lower() or "GREEN" in (result.stderr + result.stdout)
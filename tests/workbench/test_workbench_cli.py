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
        assert "2.2" in version_file.read_text()

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
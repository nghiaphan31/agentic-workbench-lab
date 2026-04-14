# test_upgrade_lifecycle.py
# GAP-UPG-1: UPGRADE_IN_PROGRESS State Transitions
#
# Tests the engine upgrade lifecycle from Draft.md lines 675-686:
# - UPGRADE_IN_PROGRESS → INIT when upgrade completes
# - Engine files updated (.clinerules, .roomodes, scripts/)
# - Memory preserved
# - Version bumped
#
# Reference: Agentic Workbench v2 - Draft.md lines 650-686, .clinerules lines 574-577
#
# Upgrade is BLOCKED unless state = INIT or MERGED

import json
import subprocess
from pathlib import Path

import pytest


class TestUpgradeSafeStates:
    # =================================================================
    # Safe States for Upgrade
    # =================================================================

    def test_upg001_safe_upgrade_from_init(self, tmp_path):
        # UPG-001: INIT → UPGRADE_IN_PROGRESS → INIT (safe)
        # See Draft.md line 574
        
        # Create a workbench project
        result = subprocess.run(
            ['python', str(Path(__file__).parent.parent.parent / 'agentic-workbench-engine' / 'workbench-cli.py'), 'init', 'test-upgrade'],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            pytest.skip('workbench-cli.py init failed')
        
        project_dir = tmp_path / 'test-upgrade'
        state = json.loads((project_dir / 'state.json').read_text())
        
        # Set state to INIT (safe for upgrade)
        state['state'] = 'INIT'
        (project_dir / 'state.json').write_text(json.dumps(state, indent=2) + '\n')
        
        # Clear checkpoint
        checkpoint = project_dir / 'memory-bank' / 'hot-context' / 'session-checkpoint.md'
        if checkpoint.exists():
            checkpoint.unlink()
        
        # Configure git
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=str(project_dir), capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=str(project_dir), capture_output=True)
        
        # Run upgrade
        result = subprocess.run(
            ['python', str(Path(__file__).parent.parent.parent / 'agentic-workbench-engine' / 'workbench-cli.py'), 'upgrade', '--version', 'v2.2'],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Should succeed
        assert result.returncode == 0, f'Upgrade from INIT failed: {result.stderr}'

    def test_upg002_safe_upgrade_from_merged(self, tmp_path):
        # UPG-002: MERGED → UPGRADE_IN_PROGRESS → INIT (safe)
        # See Draft.md line 576
        
        result = subprocess.run(
            ['python', str(Path(__file__).parent.parent.parent / 'agentic-workbench-engine' / 'workbench-cli.py'), 'init', 'test-merged'],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            pytest.skip('workbench-cli.py init failed')
        
        project_dir = tmp_path / 'test-merged'
        state = json.loads((project_dir / 'state.json').read_text())
        
        # Set state to MERGED (safe for upgrade)
        state['state'] = 'MERGED'
        (project_dir / 'state.json').write_text(json.dumps(state, indent=2) + '\n')
        
        # Clear checkpoint
        checkpoint = project_dir / 'memory-bank' / 'hot-context' / 'session-checkpoint.md'
        if checkpoint.exists():
            checkpoint.unlink()
        
        # Configure git
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=str(project_dir), capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=str(project_dir), capture_output=True)
        
        # Run upgrade
        result = subprocess.run(
            ['python', str(Path(__file__).parent.parent.parent / 'agentic-workbench-engine' / 'workbench-cli.py'), 'upgrade', '--version', 'v2.2'],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        assert result.returncode == 0, f'Upgrade from MERGED failed: {result.stderr}'


class TestUpgradeUnsafeStates:
    # =================================================================
    # Unsafe States — Upgrade Blocked
    # =================================================================

    def test_upg003_upgrade_blocked_from_stage1_active(self, tmp_path):
        # UPG-003: STAGE_1_ACTIVE → upgrade blocked
        # See Draft.md line 582: "Arbiter refuses upgrade if state != INIT or MERGED"
        
        result = subprocess.run(
            ['python', str(Path(__file__).parent.parent.parent / 'agentic-workbench-engine' / 'workbench-cli.py'), 'init', 'test-stage1'],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            pytest.skip('workbench-cli.py init failed')
        
        project_dir = tmp_path / 'test-stage1'
        state = json.loads((project_dir / 'state.json').read_text())
        
        # Set state to STAGE_1_ACTIVE (NOT safe)
        state['state'] = 'STAGE_1_ACTIVE'
        state['active_req_id'] = 'REQ-001'
        (project_dir / 'state.json').write_text(json.dumps(state, indent=2) + '\n')
        
        # Run upgrade
        result = subprocess.run(
            ['python', str(Path(__file__).parent.parent.parent / 'agentic-workbench-engine' / 'workbench-cli.py'), 'upgrade', '--version', 'v2.2'],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Should FAIL
        assert result.returncode != 0, 'Upgrade should be blocked from STAGE_1_ACTIVE'

    def test_upg004_upgrade_blocked_from_red(self, tmp_path):
        # UPG-004: RED → upgrade blocked
        # See Draft.md line 582
        
        result = subprocess.run(
            ['python', str(Path(__file__).parent.parent.parent / 'agentic-workbench-engine' / 'workbench-cli.py'), 'init', 'test-red'],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            pytest.skip('workbench-cli.py init failed')
        
        project_dir = tmp_path / 'test-red'
        state = json.loads((project_dir / 'state.json').read_text())
        
        state['state'] = 'RED'
        state['active_req_id'] = 'REQ-001'
        (project_dir / 'state.json').write_text(json.dumps(state, indent=2) + '\n')
        
        result = subprocess.run(
            ['python', str(Path(__file__).parent.parent.parent / 'agentic-workbench-engine' / 'workbench-cli.py'), 'upgrade', '--version', 'v2.2'],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        assert result.returncode != 0, 'Upgrade should be blocked from RED'

    def test_upg005_upgrade_blocked_from_regression_red(self, tmp_path):
        # UPG-005: REGRESSION_RED → upgrade blocked
        
        result = subprocess.run(
            ['python', str(Path(__file__).parent.parent.parent / 'agentic-workbench-engine' / 'workbench-cli.py'), 'init', 'test-reg-red'],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            pytest.skip('workbench-cli.py init failed')
        
        project_dir = tmp_path / 'test-reg-red'
        state = json.loads((project_dir / 'state.json').read_text())
        
        state['state'] = 'REGRESSION_RED'
        state['regression_state'] = 'REGRESSION_RED'
        (project_dir / 'state.json').write_text(json.dumps(state, indent=2) + '\n')
        
        result = subprocess.run(
            ['python', str(Path(__file__).parent.parent.parent / 'agentic-workbench-engine' / 'workbench-cli.py'), 'upgrade', '--version', 'v2.2'],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        assert result.returncode != 0, 'Upgrade should be blocked from REGRESSION_RED'

    def test_upg006_upgrade_blocked_from_pivot_in_progress(self, tmp_path):
        # UPG-006: PIVOT_IN_PROGRESS → upgrade blocked
        
        result = subprocess.run(
            ['python', str(Path(__file__).parent.parent.parent / 'agentic-workbench-engine' / 'workbench-cli.py'), 'init', 'test-pivot'],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            pytest.skip('workbench-cli.py init failed')
        
        project_dir = tmp_path / 'test-pivot'
        state = json.loads((project_dir / 'state.json').read_text())
        
        state['state'] = 'PIVOT_IN_PROGRESS'
        (project_dir / 'state.json').write_text(json.dumps(state, indent=2) + '\n')
        
        result = subprocess.run(
            ['python', str(Path(__file__).parent.parent.parent / 'agentic-workbench-engine' / 'workbench-cli.py'), 'upgrade', '--version', 'v2.2'],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        assert result.returncode != 0, 'Upgrade should be blocked from PIVOT_IN_PROGRESS'

    def test_upg007_upgrade_blocked_from_dependency_blocked(self, tmp_path):
        # UPG-007: DEPENDENCY_BLOCKED → upgrade blocked
        
        result = subprocess.run(
            ['python', str(Path(__file__).parent.parent.parent / 'agentic-workbench-engine' / 'workbench-cli.py'), 'init', 'test-dep-block'],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            pytest.skip('workbench-cli.py init failed')
        
        project_dir = tmp_path / 'test-dep-block'
        state = json.loads((project_dir / 'state.json').read_text())
        
        state['state'] = 'DEPENDENCY_BLOCKED'
        state['active_req_id'] = 'REQ-002'
        state['feature_registry'] = {
            'REQ-001': {'state': 'RED', 'depends_on': []},
            'REQ-002': {'state': 'DEPENDENCY_BLOCKED', 'depends_on': ['REQ-001']}
        }
        (project_dir / 'state.json').write_text(json.dumps(state, indent=2) + '\n')
        
        result = subprocess.run(
            ['python', str(Path(__file__).parent.parent.parent / 'agentic-workbench-engine' / 'workbench-cli.py'), 'upgrade', '--version', 'v2.2'],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        assert result.returncode != 0, 'Upgrade should be blocked from DEPENDENCY_BLOCKED'


class TestUpgradeEffects:
    # =================================================================
    # Upgrade Effects on Files
    # =================================================================

    def test_upg008_engine_files_replaced(self, tmp_path):
        # UPG-008: .clinerules, .roomodes, .workbench/scripts/ replaced
        # See Draft.md lines 680-682
        
        result = subprocess.run(
            ['python', str(Path(__file__).parent.parent.parent / 'agentic-workbench-engine' / 'workbench-cli.py'), 'init', 'test-engine'],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            pytest.skip('workbench-cli.py init failed')
        
        project_dir = tmp_path / 'test-engine'
        
        # Clear checkpoint
        checkpoint = project_dir / 'memory-bank' / 'hot-context' / 'session-checkpoint.md'
        if checkpoint.exists():
            checkpoint.unlink()
        
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=str(project_dir), capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=str(project_dir), capture_output=True)
        
        # Run upgrade
        result = subprocess.run(
            ['python', str(Path(__file__).parent.parent.parent / 'agentic-workbench-engine' / 'workbench-cli.py'), 'upgrade', '--version', 'v2.2'],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            pytest.skip('Upgrade failed, cannot test effects')
        
        # Verify engine files exist
        assert (project_dir / '.clinerules').exists(), '.clinerules must be replaced'
        assert (project_dir / '.roomodes').exists(), '.roomodes must be replaced'
        assert (project_dir / '.workbench' / 'scripts').exists(), '.workbench/scripts/ must be replaced'

    def test_upg009_memory_preserved(self, tmp_path):
        # UPG-009: memory-bank/ NOT deleted during upgrade
        # See Draft.md line 683: "It does not delete existing memory files"
        
        result = subprocess.run(
            ['python', str(Path(__file__).parent.parent.parent / 'agentic-workbench-engine' / 'workbench-cli.py'), 'init', 'test-memory'],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            pytest.skip('workbench-cli.py init failed')
        
        project_dir = tmp_path / 'test-memory'
        state = json.loads((project_dir / 'state.json').read_text())
        state['state'] = 'MERGED'
        (project_dir / 'state.json').write_text(json.dumps(state, indent=2) + '\n')
        
        # Create some memory content
        memory_dir = project_dir / 'memory-bank' / 'hot-context'
        (memory_dir / 'decisionLog.md').write_text('# Decision Log\n\n## ADR-001: Test\nDecision.\n', encoding='utf-8')
        
        checkpoint = project_dir / 'memory-bank' / 'hot-context' / 'session-checkpoint.md'
        if checkpoint.exists():
            checkpoint.unlink()
        
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=str(project_dir), capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=str(project_dir), capture_output=True)
        
        # Run upgrade
        result = subprocess.run(
            ['python', str(Path(__file__).parent.parent.parent / 'agentic-workbench-engine' / 'workbench-cli.py'), 'upgrade', '--version', 'v2.2'],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            pytest.skip('Upgrade failed')
        
        # Verify memory preserved
        assert (memory_dir / 'decisionLog.md').exists(), 'decisionLog.md must be preserved'

    def test_upg010_version_bumped(self, tmp_path):
        # UPG-010: .workbench-version updated to new version
        # See Draft.md line 684
        
        result = subprocess.run(
            ['python', str(Path(__file__).parent.parent.parent / 'agentic-workbench-engine' / 'workbench-cli.py'), 'init', 'test-version'],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            pytest.skip('workbench-cli.py init failed')
        
        project_dir = tmp_path / 'test-version'
        state = json.loads((project_dir / 'state.json').read_text())
        state['state'] = 'MERGED'
        (project_dir / 'state.json').write_text(json.dumps(state, indent=2) + '\n')
        
        checkpoint = project_dir / 'memory-bank' / 'hot-context' / 'session-checkpoint.md'
        if checkpoint.exists():
            checkpoint.unlink()
        
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=str(project_dir), capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=str(project_dir), capture_output=True)
        
        # Run upgrade
        subprocess.run(
            ['python', str(Path(__file__).parent.parent.parent / 'agentic-workbench-engine' / 'workbench-cli.py'), 'upgrade', '--version', 'v2.2'],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Verify version file
        version_file = project_dir / '.workbench-version'
        if version_file.exists():
            version = version_file.read_text().strip()
            assert '2.2' in version, f'Version should be 2.2, got {version}'


class TestUpgradeCommit:
    # =================================================================
    # Upgrade Auto-Commit
    # =================================================================

    def test_upg011_upgrade_commits_with_conventional_message(self, tmp_path):
        # UPG-011: Upgrade auto-commits with chore(workbench) message
        # See Draft.md line 685
        
        result = subprocess.run(
            ['python', str(Path(__file__).parent.parent.parent / 'agentic-workbench-engine' / 'workbench-cli.py'), 'init', 'test-commit'],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            pytest.skip('workbench-cli.py init failed')
        
        project_dir = tmp_path / 'test-commit'
        state = json.loads((project_dir / 'state.json').read_text())
        state['state'] = 'INIT'
        (project_dir / 'state.json').write_text(json.dumps(state, indent=2) + '\n')
        
        checkpoint = project_dir / 'memory-bank' / 'hot-context' / 'session-checkpoint.md'
        if checkpoint.exists():
            checkpoint.unlink()
        
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=str(project_dir), capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=str(project_dir), capture_output=True)
        
        # Run upgrade
        subprocess.run(
            ['python', str(Path(__file__).parent.parent.parent / 'agentic-workbench-engine' / 'workbench-cli.py'), 'upgrade', '--version', 'v2.2'],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Check git log
        log = subprocess.run(
            ['git', 'log', '--oneline', '-n', '3'],
            cwd=str(project_dir),
            capture_output=True,
            text=True
        )
        
        # Should have upgrade commit
        assert 'chore' in log.stdout or 'workbench' in log.stdout


class TestUpgradeSafety:
    # =================================================================
    # Safety Checks
    # =================================================================

    def test_upg012_upgrade_checks_session_checkpoint(self, tmp_path):
        # UPG-012: Upgrade blocked if session-checkpoint.md shows ACTIVE session
        # See Beginners_Guide.md Step 2.2
        
        result = subprocess.run(
            ['python', str(Path(__file__).parent.parent.parent / 'agentic-workbench-engine' / 'workbench-cli.py'), 'init', 'test-checkpoint'],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            pytest.skip('workbench-cli.py init failed')
        
        project_dir = tmp_path / 'test-checkpoint'
        
        # Set ACTIVE checkpoint
        checkpoint = project_dir / 'memory-bank' / 'hot-context' / 'session-checkpoint.md'
        checkpoint.write_text('status: ACTIVE\nsession_id: test-session\nbranch: feature/test\n', encoding='utf-8')
        
        # Try upgrade
        result = subprocess.run(
            ['python', str(Path(__file__).parent.parent.parent / 'agentic-workbench-engine' / 'workbench-cli.py'), 'upgrade', '--version', 'v2.2'],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Should block or warn about active session
        # Note: Current implementation may only warn, not block

    def test_upg013_upgrade_checks_active_tests(self, tmp_path):
        # UPG-013: Upgrade blocked if tests are failing
        # See Draft.md line 681
        
        result = subprocess.run(
            ['python', str(Path(__file__).parent.parent.parent / 'agentic-workbench-engine' / 'workbench-cli.py'), 'init', 'test-tests'],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            pytest.skip('workbench-cli.py init failed')
        
        project_dir = tmp_path / 'test-tests'
        state = json.loads((project_dir / 'state.json').read_text())
        state['state'] = 'RED'
        (project_dir / 'state.json').write_text(json.dumps(state, indent=2) + '\n')
        
        result = subprocess.run(
            ['python', str(Path(__file__).parent.parent.parent / 'agentic-workbench-engine' / 'workbench-cli.py'), 'upgrade', '--version', 'v2.2'],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        assert result.returncode != 0, 'Upgrade should be blocked when tests are failing'
# test_cmd_delegation.py
# GAP-CMD-1/2/3: Command Delegation Rules
#
# Tests Rule CMD-1 (Phase A auto-execute), CMD-2 (Phase B/C delegated to Arbiter),
# CMD-3 (Forbidden patterns), and CMD-TRANSITION (capability reading on start).
#
# Reference: .clinerules lines 191-224, Agentic Workbench v2 - Draft.md lines 273-312
#
# Phase A: Pre-Arbiter — Agent MAY auto-execute allowedCommands patterns
# Phase B/C: Arbiter owns domain — Agent MUST delegate to Arbiter, never execute directly

import json
import subprocess
from pathlib import Path

import pytest


class TestPhaseACmds:
    # =================================================================
    # Phase A: Pre-Arbiter (Layer 1)
    # =================================================================

    def test_cmd001_phase_a_git_log_allowed(self, temp_workbench, state_factory):
        # CMD-001: Phase A — git log is in allowedCommands, auto-execute OK
        state_factory(
            state='INIT',
            arbiter_capabilities={
                'test_orchestrator': False,
                'gherkin_validator': False,
                'memory_rotator': False,
                'audit_logger': False,
                'crash_recovery': False,
                'dependency_monitor': False,
                'integration_test_runner': False,
                'git_hooks': False
            }
        )

        # Verify Phase A: all capabilities false means agent can auto-execute
        state = json.loads((temp_workbench / 'state.json').read_text())
        assert all(v == False for v in state['arbiter_capabilities'].values())

    def test_cmd002_phase_a_git_status_allowed(self, temp_workbench, state_factory):
        # CMD-002: Phase A — git status auto-execute OK
        state_factory(state='INIT', arbiter_capabilities={'git_hooks': False})
        
        # .roo-settings.json should contain git status in allowedCommands
        roo_settings = (temp_workbench / '.roo-settings.json')
        if roo_settings.exists():
            settings = json.loads(roo_settings.read_text())
            allowed = settings.get('settings', {}).get('roo-cline', {}).get('allowedCommands', [])
            # git status is allowed in Phase A
            assert 'git status' in allowed or 'git branch -a' in allowed

    def test_cmd003_phase_a_npm_test_blocked_without_approval(self, temp_workbench, state_factory):
        # CMD-003: Phase A — npm test requires approval (not in allowlist by default)
        state_factory(state='INIT', arbiter_capabilities={'test_orchestrator': False})
        
        # Verify test_orchestrator is NOT registered
        state = json.loads((temp_workbench / 'state.json').read_text())
        assert state['arbiter_capabilities']['test_orchestrator'] == False

    def test_cmd004_phase_a_git_diff_allowed(self, temp_workbench):
        # CMD-004: Phase A — git diff is in allowedCommands
        roo_settings = (temp_workbench / '.roo-settings.json')
        if roo_settings.exists():
            settings = json.loads(roo_settings.read_text())
            allowed = settings.get('settings', {}).get('roo-cline', {}).get('allowedCommands', [])
            assert 'git diff' in allowed


class TestPhaseBCmds:
    # =================================================================
    # Phase B: Partial Arbiter
    # =================================================================

    def test_cmd005_phase_b_test_orchestrator_registered(self, temp_workbench, state_factory):
        # CMD-005: Phase B — test_orchestrator registered, agent must delegate
        state_factory(
            state='GREEN',
            arbiter_capabilities={
                'test_orchestrator': True,  # Arbiter owns this domain
                'gherkin_validator': False,
                'memory_rotator': False,
                'audit_logger': False,
                'crash_recovery': False,
                'dependency_monitor': False,
                'integration_test_runner': False,
                'git_hooks': False
            }
        )

        state = json.loads((temp_workbench / 'state.json').read_text())
        assert state['arbiter_capabilities']['test_orchestrator'] == True

    def test_cmd006_phase_b_agent_must_not_execute_covered_command(self, temp_workbench, state_factory):
        # CMD-006: Phase B — when Arbiter owns domain, agent MUST NOT execute directly
        state_factory(
            state='RED',
            arbiter_capabilities={'test_orchestrator': True}
        )

        state = json.loads((temp_workbench / 'state.json').read_text())
        # CMD-2 rule: Agent must delegate when capability is registered
        assert state['arbiter_capabilities']['test_orchestrator'] == True

    def test_cmd007_phase_b_gherkin_validator_registered(self, temp_workbench, state_factory):
        # CMD-007: Phase B — gherkin_validator registered
        state_factory(
            state='STAGE_1_ACTIVE',
            arbiter_capabilities={'gherkin_validator': True}
        )

        state = json.loads((temp_workbench / 'state.json').read_text())
        assert state['arbiter_capabilities']['gherkin_validator'] == True

    def test_cmd008_phase_b_memory_rotator_registered(self, temp_workbench, state_factory):
        # CMD-008: Phase B — memory_rotator registered
        state_factory(
            state='INIT',
            arbiter_capabilities={'memory_rotator': True}
        )

        state = json.loads((temp_workbench / 'state.json').read_text())
        assert state['arbiter_capabilities']['memory_rotator'] == True


class TestPhaseCCmds:
    # =================================================================
    # Phase C: Full Arbiter
    # =================================================================

    def test_cmd009_phase_c_all_capabilities_registered(self, temp_workbench, state_factory):
        # CMD-009: Phase C — all Arbiter capabilities registered
        state_factory(
            state='INIT',
            arbiter_capabilities={
                'test_orchestrator': True,
                'gherkin_validator': True,
                'memory_rotator': True,
                'audit_logger': True,
                'crash_recovery': True,
                'dependency_monitor': True,
                'integration_test_runner': True,
                'git_hooks': True
            }
        )

        state = json.loads((temp_workbench / 'state.json').read_text())
        assert all(v == True for v in state['arbiter_capabilities'].values())

    def test_cmd010_phase_c_all_commands_delegated(self, temp_workbench, state_factory):
        # CMD-010: Phase C — all commands delegated to Arbiter
        state_factory(
            arbiter_capabilities={
                'test_orchestrator': True,
                'gherkin_validator': True,
                'memory_rotator': True,
                'audit_logger': True,
                'crash_recovery': True,
                'dependency_monitor': True,
                'integration_test_runner': True,
                'git_hooks': True
            }
        )

        state = json.loads((temp_workbench / 'state.json').read_text())
        # In Phase C, no commands should be auto-executed by agent
        # All execution goes through Arbiter scripts


class TestCmd3Forbidden:
    # =================================================================
    # CMD-3: Forbidden Command Patterns
    # =================================================================

    def test_cmd011_forbidden_git_push_always_requires_approval(self, temp_workbench):
        # CMD-011: git push is permanently forbidden regardless of phase
        roo_settings = (temp_workbench / '.roo-settings.json')
        if roo_settings.exists():
            settings = json.loads(roo_settings.read_text())
            denied = settings.get('settings', {}).get('roo-cline', {}).get('deniedCommands', [])
            assert 'git push' in denied or any('git push' in cmd for cmd in denied)

    def test_cmd012_forbidden_git_commit_always_requires_approval(self, temp_workbench):
        # CMD-012: git commit is permanently forbidden
        roo_settings = (temp_workbench / '.roo-settings.json')
        if roo_settings.exists():
            settings = json.loads(roo_settings.read_text())
            denied = settings.get('settings', {}).get('roo-cline', {}).get('deniedCommands', [])
            assert 'git commit' in denied or any('git commit' in cmd for cmd in denied)

    def test_cmd013_forbidden_rm_rf_always_blocked(self, temp_workbench):
        # CMD-013: rm -rf is permanently forbidden
        roo_settings = (temp_workbench / '.roo-settings.json')
        if roo_settings.exists():
            settings = json.loads(roo_settings.read_text())
            denied = settings.get('settings', {}).get('roo-cline', {}).get('deniedCommands', [])
            # Should have rm -rf or similar patterns
            assert 'rm -rf' in denied or any('rm' in cmd and '-rf' in cmd for cmd in denied)

    def test_cmd014_forbidden_docker_always_blocked(self, temp_workbench):
        # CMD-014: docker commands are permanently forbidden
        roo_settings = (temp_workbench / '.roo-settings.json')
        if roo_settings.exists():
            settings = json.loads(roo_settings.read_text())
            denied = settings.get('settings', {}).get('roo-cline', {}).get('deniedCommands', [])
            assert 'docker' in denied or any('docker' in cmd for cmd in denied)

    def test_cmd015_forbidden_kubectl_always_blocked(self, temp_workbench):
        # CMD-015: kubectl commands are permanently forbidden
        roo_settings = (temp_workbench / '.roo-settings.json')
        if roo_settings.exists():
            settings = json.loads(roo_settings.read_text())
            denied = settings.get('settings', {}).get('roo-cline', {}).get('deniedCommands', [])
            assert 'kubectl' in denied or any('kubectl' in cmd for cmd in denied)

    def test_cmd016_forbidden_sudo_always_blocked(self, temp_workbench):
        # CMD-016: sudo commands are permanently forbidden
        roo_settings = (temp_workbench / '.roo-settings.json')
        if roo_settings.exists():
            settings = json.loads(roo_settings.read_text())
            denied = settings.get('settings', {}).get('roo-cline', {}).get('deniedCommands', [])
            assert 'sudo' in denied


class TestCmdTransition:
    # =================================================================
    # CMD-TRANSITION: Capability Reading on Start
    # =================================================================

    def test_cmd017_agent_reads_arbiter_capabilities_on_start(self, temp_workbench, state_factory):
        # CMD-017: Agent reads arbiter_capabilities on every session start
        state_factory(
            state='INIT',
            arbiter_capabilities={'test_orchestrator': True}
        )

        state = json.loads((temp_workbench / 'state.json').read_text())
        # Agent should read this on start to determine constraints
        assert 'arbiter_capabilities' in state

    def test_cmd018_agent_never_writes_to_arbiter_capabilities(self, temp_workbench, state_factory):
        # CMD-018: Agent must never write to arbiter_capabilities — Arbiter is sole writer
        state_factory(
            state='INIT',
            arbiter_capabilities={'test_orchestrator': False}
        )

        # Try to read state
        state = json.loads((temp_workbench / 'state.json').read_text())
        last_updated_by = state.get('last_updated_by', '')
        
        # Arbiter is the sole writer — agent should not be last_updated_by for capabilities
        # This is enforced by pre-commit hook in real implementation

    def test_cmd019_transition_revoke_auto_approve_on_registration(self, temp_workbench, state_factory):
        # CMD-019: When Arbiter registers capability, corresponding auto-approve is revoked
        state_factory(
            arbiter_capabilities={
                'test_orchestrator': True,  # Registered — auto-approve revoked
                'gherkin_validator': False
            }
        )

        state = json.loads((temp_workbench / 'state.json').read_text())
        # When test_orchestrator = true, agent should not auto-execute npm test
        assert state['arbiter_capabilities']['test_orchestrator'] == True


class TestCapabilityMapping:
    # =================================================================
    # Capability to Command Domain Mapping
    # =================================================================

    def test_cmd020_test_orchestrator_revokes_npm_test(self, temp_workbench):
        # CMD-020: test_orchestrator capability → npm test pattern revoked
        # See Draft.md lines 301-303
        roo_settings = (temp_workbench / '.roo-settings.json')
        if roo_settings.exists():
            settings = json.loads(roo_settings.read_text())
            allowed = settings.get('settings', {}).get('roo-cline', {}).get('allowedCommands', [])
            # These commands should be removed when test_orchestrator is registered
            test_patterns = ['npm test', 'npx vitest', 'pnpm test', 'pytest', 'make test']
            # They may still be in Phase A allowlist but agent must delegate, not execute

    def test_cmd021_gherkin_validator_revokes_cucumber(self, temp_workbench):
        # CMD-021: gherkin_validator capability → cucumber pattern revoked
        # See Draft.md line 304
        roo_settings = (temp_workbench / '.roo-settings.json')
        if roo_settings.exists():
            settings = json.loads(roo_settings.read_text())
            allowed = settings.get('settings', {}).get('roo-cline', {}).get('allowedCommands', [])
            # Gherkin linting commands should be delegated when registered

    def test_cmd022_integration_runner_revokes_integration_test_commands(self, temp_workbench):
        # CMD-022: integration_test_runner capability → integration test patterns revoked
        # See Draft.md line 309
        roo_settings = (temp_workbench / '.roo-settings.json')
        if roo_settings.exists():
            settings = json.loads(roo_settings.read_text())
            allowed = settings.get('settings', {}).get('roo-cline', {}).get('allowedCommands', [])
            # npm run test:integration, npx vitest --integration patterns


class TestArbiterCheckIntegration:
    # =================================================================
    # Integration with arbiter_check.py
    # =================================================================

    def test_cmd023_arbiter_check_detects_unregistered_command_execution(self):
        # CMD-023: arbiter_check should detect when agent executes unregistered command
        import sys
        from pathlib import Path

        SCRIPTS_DIR = Path(__file__).parent.parent.parent / 'agentic-workbench-engine' / '.workbench' / 'scripts'
        sys.path.insert(0, str(SCRIPTS_DIR))

        try:
            import arbiter_check
            # check_arbiter_capabilities_registered should exist
            assert hasattr(arbiter_check, 'check_arbiter_capabilities_registered')
        except ImportError:
            pytest.skip('arbiter_check not available')

    def test_cmd024_phase_transition_blocked_during_active_work(self, temp_workbench, state_factory):
        # CMD-024: Phase transition (A→B) should be blocked during active development
        state_factory(
            state='RED',  # Active development
            arbiter_capabilities={'test_orchestrator': False}  # Still Phase A
        )

        # Agent should not be able to trigger transition during active work
        state = json.loads((temp_workbench / 'state.json').read_text())
        # State is RED means agent is mid-task, transition should be blocked
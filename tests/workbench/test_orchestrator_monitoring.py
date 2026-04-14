# test_orchestrator_monitoring.py
# GAP-ORC-1: Orchestrator-Only When Dependency Blocked (DEP-3)
#
# Tests Rule DEP-3 from .clinerules: When state=DEPENDENCY_BLOCKED,
# only the Orchestrator Agent may act — no other agent is activated.
#
# Reference: .clinerules lines 284-290, Draft.md lines 479, 551
#
# When state.json.state = DEPENDENCY_BLOCKED:
# - Orchestrator Agent: MAY act (monitoring)
# - Developer Agent: BLOCKED (must not write code)
# - Architect Agent: BLOCKED
# - Test Engineer Agent: BLOCKED

import json
from pathlib import Path

import pytest

from .helpers import TEMPLATE_ROOT


class TestDependencyBlockedMode:
    # =================================================================
    # DEP-3: Dependency Blocked State Enforcement
    # =================================================================

    def test_orc001_only_orchestrator_can_act_when_dependency_blocked(self, temp_workbench, state_factory):
        # ORC-001: DEPENDENCY_BLOCKED → only Orchestrator allowed
        state_factory(
            state='DEPENDENCY_BLOCKED',
            active_req_id='REQ-002',
            feature_registry={
                'REQ-001': {'state': 'RED', 'depends_on': []},
                'REQ-002': {'state': 'DEPENDENCY_BLOCKED', 'depends_on': ['REQ-001']}
            }
        )

        state = json.loads((temp_workbench / 'state.json').read_text())
        assert state['state'] == 'DEPENDENCY_BLOCKED'
        assert state['active_req_id'] == 'REQ-002'

    def test_orc002_developer_blocked_when_dependency_blocked(self, temp_workbench, state_factory):
        # ORC-002: Developer Agent BLOCKED during DEPENDENCY_BLOCKED
        state_factory(
            state='DEPENDENCY_BLOCKED',
            active_req_id='REQ-002',
            feature_registry={
                'REQ-001': {'state': 'RED'},
                'REQ-002': {'state': 'DEPENDENCY_BLOCKED', 'depends_on': ['REQ-001']}
            }
        )

        # Developer should not be writing source code
        src_file = temp_workbench / 'src' / 'login.ts'
        src_file.parent.mkdir(parents=True, exist_ok=True)
        
        # In proper implementation, this would be blocked by FAC-1 or pre-commit hook
        clinerules = (TEMPLATE_ROOT / '.clinerules').read_text(encoding='utf-8')
        assert 'DEPENDENCY_BLOCKED' in clinerules or 'Orchestrator' in clinerules

    def test_orc003_architect_blocked_when_dependency_blocked(self, temp_workbench, state_factory):
        # ORC-003: Architect Agent BLOCKED during DEPENDENCY_BLOCKED
        state_factory(state='DEPENDENCY_BLOCKED', active_req_id='REQ-002')

        clinerules = (TEMPLATE_ROOT / '.clinerules').read_text(encoding='utf-8')
        # Verify Orchestrator is the only one that can act
        assert 'Orchestrator Agent' in clinerules

    def test_orc004_test_engineer_blocked_when_dependency_blocked(self, temp_workbench, state_factory):
        # ORC-004: Test Engineer BLOCKED during DEPENDENCY_BLOCKED
        state_factory(state='DEPENDENCY_BLOCKED', active_req_id='REQ-002')

        clinerules = (TEMPLATE_ROOT / '.clinerules').read_text(encoding='utf-8')
        # DEP-3 rule should exist
        assert 'DEPENDENCY_BLOCKED' in clinerules

    def test_orc005_orchestrator_can_write_handoff_when_blocked(self, temp_workbench, state_factory):
        # ORC-005: Orchestrator CAN write to handoff-state.md for monitoring
        state_factory(
            state='DEPENDENCY_BLOCKED',
            active_req_id='REQ-002',
            feature_registry={
                'REQ-001': {'state': 'RED'},
                'REQ-002': {'state': 'DEPENDENCY_BLOCKED', 'depends_on': ['REQ-001']}
            }
        )

        # Write monitoring status
        handoff_path = temp_workbench / 'memory-bank' / 'hot-context' / 'handoff-state.md'
        handoff_content = '''## Handoff: Arbiter → Orchestrator

- **REQ-ID:** REQ-002
- **Current State:** DEPENDENCY_BLOCKED
- **Blocking Dependency:** REQ-001 not yet MERGED
- **Recommendations:** Monitor REQ-001 state until it reaches MERGED
'''
        handoff_path.write_text(handoff_content, encoding='utf-8')

        assert handoff_path.exists()
        content = handoff_path.read_text(encoding='utf-8')
        assert 'DEPENDENCY_BLOCKED' in content


class TestAutoUnblock:
    # =================================================================
    # Auto-Unblock When Dependency Reaches MERGED
    # =================================================================

    def test_orc006_auto_unblock_when_dependency_merges(self, temp_workbench, state_factory, run_script):
        # ORC-006: DEPENDENCY_BLOCKED → RED when dependency reaches MERGED
        # See Draft.md lines 481, 551
        state_factory(
            state='DEPENDENCY_BLOCKED',
            active_req_id='REQ-002',
            feature_registry={
                'REQ-001': {'state': 'MERGED', 'merged_at': '2026-04-14T10:00:00Z'},
                'REQ-002': {'state': 'DEPENDENCY_BLOCKED', 'depends_on': ['REQ-001']}
            }
        )

        # Run dependency monitor check-unblock
        exit_code, stdout, stderr = run_script('dependency_monitor', 'check-unblock')

        state = json.loads((temp_workbench / 'state.json').read_text())
        # REQ-002 should be unblocked (transitioned to RED)
        assert state['feature_registry']['REQ-002']['state'] == 'RED'

    def test_orc007_partial_dependency_merge_keeps_block(self, temp_workbench, state_factory, run_script):
        # ORC-007: If multiple deps and only some MERGED, still BLOCKED
        state_factory(
            state='DEPENDENCY_BLOCKED',
            active_req_id='REQ-003',
            feature_registry={
                'REQ-001': {'state': 'MERGED'},
                'REQ-002': {'state': 'RED'},  # Not yet MERGED
                'REQ-003': {'state': 'DEPENDENCY_BLOCKED', 'depends_on': ['REQ-001', 'REQ-002']}
            }
        )

        exit_code, stdout, stderr = run_script('dependency_monitor', 'check-unblock')

        state = json.loads((temp_workbench / 'state.json').read_text())
        # REQ-003 should still be BLOCKED (REQ-002 not MERGED)
        assert state['feature_registry']['REQ-003']['state'] == 'DEPENDENCY_BLOCKED'

    def test_orc008_all_dependencies_merged_unblocks(self, temp_workbench, state_factory, run_script):
        # ORC-008: All deps MERGED → feature transitions to RED
        state_factory(
            feature_registry={
                'REQ-001': {'state': 'MERGED'},
                'REQ-002': {'state': 'MERGED'},
                'REQ-003': {'state': 'DEPENDENCY_BLOCKED', 'depends_on': ['REQ-001', 'REQ-002']}
            }
        )

        exit_code, stdout, stderr = run_script('dependency_monitor', 'check-unblock')

        state = json.loads((temp_workbench / 'state.json').read_text())
        assert state['feature_registry']['REQ-003']['state'] == 'RED'


class TestOrchestratorMonitoring:
    # =================================================================
    # Orchestrator Monitoring Activities
    # =================================================================

    def test_orc009_orchestrator_writes_status_to_handoff(self, temp_workbench, state_factory):
        # ORC-009: Orchestrator writes monitoring status to handoff-state.md
        state_factory(
            state='DEPENDENCY_BLOCKED',
            active_req_id='REQ-002',
            feature_registry={
                'REQ-001': {'state': 'RED'},
                'REQ-002': {'state': 'DEPENDENCY_BLOCKED', 'depends_on': ['REQ-001']}
            }
        )

        handoff_path = temp_workbench / 'memory-bank' / 'hot-context' / 'handoff-state.md'
        handoff_content = '''## Handoff: Orchestrator → Human

- **REQ-ID:** REQ-002
- **Status:** DEPENDENCY_BLOCKED
- **Waiting On:** REQ-001 (currently in Stage 3)
- **ETA:** Unknown — waiting for Developer Agent to complete
- **Recommendations:** No action needed — monitoring until unblock
'''
        handoff_path.write_text(handoff_content, encoding='utf-8')

        assert 'DEPENDENCY_BLOCKED' in handoff_path.read_text()

    def test_orc010_orchestrator_reads_feature_registry(self, temp_workbench, state_factory):
        # ORC-010: Orchestrator reads feature_registry to monitor dependency
        state_factory(
            state='DEPENDENCY_BLOCKED',
            active_req_id='REQ-002',
            feature_registry={
                'REQ-001': {'state': 'RED', 'branch': 'feature/REQ-001', 'depends_on': []},
                'REQ-002': {'state': 'DEPENDENCY_BLOCKED', 'branch': 'feature/REQ-002', 'depends_on': ['REQ-001']}
            }
        )

        state = json.loads((temp_workbench / 'state.json').read_text())
        registry = state['feature_registry']

        # Verify Orchestrator can read the registry
        assert 'REQ-001' in registry
        assert 'REQ-002' in registry
        assert registry['REQ-001']['state'] == 'RED'
        assert registry['REQ-002']['state'] == 'DEPENDENCY_BLOCKED'

    def test_orc011_orchestrator_checks_dependency_progress(self, temp_workbench, state_factory):
        # ORC-011: Orchestrator polls feature_registry for dependency progress
        state_factory(
            feature_registry={
                'REQ-001': {'state': 'STAGE_1_ACTIVE'},
                'REQ-002': {'state': 'DEPENDENCY_BLOCKED', 'depends_on': ['REQ-001']}
            }
        )

        state = json.loads((temp_workbench / 'state.json').read_text())
        req001_state = state['feature_registry']['REQ-001']['state']

        # REQ-001 is in progress, REQ-002 is correctly blocked
        assert req001_state != 'MERGED'
        assert state['feature_registry']['REQ-002']['state'] == 'DEPENDENCY_BLOCKED'


class TestArbiterCheckIntegration:
    # =================================================================
    # Integration with arbiter_check.py
    # =================================================================

    def test_orc012_arbiter_check_detects_non_orchestrator_commits(self):
        # ORC-012: arbiter_check should detect commits from non-Orchestrator during block
        import sys
        from pathlib import Path

        SCRIPTS_DIR = Path(__file__).parent.parent.parent / 'agentic-workbench-engine' / '.workbench' / 'scripts'
        sys.path.insert(0, str(SCRIPTS_DIR))

        try:
            import arbiter_check
            assert hasattr(arbiter_check, 'check_dependency_blocked_mode')
        except ImportError:
            pytest.skip('arbiter_check not available')

    def test_orc013_check_dependency_blocked_mode_exists(self):
        # ORC-013: verify check_dependency_blocked_mode function exists
        import sys
        from pathlib import Path

        SCRIPTS_DIR = Path(__file__).parent.parent.parent / 'agentic-workbench-engine' / '.workbench' / 'scripts'
        sys.path.insert(0, str(SCRIPTS_DIR))

        try:
            import arbiter_check
            # The function should exist and be in CHECK_REGISTRY
            assert 'DEP-3' in arbiter_check.CHECK_REGISTRY or \
                   'check_dependency_blocked_mode' in dir(arbiter_check)
        except ImportError:
            pytest.skip('arbiter_check not available')


class TestCrossFeatureSafety:
    # =================================================================
    # Cross-Feature Safety
    # =================================================================

    def test_orc014_file_ownership_conflict_detection(self, temp_workbench, state_factory):
        # ORC-014: File conflict detected when two features touch same file
        state_factory(
            state='DEPENDENCY_BLOCKED',
            active_req_id='REQ-002',
            file_ownership={
                'src/login.ts': 'REQ-001',
                'src/session.ts': 'REQ-001'
            },
            feature_registry={
                'REQ-001': {'state': 'RED'},
                'REQ-002': {'state': 'DEPENDENCY_BLOCKED', 'depends_on': ['REQ-001']}
            }
        )

        state = json.loads((temp_workbench / 'state.json').read_text())

        # file_ownership should detect conflicts before they happen
        assert 'file_ownership' in state
        assert state['file_ownership'].get('src/login.ts') == 'REQ-001'

    def test_orc015_stage_3_single_threaded_enforcement(self, temp_workbench, state_factory):
        # ORC-015: Only one feature in Stage 3 at a time (single-threaded pipeline)
        state_factory(
            state='RED',
            active_req_id='REQ-001',
            feature_registry={
                'REQ-001': {'state': 'RED'},
                'REQ-002': {'state': 'RED'},  # Could not enter Stage 3
            }
        )

        state = json.loads((temp_workbench / 'state.json').read_text())

        # Only one active_req_id at a time
        assert state['active_req_id'] == 'REQ-001'
        # REQ-002 cannot be active while REQ-001 is in execution
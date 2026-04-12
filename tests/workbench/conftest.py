# =============================================================================
# Path Constants (re-exported for test modules)
# =============================================================================

import json
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.resolve()
TEMPLATE_ROOT = REPO_ROOT / "agentic-workbench-engine"


# =============================================================================
# Default State Schema
# =============================================================================

DEFAULT_STATE = {
    "version": "2.1",
    "state": "INIT",
    "stage": None,
    "active_req_id": None,
    "feature_suite_pass_ratio": None,
    "full_suite_pass_ratio": None,
    "regression_state": "NOT_RUN",
    "regression_failures": [],
    "integration_state": "NOT_RUN",
    "integration_test_pass_ratio": None,
    "feature_registry": {},
    "file_ownership": {},
    "last_updated": None,
    "last_updated_by": "workbench-cli",
    "arbiter_capabilities": {
        "test_orchestrator": False,
        "gherkin_validator": False,
        "memory_rotator": False,
        "audit_logger": False,
        "crash_recovery": False,
        "dependency_monitor": False,
        "integration_test_runner": False,
        "git_hooks": False,
    },
}


# =============================================================================
# Hot Context Template Content
# =============================================================================

TEMPLATES = {
    "activeContext.md": "# activeContext.md — Sprint Template\n\n**Template Version:** 2.1\n**Owner:** All Agents\n**Rotation Policy:** Rotate (archive, then reset to template) at sprint end\n\n---\n\n## Session Information\n\n- **Session ID:** (auto-generated on session start)\n- **Start Time:** (YYYY-MM-DD HH:MM UTC)\n- **Branch:** (current git branch)\n- **Mode:** (current agent mode)\n\n---\n\n## Current Task\n\n**REQ-ID:** (active feature identifier, e.g., REQ-001)\n**Stage:** (Stage 1 / Stage 2 / Stage 2b / Stage 3 / Stage 4)\n\n**Task Description:**\n(TODO: Fill in the current task description)\n\n---\n\n## Last Result\n\n**Status:** (IN_PROGRESS / COMPLETED / BLOCKED / FAILED)\n\n**Summary:**\n(TODO: Fill in the last result summary)\n\n---\n\n## Next Steps\n\n- [ ] (TODO: List next actionable steps)\n- [ ]\n- [ ]\n\n---\n\n## Notes\n\n(TODO: Any additional notes, context, or observations)\n",
    "progress.md": "# progress.md — Project-Wide Checkbox State\n\n**Template Version:** 2.1\n**Owner:** All Agents\n**Rotation Policy:** Rotate (archive, then reset to template) at sprint end\n\n---\n\n## Active Features\n\n### REQ-NNN: (Feature Title)\n- [ ] Stage 1: Intent to Contract\n- [ ] Stage 2: Test Suite Authoring\n- [ ] Stage 2b: Integration Contract Scaffolding\n- [ ] Stage 3: Autonomous Execution\n- [ ] Stage 4: Validation and Delivery\n- [ ] MERGED\n\n---\n\n## Sprint Goals\n\n- [ ] (TODO: Sprint goal 1)\n- [ ] (TODO: Sprint goal 2)\n- [ ] (TODO: Sprint goal 3)\n\n---\n\n## Blocked Features\n\n- (TODO: List any features in DEPENDENCY_BLOCKED state)\n\n---\n\n## Completed This Sprint\n\n- (TODO: List completed features and their REQ-IDs)\n\n---\n\n## Notes\n\n(TODO: Any additional project-wide notes)\n",
    "productContext.md": "# productContext.md — Sprint Stories\n\n**Template Version:** 2.1\n**Owner:** All Agents\n**Rotation Policy:** Rotate (archive, then reset to template) at sprint end\n\n---\n\n## Current Sprint: S-NNN\n\n**Sprint Goal:** (TODO: Define sprint goal)\n**Duration:** (TODO: Start date - End date)\n\n---\n\n## User Stories\n\n### US-NNN: (Story Title)\n- **As a:** (user persona)\n- **I want:** (action/feature)\n- **So that:** (business value)\n- **Priority:** (P0 / P1 / P2 / P3)\n- **Acceptance Criteria:**\n  - [ ] (TODO: AC 1)\n  - [ ] (TODO: AC 2)\n\n---\n\n## Sprint Backlog\n\n- [ ] US-NNN: (TODO: Story title)\n- [ ] US-NNN: (TODO: Story title)\n- [ ] US-NNN: (TODO: Story title)\n\n---\n\n## In Progress\n\n- (TODO: Currently active user stories)\n\n---\n\n## Completed\n\n- (TODO: Completed user stories this sprint)\n\n---\n\n## Notes\n\n(TODO: Any additional sprint notes)\n",
    "decisionLog.md": "# decisionLog.md — Architecture Decision Records\n\n**Template Version:** 2.1\n**Owner:** All Agents\n**Rotation Policy:** Persist (never rotate — accumulates across sprints)\n\n---\n\n## ADR Template\n\n```markdown\n## ADR-{NNN}: {Decision Title}\n- **Date:** {YYYY-MM-DD}\n- **Context:** {The situation and constraints}\n- **Decision:** {What was decided}\n- **Consequences:** {What becomes easier/harder as a result}\n```\n\n---\n\n## Decisions\n\n(TODO: Add ADR entries here)\n",
    "systemPatterns.md": "# systemPatterns.md — Technical Conventions\n\n**Template Version:** 2.1\n**Owner:** All Agents\n**Rotation Policy:** Persist (never rotate — accumulates across sprints)\n\n---\n\n## Conventions\n\n(TODO: Document technical conventions, coding standards, and patterns)\n",
    "RELEASE.md": "# RELEASE.md — Release Tracking\n\n**Template Version:** 2.1\n**Owner:** All Agents\n**Rotation Policy:** Persist (never rotate — single source of truth for release tracking)\n\n---\n\n## Releases\n\n(TODO: Document releases with version, date, and changes)\n",
    "handoff-state.md": "# handoff-state.md — Inter-Agent Handoff Message Bus\n\n**Template Version:** 2.1\n**Owner:** All Agents\n**Rotation Policy:** Reset (overwritten to empty template, NOT archived) — handoff data is ephemeral\n\n---\n\n## Handoff Template\n\n```markdown\n## Handoff: {Source Agent Mode} → {Target Agent Mode}\n- **REQ-ID:** REQ-NNN\n- **Completed:** {list of completed artifacts}\n- **Current State:** {state.json.state value}\n- **Recommendations:** {next steps for the receiving agent}\n- **Blocked By:** {any known blockers or dependencies}\n```\n\n---\n\n## Active Handoffs\n\n(TODO: Write handoff entries here when completing tasks or reaching timebox boundaries)\n",
    "session-checkpoint.md": "# session-checkpoint.md — 5-Minute Crash Recovery Heartbeat\n\n**Template Version:** 2.1\n**Owner:** Arbiter (crash_recovery.py daemon)\n**Rotation Policy:** Reset (overwritten to empty template, NOT archived) — crash recovery data is only valid for the current session\n\n---\n\n## Checkpoint Status\n\n**status:** EMPTY\n\n---\n\n## Session Data\n\nOnly valid when `status: ACTIVE`\n\n- **session_id:** (auto-generated UUID)\n- **branch:** (current git branch)\n- **commit_hash:** (current HEAD commit)\n- **current_task:** (current task description)\n- **last_heartbeat:** (YYYY-MM-DD HH:MM UTC)\n\n---\n\n## Crash Recovery Protocol\n\nIf `status: ACTIVE` on session start:\n\n1. Read session data above\n2. Offer to resume from the checkpoint\n3. If human confirms, restore session context\n4. If human declines, reset checkpoint and start fresh\n",
}


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def temp_workbench(tmp_path):
    """
    Create a minimal workbench scaffold in a temp directory.
    
    Structure:
        tmp_path/
        ├── state.json                          # created by state_factory
        ├── memory-bank/hot-context/            # populated by state_factory
        ├── memory-bank/archive-cold/
        ├── src/
        ├── tests/unit/
        ├── tests/integration/
        ├── features/
        ├── _inbox/
        ├── docs/conversations/
        └── .workbench/scripts/                # copied from template
    """
    root = tmp_path

    # Create all directories
    for d in [
        root / "memory-bank" / "hot-context",
        root / "memory-bank" / "archive-cold",
        root / "src",
        root / "tests" / "unit",
        root / "tests" / "integration",
        root / "features",
        root / "_inbox",
        root / "docs" / "conversations",
        root / ".workbench" / "scripts",
    ]:
        d.mkdir(parents=True, exist_ok=True)

    # Copy Arbiter scripts from template
    scripts_src = TEMPLATE_ROOT / ".workbench" / "scripts"
    scripts_dst = root / ".workbench" / "scripts"
    for script in scripts_src.glob("*.py"):
        shutil.copy2(script, scripts_dst / script.name)

    return root


@pytest.fixture
def state_factory(temp_workbench):
    """
    Factory to create state.json with specific field values.
    
    Usage:
        state = state_factory(state="RED", active_req_id="REQ-001")
    
    Returns the state dict that was written.
    """
    def _make_state(**overrides):
        base = dict(DEFAULT_STATE)
        base.update(overrides)
        
        state_path = temp_workbench / "state.json"
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(base, f, indent=2)
            f.write("\n")
        
        # Populate hot-context templates
        hot_context = temp_workbench / "memory-bank" / "hot-context"
        for filename, content in TEMPLATES.items():
            (hot_context / filename).write_text(content, encoding="utf-8")
        
        return base
    return _make_state


@pytest.fixture
def feature_factory(temp_workbench):
    """
    Factory to create .feature files with specific content.
    
    Usage:
        feature_factory("REQ-001-user-login.feature", req_id="REQ-001", ...)
    
    Returns the Path to the created file.
    """
    def _create_feature(
        filename,
        *,
        req_id=None,
        feature_name=None,
        scenarios=None,
        depends_on=None,
        draft=False,
        raw_content=None,
    ):
        if filename.startswith("_inbox/"):
            features_dir = temp_workbench / "_inbox"
            filename = filename.replace("_inbox/", "")
        else:
            features_dir = temp_workbench / "features"
        
        file_path = features_dir / filename
        
        if raw_content is not None:
            file_path.write_text(raw_content, encoding="utf-8")
            return file_path
        
        lines = []
        if draft:
            lines.append("@draft")
        if req_id:
            lines.append(f"@{req_id}")
        if depends_on:
            deps_str = ", ".join(depends_on) if isinstance(depends_on, list) else depends_on
            lines.append(f"@depends-on: {deps_str}")
        
        feat_name = feature_name or filename.replace(".feature", "").replace("_", " ").title()
        lines.append(f"Feature: {feat_name}")
        lines.append("")
        
        if scenarios:
            for scenario in scenarios:
                if isinstance(scenario, dict):
                    lines.append(f"  Scenario: {scenario.get('name', 'Example')}")
                    for step in scenario.get("steps", []):
                        lines.append(f"    {step}")
                    lines.append("")
                else:
                    lines.append(f"  Scenario: {scenario}")
                    lines.append("")
        
        file_path.write_text("\n".join(lines), encoding="utf-8")
        return file_path
    return _create_feature


@pytest.fixture
def script_paths(temp_workbench):
    """Return a dict of script name -> absolute Path for all Arbiter scripts."""
    scripts_dir = temp_workbench / ".workbench" / "scripts"
    return {
        "test_orchestrator": scripts_dir / "test_orchestrator.py",
        "gherkin_validator": scripts_dir / "gherkin_validator.py",
        "integration_test_runner": scripts_dir / "integration_test_runner.py",
        "dependency_monitor": scripts_dir / "dependency_monitor.py",
        "memory_rotator": scripts_dir / "memory_rotator.py",
        "audit_logger": scripts_dir / "audit_logger.py",
        "crash_recovery": scripts_dir / "crash_recovery.py",
    }


@pytest.fixture
def mock_runner_pass(temp_workbench):
    """Set WORKBENCH_MOCK_RUNNER env var to simulate a test runner that always passes."""
    import os
    os.environ["WORKBENCH_MOCK_RUNNER"] = "pass"
    yield
    if "WORKBENCH_MOCK_RUNNER" in os.environ:
        del os.environ["WORKBENCH_MOCK_RUNNER"]


@pytest.fixture
def mock_runner_fail(temp_workbench):
    """Set WORKBENCH_MOCK_RUNNER env var to simulate a test runner that always fails."""
    import os
    os.environ["WORKBENCH_MOCK_RUNNER"] = "fail"
    yield
    if "WORKBENCH_MOCK_RUNNER" in os.environ:
        del os.environ["WORKBENCH_MOCK_RUNNER"]


@pytest.fixture
def run_script(temp_workbench, script_paths):
    """
    Helper to run an Arbiter script and return (exit_code, stdout, stderr).
    
    Usage:
        exit_code, stdout, stderr = run_script("gherkin_validator", "features/")
    """
    def _run(script_name, *args):
        script = script_paths[script_name]
        cmd = ["python", str(script)] + list(args)
        result = subprocess.run(
            cmd,
            cwd=str(temp_workbench),
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.returncode, result.stdout, result.stderr
    return _run


def read_state(temp_workbench):
    """Read state.json from temp_workbench."""
    state_path = temp_workbench / "state.json"
    with open(state_path, "r", encoding="utf-8") as f:
        return json.load(f)
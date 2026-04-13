# Agentic Workbench v2 — Gap Implementation Plan v2

**Author:** Senior Architect (Roo)
**Date:** 2026-04-13
**Supersedes:** [`plans/Gap_Implementation_Plan.md`](./Gap_Implementation_Plan.md) (v1, 2026-04-12)
**Reference Spec:** [`Agentic Workbench v2 - Draft.md`](../Agentic%20Workbench%20v2%20-%20Draft.md)
**Reference Audit:** [`plans/Enforcement_Audit_Report.md`](./Enforcement_Audit_Report.md) (2026-04-13)
**Status:** READY FOR IMPLEMENTATION

---

## What Changed in v2

This plan supersedes v1 with three additions from the Enforcement Audit Report:

| New Gap | Severity | Source |
|---------|----------|--------|
| GAP-12 | 🔴 Critical | `.roomodes` uses YAML-like format — may not be parsed by Roo Code (custom modes silently inert) |
| GAP-13 | 🔴 Critical | `gherkin_validator.py` issues `warnings` not `errors` for unresolved `@depends-on` — TRC-1 never enforced |
| GAP-14 | 🟡 Moderate | `pre-commit` hook does not validate Conventional Commits message format — CMT-1 partially unenforced |

All original gaps (GAP-1 through GAP-11) are preserved unchanged. Sprint ordering has been updated to place GAP-12 and GAP-13 in Sprint A (critical) and GAP-14 in Sprint B.

---

## Gap Summary (Complete — v2)

| # | Gap | Severity | Sprint |
|---|-----|----------|--------|
| GAP-3 | Hook installation not automated in `workbench-cli.py` | 🔴 Critical | Sprint A |
| GAP-5 | `REVIEW_PENDING → MERGED` transition not enforced | 🔴 Critical | Sprint A |
| GAP-6 | `STAGE_1_ACTIVE` / `REQUIREMENTS_LOCKED` transitions not enforced | 🔴 Critical | Sprint A |
| GAP-11 | Cold Zone MCP tool absent — `archive-cold/` is write-only with no retrieval path | 🔴 Critical | Sprint A |
| GAP-12 | `.roomodes` uses YAML-like format — custom modes may be silently inert | 🔴 Critical | Sprint A |
| GAP-13 | `gherkin_validator.py` issues warnings not errors for unresolved `@depends-on` | 🔴 Critical | Sprint A |
| GAP-7 | `file_ownership` map never populated | 🟡 Moderate | Sprint B |
| GAP-9 | `regression_failures` always empty (TODO in code) | 🟡 Moderate | Sprint B |
| GAP-4 | `arbiter_capabilities` never set to `true` | 🟡 Moderate | Sprint B |
| GAP-1 | `compliance_snapshot.py` missing | 🟡 Moderate | Sprint B |
| GAP-2 | `biome.json` template missing | 🟡 Moderate | Sprint B |
| GAP-14 | `pre-commit` hook does not validate Conventional Commits message format | 🟡 Moderate | Sprint B |
| GAP-8 | Phase 0 Ideation Pipeline absent | 🟢 Minor | Sprint C |
| GAP-10 | PyPI packaging absent | 🟢 Minor | Sprint C |
| GAP-15 | No observable proxy checks for partial/honor-only rules — Arbiter cannot warn or block on SLC-1, HND-1, MEM-2, CR-1, DEP-3, FAC-1, TRC-2, REG-1, CMD-TRANSITION | 🔴 Critical | Sprint A |

---

## Sprint A — Critical Pipeline Wiring (Do First)

**Goal:** Make the pipeline actually runnable end-to-end without manual `state.json` edits, inert hooks, inert custom modes, or inaccessible archived memory.

---

### GAP-3: Automate Hook Installation in `workbench-cli.py`

**Problem:** The hooks exist in `.workbench/hooks/` but are never installed into `.git/hooks/`. The physical barriers never fire. This single gap disables 7 rules simultaneously (CMT-1, STM-1, STM-2, REG-2, Forbidden Behaviors #3, #4, #6).

**Files to modify:**
- [`agentic-workbench-engine/workbench-cli.py`](../agentic-workbench-engine/workbench-cli.py)

**Implementation:**

Add a `_install_hooks(repo_path)` helper function and call it from both `cmd_init()` and `cmd_upgrade()`:

```python
def _install_hooks(repo_path):
    """Install Arbiter hooks from .workbench/hooks/ into .git/hooks/."""
    hooks_src = repo_path / ".workbench" / "hooks"
    hooks_dst = repo_path / ".git" / "hooks"

    if not hooks_src.exists():
        print(f"  WARNING: .workbench/hooks/ not found — skipping hook installation")
        return

    hooks_dst.mkdir(parents=True, exist_ok=True)

    for hook_file in hooks_src.iterdir():
        if hook_file.is_file():
            dst = hooks_dst / hook_file.name
            shutil.copy2(hook_file, dst)
            # Make executable on Unix/Mac
            import stat
            dst.chmod(dst.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            print(f"  Installed hook: {hook_file.name} -> .git/hooks/{hook_file.name}")
```

Add a new `install-hooks` subcommand for manual re-installation:

```
workbench-cli.py install-hooks   — (Re)install Arbiter hooks into .git/hooks/
```

**Call sites:**
- `cmd_init()`: call `_install_hooks(project_path)` after the initial commit
- `cmd_upgrade()`: call `_install_hooks(repo_path)` after engine overwrite
- New `cmd_install_hooks()`: standalone command for manual re-installation

**Test coverage needed:**
- `tests/workbench/test_workbench_cli.py`: add test that after `cmd_init()`, `.git/hooks/pre-commit` exists and is executable

**Post-fix enforcement impact:** Activates Rules CMT-1, STM-1 (partial), STM-2 (partial), REG-2 (partial), Forbidden Behaviors #3, #4, #6.

---

### GAP-5: `REVIEW_PENDING → MERGED` State Transition

**Problem:** Nothing writes `MERGED` to `state.json` or updates `feature_registry[REQ-NNN].state`. The pipeline loop never closes; `dependency_monitor.py` can never unblock downstream features.

**Files to modify:**
- [`agentic-workbench-engine/workbench-cli.py`](../agentic-workbench-engine/workbench-cli.py)

**Implementation:**

Add a `merge` subcommand to `workbench-cli.py`:

```
workbench-cli.py merge --req-id REQ-NNN   — Mark feature as MERGED, close pipeline cycle
```

```python
def cmd_merge(req_id):
    """Mark a feature as MERGED and close the pipeline cycle."""
    repo_path = Path.cwd()
    state = load_state_json(repo_path)

    if not state:
        print("ERROR: No state.json found.", file=sys.stderr)
        sys.exit(1)

    current_state = state.get("state")
    if current_state != "REVIEW_PENDING":
        print(f"ERROR: Cannot merge — state is {current_state} (expected REVIEW_PENDING)", file=sys.stderr)
        sys.exit(1)

    registry = state.get("feature_registry", {})
    if req_id not in registry:
        print(f"ERROR: {req_id} not found in feature_registry", file=sys.stderr)
        sys.exit(1)

    registry[req_id]["state"] = "MERGED"
    registry[req_id]["merged_at"] = datetime.now(timezone.utc).isoformat()

    state["state"] = "MERGED"
    state["active_req_id"] = None
    state["stage"] = None
    state["feature_registry"] = registry
    state["last_updated"] = datetime.now(timezone.utc).isoformat()
    state["last_updated_by"] = "workbench-cli"

    state_path = repo_path / "state.json"
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        f.write("\n")

    print(f"[WORKBENCH-CLI] Feature {req_id} MERGED")

    # Trigger dependency monitor to unblock downstream features
    monitor_script = repo_path / ".workbench" / "scripts" / "dependency_monitor.py"
    if monitor_script.exists():
        subprocess.run(["python", str(monitor_script), "check-unblock"], cwd=repo_path)

    print(f"\n[WORKBENCH-CLI] Pipeline cycle complete. Ready for next feature.")
```

**Test coverage needed:**
- `tests/workbench/test_workbench_cli.py`: test that `cmd_merge("REQ-001")` transitions `state = MERGED`, sets `feature_registry["REQ-001"]["state"] = "MERGED"`, clears `active_req_id`
- Test that `cmd_merge` fails when `state != REVIEW_PENDING`

**Post-fix enforcement impact:** Closes the pipeline loop. Enables `dependency_monitor.py` to auto-unblock downstream features. Eliminates the need to manually edit `state.json` for the final transition.

---

### GAP-6: `STAGE_1_ACTIVE` and `REQUIREMENTS_LOCKED` State Transitions

**Problem:** The pipeline entry path (`INIT → STAGE_1_ACTIVE → REQUIREMENTS_LOCKED → RED`) requires humans to manually edit `state.json`, violating the Arbiter-owns-state-json contract.

**Files to modify:**
- [`agentic-workbench-engine/workbench-cli.py`](../agentic-workbench-engine/workbench-cli.py)

**Implementation:**

Add four new subcommands:

```
workbench-cli.py start-feature --req-id REQ-NNN [--slug user-login]
    — Transitions INIT/MERGED → STAGE_1_ACTIVE
    — Creates feature_registry entry for REQ-NNN
    — Sets active_req_id = REQ-NNN

workbench-cli.py lock-requirements --req-id REQ-NNN
    — Transitions STAGE_1_ACTIVE → REQUIREMENTS_LOCKED
    — Validates .feature file exists in /features/
    — Triggers gherkin_validator.py on the feature file
    — Checks dependency gate; sets DEPENDENCY_BLOCKED if unmet deps
    — Sets stage = 2 (ready for Test Engineer)

workbench-cli.py review-pending --req-id REQ-NNN
    — Transitions GREEN → REVIEW_PENDING (after integration tests pass)
    — Validates state.json.integration_state = GREEN before allowing transition
    — Sets stage = 4

workbench-cli.py set-red --req-id REQ-NNN
    — Transitions REQUIREMENTS_LOCKED → RED (after Test Engineer confirms RED state)
    — Called by Test Engineer Agent after writing failing tests
```

```python
def cmd_start_feature(req_id, slug=None):
    """Transition INIT/MERGED → STAGE_1_ACTIVE and register the feature."""
    repo_path = Path.cwd()
    state = load_state_json(repo_path)
    if not state:
        print("ERROR: No state.json found.", file=sys.stderr)
        sys.exit(1)
    current_state = state.get("state")
    if current_state not in ["INIT", "MERGED"]:
        print(f"ERROR: Cannot start feature — state is {current_state} (expected INIT or MERGED)", file=sys.stderr)
        sys.exit(1)
    registry = state.get("feature_registry", {})
    branch_slug = slug or req_id.lower()
    registry[req_id] = {
        "state": "STAGE_1_ACTIVE",
        "branch": f"feature/S1/{req_id}-{branch_slug}" if slug else f"feature/S1/{req_id}",
        "depends_on": [],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    state["state"] = "STAGE_1_ACTIVE"
    state["stage"] = 1
    state["active_req_id"] = req_id
    state["feature_registry"] = registry
    state["last_updated"] = datetime.now(timezone.utc).isoformat()
    state["last_updated_by"] = "workbench-cli"
    _write_state(repo_path, state)
    print(f"[WORKBENCH-CLI] Feature {req_id} started — state = STAGE_1_ACTIVE")
    print(f"  Next: Author .feature file, then run: workbench-cli.py lock-requirements --req-id {req_id}")


def cmd_lock_requirements(req_id):
    """Transition STAGE_1_ACTIVE → REQUIREMENTS_LOCKED after HITL 1 approval."""
    repo_path = Path.cwd()
    state = load_state_json(repo_path)
    if not state:
        print("ERROR: No state.json found.", file=sys.stderr)
        sys.exit(1)
    current_state = state.get("state")
    if current_state != "STAGE_1_ACTIVE":
        print(f"ERROR: Cannot lock requirements — state is {current_state} (expected STAGE_1_ACTIVE)", file=sys.stderr)
        sys.exit(1)
    features_dir = repo_path / "features"
    feature_files = list(features_dir.glob(f"{req_id}-*.feature"))
    if not feature_files:
        print(f"ERROR: No .feature file found for {req_id} in /features/", file=sys.stderr)
        sys.exit(1)
    validator = repo_path / ".workbench" / "scripts" / "gherkin_validator.py"
    if validator.exists():
        result = subprocess.run(
            ["python", str(validator), str(features_dir)],
            cwd=repo_path, capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"ERROR: Gherkin validation failed for {req_id}", file=sys.stderr)
            print(result.stdout)
            sys.exit(1)
    registry = state.get("feature_registry", {})
    feature_entry = registry.get(req_id, {})
    depends_on = feature_entry.get("depends_on", [])
    unmet_deps = [dep for dep in depends_on if registry.get(dep, {}).get("state") != "MERGED"]
    if unmet_deps:
        state["state"] = "DEPENDENCY_BLOCKED"
        registry[req_id]["state"] = "DEPENDENCY_BLOCKED"
        print(f"[WORKBENCH-CLI] {req_id} DEPENDENCY_BLOCKED — unmet: {unmet_deps}")
    else:
        state["state"] = "REQUIREMENTS_LOCKED"
        state["stage"] = 2
        registry[req_id]["state"] = "REQUIREMENTS_LOCKED"
        print(f"[WORKBENCH-CLI] Requirements locked — state = REQUIREMENTS_LOCKED")
        print(f"  Next: Test Engineer Agent writes failing tests, then run: workbench-cli.py set-red --req-id {req_id}")
    state["feature_registry"] = registry
    state["last_updated"] = datetime.now(timezone.utc).isoformat()
    state["last_updated_by"] = "workbench-cli"
    _write_state(repo_path, state)


def cmd_set_red(req_id):
    """Transition REQUIREMENTS_LOCKED → RED after Test Engineer confirms failing tests."""
    repo_path = Path.cwd()
    state = load_state_json(repo_path)
    if not state:
        print("ERROR: No state.json found.", file=sys.stderr)
        sys.exit(1)
    current_state = state.get("state")
    if current_state != "REQUIREMENTS_LOCKED":
        print(f"ERROR: Cannot set RED — state is {current_state} (expected REQUIREMENTS_LOCKED)", file=sys.stderr)
        sys.exit(1)
    state["state"] = "RED"
    state["stage"] = 3
    registry = state.get("feature_registry", {})
    if req_id in registry:
        registry[req_id]["state"] = "RED"
    state["feature_registry"] = registry
    state["last_updated"] = datetime.now(timezone.utc).isoformat()
    state["last_updated_by"] = "workbench-cli"
    _write_state(repo_path, state)
    print(f"[WORKBENCH-CLI] {req_id} — state = RED. Developer Agent may now begin Stage 3.")


def cmd_review_pending(req_id):
    """Transition GREEN → REVIEW_PENDING after integration tests pass."""
    repo_path = Path.cwd()
    state = load_state_json(repo_path)
    if not state:
        print("ERROR: No state.json found.", file=sys.stderr)
        sys.exit(1)
    current_state = state.get("state")
    if current_state != "GREEN":
        print(f"ERROR: Cannot set REVIEW_PENDING — state is {current_state} (expected GREEN)", file=sys.stderr)
        sys.exit(1)
    integration_state = state.get("integration_state")
    if integration_state != "GREEN":
        print(f"ERROR: Cannot set REVIEW_PENDING — integration_state is {integration_state} (expected GREEN)", file=sys.stderr)
        print(f"  Run: python .workbench/scripts/integration_test_runner.py run --set-state", file=sys.stderr)
        sys.exit(1)
    state["state"] = "REVIEW_PENDING"
    state["stage"] = 4
    registry = state.get("feature_registry", {})
    if req_id in registry:
        registry[req_id]["state"] = "REVIEW_PENDING"
    state["feature_registry"] = registry
    state["last_updated"] = datetime.now(timezone.utc).isoformat()
    state["last_updated_by"] = "workbench-cli"
    _write_state(repo_path, state)
    print(f"[WORKBENCH-CLI] {req_id} — state = REVIEW_PENDING. Awaiting HITL 2 approval.")
    print(f"  Next: Lead Engineer reviews PR, then run: workbench-cli.py merge --req-id {req_id}")
```

Add a shared helper:
```python
def _write_state(repo_path, state):
    state_path = repo_path / "state.json"
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        f.write("\n")
```

**Test coverage needed:**
- `tests/workbench/test_workbench_cli.py`: test full lifecycle sequence: `start-feature` → `lock-requirements` → `set-red` → `review-pending` → `merge`
- Test that `review-pending` fails when `integration_state != GREEN` (enforces INT-1)

**Post-fix enforcement impact:** Eliminates the STM-1 paradox. Makes the full pipeline runnable without manual `state.json` editing. Enforces INT-1 (integration gate) at the `review-pending` transition.

---

### GAP-11: Cold Zone MCP Tool — `archive-cold/` Has No Retrieval Path

**Problem:** Rule MEM-1 forbids direct access to `memory-bank/archive-cold/` but provides no alternative. The Cold Zone is write-only. No MCP server exists.

**Files to create:**
- `agentic-workbench-engine/.workbench/mcp/archive_query_server.py`
- `agentic-workbench-engine/.workbench/mcp/README.md`

**Files to modify:**
- `agentic-workbench-engine/.roo-settings.json` — add `mcpServers` entry
- `agentic-workbench-engine/.clinerules` — update Rule MEM-1 to reference MCP tool by name

**Implementation:**

```python
#!/usr/bin/env python3
"""
archive_query_server.py — Cold Zone MCP Server

Owner: The Arbiter (Layer 2)
Version: 2.1
Location: .workbench/mcp/archive_query_server.py

Exposes memory-bank/archive-cold/ via MCP tools.
Agents MUST use these tools instead of reading archive-cold/ directly.

Usage:
  python archive_query_server.py   # Start MCP server (stdio transport)
"""

import json
import sys
from pathlib import Path

ARCHIVE_PATH = Path(__file__).parent.parent.parent / "memory-bank" / "archive-cold"
MAX_RESULTS = 3
DEFAULT_MAX_LINES = 100


def search_archive(query: str, sprint: str = None) -> list:
    """Search archive-cold/ for files matching query. Returns max 3 results."""
    if not ARCHIVE_PATH.exists():
        return []
    results = []
    for f in sorted(ARCHIVE_PATH.glob("*.md"), reverse=True):
        if sprint and sprint.lower() not in f.name.lower():
            continue
        try:
            content = f.read_text(encoding="utf-8")
            if query.lower() in content.lower() or query.lower() in f.name.lower():
                lines = content.split("\n")
                excerpt_lines = [l for l in lines if query.lower() in l.lower()][:3]
                results.append({
                    "filename": f.name,
                    "excerpt": "\n".join(excerpt_lines)[:300],
                    "size_lines": len(lines)
                })
                if len(results) >= MAX_RESULTS:
                    break
        except Exception:
            continue
    return results


def read_archive_file(filename: str, max_lines: int = DEFAULT_MAX_LINES) -> str:
    """Read a specific archived file (truncated to max_lines). Path traversal blocked."""
    file_path = ARCHIVE_PATH / filename
    # Security: only allow files within archive-cold/
    try:
        file_path.resolve().relative_to(ARCHIVE_PATH.resolve())
    except ValueError:
        return "ERROR: Access denied — file is outside archive-cold/"
    if not file_path.exists():
        return f"ERROR: File not found: {filename}"
    lines = file_path.read_text(encoding="utf-8").split("\n")
    truncated = lines[:max_lines]
    if len(lines) > max_lines:
        truncated.append(f"\n... [{len(lines) - max_lines} lines truncated — use max_lines to read more]")
    return "\n".join(truncated)
```

**MCP configuration** — add to `agentic-workbench-engine/.roo-settings.json`:

```json
{
  "mcpServers": {
    "archive-query": {
      "command": "python",
      "args": [".workbench/mcp/archive_query_server.py"],
      "description": "Cold Zone archive query — search and read archived memory-bank files"
    }
  }
}
```

**Update Rule MEM-1 in `.clinerules`:**

```markdown
> **Rule MEM-1:** The agent MUST NOT directly read `memory-bank/archive-cold/` files.
> Cold Zone files are accessed exclusively through the `archive-query` MCP tool:
>   - `search_archive(query)` — find relevant archived files (returns max 3 results with excerpts)
>   - `read_archive_file(filename, max_lines=100)` — read a specific file (truncated)
> Direct access floods the context window with stale data.
```

**Test coverage needed:**
- `tests/workbench/test_archive_query_server.py` (new file):
  - Test `search_archive("REQ-001")` returns matching archived files
  - Test `read_archive_file(filename, max_lines=10)` returns truncated content
  - Test path traversal attack is blocked (`../../../etc/passwd`)
  - Test `search_archive` returns max 3 results even when more match

**Post-fix enforcement impact:** Makes Rule MEM-1 enforceable — agents now have a compliant path to access Cold Zone data.

---

### GAP-12 (NEW): `.roomodes` Format Compatibility

**Problem:** Both `.roomodes` files use a YAML-like `modes:` key structure. Roo Code expects `.roomodes` to be a JSON file with a `customModes` array schema. If Roo Code cannot parse the current format, all custom agent modes (`test-engineer`, `reviewer-security`, `documentation-librarian`) are silently inert — their file access constraints and system prompts never load.

**Files to modify:**
- [`agentic-workbench-engine/.roomodes`](../agentic-workbench-engine/.roomodes)
- [`.roomodes`](../.roomodes) (lab root)

**Implementation:**

Convert both `.roomodes` files from YAML-like format to the correct Roo Code JSON `customModes` array format:

```json
{
  "customModes": [
    {
      "slug": "test-engineer",
      "name": "Test Engineer",
      "roleDefinition": "You are the **Test Engineer Agent**. Your role is to write failing test suites (.spec.ts) that define the mathematical boundaries of success for feature requirements.\n\n**Stage 2 Responsibilities:**\n- Read approved .feature files from /features/\n- Write failing unit/acceptance test files to /tests/unit/\n- Name files: {REQ-NNN}-{slug}.spec.ts\n- Scope each test file to a single REQ-NNN\n- Ensure tests fail against current codebase (RED state confirmed by Arbiter)\n\n**Stage 2b Responsibilities (Integration Contract Scaffolding):**\n- Read state.json.feature_registry to identify all features in MERGED state\n- Write integration skeleton files to /tests/integration/\n- Name files: {FLOW-NNN}-{slug}.integration.spec.ts\n- These tests are intentionally RED — they are contracts, not implementations\n\n**Files you MUST NOT write:**\n- /src — source code is written by the Developer Agent\n- .feature files — contracts are written by the Architect Agent",
      "groups": ["read", "edit"],
      "source": "project"
    },
    {
      "slug": "reviewer-security",
      "name": "Reviewer / Security",
      "roleDefinition": "You are the **Reviewer / Security Agent**. Your role is to perform static analysis and security scans on Pull Requests before human approval.\n\n**Core Responsibilities:**\n- Run static analysis on /src changes to ensure no architectural rules were bypassed\n- Run security scans to identify vulnerabilities, exposed secrets, or unsafe patterns\n- Generate Static Analysis Logs and Security Scan Reports\n- Report findings to the human via Roo Chat for HITL 2 review\n\n**Files you MAY read:** All files — Read-Only\n**Files you MUST NOT write:** /src, /tests, .feature files",
      "groups": ["read"],
      "source": "project"
    },
    {
      "slug": "documentation-librarian",
      "name": "Documentation / Librarian",
      "roleDefinition": "You are the **Documentation / Librarian Agent**. Your role is to continuously compile OpenAPI contracts, system topology graphs, and executive summaries from the live repository state.\n\n**Core Responsibilities:**\n- Generate OpenAPI contracts from /src API definitions\n- Generate Mermaid.js topology graphs showing system architecture\n- Generate executive summaries for non-technical stakeholders\n- Triggered by the Python Arbiter's post-tag hook for compliance snapshots\n\n**Files you MAY write:** Wiki pages and documentation in /docs/ only\n**Files you MUST NOT write:** /src, /tests, .feature files",
      "groups": ["read", "edit"],
      "source": "project"
    }
  ]
}
```

> **Note on built-in modes:** The `architect`, `developer`, and `orchestrator` modes are Roo Code built-ins and do not need to be defined in `.roomodes`. Only the three custom modes (`test-engineer`, `reviewer-security`, `documentation-librarian`) need to be in the JSON file. The system prompts for built-in modes are augmented by `.clinerules` (which is injected as a system context file).

**Verification step:** After converting, open VS Code with the Roo Code extension and verify that the three custom modes appear in the mode selector. If they do not appear, the format is still incorrect.

**Test coverage needed:**
- Manual verification: custom modes appear in Roo Code mode selector after conversion
- `tests/workbench/test_roomodes_format.py` (new file): test that `.roomodes` is valid JSON and contains `customModes` array with the three expected slugs

**Post-fix enforcement impact:** Activates the file access constraint tables and system prompts for `test-engineer`, `reviewer-security`, and `documentation-librarian` modes. Makes Rule FAC-1 partially enforceable (agent is now aware of constraints via system prompt).

---

### GAP-13 (NEW): `gherkin_validator.py` Warning vs. Error for `@depends-on`

**Problem:** [`gherkin_validator.py` line 69](../agentic-workbench-engine/.workbench/scripts/gherkin_validator.py) issues a `warnings.append()` (not `errors.append()`) when a `@depends-on` reference exists in `feature_registry` but is not in `MERGED` state. This means Rule TRC-1 (no Stage 3 without MERGED dependencies) is never enforced at commit time — the warning is easy to ignore.

**Files to modify:**
- [`agentic-workbench-engine/.workbench/scripts/gherkin_validator.py`](../agentic-workbench-engine/.workbench/scripts/gherkin_validator.py)

**Implementation:**

In `validate_feature_file()`, split the `@depends-on` validation into two cases:

```python
# Validate @depends-on references
if req_id and depends_on_list:
    state = load_state()
    if state:
        registry = state.get("feature_registry", {})
        for dep_id in depends_on_list:
            if dep_id not in registry:
                # Dependency not yet registered — warn only (may be planned)
                warnings.append(
                    f"@depends-on references {dep_id} but it is not in feature_registry (may be planned)"
                )
            else:
                dep_state = registry[dep_id].get("state", "UNKNOWN")
                if dep_state != "MERGED":
                    # Dependency exists but is not MERGED — this is a blocking error
                    errors.append(
                        f"@depends-on references {dep_id} but its state is '{dep_state}' (must be MERGED before Stage 3)"
                    )
```

**Logic:**
- Dependency **not in registry** → `warnings` (may be planned but not yet started — non-blocking)
- Dependency **in registry but not MERGED** → `errors` (exists but not ready — blocking)

**Test coverage needed:**
- `tests/workbench/test_gherkin_validator.py`: add test that a `.feature` file with `@depends-on: REQ-001` where `REQ-001` is in `feature_registry` with `state = RED` produces an **error** (not a warning)
- Add test that `@depends-on: REQ-999` where `REQ-999` is NOT in `feature_registry` produces a **warning** (not an error)
- Add test that `@depends-on: REQ-001` where `REQ-001` has `state = MERGED` produces no errors and no warnings

**Post-fix enforcement impact:** Makes Rule TRC-1 deterministically enforced at commit time. The `pre-commit` hook will block commits to `.feature` files that declare unmet dependencies.

---

### GAP-15 (NEW): `arbiter_check.py` — Compliance Health Scanner

**Problem:** The 9 remaining partial/honor-only rules (SLC-1, HND-1, MEM-2, CR-1, DEP-3, FAC-1, TRC-2/DEP-2, REG-1, CMD-TRANSITION) have no observable proxy checks. The Arbiter never warns, never blocks, and never suggests manual enforcement for these rules. The agent can violate them silently with zero feedback.

**Core insight:** Even when a rule cannot be *fully* enforced deterministically, the Arbiter can check **observable proxies** — file timestamps, `state.json` fields, git log patterns, directory contents — and emit structured warnings or hard blocks. This converts "honor-only" into "warned + suggested" for most rules.

**Files to create:**
- [`agentic-workbench-engine/.workbench/scripts/arbiter_check.py`](../agentic-workbench-engine/.workbench/scripts/arbiter_check.py)

**Files to modify:**
- [`agentic-workbench-engine/workbench-cli.py`](../agentic-workbench-engine/workbench-cli.py) — add `check` subcommand delegating to `arbiter_check.py`
- [`agentic-workbench-engine/.workbench/hooks/pre-commit`](../agentic-workbench-engine/.workbench/hooks/pre-commit) — call `arbiter_check.py check-session --block-on-critical` at the top
- [`agentic-workbench-engine/.clinerules`](../agentic-workbench-engine/.clinerules) — update Startup Protocol (SLC-1) to require `python .workbench/scripts/arbiter_check.py check-session` as step 0

**Usage:**

```sh
# Full compliance scan (run manually or from workbench-cli)
python .workbench/scripts/arbiter_check.py check

# Lightweight session-start check (run from pre-commit hook and .clinerules startup)
python .workbench/scripts/arbiter_check.py check-session --block-on-critical

# Check a single rule
python .workbench/scripts/arbiter_check.py check --rule SLC-1
```

**Implementation — Check Registry:**

Each check is a function that returns a `CheckResult(rule, status, message, suggestion, severity)` where `severity` is `CRITICAL` (block), `WARNING` (warn + log), or `INFO`.

```python
CHECK_REGISTRY = {
    "SLC-1":          check_startup_protocol,
    "SLC-2":          check_audit_log_immutability,
    "HND-1":          check_handoff_read,
    "HND-2":          check_handoff_freshness,
    "MEM-1":          check_cold_zone_access,
    "MEM-2":          check_decision_log_updated,
    "CR-1":           check_crash_checkpoint,
    "DEP-3":          check_dependency_blocked_mode,
    "FAC-1":          check_file_access_constraints,
    "TRC-2":          check_live_imports_from_non_merged,
    "REG-1":          check_regression_failures_populated,
    "CMD-TRANSITION": check_arbiter_capabilities_registered,
    "FOR-1":          check_forbidden_self_declaration,
}
```

**Per-rule observable proxy check specifications:**

| Rule | Check ID | Observable Proxy | Severity | Response |
|------|----------|-----------------|----------|----------|
| SLC-1 | `check_startup_protocol` | `activeContext.md` mtime < 10 min ago → startup likely ran; if mtime > 60 min ago and `state != INIT` → warn | WARNING | Warn + suggest running startup protocol |
| SLC-2 | `check_audit_log_immutability` | Compare `docs/conversations/*.md` git object hash vs current content — any mismatch = tampered | CRITICAL | Block + report tampered files |
| HND-1 | `check_handoff_read` | `handoff-state.md` mtime vs last commit time — if handoff is newer than last read (mtime not updated) → warn | WARNING | Warn + suggest reading handoff-state.md |
| HND-2 | `check_handoff_freshness` | Check if `handoff-state.md` contains sprint markers older than current sprint in `progress.md` | WARNING | Warn + suggest `memory_rotator.py rotate` |
| MEM-1 | `check_cold_zone_access` | `git log --diff-filter=M -- memory-bank/archive-cold/` — any direct edits to cold zone files | CRITICAL | Block + report direct cold zone writes |
| MEM-2 | `check_decision_log_updated` | `decisionLog.md` mtime vs sprint start date in `progress.md` — if no update this sprint → warn | WARNING | Warn + suggest logging decisions in ADR format |
| CR-1 | `check_crash_checkpoint` | Read `session-checkpoint.md` — if `status: ACTIVE` and last heartbeat > 30 min ago → stale crash | WARNING | Warn + suggest `crash_recovery.py status` and offer resume |
| DEP-3 | `check_dependency_blocked_mode` | `state.json.state == DEPENDENCY_BLOCKED` → check if any non-Orchestrator work has been committed since block began (git log since `blocked_at` timestamp) | CRITICAL | Block + report non-Orchestrator commits during block |
| FAC-1 | `check_file_access_constraints` | Read `state.json.stage` → map to allowed write paths → check `git diff --cached` for files outside allowed scope | CRITICAL | Block + report out-of-scope file writes |
| TRC-2 | `check_live_imports_from_non_merged` | Scan `src/` for `import` / `require` / `from` statements → extract module names → cross-reference against `feature_registry` for non-MERGED features | WARNING | Warn + list suspect imports with their feature state |
| REG-1 | `check_regression_failures_populated` | `state.json.regression_state == REGRESSION_RED` and `regression_failures == []` → Arbiter has no actionable data | WARNING | Warn + suggest running `test_orchestrator.py run --scope full --set-state` |
| CMD-TRANSITION | `check_arbiter_capabilities_registered` | All `arbiter_capabilities` values are `false` → Phase A not configured | WARNING | Warn + suggest `workbench-cli.py register-arbiter` |
| FOR-1 | `check_forbidden_self_declaration` | `state.json.state` is not `GREEN` but `handoff-state.md` contains "Completed" or "done" markers → possible self-declaration | WARNING | Warn + remind agent that completion requires Arbiter-confirmed GREEN |

**`check-session` mode (lightweight — runs at every session start and in pre-commit):**

Runs only the CRITICAL checks plus CR-1 (crash recovery). Designed to complete in < 1 second:
- `check_audit_log_immutability` (SLC-2)
- `check_cold_zone_access` (MEM-1)
- `check_dependency_blocked_mode` (DEP-3)
- `check_file_access_constraints` (FAC-1)
- `check_crash_checkpoint` (CR-1)

**Output format:**

```
[ARBITER CHECK] Running compliance health scan...

[CRITICAL] FAC-1 — File access constraint violation
  Stage 2 (Test Engineer) must not write to /src/
  Staged files outside allowed scope: src/auth/login.ts
  ACTION REQUIRED: Unstage src/auth/login.ts before committing.
  Rule: FAC-1 in .clinerules

[WARNING] MEM-2 — Decision log not updated this sprint
  decisionLog.md last modified: 2026-04-01 (12 days ago)
  Sprint started: 2026-04-08 (per progress.md)
  SUGGESTION: Log significant decisions in ADR format in decisionLog.md
  Rule: MEM-2 in .clinerules

[WARNING] CMD-TRANSITION — arbiter_capabilities not registered
  All arbiter_capabilities entries are false — Phase A not configured
  SUGGESTION: Run: python workbench-cli.py register-arbiter
  Rule: CMD-TRANSITION in .clinerules

[INFO] CR-1 — No active crash checkpoint found (ok)

[ARBITER CHECK] Scan complete: 1 CRITICAL, 2 WARNING, 1 INFO
[ARBITER CHECK] BLOCKED: 1 critical violation must be resolved before proceeding.
```

**Integration with `.clinerules` Startup Protocol:**

Update Rule SLC-1 in `.clinerules` to add step 0:

```
0. **SCAN** — Run `python .workbench/scripts/arbiter_check.py check-session`
   - If any CRITICAL violations: resolve before proceeding
   - If any WARNING violations: acknowledge and log to handoff-state.md
1. CHECK for activeContext.md ...
```

**Integration with `pre-commit` hook:**

Add as the first check in `pre-commit` (before section 1):

```sh
# =============================================================================
# 0. ARBITER COMPLIANCE HEALTH SCAN (session-start checks)
# =============================================================================
if [ -f ".workbench/scripts/arbiter_check.py" ]; then
    python .workbench/scripts/arbiter_check.py check-session --block-on-critical
    if [ $? -ne 0 ]; then
        echo "[PRE-COMMIT] BLOCKED by Arbiter compliance health scan"
        exit 1
    fi
fi
```

**Integration with `workbench-cli.py status`:**

Extend `cmd_status()` to call `arbiter_check.py check` and display the full compliance report alongside the existing state summary.

**Test coverage needed:**
- `tests/workbench/test_arbiter_check.py` (new file):
  - `test_slc2_detects_tampered_audit_log`: modify a `docs/conversations/*.md` file → check reports CRITICAL
  - `test_fac1_blocks_out_of_scope_write`: stage a `/src/` file while `state.json.stage = 2` → check reports CRITICAL
  - `test_dep3_blocks_non_orchestrator_commit_during_block`: `state = DEPENDENCY_BLOCKED` + non-Orchestrator commit → CRITICAL
  - `test_mem1_detects_cold_zone_direct_write`: git log shows edit to `archive-cold/` → CRITICAL
  - `test_cr1_warns_on_stale_checkpoint`: `session-checkpoint.md` has `status: ACTIVE` with old heartbeat → WARNING
  - `test_mem2_warns_when_decision_log_stale`: `decisionLog.md` not modified this sprint → WARNING
  - `test_cmd_transition_warns_when_capabilities_false`: all `arbiter_capabilities = false` → WARNING
  - `test_trc2_warns_on_suspect_imports`: `src/` contains import from non-MERGED feature module → WARNING
  - `test_for1_warns_on_self_declaration`: `handoff-state.md` contains "Completed" but `state != GREEN` → WARNING
  - `test_check_session_only_runs_critical_checks`: `check-session` mode skips WARNING-only checks
  - `test_full_check_runs_all_checks`: `check` mode runs all 13 checks

**Post-fix enforcement impact:**

This single gap converts **all 9 remaining honor-only rules** from silent violations to **warned + suggested** violations. For 4 of them (SLC-2, MEM-1, DEP-3, FAC-1), the Arbiter can **block** deterministically. The remaining 5 (SLC-1, HND-1, MEM-2, CR-1, TRC-2) move from honor-only to **warned** — the agent receives explicit feedback and a suggested remediation action.

**Revised enforcement forecast after GAP-15:**

| Rule | Before GAP-15 | After GAP-15 |
|------|--------------|--------------|
| SLC-1 | 🔴 Honor | 🟡 Warned (proxy check on activeContext.md mtime) |
| SLC-2 | 🟡 Partial | 🟢 Enforced (git hash comparison blocks tampered logs) |
| HND-1 | 🔴 Honor | 🟡 Warned (handoff-state.md mtime proxy) |
| HND-2 | 🟡 Partial | 🟢 Enforced (sprint marker staleness check) |
| MEM-1 | 🟡 Partial | 🟢 Enforced (git log on archive-cold/ blocks direct writes) |
| MEM-2 | 🔴 Honor | 🟡 Warned (decisionLog.md mtime vs sprint start) |
| CR-1 | 🔴 Honor | 🟡 Warned (session-checkpoint.md ACTIVE status check) |
| DEP-3 | 🔴 Honor | 🟢 Enforced (blocks non-Orchestrator commits during DEPENDENCY_BLOCKED) |
| FAC-1 | 🟡 Partial | 🟢 Enforced (staged file scope check against current stage) |
| TRC-2/DEP-2 | 🔴 Honor | 🟡 Warned (import scanner against feature_registry) |
| REG-1 | 🔴 Honor | 🟡 Warned (regression_failures empty when REGRESSION_RED) |
| CMD-TRANSITION | 🔴 Honor | 🟡 Warned (arbiter_capabilities all-false check) |
| FOR-1 | 🟡 Partial | 🟡 Warned (self-declaration proxy in handoff-state.md) |

---

## Sprint B — Correctness Improvements (Do Second)

**Goal:** Make the implemented features work correctly and completely per spec.

---

### GAP-7: Populate `file_ownership` Map in `pre-commit` Hook

**Problem:** The `pre-commit` hook reads `file_ownership` for conflict detection but nothing ever writes to it. The map is always `{}`.

**Files to modify:**
- [`agentic-workbench-engine/.workbench/hooks/pre-commit`](../agentic-workbench-engine/.workbench/hooks/pre-commit)

**Implementation:**

In the `pre-commit` hook, after section 5 (file ownership conflict check), add section 6:

```sh
# =============================================================================
# 6. UPDATE FILE OWNERSHIP MAP
# =============================================================================
STAGED_SRC=$(git diff --cached --name-only --diff-filter=ACM | grep "^src/" || true)
if [ -n "$STAGED_SRC" ] && [ -f "state.json" ]; then
    python -c "
import json, sys
from datetime import datetime, timezone

state = json.load(open('state.json'))
active_req_id = state.get('active_req_id')

if not active_req_id:
    sys.exit(0)

ownership = state.get('file_ownership', {})
staged_files = '''$STAGED_SRC'''.strip().split('\n')

for f in staged_files:
    if f.strip():
        ownership[f.strip()] = active_req_id

state['file_ownership'] = ownership
state['last_updated_by'] = 'pre-commit'
state['last_updated'] = datetime.now(timezone.utc).isoformat()

with open('state.json', 'w') as out:
    json.dump(state, out, indent=2)
    out.write('\n')

print(f'[PRE-COMMIT] Updated file_ownership for {len(staged_files)} files (owner: {active_req_id})')
" 2>/dev/null || echo "[PRE-COMMIT] File ownership update skipped"
fi
```

Also add `pre-commit` to the `ALLOWED_WRITERS` list in section 1 of the hook:

```sh
ALLOWED_WRITERS="test_orchestrator.py integration_test_runner.py dependency_monitor.py memory_rotator.py audit_logger.py crash_recovery.py workbench-cli pre-commit"
```

**Test coverage needed:**
- `tests/workbench/test_hooks_pre_commit.py`: add test that after a commit with staged `/src/` files, `state.json.file_ownership` is populated with the correct `active_req_id`

---

### GAP-9: Populate `regression_failures` with Actual Test Output

**Problem:** [`test_orchestrator.py` line 227](../agentic-workbench-engine/.workbench/scripts/test_orchestrator.py) has `state["regression_failures"] = []  # TODO: parse from test output`. The Developer Agent has no actionable failure details.

**Files to modify:**
- [`agentic-workbench-engine/.workbench/scripts/test_orchestrator.py`](../agentic-workbench-engine/.workbench/scripts/test_orchestrator.py)

**Implementation:**

Update `run_tests()` to return a `failures` list alongside `exit_code` and `pass_ratio`. Try pytest JSON report first, then vitest JSON reporter, then fall back to exit-code-only. Replace the TODO line in `main()` Phase 2 block:

```python
# OLD:
state["regression_failures"] = []  # TODO: parse from test output
# NEW:
state["regression_failures"] = result.get("failures", [])
```

Also update `run_feature_scope()` and `run_full_regression()` to return `failures` in their result dicts.

**Test coverage needed:**
- `tests/workbench/test_test_orchestrator.py`: add test that when `WORKBENCH_MOCK_RUNNER=fail`, `regression_failures` is non-empty after `--scope full --set-state`

---

### GAP-4: Automate `arbiter_capabilities` Registration

**Problem:** All `arbiter_capabilities` entries remain `false` forever. The Phase B/C migration never happens.

**Files to modify:**
- Each script in [`agentic-workbench-engine/.workbench/scripts/`](../agentic-workbench-engine/.workbench/scripts/)
- [`agentic-workbench-engine/workbench-cli.py`](../agentic-workbench-engine/workbench-cli.py)

**Implementation:**

Add a `register` subcommand to each Arbiter script. The script sets its own `arbiter_capabilities` key to `true` in `state.json`.

Add `register-arbiter` command to `workbench-cli.py` that runs all 7 `register` commands in sequence and also sets `git_hooks = true` if `.git/hooks/pre-commit` exists.

**Capability key mapping:**

| Script | `arbiter_capabilities` key |
|--------|---------------------------|
| `test_orchestrator.py` | `test_orchestrator` |
| `gherkin_validator.py` | `gherkin_validator` |
| `memory_rotator.py` | `memory_rotator` |
| `audit_logger.py` | `audit_logger` |
| `crash_recovery.py` | `crash_recovery` |
| `dependency_monitor.py` | `dependency_monitor` |
| `integration_test_runner.py` | `integration_test_runner` |

**Test coverage needed:**
- Each `test_*.py`: add test that `python {script} register` sets the correct `arbiter_capabilities` key to `true`

---

### GAP-1: `compliance_snapshot.py` — Compliance Vault Script

**Problem:** The `post-tag` hook stubs out `compliance_snapshot.py` with a TODO. Phase 3 compliance snapshots are not automated.

**Files to create:**
- [`agentic-workbench-engine/.workbench/scripts/compliance_snapshot.py`](../agentic-workbench-engine/.workbench/scripts/compliance_snapshot.py)

**Implementation:**

```
python compliance_snapshot.py --tag v1.0.0
```

The script:
1. Creates `compliance-vault/{tag}/` directory
2. Generates a Traceability Matrix from `state.json.feature_registry` — mapping `REQ-NNN` → `.feature` file → test files → source files (via `file_ownership`)
3. Copies all `.feature` files into the vault
4. Copies `state.json` snapshot into the vault
5. Generates a timestamped `COMPLIANCE_SNAPSHOT_{tag}_{timestamp}.md` summary

**Test coverage needed:**
- `tests/workbench/test_compliance_snapshot.py` (new file): test that `compliance_snapshot.py --tag v1.0.0` creates the vault directory, generates the traceability matrix, and copies feature files

---

### GAP-2: `biome.json` Template

**Problem:** No `biome.json` exists in the engine repo. The `pre-commit` hook silently skips linting.

**Files to create:**
- [`agentic-workbench-engine/biome.json`](../agentic-workbench-engine/biome.json)

**Implementation:**

```json
{
  "$schema": "https://biomejs.dev/schemas/1.6.0/schema.json",
  "organizeImports": { "enabled": true },
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true,
      "suspicious": { "noExplicitAny": "warn" },
      "style": { "noNonNullAssertion": "warn" }
    }
  },
  "formatter": {
    "enabled": true,
    "indentStyle": "space",
    "indentWidth": 2,
    "lineWidth": 100
  },
  "files": {
    "include": ["src/**", "tests/**"],
    "ignore": ["node_modules/**", "dist/**", ".workbench/**"]
  }
}
```

Also add `biome.json` to `ENGINE_FILES` in `workbench-cli.py` so it is copied during `init` and `upgrade`.

**Test coverage needed:**
- `tests/workbench/test_workbench_cli.py`: add assertion that after `cmd_init()`, `biome.json` exists in the project root

---

### GAP-14 (NEW): Conventional Commits Validation in `pre-commit` Hook

**Problem:** The `pre-commit` hook does not validate commit message format. Rule CMT-1 requires Conventional Commits but this is never enforced.

**Files to modify:**
- [`agentic-workbench-engine/.workbench/hooks/pre-commit`](../agentic-workbench-engine/.workbench/hooks/pre-commit)

**Implementation:**

Add section 7 to the `pre-commit` hook after the file ownership update:

```sh
# =============================================================================
# 7. CONVENTIONAL COMMITS MESSAGE VALIDATION
# =============================================================================
COMMIT_MSG_FILE=".git/COMMIT_EDITMSG"
if [ -f "$COMMIT_MSG_FILE" ]; then
    COMMIT_MSG=$(head -1 "$COMMIT_MSG_FILE")
    if ! echo "$COMMIT_MSG" | grep -qE "^(feat|fix|docs|chore|refactor|test|perf|ci)(\(.+\))?: .{1,}"; then
        echo "[PRE-COMMIT] BLOCKED: Commit message does not follow Conventional Commits format"
        echo "  Message: '$COMMIT_MSG'"
        echo "  Required: <type>(<scope>): <description>"
        echo "  Allowed types: feat, fix, docs, chore, refactor, test, perf, ci"
        echo "  Example: feat(REQ-001): add user authentication endpoint"
        exit 1
    fi
    echo "[PRE-COMMIT] Commit message format: valid"
fi
```

**Test coverage needed:**
- `tests/workbench/test_hooks_pre_commit.py`: add test that `"bad message"` is blocked; `"feat(REQ-001): add login"` is allowed; `"chore(config): update biome"` is allowed

**Post-fix enforcement impact:** Makes Rule CMT-1 (Conventional Commits) deterministically enforced at commit time.

---

## Sprint C — Enhancement Features (Do Last)

**Goal:** Add the Phase 0 discovery pipeline and PyPI packaging for distribution.

---

### GAP-8: Phase 0 — Ideation & Discovery Pipeline

**Problem:** The Architect Agent's prompt jumps directly to Gherkin writing. The Phase 0 Socratic discovery loop is absent.

**Files to modify:**
- [`agentic-workbench-engine/.roomodes`](../agentic-workbench-engine/.roomodes) — Architect Agent `roleDefinition` (after GAP-12 JSON conversion)
- [`agentic-workbench-engine/memory-bank/hot-context/`](../agentic-workbench-engine/memory-bank/hot-context/) — add `narrativeRequest.md` template

**Implementation:**

Add `narrativeRequest.md` template to `memory-bank/hot-context/`. Update the Architect Agent's `roleDefinition` in `.roomodes` to prepend Phase 0 instructions before the Stage 1 Gherkin authoring instructions. Add `narrativeRequest.md` to `memory_rotator.py` rotation policy (Rotate) and to `workbench-cli.py` `cmd_init()` hot-context copy.

**Test coverage needed:**
- `tests/workbench/test_memory_rotator.py`: add test that `narrativeRequest.md` is archived + reset at sprint end

---

### GAP-10: PyPI Packaging

**Problem:** No `pyproject.toml` exists. `pip install agentic-workbench-cli` is not possible.

**Files to create:**
- [`agentic-workbench-engine/pyproject.toml`](../agentic-workbench-engine/pyproject.toml)

**Implementation:**

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "agentic-workbench-cli"
version = "2.1.0"
description = "Agentic Workbench v2 — Deterministic bootstrapper and lifecycle manager"
readme = "README.md"
requires-python = ">=3.10"
license = { text = "MIT" }

[project.scripts]
workbench-cli = "workbench_cli:main"
```

**Test coverage needed:**
- Verify `pip install -e .` works in a clean virtualenv
- Verify `workbench-cli --version` works after pip install

---

## Implementation Checklist (v2 — Complete)

### Sprint A — Critical (implement in this order)

- [ ] **GAP-3a:** Add `_install_hooks(repo_path)` helper to `workbench-cli.py`
- [ ] **GAP-3b:** Call `_install_hooks()` from `cmd_init()` and `cmd_upgrade()`
- [ ] **GAP-3c:** Add `install-hooks` subcommand to `workbench-cli.py`
- [ ] **GAP-3d:** Add test: after `cmd_init()`, `.git/hooks/pre-commit` exists and is executable
- [ ] **GAP-6a:** Add `start-feature --req-id` subcommand to `workbench-cli.py`
- [ ] **GAP-6b:** Add `lock-requirements --req-id` subcommand to `workbench-cli.py`
- [ ] **GAP-6c:** Add `set-red --req-id` subcommand to `workbench-cli.py`
- [ ] **GAP-6d:** Add `review-pending --req-id` subcommand (validates `integration_state = GREEN`)
- [ ] **GAP-6e:** Add `_write_state()` helper to `workbench-cli.py`
- [ ] **GAP-6f:** Add tests for full lifecycle: `start-feature` → `lock-requirements` → `set-red` → `review-pending` → `merge`
- [ ] **GAP-5a:** Add `merge --req-id` subcommand to `workbench-cli.py`
- [ ] **GAP-5b:** `merge` command updates `feature_registry[REQ-NNN].state = "MERGED"` with `merged_at`
- [ ] **GAP-5c:** `merge` command triggers `dependency_monitor.py check-unblock`
- [ ] **GAP-5d:** Add test: `cmd_merge("REQ-001")` transitions state correctly; fails when `state != REVIEW_PENDING`
- [ ] **GAP-11a:** Create `.workbench/mcp/` directory in engine
- [ ] **GAP-11b:** Create `archive_query_server.py` MCP server with `search_archive` and `read_archive_file` tools
- [ ] **GAP-11c:** Add `mcpServers.archive-query` entry to `agentic-workbench-engine/.roo-settings.json`
- [ ] **GAP-11d:** Update Rule MEM-1 in `.clinerules` to reference the `archive-query` MCP tool by name
- [ ] **GAP-11e:** Create `tests/workbench/test_archive_query_server.py` with search, read, path-traversal, and max-results tests
- [ ] **GAP-12a:** Convert `agentic-workbench-engine/.roomodes` from YAML-like to JSON `customModes` array format
- [ ] **GAP-12b:** Convert lab root `.roomodes` from YAML-like to JSON `customModes` array format
- [ ] **GAP-12c:** Verify custom modes appear in Roo Code mode selector after conversion
- [ ] **GAP-12d:** Create `tests/workbench/test_roomodes_format.py` — validate JSON format and expected slugs
- [ ] **GAP-13a:** Update `gherkin_validator.py` — split `@depends-on` check into warning (not in registry) vs. error (in registry but not MERGED)
- [ ] **GAP-13b:** Add test: `@depends-on` referencing non-MERGED feature in registry produces error
- [ ] **GAP-13c:** Add test: `@depends-on` referencing unknown feature produces warning only
- [ ] **GAP-13d:** Add test: `@depends-on` referencing MERGED feature produces no errors/warnings
- [ ] **GAP-15a:** Create `arbiter_check.py` with `CHECK_REGISTRY` of 13 observable proxy checks
- [ ] **GAP-15b:** Implement `check` mode (full scan, all 13 checks)
- [ ] **GAP-15c:** Implement `check-session` mode (CRITICAL checks only: SLC-2, MEM-1, DEP-3, FAC-1, CR-1)
- [ ] **GAP-15d:** Implement `check_startup_protocol` (SLC-1 proxy: `activeContext.md` mtime)
- [ ] **GAP-15e:** Implement `check_audit_log_immutability` (SLC-2: git hash vs current content — CRITICAL/block)
- [ ] **GAP-15f:** Implement `check_handoff_read` (HND-1 proxy: `handoff-state.md` mtime vs last commit)
- [ ] **GAP-15g:** Implement `check_handoff_freshness` (HND-2: sprint marker staleness)
- [ ] **GAP-15h:** Implement `check_cold_zone_access` (MEM-1: git log on `archive-cold/` — CRITICAL/block)
- [ ] **GAP-15i:** Implement `check_decision_log_updated` (MEM-2: `decisionLog.md` mtime vs sprint start)
- [ ] **GAP-15j:** Implement `check_crash_checkpoint` (CR-1: `session-checkpoint.md` ACTIVE + stale heartbeat)
- [ ] **GAP-15k:** Implement `check_dependency_blocked_mode` (DEP-3: non-Orchestrator commits during DEPENDENCY_BLOCKED — CRITICAL/block)
- [ ] **GAP-15l:** Implement `check_file_access_constraints` (FAC-1: staged files vs stage-allowed scope — CRITICAL/block)
- [ ] **GAP-15m:** Implement `check_live_imports_from_non_merged` (TRC-2: import scanner vs `feature_registry`)
- [ ] **GAP-15n:** Implement `check_regression_failures_populated` (REG-1: `regression_failures` empty when REGRESSION_RED)
- [ ] **GAP-15o:** Implement `check_arbiter_capabilities_registered` (CMD-TRANSITION: all-false warning)
- [ ] **GAP-15p:** Implement `check_forbidden_self_declaration` (FOR-1: "Completed" in handoff but state != GREEN)
- [ ] **GAP-15q:** Add `check` subcommand to `workbench-cli.py` delegating to `arbiter_check.py check`
- [ ] **GAP-15r:** Extend `cmd_status()` in `workbench-cli.py` to call `arbiter_check.py check` and display report
- [ ] **GAP-15s:** Add section 0 to `pre-commit` hook calling `arbiter_check.py check-session --block-on-critical`
- [ ] **GAP-15t:** Update `.clinerules` Startup Protocol (SLC-1) to add step 0: run `arbiter_check.py check-session`
- [ ] **GAP-15u:** Create `tests/workbench/test_arbiter_check.py` with 11 test cases covering all check functions

### Sprint B — Correctness (implement after Sprint A)

- [ ] **GAP-7a:** Add file ownership write step (section 6) to `pre-commit` hook
- [ ] **GAP-7b:** Add `pre-commit` to `ALLOWED_WRITERS` in `pre-commit` hook section 1
- [ ] **GAP-7c:** Add test: staged `/src/` files populate `file_ownership` after commit
- [ ] **GAP-9a:** Update `run_tests()` in `test_orchestrator.py` to return `failures` list
- [ ] **GAP-9b:** Parse pytest JSON report for failure details
- [ ] **GAP-9c:** Parse vitest JSON reporter output for failure details
- [ ] **GAP-9d:** Replace `regression_failures = []  # TODO` with `result.get("failures", [])`
- [ ] **GAP-9e:** Add test: `WORKBENCH_MOCK_RUNNER=fail` produces non-empty `regression_failures`
- [ ] **GAP-4a:** Add `register` subcommand to each of the 7 Arbiter scripts
- [ ] **GAP-4b:** Add `register-arbiter` command to `workbench-cli.py`
- [ ] **GAP-4c:** Add test: `python test_orchestrator.py register` sets `arbiter_capabilities.test_orchestrator = true`
- [ ] **GAP-1a:** Create `compliance_snapshot.py` with `--tag` argument
- [ ] **GAP-1b:** Generate Traceability Matrix from `feature_registry` + `file_ownership`
- [ ] **GAP-1c:** Create `compliance-vault/{tag}/` with snapshot files
- [ ] **GAP-1d:** Add test: `compliance_snapshot.py --tag v1.0.0` creates vault with traceability matrix
- [ ] **GAP-2a:** Create `biome.json` template in engine root
- [ ] **GAP-2b:** Add `biome.json` to `ENGINE_FILES` in `workbench-cli.py`
- [ ] **GAP-2c:** Add test: after `cmd_init()`, `biome.json` exists in project root
- [ ] **GAP-14a:** Add section 7 (Conventional Commits validation) to `pre-commit` hook
- [ ] **GAP-14b:** Add test: non-Conventional Commits message is blocked; valid message is allowed

### Sprint C — Enhancements (implement last)

- [ ] **GAP-8a:** Create `narrativeRequest.md` template in `memory-bank/hot-context/`
- [ ] **GAP-8b:** Add Phase 0 instructions to Architect Agent `roleDefinition` in `.roomodes`
- [ ] **GAP-8c:** Add `narrativeRequest.md` to `memory_rotator.py` rotation policy (Rotate)
- [ ] **GAP-8d:** Add `narrativeRequest.md` to `workbench-cli.py` `cmd_init()` hot-context copy
- [ ] **GAP-8e:** Add test: `narrativeRequest.md` is archived + reset at sprint end
- [ ] **GAP-10a:** Create `pyproject.toml` in engine root
- [ ] **GAP-10b:** Verify `pip install -e .` works in clean virtualenv
- [ ] **GAP-10c:** Verify `workbench-cli --version` works after pip install

---

## Post-Implementation Enforcement Forecast

The following table estimates the enforcement level for each rule **after all gaps in this plan are fully implemented**. Rules that remain honor-only after full implementation represent the **irreducible minimum** — they require either Roo Code platform features that do not exist, or static analysis tooling beyond the scope of this plan.

> **Note:** Sprint A column now includes GAP-15 (`arbiter_check.py`). The "After Sprint A" column reflects the state after all Sprint A gaps including GAP-15 are implemented.

| Rule | Current | After Sprint A (incl. GAP-15) | After Sprint B | After Sprint C | Final |
|------|---------|-------------------------------|----------------|----------------|-------|
| SLC-1 (startup sequence CHECK→CREATE→READ→ACT) | 🔴 Honor | 🟡 Warned (activeContext.md mtime proxy) | 🟡 Warned | 🟡 Warned | 🟡 Warned |
| SLC-2 (audit log immutability) | 🟡 Partial | 🟢 Enforced (git hash comparison — blocks tampered logs) | 🟢 Enforced | 🟢 Enforced | 🟢 Enforced |
| HND-1 (read handoff before acting) | 🔴 Honor | 🟡 Warned (handoff-state.md mtime proxy) | 🟡 Warned | 🟡 Warned | 🟡 Warned |
| HND-2 (handoff ephemeral reset) | 🟡 Partial | 🟢 Enforced (sprint marker staleness check) | 🟢 Enforced | 🟢 Enforced | 🟢 Enforced |
| TRC-1 (no Stage 3 without MERGED deps) | 🔴 Honor | 🟢 Enforced (gherkin_validator error + pre-commit block) | 🟢 Enforced | 🟢 Enforced | 🟢 Enforced |
| TRC-2 (no live API imports from non-MERGED) | 🔴 Honor | 🟡 Warned (import scanner vs feature_registry) | 🟡 Warned | 🟡 Warned | 🟡 Warned |
| CMT-1 (conventional commits + no main commits) | 🔴 Honor | 🟡 Partial (pre-push blocks main; commit msg added in Sprint B) | 🟢 Enforced | 🟢 Enforced | 🟢 Enforced |
| STM-1 (agent must not write state.json) | 🔴 Honor | 🟢 Enforced (pre-commit ALLOWED_WRITERS check) | 🟢 Enforced | 🟢 Enforced | 🟢 Enforced |
| STM-2 (not GREEN until Phase 2 passes) | 🟡 Partial | 🟢 Enforced (test_orchestrator two-phase + state machine CLI) | 🟢 Enforced | 🟢 Enforced | 🟢 Enforced |
| INT-1 (no completion until integration GREEN) | 🔴 Honor | 🟢 Enforced (review-pending validates integration_state = GREEN) | 🟢 Enforced | 🟢 Enforced | 🟢 Enforced |
| REG-1 (regression log as primary input) | 🔴 Honor | 🟡 Warned (regression_failures empty when REGRESSION_RED) | 🟡 Warned | 🟡 Warned | 🟡 Warned |
| REG-2 (full suite after Phase 1 GREEN) | 🟡 Partial | 🟢 Enforced (test_orchestrator Phase 2 mandatory) | 🟢 Enforced | 🟢 Enforced | 🟢 Enforced |
| CMD-1 (Phase A auto-approve allowlist) | 🟡 Partial | 🟡 Partial | 🟡 Partial | 🟡 Partial | 🟡 Partial |
| CMD-2 (Arbiter-owned domains not executed directly) | 🟡 Partial | 🟡 Partial | 🟢 Enforced (arbiter_capabilities registered) | 🟢 Enforced | 🟢 Enforced |
| CMD-3 (permanently forbidden commands) | 🟡 Partial | 🟡 Partial | 🟡 Partial | 🟡 Partial | 🟡 Partial |
| CMD-TRANSITION (read arbiter_capabilities on start) | 🔴 Honor | 🟡 Warned (all-false warning in check-session) | 🟡 Warned | 🟡 Warned | 🟡 Warned |
| MEM-1 (no direct Cold Zone access) | 🔴 Honor | 🟢 Enforced (git log on archive-cold/ — CRITICAL block) | 🟢 Enforced | 🟢 Enforced | 🟢 Enforced |
| MEM-2 (decision logging in ADR format) | 🔴 Honor | 🟡 Warned (decisionLog.md mtime vs sprint start) | 🟡 Warned | 🟡 Warned | 🟡 Warned |
| DEP-1 (dependency gate at Stage 3 entry) | 🔴 Honor | 🟢 Enforced (gherkin_validator + state machine CLI) | 🟢 Enforced | 🟢 Enforced | 🟢 Enforced |
| DEP-2 (no live API imports from non-MERGED) | 🔴 Honor | 🟡 Warned (import scanner — same as TRC-2) | 🟡 Warned | 🟡 Warned | 🟡 Warned |
| DEP-3 (only Orchestrator acts when DEPENDENCY_BLOCKED) | 🔴 Honor | 🟢 Enforced (blocks non-Orchestrator commits during DEPENDENCY_BLOCKED) | 🟢 Enforced | 🟢 Enforced | 🟢 Enforced |
| FAC-1 (mode-specific file access constraints) | 🔴 Honor | 🟢 Enforced (staged file scope check vs current stage — CRITICAL block) | 🟢 Enforced | 🟢 Enforced | 🟢 Enforced |
| CR-1 (offer resume after crash) | 🔴 Honor | 🟡 Warned (session-checkpoint.md ACTIVE + stale heartbeat) | 🟡 Warned | 🟡 Warned | 🟡 Warned |
| FOR-1 (forbidden behaviors) | 🔴 Honor | 🟡 Warned (self-declaration proxy in handoff-state.md) | 🟡 Warned | 🟡 Warned | 🟡 Warned |

### Final Score After Full Implementation (with GAP-15)

| Rating | Current | After All Sprints | Delta |
|--------|---------|-------------------|-------|
| 🟢 ENFORCED | 0 (0%) | 14 (58%) | +14 |
| 🟡 WARNED / PARTIALLY ENFORCED | 7 (29%) | 10 (42%) | +3 |
| 🔴 HONOR-ONLY (silent) | 17 (71%) | 0 (0%) | -17 |

**Projected enforcement level after full implementation: 100% warned or enforced (up from 29%). Zero silent violations.**

> **Key distinction:** "Warned" means the Arbiter detects a proxy signal and emits a structured warning with a suggested remediation — the agent cannot violate the rule silently. "Enforced" means the Arbiter blocks the operation deterministically. Both are vastly superior to the current honor-only state.

### The Irreducible Warned Floor (rules that cannot be fully blocked)

These rules cannot be *fully blocked* (exit 1) because the Arbiter cannot intercept the agent's cognitive process — only its git operations. However, with GAP-15, **none of them are silent anymore**:

| Rule | Why It Cannot Be Fully Blocked | GAP-15 Mitigation |
|------|-------------------------------|-------------------|
| SLC-1 (startup sequence) | Roo Code has no mechanism to mandate tool calls before cognitive work begins | `check-session` warns if `activeContext.md` mtime suggests startup was skipped |
| HND-1 (read handoff before acting) | No pre-action file read enforcement | `check-session` warns if `handoff-state.md` mtime suggests it was not read |
| TRC-2 / DEP-2 (no live API imports) | Full static analysis requires AST parsing — expensive | Import scanner warns on suspect `import` statements vs `feature_registry` |
| REG-1 (regression log as primary input) | Cannot force agent to prioritize a specific file | Warns when `regression_failures` is empty during REGRESSION_RED state |
| MEM-2 (decision logging) | Cannot verify post-session that ADR was written | Warns when `decisionLog.md` mtime predates current sprint |
| CMD-TRANSITION (read arbiter_capabilities) | No pre-action enforcement | Warns when all `arbiter_capabilities` are false |
| CR-1 (offer resume after crash) | Daemon startup requires OS-level hooks | Warns when stale ACTIVE checkpoint is detected |
| FOR-1 (self-declaration) | Cannot intercept agent's internal reasoning | Warns when "Completed" appears in handoff but state is not GREEN |

> **Note:** With GAP-15, the "irreducible floor" shifts from "honor-only (silent)" to "warned (visible)". The agent receives explicit feedback for every rule violation, even those that cannot be physically blocked. This is the maximum achievable enforcement level without changes to the Roo Code platform itself.

---

## Files Changed Summary (v2 — Complete)

| File | Sprint | Change Type |
|------|--------|-------------|
| `agentic-workbench-engine/workbench-cli.py` | A | Modify — add `start-feature`, `lock-requirements`, `set-red`, `review-pending`, `merge`, `install-hooks`, `register-arbiter` commands; add `_install_hooks()`, `_write_state()` helpers |
| `agentic-workbench-engine/.workbench/mcp/archive_query_server.py` | A | **Create new** — MCP server exposing Cold Zone query tools |
| `agentic-workbench-engine/.workbench/mcp/README.md` | A | **Create new** — MCP server setup instructions |
| `agentic-workbench-engine/.roo-settings.json` | A | Modify — add `mcpServers.archive-query` entry |
| `agentic-workbench-engine/.clinerules` | A | Modify — update Rule MEM-1 to reference `archive-query` MCP tool by name |
| `agentic-workbench-engine/.roomodes` | A | **Convert** — YAML-like format → JSON `customModes` array (GAP-12) |
| `.roomodes` (lab root) | A | **Convert** — YAML-like format → JSON `customModes` array (GAP-12) |
| `agentic-workbench-engine/.workbench/scripts/gherkin_validator.py` | A | Modify — split `@depends-on` check: warning (not in registry) vs. error (in registry but not MERGED) (GAP-13) |
| `agentic-workbench-engine/.workbench/hooks/pre-commit` | B | Modify — add section 6 (file ownership write), section 7 (Conventional Commits validation); add `pre-commit` to ALLOWED_WRITERS |
| `agentic-workbench-engine/.workbench/scripts/test_orchestrator.py` | B | Modify — parse test output into `regression_failures`; add `register` command |
| `agentic-workbench-engine/.workbench/scripts/gherkin_validator.py` | B | Modify — add `register` command |
| `agentic-workbench-engine/.workbench/scripts/memory_rotator.py` | B | Modify — add `register` command |
| `agentic-workbench-engine/.workbench/scripts/audit_logger.py` | B | Modify — add `register` command |
| `agentic-workbench-engine/.workbench/scripts/crash_recovery.py` | B | Modify — add `register` command |
| `agentic-workbench-engine/.workbench/scripts/dependency_monitor.py` | B | Modify — add `register` command |
| `agentic-workbench-engine/.workbench/scripts/integration_test_runner.py` | B | Modify — add `register` command |
| `agentic-workbench-engine/.workbench/scripts/compliance_snapshot.py` | B | **Create new** — compliance vault generator |
| `agentic-workbench-engine/biome.json` | B | **Create new** — Biome linter/formatter config |
| `tests/workbench/test_archive_query_server.py` | A | **Create new** — MCP server tests |
| `tests/workbench/test_roomodes_format.py` | A | **Create new** — `.roomodes` JSON format validation tests |
| `tests/workbench/test_compliance_snapshot.py` | B | **Create new** — compliance snapshot tests |
| `agentic-workbench-engine/memory-bank/hot-context/narrativeRequest.md` | C | **Create new** — Phase 0 narrative request template |
| `agentic-workbench-engine/pyproject.toml` | C | **Create new** — PyPI packaging config |
| `agentic-workbench-engine/.workbench/scripts/arbiter_check.py` | A | **Create new** — Compliance health scanner with 13 observable proxy checks (GAP-15) |
| `agentic-workbench-engine/.workbench/hooks/pre-commit` | A | Modify — add section 0 calling `arbiter_check.py check-session --block-on-critical` (GAP-15) |
| `agentic-workbench-engine/.clinerules` | A | Modify — update SLC-1 Startup Protocol to add step 0: run `arbiter_check.py check-session` (GAP-15) |
| `tests/workbench/test_arbiter_check.py` | A | **Create new** — 11 test cases for all observable proxy check functions (GAP-15) |
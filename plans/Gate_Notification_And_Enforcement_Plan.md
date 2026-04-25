# Proactive Gate Notification & Pipeline Enrollment Enforcement Plan

**Date:** 2026-04-25
**Author:** Orchestrator Agent
**Problem Statement:** Agents bypassed the pipeline for `feature/codebase-memory-mcp` (no REQ-ID, no `.feature` file, no state registration). Additionally, there's no proactive notification when HITL gates are pending — the human must manually know to check.

---

## Problem 1: No Pipeline Enrollment Enforcement

### Root Cause
When a human requests new functionality, agents should route it through Stage 1 (Architect Agent → Gherkin → REQ-ID → HITL Gate 1). Instead, agents treated direct engineering work as valid without pipeline enrollment.

### What Should Have Happened
```
Human: "Add codebase-memory MCP functionality"
  ↓
Orchestrator: "This is new feature work. Must enroll in pipeline first."
  ↓
Architect Agent: Creates REQ-NNN-{slug}.feature
  ↓
HITL Gate 1: Human approves requirements
  ↓
state.json updates: state=STAGE_1_ACTIVE, active_req_id=REQ-NNN, feature_registry[REQ-NNN]={state: REQUIREMENTS_LOCKED, ...}
  ↓
...full pipeline follows...
```

### What's Missing
1. **Orchestrator gatekeeper** — No validation that new work has valid `active_req_id` in state.json before proceeding
2. **Startup compliance check** — Session scan doesn't verify the agent is working on a registered feature
3. **No "enrollment required" alert** — Agents should stop and say "this feature is not in state.json.feature_registry" instead of proceeding

---

## Problem 2: No Proactive Gate Notification

### Root Cause
No script monitors `state.json` for pending gates and surfaces them to the human. The human is expected to manually know when to act.

### What's Missing
1. **No `gate_notification.py`** — Nothing polls state.json for `REVIEW_PENDING` or `REQUIREMENTS_LOCKED` states
2. **No proactive suggestion in memory-bank** — `activeContext.md` never says "⚠️ HITL Gate 2 pending — your action needed"
3. **No Orchestrator monitoring for gates** — `orchestrator_monitor.py` only handles dependency unblock, not gate status
4. **No background daemon** — No process periodically surfaces pending actions

---

## Implementation Plan

### Phase 1: Pipeline Enrollment Enforcement

#### Step 1.1 — Create `gatekeeper.py` (Arbiter Script)
**File:** `agentic-workbench-engine/.workbench/scripts/gatekeeper.py`

**Purpose:** Validates that any active work is enrolled in the pipeline (has a valid `active_req_id` in `state.json.feature_registry` with a non-TERMINAL state).

**Logic:**
```python
def check_enrollment():
    state = read_state_json()
    
    if state['active_req_id'] is null:
        return Result(level="CRITICAL", message="No active feature. All new work must be enrolled via Stage 1 (Architect Agent). Run: workbench-cli.py init-feature")
    
    req_id = state['active_req_id']
    if req_id not in state['feature_registry']:
        return Result(level="CRITICAL", message=f"{req_id} is not in feature_registry. Must create .feature file and get HITL Gate 1 approval first.")
    
    feature_state = state['feature_registry'][req_id]['state']
    TERMINAL_STATES = ['MERGED', 'ABANDONED']
    if feature_state in TERMINAL_STATES:
        return Result(level="WARNING", message=f"{req_id} is {feature_state}. Next feature cycle must be started.")
    
    return Result(level="OK")
```

**Trigger:** Called during SCAN step of startup protocol (SLC-1 step 0).

---

#### Step 1.2 — Update `arbiter_check.py` — Add `check-enrollment` command
**File:** `agentic-workbench-engine/.workbench/scripts/arbiter_check.py`

**Mode:** Add new check mode `check-enrollment` that runs gatekeeper validation.

**Output:** CRITICAL violation logged to `handoff-state.md` if not enrolled.

---

#### Step 1.3 — Add `arbiter_capabilities.gatekeeper = true` to state.json
**File:** `agentic-workbench-engine/state.json`

**New capability:**
```json
"gatekeeper": false
```

---

#### Step 1.4 — Write test: `test_gatekeeper.py`
**File:** `tests/workbench/test_gatekeeper.py`

**Coverage:**
- Test that un-enrolled work triggers CRITICAL
- Test that enrolled feature with valid state passes
- Test that TERMINAL state triggers WARNING (not CRITICAL)
- Test that missing active_req_id triggers CRITICAL

---

### Phase 2: Proactive Gate Notification

#### Step 2.1 — Create `gate_notification.py` (Arbiter Script)
**File:** `agentic-workbench-engine/.workbench/scripts/gate_notification.py`

**Purpose:** Polls state.json for gate-blocking states and writes actionable notifications to `handoff-state.md`.

**Check these states:**
| State | Gate | Notification |
|-------|------|--------------|
| `REQUIREMENTS_LOCKED` | HITL 1 pending | "Product Owner must approve requirements for {active_req_id}" |
| `REVIEW_PENDING` | HITL 2 pending | "⚠️ HUMAN BLOCKING: Lead Engineer must approve PR for {active_req_id} to proceed" |
| `DEPENDENCY_BLOCKED` | Orchestrator monitoring | "Feature {active_req_id} blocked by dependencies: {list}" |
| `PIVOT_IN_PROGRESS` | HITL 1.5 pending | "⚠️ HUMAN BLOCKING: Pivot approval needed for {active_req_id}" |

**Output format in handoff-state.md:**
```markdown
## ⚠️ Pending Human Actions

| REQ-ID | Gate | Blocking Since | Action Required |
|--------|------|----------------|----------------|
| REQ-001 | HITL 2 | 2026-04-25T19:45 | Approve PR merge |
```

**Trigger options:**
1. Post-commit hook — after any commit, run gate_notification check
2. Startup scan — include gate status in SCAN→CHECK→CREATE→READ→ACT protocol
3. Daemon mode — optional background process (lower priority)

---

#### Step 2.2 — Update `arbiter_check.py` — Add `check-gates` command
**File:** `agentic-workbench-engine/.workbench/scripts/arbiter_check.py`

**Mode:** Add `check-gates` that runs gate_notification and reports pending human actions.

**Output:** Formatted table of pending gates for Roo Chat display.

---

#### Step 2.3 — Update `activeContext.md` template — Add "Pending Actions" section
**File:** `memory-bank/hot-context/activeContext.md`

**Add section:**
```markdown
## ⚠️ Pending Human Actions

<!-- Auto-populated by gate_notification.py -->
<!-- Format: REQ-ID | Gate | Action Required -->

_(empty if no pending gates)_
```

---

#### Step 2.4 — Enhance startup protocol to surface pending gates
**File:** `.clinerules` Section 1.1

**Update SCAN step to include gate check:**
```
0. SCAN — Run arbiter_check.py check-session (5-rule scan)
   + Run arbiter_check.py check-gates (report pending human actions)
   → If any gates pending: surface to Roo Chat immediately
```

---

#### Step 2.5 — Add `arbiter_capabilities.gate_notification = true` to state.json
**File:** `agentic-workbench-engine/state.json`

---

#### Step 2.6 — Write test: `test_gate_notification.py`
**File:** `tests/workbench/test_gate_notification.py`

**Coverage:**
- Test that REQUIREMENTS_LOCKED surfaces HITL 1 pending
- Test that REVIEW_PENDING surfaces HITL 2 pending
- Test that DEPENDENCY_BLOCKED surfaces dependency list
- Test that activeContext.md is updated with pending table
- Test that handoff-state.md is updated with pending table

---

### Phase 3: Orchestrator Monitoring Enhancement

#### Step 3.1 — Create/enhance `orchestrator_monitor.py`
**File:** `agentic-workbench-engine/.workbench/scripts/orchestrator_monitor.py`

**Purpose:** Orchestrator Agent's active monitoring script (extends dependency_monitor.py).

**Functions:**
1. `check_pending_gates()` — calls gate_notification logic
2. `check_dependency_blocks()` — existing dependency_monitor logic
3. `check_blocking_states()` — RED, REGRESSION_RED, INTEGRATION_RED states
4. `generate_handoff_report()` — writes comprehensive status to handoff-state.md

**Output format:**
```markdown
## Orchestrator Status Report

### Pending Human Actions
| REQ-ID | Gate | Feature | Blocking Since |
|--------|------|--------|----------------|
| REQ-001 | HITL 2 | codebase-memory-mcp | 2026-04-25T19:45 |

### Dependency Blocks
| REQ-ID | Blocked By | Status |
|--------|-----------|--------|
| REQ-042 | REQ-038 (not MERGED) | DEPENDENCY_BLOCKED |

### Blocking States
| Feature | State | Last Updated |
|---------|-------|--------------|
| REQ-001 | REGRESSION_RED | 2026-04-25T18:30 |
```

---

#### Step 3.2 — Add `arbiter_capabilities.orchestrator_monitor = true` to state.json

---

#### Step 3.3 — Write test: `test_orchestrator_monitoring.py`
**File:** `tests/workbench/test_orchestrator_monitoring.py`

---

## File Inventory

### New Files
| File | Purpose |
|------|---------|
| `agentic-workbench-engine/.workbench/scripts/gatekeeper.py` | Pipeline enrollment validation |
| `tests/workbench/test_gatekeeper.py` | Gatekeeper tests |
| `tests/workbench/test_gate_notification.py` | Gate notification tests |
| `tests/workbench/test_orchestrator_monitoring.py` | Orchestrator monitoring tests |

### Modified Files
| File | Changes |
|------|---------|
| `agentic-workbench-engine/.workbench/scripts/arbiter_check.py` | Add `check-enrollment` and `check-gates` modes |
| `agentic-workbench-engine/state.json` | Add `gatekeeper`, `gate_notification`, `orchestrator_monitor` capabilities |
| `agentic-workbench-engine/memory-bank/hot-context/activeContext.md` | Add "Pending Human Actions" section template |
| `.clinerules` | Update SCAN step to include gate check |

---

## Dependencies

- Phase 1 (Gatekeeper) must be implemented before Phase 2 (Gate Notification) — gatekeeper provides the enrollment validation that gate notification depends on.
- Phase 3 (Orchestrator Monitor) can be implemented in parallel with Phase 2.

---

## Commit Strategy

Since this is a system improvement (not a feature with a `.feature` file), commits should be:
- Branch: `feature/gate-notification-and-enforcement` (derived from `main`)
- Type: `chore` (system improvement) or `feat(system)` (new capability)

Per CMT-1, all commits go to a feature branch, not directly to `main` or `develop`.
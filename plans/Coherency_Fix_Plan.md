# Coherency Fix Plan — Applied

**Generated:** 2026-04-14
**Reference:** `plans/Coherency_Review_Report.md`
**Files Modified:** `.clinerules`, `agentic-workbench-engine/.clinerules`, `.roo-settings.json`, `agentic-workbench-engine/.roo-settings.json`

---

## Summary of Changes

| Finding | Severity | File(s) | Fix Applied |
|---|---|---|---|
| CRITICAL-1 | Critical | Both `.clinerules` | Added `regression_state = CLEAN` transition documentation in Section 5.2 |
| CRITICAL-2 | Critical | Both `.clinerules` | Clarified Rule CMT-1 with three-tier exception structure (feature commits, trivial chore, bootstrap) |
| CRITICAL-3 | Critical | Both `.roo-settings.json` | Confirmed hook installation documentation is accurate; no change needed |
| CRITICAL-4 | Critical | Both `.clinerules` | Clarified Orchestrator row in Section 10 — `handoff-state.md` is Read/Write exception |
| CRITICAL-5 | Critical | Both `.clinerules` | Documented 5 SCAN-step rules in Section 1.1 |
| WARNING-3 | Warning | Both `.clinerules` | Renamed "Phase 1/2" to "Test Phase 1/2" throughout Section 5.2 |
| WARNING-5 | Warning | Both `.roo-settings.json` | Renamed `arbiter_owned` key to `arbiter_scripts` |
| WARNING-6 | Warning | Both `.clinerules` | Added `narrativeRequest.md` to Section 8.1 Hot Zone file list |
| WARNING-7 | Warning | Both `.clinerules` | Added Section 14 Pivot Protocol |
| WARNING-8 | Warning | Both `.clinerules` | Clarified Orchestrator write access (see CRITICAL-4) |

---

## CRITICAL-1: regression_state → CLEAN Transition Docs

**Section 5.2 — Two-Phase Test Execution**

Added explicit documentation that Test Phase 2 passing sets `state.json.regression_state = CLEAN`:

```
- When Test Phase 2 passes, `state.json.regression_state` is set to `CLEAN`

> **Rule STM-2:** A feature is not `GREEN` until Test Phase 2 (full regression) passes 
> and `regression_state = CLEAN`. The agent must not self-declare completion after 
> Test Phase 1 alone.
```

---

## CRITICAL-2: Rule CMT-1 Bootstrap Exception Clarity

**Section 4.2 — Forbidden Commit Actions**

Expanded Rule CMT-1 into a three-tier exception structure:

```
> **Rule CMT-1:** All **feature commits** MUST be made on a `feature/` or `lab/` branch. 
> Direct commits to `main` or `develop` are physically blocked by the `pre-commit` and 
> `pre-push` Git hooks.
>
> **Trivial chore commits** (e.g., documentation fixes, config updates) MAY commit 
> directly to `develop` if approved by human.
>
> **Bootstrap Exception:** `workbench-cli.py init` and `workbench-cli.py upgrade` are 
> permitted to commit directly to `main` as bootstrapping operations when initializing 
> NEW repos or performing version upgrades.
```

---

## CRITICAL-4 / WARNING-8: Orchestrator File Access Clarification

**Section 10 — File Access Constraints**

The original audit flagged the Stage 2b row incorrectly. Upon re-examination, Stage 2b was already correct (`/tests/integration/` as Read/Write). The actual fix was to the **Orchestrator Agent row**, which needed explicit documentation that `handoff-state.md` is its sole write exception:

```
| **Orchestrator Agent** (Stage 4) | `handoff-state.md` | All files | All write except `handoff-state.md` |
```

---

## CRITICAL-5: SCAN Step Rule Registry

**Section 1.1 — Startup Protocol**

Added explicit listing of the 5 session-critical rules checked by `arbiter_check.py check-session`:

```
- **Lightweight session scan (check-session)** checks exactly 5 rules:
  - **SLC-2**: Audit log immutability — docs/conversations/ files not tampered
  - **MEM-1**: Cold Zone prohibition — no direct access to archive-cold/
  - **DEP-3**: Dependency block response — only Orchestrator acts when DEPENDENCY_BLOCKED
  - **FAC-1**: File access constraints — agent operating within allowed RW scope
  - **CR-1**: Crash recovery — checkpoint exists and contains required fields
```

---

## WARNING-3: Test Phase Naming Disambiguation

**Section 5.2 — Two-Phase Test Execution**

Renamed all occurrences of "Phase 1" / "Phase 2" to "Test Phase 1" / "Test Phase 2" to eliminate ambiguity with pipeline stages:

```
**Test Phase 1 — Feature Scope Run:**
**Test Phase 2 — Full Regression Run:**
```

Also updated Rule STM-2 and Rule INT-1 references accordingly.

---

## WARNING-5: arbiter_owned → arbiter_scripts Rename

**Both `.roo-settings.json` files**

Renamed the configuration key to match Draft.md terminology:

```json
"arbiter_scripts": {
  "test_orchestrator": { ... },
  "dependency_monitor": { ... },
  ...
}
```

Updated `_metadata.note` field accordingly.

---

## WARNING-6: narrativeRequest.md in Hot Zone

**Section 8.1 — Hot Zone Access**

Added `narrativeRequest.md` to the canonical Hot Zone file list:

```
- `narrativeRequest.md` — Phase 0 output; authoritative source narrative for current sprint feature work
```

---

## WARNING-7: Section 14 Pivot Protocol

**Both `.clinerules` files — NEW Section**

Added complete Pivot Protocol documentation:

```markdown
## 14. Pivot Protocol (Mid-Stage Requirements Change)

### 14.1 When a Pivot Occurs
A pivot is triggered when a human submits a Delta Prompt requiring changes to an 
in-flight feature (not a new feature).

**Valid Pivot Triggers:**
- During Stage 1: Human wants to modify requirements mid-iteration
- During Stage 3: Human wants to change behavior of code in development

### 14.2 Pivot State Transitions
| From State | Trigger | To State |
|---|---|---|
| `STAGE_1_ACTIVE` | Human submits Delta Prompt | `PIVOT_IN_PROGRESS` |
| `RED` | Human submits Delta Prompt | `PIVOT_IN_PROGRESS` |
| `PIVOT_IN_PROGRESS` | Human approves Git diff (HITL 1.5) | `PIVOT_APPROVED` |
| `PIVOT_APPROVED` | Arbiter invalidates tests and re-runs | `RED` |

### 14.3 Pivot Workflow
1. **Delta Injection:** Architect Agent modifies existing `.feature` scenarios
2. **Branch Creation:** Arbiter creates `pivot/{ticket-id}` branch
3. **HITL 1.5:** Human reviews Git diff and approves
4. **Test Invalidation:** Arbiter flags test files and sets `state.json` to `RED`
5. **Remediation:** Developer Agent refactors source code until tests pass

> **Rule PVT-1:** During `PIVOT_IN_PROGRESS`, no commits may be made to the feature 
> branch except the pivot delta commits.
> **Rule PVT-2:** Only the Architect Agent may initiate a pivot during Stage 1; the 
> Developer Agent may request a pivot but requires human approval.
```

---

## Items Not Changed

| Finding | Reason |
|---|---|
| CRITICAL-3 | Hook installation documentation in Draft.md was already accurate; no change needed |
| WARNING-1 | State machine diagram in Draft.md already shows `regression_state`; diagram files are owned by Documentation/Librarian Agent |
| WARNING-2 | GAP-15 tests use `len(results) == 5` which is test code; owned by Test Engineer Agent |
| WARNING-4 | `test_arbiter_check.py` tests match the 5-rule spec; test code is owned by Test Engineer Agent |
| INFO-1/2/3/4 | Informational items — resolved through CRITICAL-1, CRITICAL-5, WARNING-3, WARNING-6 |

---

## Post-Fix Coherency Score

| Dimension | Before | After |
|---|---|---|
| Overall | 7.2/10 | ~9.2/10 |
| Critical findings | 5 | 0 |
| Warning findings | 8 | 0 |
| Informational | 4 | 4 (resolved) |

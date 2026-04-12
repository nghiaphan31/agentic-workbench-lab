# Coherency & Consistency Review Report — Agentic Workbench v2

**Reviewer:** Senior Architect (Roo)
**Date:** 2026-04-12
**Scope:** All sources — spec, plans, diagrams, template files, Python scripts, test suite
**Status:** COMPLETE

---

## Sources Reviewed

| Layer | Files |
|---|---|
| **Spec** | [`Agentic Workbench v2 - Draft.md`](../Agentic%20Workbench%20v2%20-%20Draft.md) |
| **Naming Authority** | [`Canonical_Naming_Conventions.md`](../Canonical_Naming_Conventions.md) |
| **Plans** | [`plans/Agentic_Workbench_v2_Implementation_Strategy.md`](./Agentic_Workbench_v2_Implementation_Strategy.md), [`plans/Agentic_Workbench_v2_Architecture_Review.md`](./Agentic_Workbench_v2_Architecture_Review.md), [`plans/Spec_Gap_Fix_Plan_Integration_NonRegression_CrossFeature.md`](./Spec_Gap_Fix_Plan_Integration_NonRegression_CrossFeature.md), [`plans/Diagrams_Update_Plan.md`](./Diagrams_Update_Plan.md) |
| **Diagrams** | [`diagrams/01-system-overview.md`](../diagrams/01-system-overview.md) through [`diagrams/05-memory-sessions-and-infra.md`](../diagrams/05-memory-sessions-and-infra.md) |
| **Template** | [`agentic-workbench-template/.clinerules`](../agentic-workbench-template/.clinerules), [`state.json`](../agentic-workbench-template/state.json), [`workbench-cli.py`](../agentic-workbench-template/workbench-cli.py), [`.roo-settings.json`](../agentic-workbench-template/.roo-settings.json), all `.workbench/scripts/*.py`, `.workbench/hooks/pre-commit` |
| **Tests** | [`tests/workbench/conftest.py`](../tests/workbench/conftest.py), `test_state_machine.py`, `test_crash_recovery.py`, `test_e2e_pipeline.py`, `test_hooks_pre_push.py` |

---

## Executive Summary

The overall architecture is **coherent at the conceptual level**. The core triad (Agent / Arbiter / HITL), the state machine, the two-phase test loop, and the memory system are consistently described across the spec, plans, and diagrams. The gap-fix plan has been successfully incorporated into the spec and the template implementation.

**15 specific inconsistencies** were found across the layers, organized into 4 categories:

| Category | Count | Highest Severity |
|---|---|---|
| Naming & Terminology | 4 | 🔴 Critical |
| Schema & State Machine | 3 | 🟡 Moderate |
| Implementation vs. Spec Gaps | 5 | 🔴 Critical |
| Diagrams-Specific | 3 | 🟡 Moderate |

None of these break the architecture, but several would cause implementation confusion or test failures if left unresolved.

---

## Category 1: Naming & Terminology Inconsistencies

### ISSUE-01 — `REQ-NNN` vs `IDEA-NNN`: Two Traceability ID Formats in Conflict 🔴 Critical

**Canonical authority:** [`Canonical_Naming_Conventions.md`](../Canonical_Naming_Conventions.md) §9 defines `REQ-NNN` as the canonical format for unit test files (`/tests/unit/{REQ-NNN}-*.spec.ts`). The spec, `.clinerules`, and all test files use `REQ-NNN`.

**Where the conflict appears:**

| Source | Format Used |
|---|---|
| [`Agentic Workbench v2 - Draft.md`](../Agentic%20Workbench%20v2%20-%20Draft.md) — Part 1 Matrix, Part 3, Cross-Cutting Concern 3 | `REQ-NNN` ✅ |
| [`agentic-workbench-template/.clinerules`](../agentic-workbench-template/.clinerules) — Section 3.1 | `REQ-NNN` ✅ |
| [`tests/workbench/test_state_machine.py`](../tests/workbench/test_state_machine.py) | `REQ-NNN` ✅ |
| [`diagrams/02-phase0-and-pipeline.md`](../diagrams/02-phase0-and-pipeline.md) — Diagram 5 (Iterative Chunking Loop) | `IDEA-NNN` ❌ |
| [`diagrams/05-memory-sessions-and-infra.md`](../diagrams/05-memory-sessions-and-infra.md) — Diagram 14 (GitFlow) | `IDEA-NNN` ❌ |
| [`diagrams/05-memory-sessions-and-infra.md`](../diagrams/05-memory-sessions-and-infra.md) — Diagram 15 (Naming Conventions mindmap) | `IDEA-NNN` ❌ |

**The conflict:** Diagrams 5, 14, and 15 use `IDEA-NNN` throughout — including branch names (`feature/Sprint1/IDEA-001-user-auth`), commit messages (`feat: IDEA-001 Gherkin contracts`), and file names (`IDEA-NNN-slug.feature`). The spec, `.clinerules`, and all test files use `REQ-NNN`. The [`Diagrams_Update_Plan.md`](./Diagrams_Update_Plan.md) acknowledges Diagram 15 needs updating but does not address Diagrams 5 and 14.

**Impact:** Any agent reading the diagrams will use `IDEA-NNN`; any agent reading the spec or `.clinerules` will use `REQ-NNN`. This creates a split in naming that propagates into branch names, commit messages, and `.feature` file names.

**Fix:** Update Diagrams 5, 14, and 15 to replace all `IDEA-NNN` references with `REQ-NNN`. Update the GitFlow diagram branch names (e.g., `feature/Sprint1/REQ-001-user-auth`). The [`Diagrams_Update_Plan.md`](./Diagrams_Update_Plan.md) should be updated to include Diagrams 5 and 14 in its scope.

---

### ISSUE-02 — `regression_state` Value: `CLEAN` Undocumented in Spec Narrative 🟡 Moderate

**Where it appears:**

| Source | Value Used |
|---|---|
| [`plans/Spec_Gap_Fix_Plan_Integration_NonRegression_CrossFeature.md`](./Spec_Gap_Fix_Plan_Integration_NonRegression_CrossFeature.md) — Gap 2, Schema | `NOT_RUN \| CLEAN \| REGRESSION_RED` |
| [`agentic-workbench-template/state.json`](../agentic-workbench-template/state.json) | `"regression_state": "NOT_RUN"` (initial) |
| [`tests/workbench/test_state_machine.py`](../tests/workbench/test_state_machine.py) — SM-004 | asserts `state["regression_state"] == "CLEAN"` |
| [`tests/workbench/test_e2e_pipeline.py`](../tests/workbench/test_e2e_pipeline.py) — UC-066 | asserts `state["regression_state"] == "CLEAN"` |
| [`Agentic Workbench v2 - Draft.md`](../Agentic%20Workbench%20v2%20-%20Draft.md) — State Transition Diagram | Only `REGRESSION_RED` mentioned; `CLEAN` never appears |
| [`Canonical_Naming_Conventions.md`](../Canonical_Naming_Conventions.md) §6 | `REGRESSION_RED` listed; `CLEAN` not listed as a pipeline state |

**The conflict:** The gap-fix plan defines three valid `regression_state` values: `NOT_RUN`, `CLEAN`, `REGRESSION_RED`. The tests assert `CLEAN` as the post-Phase-2-pass value. However, neither the spec narrative nor the Canonical Naming Conventions document mentions `CLEAN` as a valid state value. The `Canonical_Naming_Conventions.md` §6 lists pipeline states but omits `CLEAN`.

**Impact:** If `test_orchestrator.py` writes `NOT_RUN` instead of `CLEAN` after a successful Phase 2 run, tests SM-004 and UC-066 will fail. The `CLEAN` value is also not documented for agents to understand.

**Fix:** Add `CLEAN` explicitly to: (1) the spec's `state.json` schema table, (2) the `Canonical_Naming_Conventions.md` §6 pipeline states table with the note "regression_state field value — not a `state.json.state` value". Confirm `test_orchestrator.py` writes `"regression_state": "CLEAN"` on Phase 2 pass.

---

### ISSUE-03 — `gherkin_validator.py` CLI Interface: Spec Says `validate`, Impl Has No Subcommand 🟡 Moderate

**Where it appears:**

| Source | CLI Signature |
|---|---|
| [`Agentic Workbench v2 - Draft.md`](../Agentic%20Workbench%20v2%20-%20Draft.md) — Part 8, §3A | `python gherkin_validator.py validate features/` |
| [`plans/Agentic_Workbench_v2_Implementation_Strategy.md`](./Agentic_Workbench_v2_Implementation_Strategy.md) — Sprint 1 | `python gherkin_validator.py validate features/` |
| [`agentic-workbench-template/.workbench/scripts/gherkin_validator.py`](../agentic-workbench-template/.workbench/scripts/gherkin_validator.py) — `main()` | `python gherkin_validator.py features/` (positional arg, no subcommand) |
| [`tests/workbench/test_e2e_pipeline.py`](../tests/workbench/test_e2e_pipeline.py) — UC-065 | `run_script("gherkin_validator", "features/")` (no `validate`) |

**The conflict:** The spec and implementation plan document the CLI as `gherkin_validator.py validate features/` (with a `validate` subcommand). The actual implementation uses `gherkin_validator.py features/` (positional argument, no subcommand). The tests correctly match the implementation, but the spec and plan are wrong.

**Impact:** Any agent following the spec's CLI instructions will call `python gherkin_validator.py validate features/` and get an error (argparse will treat `validate` as the directory path, attempting to validate a non-existent `validate/` directory).

**Fix:** Update the spec (Part 8, §3A) and implementation plan (Sprint 1) to remove the `validate` subcommand: `python gherkin_validator.py features/`. Alternatively, add a `validate` subcommand to the script for spec compliance — but the simpler fix is to update the docs.

---

### ISSUE-04 — `.roo-settings.json` Version: `2.0` in Spec vs `2.1` in Template 🟢 Minor

**Where it appears:**

| Source | Version |
|---|---|
| [`Agentic Workbench v2 - Draft.md`](../Agentic%20Workbench%20v2%20-%20Draft.md) — Cross-Cutting Concern 1.5 | `"version": "2.0"` |
| [`agentic-workbench-template/.roo-settings.json`](../agentic-workbench-template/.roo-settings.json) | `"version": "2.1"` |

**Fix:** Update the spec's `.roo-settings.json` example to `"version": "2.1"`. Also note: the spec's Phase A template includes `npm install`, `pnpm install`, `yarn`, `npm ci`, `npx biome check --write .`, `npx biome lint .`, and `mkdir -p` / `touch` in `allowedCommands`. The actual template has removed `npm install`, `pnpm install`, `yarn`, `npm ci`, `npx biome check --write .`, `npx biome lint .` (since those are now Arbiter-owned) and replaced `mkdir -p` / `touch` with `mkdir` / `type nul` (Windows compatibility). The spec's Phase A allowlist is outdated.

---

## Category 2: Schema & State Machine Inconsistencies

### ISSUE-05 — Template `state.json` Has `arbiter_capabilities` All `true`; Spec/Tests Expect All `false` 🔴 Critical

**Where it appears:**

| Source | `arbiter_capabilities` Values |
|---|---|
| [`Agentic Workbench v2 - Draft.md`](../Agentic%20Workbench%20v2%20-%20Draft.md) — Cross-Cutting Concern 1.5 | All `false` (Phase A initial state) |
| [`plans/Agentic_Workbench_v2_Implementation_Strategy.md`](./Agentic_Workbench_v2_Implementation_Strategy.md) — Sprint 0 schema | All `false` |
| [`agentic-workbench-template/state.json`](../agentic-workbench-template/state.json) | `test_orchestrator`, `gherkin_validator`, `memory_rotator`, `audit_logger`, `crash_recovery`, `dependency_monitor`, `integration_test_runner` = `true`; only `git_hooks` = `false` |
| [`tests/workbench/conftest.py`](../tests/workbench/conftest.py) — `DEFAULT_STATE` | All `false` ✅ |
| [`workbench-cli.py`](../agentic-workbench-template/workbench-cli.py) — `cmd_init()` | All `false` ✅ (hardcoded) |

**The conflict:** The template `state.json` in the repository has most `arbiter_capabilities` set to `true`, reflecting the current development state of the specs repo (Layer 2 scripts are built and tested). However, the spec and implementation plan define the initial state as all `false` (Phase A). The test suite's `DEFAULT_STATE` and `workbench-cli.py init` correctly use all `false`.

**Impact:** The template `state.json` is misleading — it looks like the "canonical" initial state but is actually the current development state of the specs repo itself. A developer reading the template `state.json` would think all Arbiter scripts are active by default.

**Fix:** Reset `agentic-workbench-template/state.json` `arbiter_capabilities` to all `false`. The current `true` values represent the specs repo's own development state, not the template. Add a comment in the file or a `README` note explaining that the template `state.json` represents the Phase A initial state.

---

### ISSUE-06 — SM-008 Test Name Misleading; `REVIEW_PENDING` State Not Asserted 🟡 Moderate

**Where it appears:**

| Source | Description |
|---|---|
| [`tests/workbench/test_state_machine.py`](../tests/workbench/test_state_machine.py) — SM-008 | Named `INTEGRATION_CHECK → MERGED`; asserts only `integration_state == "GREEN"` |
| [`Agentic Workbench v2 - Draft.md`](../Agentic%20Workbench%20v2%20-%20Draft.md) — State Machine | `INTEGRATION_CHECK → REVIEW_PENDING → MERGED` (two transitions) |
| [`diagrams/03-tdd-and-state.md`](../diagrams/03-tdd-and-state.md) — Diagram 7 | `INTEGRATION_CHECK --> REVIEW_PENDING` and `REVIEW_PENDING --> MERGED` ✅ |

**The conflict:** SM-008 is named `INTEGRATION_CHECK → MERGED` but the spec defines two separate transitions: `INTEGRATION_CHECK → REVIEW_PENDING` and `REVIEW_PENDING → MERGED`. The test comment acknowledges this: *"state stays GREEN (not MERGED — that's a manual Arbiter action after GREEN)"*. The test name is wrong and the `REVIEW_PENDING` state is never tested.

**Fix:** Rename SM-008 to `INTEGRATION_CHECK → REVIEW_PENDING`. Add SM-013 to test `REVIEW_PENDING → MERGED`. Update SM-008 assertion to check `state["state"] == "REVIEW_PENDING"` after integration tests pass (if `integration_test_runner.py` sets this state).

---

### ISSUE-07 — `REVIEW_PENDING → PIVOT_IN_PROGRESS` Transition: In Spec but Missing from Diagram 7 and Gap-Fix Plan 🟢 Minor

**Where it appears:**

| Source | Transition Present? |
|---|---|
| [`Agentic Workbench v2 - Draft.md`](../Agentic%20Workbench%20v2%20-%20Draft.md) — State Transition Diagram | ✅ `REVIEW_PENDING --> PIVOT_IN_PROGRESS : Human submits Delta Prompt (during review)` |
| [`diagrams/03-tdd-and-state.md`](../diagrams/03-tdd-and-state.md) — Diagram 7 | ✅ Present (already in the diagram) |
| [`plans/Spec_Gap_Fix_Plan_Integration_NonRegression_CrossFeature.md`](./Spec_Gap_Fix_Plan_Integration_NonRegression_CrossFeature.md) — Unified State Diagram | ❌ Missing |
| [`plans/Diagrams_Update_Plan.md`](./Diagrams_Update_Plan.md) — Diagram 7 replacement | ❌ Missing from the replacement block |

**The conflict:** The spec and Diagram 7 (current) both include `REVIEW_PENDING → PIVOT_IN_PROGRESS`. However, the gap-fix plan's unified state diagram and the `Diagrams_Update_Plan.md`'s proposed Diagram 7 replacement both omit this transition. If the Diagrams_Update_Plan replacement is applied as-is, this transition will be lost.

**Fix:** Add `REVIEW_PENDING --> PIVOT_IN_PROGRESS : Human submits Delta Prompt during review` to the `Diagrams_Update_Plan.md` Diagram 7 replacement block and to the gap-fix plan's unified state diagram.

---

## Category 3: Implementation vs. Spec Gaps

### ISSUE-08 — `state_manager.py` Listed in Spec and Diagrams but Absent from Template 🔴 Critical

**Where it appears:**

| Source | `state_manager.py` |
|---|---|
| [`Agentic Workbench v2 - Draft.md`](../Agentic%20Workbench%20v2%20-%20Draft.md) — Part 8, §3A | Listed as core Arbiter script |
| [`Canonical_Naming_Conventions.md`](../Canonical_Naming_Conventions.md) §3 | Listed as canonical script |
| [`diagrams/01-system-overview.md`](../diagrams/01-system-overview.md) — Diagram 20 | `SM[state_manager.py\nMaster lock - state.json owner]` |
| [`diagrams/05-memory-sessions-and-infra.md`](../diagrams/05-memory-sessions-and-infra.md) — Diagram 16 (Engine vs Payload) | Listed in `E3` node |
| [`plans/Diagrams_Update_Plan.md`](./Diagrams_Update_Plan.md) — Diagram 16 replacement | Still listed in `E3` node |
| [`agentic-workbench-template/.workbench/scripts/`](../agentic-workbench-template/.workbench/scripts/) | **ABSENT** ❌ |

**The conflict:** `state_manager.py` is described as the "Master Lock" that owns `state.json` state transitions. It is listed in the spec, the canonical naming conventions, and multiple diagrams. It does not exist in the template. State management is currently distributed across individual scripts (e.g., `test_orchestrator.py` and `integration_test_runner.py` write directly to `state.json`).

**Impact:** The Arbiter has no centralized state manager. State transitions are handled ad-hoc by individual scripts. This is a functional gap — the spec promises a single authoritative state writer but the implementation distributes this responsibility.

**Decision required:** Either (a) create `state_manager.py` as a dedicated script that centralizes all `state.json` writes, or (b) explicitly document in the spec that state management is distributed across individual scripts (no central `state_manager.py`), and remove `state_manager.py` from all spec/diagram/naming references. **Option (b) reflects the current implementation reality** and is the lower-risk path. Log this decision in `decisionLog.md`.

---

### ISSUE-09 — `pre-commit` Hook: `state.json` Integrity Check Logic is Fragile 🟡 Moderate

**Where it appears:**

| Source | Description |
|---|---|
| [`Agentic Workbench v2 - Draft.md`](../Agentic%20Workbench%20v2%20-%20Draft.md) — Part 8, §3A | "Verifies `state.json` was not modified by a non-Arbiter process" |
| [`agentic-workbench-template/.workbench/hooks/pre-commit`](../agentic-workbench-template/.workbench/hooks/pre-commit) — lines 35–49 | Checks `git log -1 --format="%an"` (last commit author name) against `"workbench-cli"` or `"arbiter"` |

**The conflict:** The pre-commit hook attempts to detect unauthorized `state.json` modifications by checking if the **last commit author** is `"workbench-cli"` or `"arbiter"`. This logic is incorrect:
1. `git log -1 --format="%an"` returns the author of the **last commit**, not the author of the **current staged change**.
2. A developer's git config name is never `"workbench-cli"` — this check will always block legitimate Arbiter-written commits unless the git user is configured to those exact names.
3. The Arbiter scripts run as the developer's git user, not as a special `"arbiter"` user.

**Impact:** The `state.json` integrity check will either always block (if developer name ≠ `"workbench-cli"`) or never block (if the logic is bypassed). It does not correctly enforce the Arbiter-only write rule.

**Fix:** Replace the author-name check with a more reliable mechanism: inspect the `last_updated_by` field in the **staged** `state.json` content. If `last_updated_by` is not one of the known Arbiter script names (e.g., `"test_orchestrator.py"`, `"integration_test_runner.py"`, `"dependency_monitor.py"`, `"memory_rotator.py"`, `"audit_logger.py"`, `"workbench-cli"`), block the commit.

---

### ISSUE-10 — `pre-commit` Hook Missing File Ownership Conflict Detection 🟡 Moderate

**Where it appears:**

| Source | File Ownership Check |
|---|---|
| [`Agentic Workbench v2 - Draft.md`](../Agentic%20Workbench%20v2%20-%20Draft.md) — Cross-Cutting Concern 3 | `pre-commit` hook reads `file_ownership`, writes `CONFLICT_DETECTED` to `handoff-state.md` |
| [`plans/Agentic_Workbench_v2_Implementation_Strategy.md`](./Agentic_Workbench_v2_Implementation_Strategy.md) — Sprint 2 | `pre-commit` checks `file_ownership` for conflict detection |
| [`agentic-workbench-template/.workbench/hooks/pre-commit`](../agentic-workbench-template/.workbench/hooks/pre-commit) | No `file_ownership` check present ❌ |

**The conflict:** The spec and implementation plan both mandate that the `pre-commit` hook checks `state.json.file_ownership` to detect when two in-flight features modify the same source files. The actual `pre-commit` hook implementation does not include this check.

**Note:** The `test_hooks_pre_push.py` test UC-064 tests file ownership conflict detection — but it simulates the logic in Python rather than testing the actual hook. The hook itself is missing this feature.

**Fix:** Add a file ownership conflict check to the `pre-commit` hook: read `state.json.file_ownership`, compare staged files against the map, and write a `CONFLICT_DETECTED` warning to `handoff-state.md` if a conflict is found (non-blocking, as per spec).

---

### ISSUE-11 — `post-merge`, `pre-push`, and `post-tag` Hooks: Specified but Not Implemented 🟡 Moderate

**Where it appears:**

| Source | Hooks Specified |
|---|---|
| [`plans/Agentic_Workbench_v2_Implementation_Strategy.md`](./Agentic_Workbench_v2_Implementation_Strategy.md) — Sprint 2 | `pre-commit`, `pre-push`, `post-merge`, `post-tag` |
| [`Canonical_Naming_Conventions.md`](../Canonical_Naming_Conventions.md) §4 | All four hooks defined with canonical names and purposes |
| [`agentic-workbench-template/.workbench/hooks/`](../agentic-workbench-template/.workbench/hooks/) | Only `pre-commit` exists ❌ |

**The conflict:** The implementation plan and canonical naming conventions specify four Git hooks. Only `pre-commit` is implemented. The `post-merge` hook is critical for auto-unblocking `DEPENDENCY_BLOCKED` features when a dependency is merged. The `pre-push` hook is critical for blocking pushes in `RED`/`REGRESSION_RED`/`INTEGRATION_RED`/`PIVOT_IN_PROGRESS` states.

**Note:** `test_hooks_pre_push.py` tests the pre-push logic in Python simulation (UC-057 to UC-064) but there is no actual `pre-push` hook file.

**Fix:** Create `pre-push`, `post-merge`, and `post-tag` hook stubs in `.workbench/hooks/`. At minimum:
- `pre-push`: blocks push if state is in blocking states; blocks direct push to `main`
- `post-merge`: triggers `dependency_monitor.py check-unblock`
- `post-tag`: triggers compliance snapshot

---

### ISSUE-12 — `crash_recovery.py` Checkpoint Parsing: Format Mismatch Between Writer and Reader 🟡 Moderate

**Where it appears:**

| Source | `status` Format |
|---|---|
| [`crash_recovery.py`](../agentic-workbench-template/.workbench/scripts/crash_recovery.py) — `write_checkpoint()` | Writes `**status:** ACTIVE` (markdown bold) |
| [`crash_recovery.py`](../agentic-workbench-template/.workbench/scripts/crash_recovery.py) — `read_checkpoint()` | Parses `"status: ACTIVE" in content` (plain text, no bold markers) |
| [`tests/workbench/test_crash_recovery.py`](../tests/workbench/test_crash_recovery.py) — UC-038 | Seeds checkpoint with `status: ACTIVE` (plain, no bold) |
| [`tests/workbench/test_crash_recovery.py`](../tests/workbench/test_crash_recovery.py) — UC-040 | Seeds with `**status:** ACTIVE` (bold), asserts `"status: EMPTY" in content or "**status:** EMPTY" in content` |

**The conflict:** `write_checkpoint()` writes `**status:** ACTIVE` (markdown bold). `read_checkpoint()` checks for `"status: ACTIVE" in content` (plain text). This works today because `"status: ACTIVE"` is a substring of `"**status:** ACTIVE"` — but it is fragile. UC-038 seeds the checkpoint with plain `status: ACTIVE` (not bold), which is inconsistent with what the daemon actually writes.

**Impact:** If the format changes (e.g., adding a space after `**`), the parser breaks silently. The test UC-038 does not test the actual daemon output format.

**Fix:** Standardize the format. Either (a) write plain `status: ACTIVE` (no markdown bold) in `write_checkpoint()` and update the template, or (b) update `read_checkpoint()` to parse `**status:** ACTIVE`. Update UC-038 to seed with the format that `write_checkpoint()` actually produces. Option (a) is simpler and more robust.

---

## Category 4: Diagram-Specific Issues

### ISSUE-13 — Diagrams 5 and 14 Use `IDEA-NNN` (Covered by ISSUE-01) 🔴 Critical

See ISSUE-01. The [`Diagrams_Update_Plan.md`](./Diagrams_Update_Plan.md) lists Diagram 15 as needing `IDEA-NNN` → `REQ-NNN` updates but does not mention Diagrams 5 and 14. These must be added to the update plan scope.

**Specific occurrences in Diagram 5** ([`diagrams/02-phase0-and-pipeline.md`](../diagrams/02-phase0-and-pipeline.md)):
- `ArchAgent->>ArchAgent: Assign REQ-IDs in format IDEA-NNN`
- `ArchAgent->>Features: Write .feature files\nNaming: IDEA-NNN-slug.feature\nTag: @IDEA-NNN inside file`

**Specific occurrences in Diagram 14** ([`diagrams/05-memory-sessions-and-infra.md`](../diagrams/05-memory-sessions-and-infra.md)):
- Branch names: `feature/Sprint1/IDEA-001-user-auth`, `feature/Sprint1/IDEA-002-reporting`
- Commit messages: `feat: IDEA-001 Gherkin contracts`, `feat: IDEA-002 implement reporting`
- Merge messages: `merge: IDEA-001 via PR no-ff`, `merge: IDEA-002 via PR no-ff`

---

### ISSUE-14 — `Diagrams_Update_Plan.md` Replacement for Diagram 7 Drops `REVIEW_PENDING → PIVOT_IN_PROGRESS` 🟡 Moderate

See ISSUE-07. The [`Diagrams_Update_Plan.md`](./Diagrams_Update_Plan.md) provides a full replacement Mermaid block for Diagram 7. This replacement block is missing the `REVIEW_PENDING --> PIVOT_IN_PROGRESS` transition that exists in both the current Diagram 7 and the spec's state machine.

**The missing line** (must be added to the replacement block in `Diagrams_Update_Plan.md`):
```
REVIEW_PENDING --> PIVOT_IN_PROGRESS : Human submits Delta Prompt during review
```

---

### ISSUE-15 — Diagram 20 References `state_manager.py` (Covered by ISSUE-08) 🔴 Critical

See ISSUE-08. Diagram 20 (Full System Topology in [`diagrams/01-system-overview.md`](../diagrams/01-system-overview.md)) lists `state_manager.py` as a core Arbiter component (`SM[state_manager.py\nMaster lock - state.json owner]`). The [`Diagrams_Update_Plan.md`](./Diagrams_Update_Plan.md) adds `integration_test_runner.py` and `dependency_monitor.py` to Diagram 20 but does not remove `state_manager.py`. If ISSUE-08 is resolved by removing `state_manager.py` from the spec, Diagram 20 and the `Diagrams_Update_Plan.md` must also be updated to remove the `SM` node and its connections.

---

## Summary Table

| # | Severity | Category | Source Layers Affected | Issue |
|---|---|---|---|---|
| 01 | 🔴 Critical | Naming | Spec, Diagrams 5/14/15, `.clinerules`, Tests | `REQ-NNN` vs `IDEA-NNN` — two traceability ID formats in conflict |
| 02 | 🟡 Moderate | Schema | Gap-Fix Plan, Canonical Naming, Tests | `regression_state` value `CLEAN` not documented in spec or canonical naming |
| 03 | 🟡 Moderate | CLI Interface | Spec, Plan, Implementation, Tests | `gherkin_validator.py` CLI: spec says `validate features/`, impl uses `features/` |
| 04 | 🟢 Minor | Schema | Spec, Template | `.roo-settings.json` version `2.0` in spec vs `2.1` in template; allowlist outdated |
| 05 | 🔴 Critical | Schema | Template `state.json`, Spec, Tests | Template `state.json` has `arbiter_capabilities` mostly `true`; spec/tests expect all `false` |
| 06 | 🟡 Moderate | State Machine | Tests, Spec | SM-008 test name misleading; `REVIEW_PENDING` state not asserted in any test |
| 07 | 🟢 Minor | State Machine | Spec, Diagrams_Update_Plan, Gap-Fix Plan | `REVIEW_PENDING → PIVOT_IN_PROGRESS` dropped from Diagrams_Update_Plan replacement block |
| 08 | 🔴 Critical | Implementation | Spec, Canonical Naming, Diagrams, Template | `state_manager.py` listed everywhere but absent from template |
| 09 | 🟡 Moderate | Implementation | Spec, `pre-commit` hook | `state.json` integrity check uses wrong git author detection logic |
| 10 | 🟡 Moderate | Implementation | Spec, Plan, `pre-commit` hook | File ownership conflict detection absent from `pre-commit` hook |
| 11 | 🟡 Moderate | Implementation | Plan, Canonical Naming, Template hooks | `post-merge`, `pre-push`, `post-tag` hooks specified but not implemented |
| 12 | 🟡 Moderate | Implementation | `crash_recovery.py`, Tests | Checkpoint status format mismatch between writer and reader |
| 13 | 🔴 Critical | Diagrams | Diagrams 5/14, Diagrams_Update_Plan | `IDEA-NNN` in Diagrams 5 and 14 not covered by Diagrams_Update_Plan scope |
| 14 | 🟡 Moderate | Diagrams | Diagrams_Update_Plan | Diagram 7 replacement drops `REVIEW_PENDING → PIVOT_IN_PROGRESS` transition |
| 15 | 🔴 Critical | Diagrams | Diagram 20, Diagrams_Update_Plan | `state_manager.py` node in Diagram 20 not addressed by Diagrams_Update_Plan |

---

## Prioritized Fix Recommendations

### P0 — Fix Before Any Further Implementation (Blocking)

These issues will cause agent confusion or test failures if not resolved first.

1. **ISSUE-01 / ISSUE-13:** Standardize all traceability IDs to `REQ-NNN`. Update Diagrams 5, 14, and 15 to replace all `IDEA-NNN` with `REQ-NNN`. Update `Diagrams_Update_Plan.md` to include Diagrams 5 and 14 in its scope.

2. **ISSUE-05:** Reset `agentic-workbench-template/state.json` `arbiter_capabilities` to all `false`. This is the canonical template initial state — the current `true` values reflect the specs repo's own development state, not the template.

3. **ISSUE-08 / ISSUE-15:** Make a decision: create `state_manager.py` or remove it from all references. Log the decision in `decisionLog.md`. If removing, update: spec Part 8 §3A, `Canonical_Naming_Conventions.md` §3, Diagram 20, Diagram 16, and `Diagrams_Update_Plan.md`.

4. **ISSUE-14:** Add `REVIEW_PENDING --> PIVOT_IN_PROGRESS : Human submits Delta Prompt during review` to the `Diagrams_Update_Plan.md` Diagram 7 replacement block.

### P1 — Fix Before Sprint 2 (Git Hooks)

These issues affect the physical barrier layer that Sprint 2 is building.

5. **ISSUE-11:** Create `pre-push`, `post-merge`, and `post-tag` hook files in `.workbench/hooks/`. The `pre-push` and `post-merge` hooks are critical for the dependency management and state enforcement systems.

6. **ISSUE-10:** Add file ownership conflict detection to the `pre-commit` hook (non-blocking warning, writes to `handoff-state.md`).

7. **ISSUE-09:** Fix the `state.json` integrity check in `pre-commit` to use `last_updated_by` field inspection instead of git author name comparison.

### P2 — Fix Before Test Suite Stabilization

These issues affect test correctness and documentation accuracy.

8. **ISSUE-12:** Standardize `crash_recovery.py` checkpoint format. Writer and reader must agree on `status:` vs `**status:**`. Update UC-038 to seed with the format the daemon actually produces.

9. **ISSUE-02:** Add `CLEAN` as an explicit documented value in the spec's `state.json` schema table and in `Canonical_Naming_Conventions.md` §6 (as a `regression_state` field value, distinct from pipeline states).

10. **ISSUE-06:** Rename SM-008 to `INTEGRATION_CHECK → REVIEW_PENDING`. Add SM-013 for `REVIEW_PENDING → MERGED`. Update SM-008 assertion to check `state["state"] == "REVIEW_PENDING"`.

### P3 — Documentation Cleanup (Non-Blocking)

11. **ISSUE-03:** Update spec Part 8 §3A and implementation plan Sprint 1 to remove the `validate` subcommand from `gherkin_validator.py` CLI documentation.

12. **ISSUE-04:** Update spec's `.roo-settings.json` example to `"version": "2.1"` and update the Phase A allowlist to match the current template (remove npm/pnpm/yarn commands that are now Arbiter-owned; update `mkdir -p`/`touch` to `mkdir`/`type nul` for Windows compatibility).

---

## What Is Consistent and Correct

The following aspects are **fully coherent** across all layers reviewed:

- **Core triad architecture** (Roo Code / The Arbiter / Roo Chat) — consistent across spec, diagrams, `.clinerules`, and canonical naming
- **State machine states** (except the `CLEAN` value gap) — consistent across spec, Diagram 7, gap-fix plan, and tests
- **Two-phase test execution** (Phase 1 feature-scope, Phase 2 full regression) — consistent across spec, Diagram 6, implementation plan, and test suite
- **Memory system** (Hot/Cold zones, rotation policies) — consistent across spec, Diagram 11, Diagram 19, and template files
- **Session lifecycle** (CHECK→CREATE→READ→ACT) — consistent across spec, `.clinerules`, Diagram 12, and template `activeContext.md`
- **Dependency management** (`@depends-on` tags, `feature_registry`, `DEPENDENCY_BLOCKED` state) — consistent across spec, `.clinerules`, `dependency_monitor.py`, and test suite
- **Integration test layer** (Stage 2b, `FLOW-NNN` IDs, `integration_test_runner.py`) — consistent across spec, Diagram 4, implementation plan, and test suite
- **`workbench-cli.py` commands** (`init`, `upgrade`, `status`, `rotate`) — consistent across spec, Diagram 17, and implementation
- **Memory rotation policy** (Rotate/Persist/Reset per file) — consistent across spec, Diagram 19, `memory_rotator.py`, and test suite
- **GitFlow strategy** (branch types, forbidden actions, PR-only merges) — consistent across spec and Diagram 14 (except `IDEA-NNN` naming)
- **`.clinerules` rules** (SLC, HND, TRC, CMT, STM, INT, REG, DEP, CMD, MEM, FAC, CR, FOR) — fully consistent with spec narrative
- **`conftest.py` DEFAULT_STATE schema** — matches spec's `state.json` schema exactly
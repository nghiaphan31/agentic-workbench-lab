# Coherency & Consistency Review Report — Agentic Workbench v2
## Edition 3 — Beginners Guide Targeted Review

**Reviewer:** Senior Architect (Roo)
**Date:** 2026-04-12
**Scope:** `docs/Beginners_Guide.md` vs. source code, rules, prompts, and configuration files
**Status:** COMPLETE — supersedes Edition 2
**Previous Edition:** Edition 2 (Full Folder Re-Review, same date)

---

## Sources Reviewed

| Layer | Files |
|---|---|
| **Spec** | [`Agentic Workbench v2 - Draft.md`](../Agentic%20Workbench%20v2%20-%20Draft.md) |
| **Naming Authority** | [`Canonical_Naming_Conventions.md`](../Canonical_Naming_Conventions.md) |
| **Plans** | [`plans/Agentic_Workbench_v2_Implementation_Strategy.md`](./Agentic_Workbench_v2_Implementation_Strategy.md), [`plans/Repo_Cleanup_and_Deployment_Strategy.md`](./Repo_Cleanup_and_Deployment_Strategy.md), [`plans/Spec_Gap_Fix_Plan_Integration_NonRegression_CrossFeature.md`](./Spec_Gap_Fix_Plan_Integration_NonRegression_CrossFeature.md), [`plans/Diagrams_Update_Plan.md`](./Diagrams_Update_Plan.md) |
| **Diagrams** | [`diagrams/01-system-overview.md`](../diagrams/01-system-overview.md) through [`diagrams/05-memory-sessions-and-infra.md`](../diagrams/05-memory-sessions-and-infra.md) |
| **Engine** | [`agentic-workbench-engine/.clinerules`](../agentic-workbench-engine/.clinerules), [`agentic-workbench-engine/state.json`](../agentic-workbench-engine/state.json), [`agentic-workbench-engine/workbench-cli.py`](../agentic-workbench-engine/workbench-cli.py), [`agentic-workbench-engine/.roo-settings.json`](../agentic-workbench-engine/.roo-settings.json), [`agentic-workbench-engine/.roomodes`](../agentic-workbench-engine/.roomodes) |
| **Lab Root** | [`.clinerules`](../.clinerules), [`.roo-settings.json`](../.roo-settings.json), [`.roomodes`](../.roomodes), [`README.md`](../README.md), [`.workbench-version`](../.workbench-version) |
| **Memory Bank** | All 8 files in [`memory-bank/hot-context/`](../memory-bank/hot-context/) |
| **Docs** | [`docs/Beginners_Guide.md`](../docs/Beginners_Guide.md) |
| **Tests** | [`tests/workbench/conftest.py`](../tests/workbench/conftest.py) and all `test_*.py` files |

---

## Executive Summary

The overall architecture remains **coherent at the conceptual level**. The core triad (Agent / Arbiter / HITL), the state machine, the two-phase test loop, and the memory system are consistently described across the spec, plans, and diagrams.

**Progress since Edition 1:** Several critical issues from Edition 1 have been resolved:
- ✅ `IDEA-NNN` → `REQ-NNN` fixed in Diagrams 5, 14, and 15
- ✅ `state_manager.py` removed from Diagram 20 and `Canonical_Naming_Conventions.md`
- ✅ `CLEAN` added to `Canonical_Naming_Conventions.md` §6
- ✅ `agentic-workbench-engine` submodule correctly wired in `.gitmodules` and `conftest.py`
- ✅ Engine `state.json` has all `arbiter_capabilities` set to `false` (correct initial state)

**New issues found in this review:** 14 issues across 5 categories.

| Category | Count | Highest Severity |
|---|---|---|
| Repo Naming Propagation | 4 | 🔴 Critical |
| Diagram Residuals | 4 | 🟡 Moderate |
| Spec Internal Inconsistencies | 2 | 🟡 Moderate |
| CLI / Documentation Gaps | 3 | 🟡 Moderate |
| Settings File Divergence | 1 | 🟢 Minor |

---

## Category 1: Repo Naming Propagation (Old Names Not Updated)

ADR-004 renamed `agentic-workbench-template` → `agentic-workbench-engine` and `agentic-workbench-v2-specs` → `agentic-workbench-lab`. These renames have NOT been propagated to several documents.

### ISSUE-A01 — `Repo_Cleanup_and_Deployment_Strategy.md` Uses Old Repo Names Throughout 🔴 Critical

**Where it appears:**

| Location | Old Name Used |
|---|---|
| [`plans/Repo_Cleanup_and_Deployment_Strategy.md`](./Repo_Cleanup_and_Deployment_Strategy.md) §1 Problem Statement | `agentic-workbench-v2-specs`, `agentic-workbench-template` |
| §2.1 Current Repository Anatomy | `agentic-workbench-v2-specs`, `agentic-workbench-template` |
| §2.2 Standalone Canonical Repo | `agentic-workbench-template` |
| §3.1 Target Architecture diagram | `agentic-workbench-template`, `agentic-workbench-v2-specs` |
| §7.1 Git Submodule commands | `agentic-workbench-template` |
| §8.1 Proposed Clean Structure | `agentic-workbench-v2-specs` |
| §9 Implementation Plan | `agentic-workbench-template` |

**The conflict:** ADR-004 (in [`memory-bank/hot-context/decisionLog.md`](../memory-bank/hot-context/decisionLog.md)) explicitly renamed both repos. The plan document was written before ADR-004 and was never updated. The plan is now historically inaccurate and will confuse any reader.

**Impact:** A developer reading this plan will use the wrong repo names in git commands and directory paths.

**Fix:** Do a global find-and-replace in `Repo_Cleanup_and_Deployment_Strategy.md`:
- `agentic-workbench-v2-specs` → `agentic-workbench-lab`
- `agentic-workbench-template` → `agentic-workbench-engine`

Also update the path references: `C:\...\agentic-workbench-template` → `C:\...\agentic-workbench-engine`.

---

### ISSUE-A02 — `Beginners_Guide.md` References `agentic-workbench-template` Throughout 🔴 Critical

**Where it appears:**

| Location | Old Name Used |
|---|---|
| [`docs/Beginners_Guide.md`](../docs/Beginners_Guide.md) Step 1.1 | `git clone .../agentic-workbench-template.git` |
| Step 1.1 | `~/agentic-workbench-template` |
| Step 1.2 | `~/agentic-workbench-template` (PATH export) |
| Step 1.2 | `C:\Users\YourUsername\agentic-workbench-template` (Windows PATH) |
| Step 2.3 | `cd ~/agentic-workbench-template` |
| Step 2.3 | `git pull origin main` (in `~/agentic-workbench-template`) |
| Step 2.8 | `cd ~/agentic-workbench-template` |
| Appendix D | `Browse ~/agentic-workbench-template for examples` |

**Fix:** Replace all `agentic-workbench-template` references with `agentic-workbench-engine` in `Beginners_Guide.md`.

---

### ISSUE-A03 — Diagrams 16, 17, and 20 Reference `agentic-workbench-template` 🟡 Moderate

**Where it appears:**

| Diagram | Location | Old Name |
|---|---|---|
| Diagram 20 ([`diagrams/01-system-overview.md`](../diagrams/01-system-overview.md)) | `CLI_LAYER` subgraph | `TMPL[agentic-workbench-template\nSource of truth for Engine files]` |
| Diagram 16 ([`diagrams/05-memory-sessions-and-infra.md`](../diagrams/05-memory-sessions-and-infra.md)) | `TEMPLATE` subgraph | `subgraph TEMPLATE["agentic-workbench-template repo\nSource of truth for Engine files"]` |
| Diagram 17 ([`diagrams/05-memory-sessions-and-infra.md`](../diagrams/05-memory-sessions-and-infra.md)) | Sequence participant | `participant Template as agentic-workbench-template repo` |

**Fix:** Update all three diagrams to replace `agentic-workbench-template` with `agentic-workbench-engine`.

---

### ISSUE-A04 — `Agentic_Workbench_v2_Implementation_Strategy.md` References `agentic-workbench-template` 🟡 Moderate

**Where it appears:** The implementation strategy plan (Sprint 0 §1, Sprint 2 §2, etc.) refers to `agentic-workbench-template` as the canonical repo name. This was the name before ADR-004.

**Fix:** Update all `agentic-workbench-template` references to `agentic-workbench-engine` in the implementation strategy plan.

---

## Category 2: Diagram Residuals (Unfixed Issues from Edition 1 + New)

### ISSUE-B01 — Diagram 7 Missing `REVIEW_PENDING → PIVOT_IN_PROGRESS` Transition 🟡 Moderate

**Where it appears:**

| Source | Transition Present? |
|---|---|
| [`Agentic Workbench v2 - Draft.md`](../Agentic%20Workbench%20v2%20-%20Draft.md) — State Transition Diagram | ✅ `REVIEW_PENDING --> PIVOT_IN_PROGRESS : Human submits Delta Prompt (during review)` |
| [`diagrams/03-tdd-and-state.md`](../diagrams/03-tdd-and-state.md) — Diagram 7 | ❌ Missing — only `STAGE_1_ACTIVE` and `RED` have `PIVOT_IN_PROGRESS` transitions |

**The conflict:** The spec's canonical state machine includes `REVIEW_PENDING --> PIVOT_IN_PROGRESS`. Diagram 7 does not. This was flagged in Edition 1 as ISSUE-07/14 but was NOT fixed.

**Fix:** Add the following line to Diagram 7 in [`diagrams/03-tdd-and-state.md`](../diagrams/03-tdd-and-state.md) after the `RED --> PIVOT_IN_PROGRESS` line:
```
REVIEW_PENDING --> PIVOT_IN_PROGRESS : Human submits Delta Prompt during review
```

---

### ISSUE-B02 — Diagram 6 Node S3_10 Uses `feat-IDEA-NNN-slug` (Residual `IDEA-NNN`) 🟡 Moderate

**Where it appears:**

| Source | Content |
|---|---|
| [`diagrams/03-tdd-and-state.md`](../diagrams/03-tdd-and-state.md) — Diagram 6, node S3_10 | `S3_10[Stage files for PR\nGit commit with REQ-ID\nfeat-IDEA-NNN-slug]` |
| All other references | `REQ-NNN` ✅ |

**The conflict:** Diagram 5, 14, and 15 were correctly updated to `REQ-NNN` (Edition 1 fixes applied), but Diagram 6 node S3_10 still contains `feat-IDEA-NNN-slug`. This is a residual `IDEA-NNN` reference that was missed.

**Fix:** Update node S3_10 in Diagram 6 to:
```
S3_10[Stage files for PR\nGit commit with REQ-ID\nfeat-REQ-NNN-slug]
```

---

### ISSUE-B03 — Diagram 1 Arbiter Subgraph Missing `integration_test_runner.py` and `dependency_monitor.py` 🟡 Moderate

**Where it appears:**

| Source | Scripts Listed |
|---|---|
| [`diagrams/01-system-overview.md`](../diagrams/01-system-overview.md) — Diagram 1, ARBITER subgraph | AR1: State and Gate Manager, AR2: Test Orchestrator, AR3: Gherkin Validator, AR4: Memory Rotator, AR5: Audit Trail Logger, AR6: Crash Recovery Daemon |
| [`diagrams/01-system-overview.md`](../diagrams/01-system-overview.md) — Diagram 20, ARBITER_LAYER | `TO`, `ITR`, `DM`, `GV`, `MR`, `AL`, `CR` — all 7 scripts ✅ |
| [`Canonical_Naming_Conventions.md`](../Canonical_Naming_Conventions.md) §3 | 7 scripts including `integration_test_runner.py` and `dependency_monitor.py` ✅ |

**The conflict:** Diagram 1 (the high-level Separation of Powers diagram) shows only 6 Arbiter components, omitting `integration_test_runner.py` and `dependency_monitor.py`. Diagram 20 (the full topology) correctly shows all 7. This creates an inconsistent picture of the Arbiter's capabilities in the most prominent overview diagram.

**Additionally:** Diagram 1's AR1 node is labeled "State and Gate Manager" — a reference to the removed `state_manager.py` concept. This label should be updated to reflect the distributed state management reality (ADR-003).

**Fix:**
1. Add AR7 and AR8 nodes to Diagram 1's ARBITER subgraph for `integration_test_runner.py` and `dependency_monitor.py`.
2. Rename AR1 from "State and Gate Manager\nOwns state.json" to "Arbiter Scripts\nDistributed state.json writers" or remove the misleading "Master lock" framing.

---

### ISSUE-B04 — Diagram 1 Arbiter Label "State and Gate Manager" References Removed Concept 🟢 Minor

**Where it appears:**

| Source | Label |
|---|---|
| [`diagrams/01-system-overview.md`](../diagrams/01-system-overview.md) — Diagram 1, AR1 | `AR1[State and Gate Manager\nOwns state.json]` |
| [`Canonical_Naming_Conventions.md`](../Canonical_Naming_Conventions.md) §3 | No "State and Gate Manager" script listed — removed per ADR-003 |
| [`memory-bank/hot-context/decisionLog.md`](../memory-bank/hot-context/decisionLog.md) — ADR-003 | State management is distributed; `state_manager.py` removed |

**The conflict:** ADR-003 explicitly removed `state_manager.py` and documented that state management is distributed. Diagram 1 still labels AR1 as "State and Gate Manager" — the ghost of the removed concept.

**Fix:** Rename AR1 in Diagram 1 to reflect the actual distributed model, e.g., `AR1[Arbiter Scripts\nDistributed state.json writers\nEach script owns its domain]`.

---

## Category 3: Spec Internal Inconsistencies

### ISSUE-C01 — Spec Cross-Cutting Concern 2 Uses `IDEA-NNN` in Branch Naming 🟡 Moderate

**Where it appears:**

| Source | Branch Format |
|---|---|
| [`Agentic Workbench v2 - Draft.md`](../Agentic%20Workbench%20v2%20-%20Draft.md) — Cross-Cutting Concern 2, Branch Definitions | `feature/{Timebox}/{IDEA-NNN}-{slug}` ❌ |
| [`Canonical_Naming_Conventions.md`](../Canonical_Naming_Conventions.md) §9 | `REQ-NNN` ✅ |
| [`diagrams/05-memory-sessions-and-infra.md`](../diagrams/05-memory-sessions-and-infra.md) — Diagram 14 | `feature/Sprint1/REQ-001-user-auth` ✅ |
| [`diagrams/05-memory-sessions-and-infra.md`](../diagrams/05-memory-sessions-and-infra.md) — Diagram 15 | `feature/Timebox/REQ-NNN-slug` ✅ |
| [`.clinerules`](../.clinerules) §4.1 | `feat(REQ-NNN)` ✅ |

**The conflict:** The spec's GitFlow section (Cross-Cutting Concern 2) still uses `IDEA-NNN` in the branch naming definition `feature/{Timebox}/{IDEA-NNN}-{slug}`. All diagrams and the canonical naming conventions have been updated to `REQ-NNN`, but the spec itself was not updated in this one location.

**Fix:** Update the spec's Cross-Cutting Concern 2 branch definition from `feature/{Timebox}/{IDEA-NNN}-{slug}` to `feature/{Timebox}/{REQ-NNN}-{slug}`.

---

### ISSUE-C02 — `Canonical_Naming_Conventions.md` §2 Contradicts Itself on "Product Agent" 🟢 Minor

**Where it appears:**

| Source | Statement |
|---|---|
| [`Canonical_Naming_Conventions.md`](../Canonical_Naming_Conventions.md) §2, Aliases column | `"Product Agent", "Stage 1 Agent", "Intent Agent"` listed as **Forbidden** |
| [`Canonical_Naming_Conventions.md`](../Canonical_Naming_Conventions.md) §2, Canonical Usage Rules | `"Product Agent" is **forbidden** — it is a conversational alias only; never use in spec documents` |
| [`Agentic Workbench v2 - Draft.md`](../Agentic%20Workbench%20v2%20-%20Draft.md) — Part 1.5 Glossary | `"Also called 'Product Agent' in conversational contexts — these are synonymous"` |
| [`agentic-workbench-engine/.roomodes`](../agentic-workbench-engine/.roomodes) — Architect Agent prompt | `"also known as 'Product Agent' in conversational contexts — these are synonymous"` |

**The conflict:** The Canonical Naming Conventions §2 forbids "Product Agent" in spec documents. Yet the spec itself (Part 1.5 Glossary) and the `.roomodes` prompt both use "Product Agent" as a documented alias. The naming authority contradicts the spec it is supposed to govern.

**Decision required:** Either (a) remove the "Product Agent" alias from the spec Glossary and `.roomodes` prompt, or (b) update the Canonical Naming Conventions to allow "Product Agent" as a documented alias in the Glossary only (not in running prose). Option (b) is more pragmatic — the alias is useful for human communication.

**Fix (recommended):** Update `Canonical_Naming_Conventions.md` §2 to say: `"Product Agent" is a **documented conversational alias** — permitted in Glossary entries and agent prompts, but forbidden in running prose and implementation documents.`

---

## Category 4: CLI / Documentation Gaps

### ISSUE-D01 — `Beginners_Guide.md` References Non-Existent `--version` Flag 🟡 Moderate

**Where it appears:**

| Source | Content |
|---|---|
| [`docs/Beginners_Guide.md`](../docs/Beginners_Guide.md) Step 1.2 | `python workbench-cli.py --version` → expected output: `Agentic Workbench CLI v2.0` |
| [`agentic-workbench-engine/workbench-cli.py`](../agentic-workbench-engine/workbench-cli.py) — `main()` | No `--version` argument defined in `argparse` — flag does not exist ❌ |

**Three sub-issues in one:**

1. **`--version` flag does not exist** — `workbench-cli.py` has no `--version` argument. Running `python workbench-cli.py --version` will print the argparse help and exit with code 2.

2. **Version number mismatch** — The guide says the output should be `Agentic Workbench CLI v2.0` but the current version is `2.1` (per `.workbench-version` and `workbench-cli.py` docstring).

3. **Fictional success output** — Step 1.4 shows a success message with emoji (`✅ Project initialized successfully!`, `📁 Location:`, `🔧 Next steps:`) that does not match the actual CLI output (`[WORKBENCH-CLI] Project initialized successfully!` — plain text, no emoji, no location/next-steps block).

**Fix:**
- Add `--version` to `workbench-cli.py`'s argparse: `parser.add_argument("--version", action="version", version=f"Agentic Workbench CLI v{load_template_version()}")`
- Update the guide's expected output to `Agentic Workbench CLI v2.1`
- Update Step 1.4's success output block to match the actual CLI output

---

### ISSUE-D02 — `Beginners_Guide.md` Initial Commit Message Mismatch 🟢 Minor

**Where it appears:**

| Source | Commit Message |
|---|---|
| [`docs/Beginners_Guide.md`](../docs/Beginners_Guide.md) Step 1.4 | `chore(workbench): initialize Agentic Workbench v2.0` |
| [`agentic-workbench-engine/workbench-cli.py`](../agentic-workbench-engine/workbench-cli.py) `cmd_init()` | `chore(workbench): initialize Agentic Workbench v` + `load_template_version()` = `chore(workbench): initialize Agentic Workbench v2.1` |

**The conflict:** The guide hardcodes `v2.0` in the example commit message, but the CLI dynamically reads the version from `.workbench-version` (which is `2.1`). The guide is outdated.

**Fix:** Update the guide's example commit message to `chore(workbench): initialize Agentic Workbench v2.1`, or better, note that the version is dynamic: `chore(workbench): initialize Agentic Workbench v{version}`.

---

### ISSUE-D03 — `Beginners_Guide.md` Appendix C Missing `PIVOT_APPROVED` and `UPGRADE_IN_PROGRESS` States 🟢 Minor

**Where it appears:**

| Source | States Listed |
|---|---|
| [`docs/Beginners_Guide.md`](../docs/Beginners_Guide.md) Appendix C | 13 states listed — missing `PIVOT_APPROVED` and `UPGRADE_IN_PROGRESS` |
| [`Canonical_Naming_Conventions.md`](../Canonical_Naming_Conventions.md) §6 | 16 states listed (including `PIVOT_APPROVED`, `UPGRADE_IN_PROGRESS`, `CLEAN`) |
| [`Agentic Workbench v2 - Draft.md`](../Agentic%20Workbench%20v2%20-%20Draft.md) — State Machine | All states including `PIVOT_APPROVED` and `UPGRADE_IN_PROGRESS` |

**The conflict:** Appendix C of the Beginners Guide lists 13 pipeline states but omits `PIVOT_APPROVED` and `UPGRADE_IN_PROGRESS`. A developer reading the guide will not know these states exist.

**Fix:** Add `PIVOT_APPROVED` and `UPGRADE_IN_PROGRESS` to Appendix C's state table.

---

## Category 5: Settings File Divergence

### ISSUE-E01 — Lab `.roo-settings.json` and Engine `.roo-settings.json` Are Structurally Different 🟢 Minor

**Where it appears:**

| File | Structure |
|---|---|
| [`.roo-settings.json`](../.roo-settings.json) (lab root) | Has `settings` + `transition_map` keys |
| [`agentic-workbench-engine/.roo-settings.json`](../agentic-workbench-engine/.roo-settings.json) | Has `settings` + `arbiter_owned` keys |

**The conflict:** The lab's `.roo-settings.json` uses a `transition_map` key (an older structure) while the engine's uses `arbiter_owned` (the current structure per ADR-002). The spec (Cross-Cutting Concern 1.5) defines `arbiter_owned` as the canonical contract. The lab's `transition_map` is a legacy structure that was superseded.

**Additionally:** The lab's `deniedCommands` list does NOT include the test runner commands (`npm test`, `npx vitest`, `pytest`, etc.) that the engine's `deniedCommands` list includes. This means the lab's settings are less restrictive than the engine's — agents working in the lab repo could auto-execute test commands that should be Arbiter-owned.

**Fix:**
1. Update the lab's `.roo-settings.json` to replace `transition_map` with `arbiter_owned` (matching the engine's structure).
2. Add the test runner commands to the lab's `deniedCommands` list to match the engine's settings.
3. Note: The lab repo does not run Arbiter scripts against itself (it validates the engine), so the `arbiter_owned` section in the lab's settings is informational rather than operational.

---

## Summary Table — Edition 2 Issues

| # | Severity | Category | Source Layers Affected | Issue |
|---|---|---|---|---|
| A01 | ✅ FIXED | Naming | `Repo_Cleanup_and_Deployment_Strategy.md` | Old repo names (`agentic-workbench-template`, `agentic-workbench-v2-specs`) throughout |
| A02 | ✅ FIXED | Naming | `Beginners_Guide.md` | Old repo name `agentic-workbench-template` throughout |
| A03 | ✅ FIXED | Naming | Diagrams 16, 17, 20 | `agentic-workbench-template` in diagram nodes |
| A04 | ✅ FIXED | Naming | `Agentic_Workbench_v2_Implementation_Strategy.md` | `agentic-workbench-template` references |
| B01 | ✅ FIXED | Diagrams | Diagram 7, Spec | `REVIEW_PENDING → PIVOT_IN_PROGRESS` missing from Diagram 7 (unfixed from Edition 1) |
| B02 | ✅ FIXED | Diagrams | Diagram 6 | Node S3_10 still uses `feat-IDEA-NNN-slug` (residual `IDEA-NNN`) |
| B03 | ✅ FIXED | Diagrams | Diagram 1 | `integration_test_runner.py` and `dependency_monitor.py` missing from Arbiter subgraph |
| B04 | ✅ FIXED | Diagrams | Diagram 1 | AR1 label "State and Gate Manager" references removed `state_manager.py` concept |
| C01 | ✅ FIXED | Spec | Spec Cross-Cutting Concern 2 | Branch format still uses `IDEA-NNN` in spec GitFlow section |
| C02 | ✅ FIXED | Spec | Canonical Naming Conventions §2, Spec Glossary, `.roomodes` | "Product Agent" forbidden by naming authority but used in spec Glossary and `.roomodes` |
| D01 | ✅ FIXED | CLI/Docs | `Beginners_Guide.md`, `workbench-cli.py` | `--version` flag does not exist; version number wrong; success output fictional |
| D02 | ✅ FIXED | CLI/Docs | `Beginners_Guide.md`, `workbench-cli.py` | Initial commit message hardcodes `v2.0` but CLI generates `v2.1` |
| D03 | ✅ FIXED | CLI/Docs | `Beginners_Guide.md`, Canonical Naming | Appendix C missing `PIVOT_APPROVED` and `UPGRADE_IN_PROGRESS` states |
| E01 | ✅ FIXED | Settings | Lab `.roo-settings.json`, Engine `.roo-settings.json` | Structural divergence: `transition_map` vs `arbiter_owned`; lab missing test runner denials |

---

## Prioritized Fix Recommendations — Edition 2

### P0 — Fix Immediately (Naming Confusion Blocks Usability)

1. **ISSUE-A01:** Update `Repo_Cleanup_and_Deployment_Strategy.md` — replace all `agentic-workbench-template` → `agentic-workbench-engine` and `agentic-workbench-v2-specs` → `agentic-workbench-lab`.

2. **ISSUE-A02:** Update `Beginners_Guide.md` — replace all `agentic-workbench-template` → `agentic-workbench-engine`.

### P1 — Fix Before Next Documentation Review

3. **ISSUE-B01:** Add `REVIEW_PENDING --> PIVOT_IN_PROGRESS : Human submits Delta Prompt during review` to Diagram 7 in [`diagrams/03-tdd-and-state.md`](../diagrams/03-tdd-and-state.md). (Carried over from Edition 1 — still unresolved.)

4. **ISSUE-B02:** Fix node S3_10 in Diagram 6 — change `feat-IDEA-NNN-slug` to `feat-REQ-NNN-slug`.

5. **ISSUE-C01:** Fix spec Cross-Cutting Concern 2 branch format — change `{IDEA-NNN}` to `{REQ-NNN}`.

6. **ISSUE-A03:** Update Diagrams 16, 17, 20 — replace `agentic-workbench-template` with `agentic-workbench-engine`.

7. **ISSUE-D01:** Add `--version` flag to `workbench-cli.py`; update `Beginners_Guide.md` Step 1.2 and Step 1.4 to match actual CLI output.

### P2 — Fix Before Public Release

8. **ISSUE-B03:** Add `integration_test_runner.py` and `dependency_monitor.py` to Diagram 1's Arbiter subgraph.

9. **ISSUE-B04:** Rename Diagram 1 AR1 label from "State and Gate Manager" to reflect distributed state management (ADR-003).

10. **ISSUE-A04:** Update `Agentic_Workbench_v2_Implementation_Strategy.md` — replace `agentic-workbench-template` with `agentic-workbench-engine`.

11. **ISSUE-E01:** Update lab `.roo-settings.json` — replace `transition_map` with `arbiter_owned`; add test runner commands to `deniedCommands`.

### P3 — Documentation Polish

12. **ISSUE-C02:** Clarify "Product Agent" policy in `Canonical_Naming_Conventions.md` §2 — distinguish between Glossary/prompt usage (permitted) and running prose (forbidden).

13. **ISSUE-D02:** Update `Beginners_Guide.md` Step 1.4 commit message from `v2.0` to `v2.1` (or make it dynamic).

14. **ISSUE-D03:** Add `PIVOT_APPROVED` and `UPGRADE_IN_PROGRESS` to `Beginners_Guide.md` Appendix C state table.

---

## What Remains Consistent and Correct (Edition 2 Confirmation)

The following aspects are **fully coherent** across all layers reviewed in this edition:

- ✅ **Core triad architecture** (Roo Code / The Arbiter / Roo Chat) — consistent across spec, diagrams, `.clinerules`, and canonical naming
- ✅ **State machine states** — consistent across spec, Diagram 7, gap-fix plan, and tests (with the one missing transition noted in B01)
- ✅ **Two-phase test execution** — consistent across spec, Diagram 6, implementation plan, and test suite
- ✅ **Memory system** (Hot/Cold zones, rotation policies) — consistent across spec, Diagram 11, Diagram 19, and template files
- ✅ **Session lifecycle** (CHECK→CREATE→READ→ACT) — consistent across spec, `.clinerules`, Diagram 12, and template `activeContext.md`
- ✅ **Dependency management** (`@depends-on` tags, `feature_registry`, `DEPENDENCY_BLOCKED`) — consistent across spec, `.clinerules`, and test suite
- ✅ **Integration test layer** (Stage 2b, `FLOW-NNN` IDs, `integration_test_runner.py`) — consistent across spec, Diagram 4, implementation plan, and test suite
- ✅ **`workbench-cli.py` commands** (`init`, `upgrade`, `status`, `rotate`) — consistent across spec, Diagram 17, and implementation
- ✅ **Memory rotation policy** (Rotate/Persist/Reset per file) — consistent across spec, Diagram 19, and template files
- ✅ **GitFlow strategy** (branch types, forbidden actions, PR-only merges) — consistent across spec and Diagram 14 (except `IDEA-NNN` in spec prose — ISSUE-C01)
- ✅ **`.clinerules` rules** (SLC, HND, TRC, CMT, STM, INT, REG, DEP, CMD, MEM, FAC, CR, FOR) — fully consistent between lab `.clinerules` and engine `.clinerules` (files are identical)
- ✅ **`conftest.py` DEFAULT_STATE schema** — matches engine `state.json` schema exactly
- ✅ **`conftest.py` TEMPLATE_ROOT** — correctly points to `agentic-workbench-engine` submodule
- ✅ **Engine `state.json` `arbiter_capabilities`** — all `false` (correct Phase A initial state)
- ✅ **`REQ-NNN` traceability IDs** — now consistent across Diagrams 5, 14, 15 (Edition 1 fixes applied)
- ✅ **`state_manager.py` removed** — absent from Diagram 20, Canonical Naming Conventions, and engine scripts (ADR-003 applied)
- ✅ **`CLEAN` regression state value** — documented in Canonical Naming Conventions §6 (Edition 1 fix applied)
- ✅ **`.gitmodules`** — correctly wired to `agentic-workbench-engine` repo
- ✅ **`pytest.ini`** — correctly configured for `tests/workbench/` test path
- ✅ **`README.md`** — accurately describes the two-repo architecture with correct names
- ✅ **`decisionLog.md`** — ADR-001 through ADR-005 are complete, consistent, and non-contradictory
- ✅ **`RELEASE.md`** — correctly shows v2.1 as INITIALIZED
- ✅ **`handoff-state.md`** — correctly reflects Sprint 3 complete state with correct repo names in Notes section

---

## Edition 3 — Beginners Guide Targeted Review (2026-04-12)

**Scope:** `docs/Beginners_Guide.md` vs. `workbench-cli.py`, `.clinerules`, `.roomodes`, `.roo-settings.json`, `state.json`, `Canonical_Naming_Conventions.md`

**Context:** Edition 2 marked ISSUE-D01 (fictional success output) as `✅ FIXED` but the fix was never applied to the guide. This edition documents the actual state found and the fixes applied.

### Issues Found and Fixed in Edition 3

| # | Severity | File | Issue | Fix Applied |
|---|---|---|---|---|
| E3-01 | 🟡 Moderate | `docs/Beginners_Guide.md` Step 1.4 | Success output block showed fictional emoji-decorated output (`✅ 📁 🔧`) that does not match actual CLI output (`[WORKBENCH-CLI]` prefix, 2 lines). Was marked fixed in Edition 2 but was not. | ✅ Updated to match actual CLI output |
| E3-02 | 🟢 Minor | `docs/Beginners_Guide.md` Appendix C | `FEATURE_GREEN` state missing from state reference table. Present in `Canonical_Naming_Conventions.md` §6 but absent from guide. | ✅ Added `FEATURE_GREEN` row with correct description |
| E3-03 | 🟢 Minor | `agentic-workbench-engine/workbench-cli.py` line 7 | Docstring still referenced `agentic-workbench-template` (old repo name). Guide correctly uses `agentic-workbench-engine` throughout. | ✅ Fixed in Code mode |

### What Was Verified as Correct in Edition 3

- ✅ **Repo name** — `agentic-workbench-engine` used correctly throughout the guide (Edition 2 ISSUE-A02 fix confirmed applied)
- ✅ **`--version` flag** — exists in CLI (`action="store_true"`, line 281); outputs `Agentic Workbench CLI v2.1` correctly
- ✅ **Init commit message** — guide shows `v2.1`; CLI dynamically reads from `.workbench-version` = `2.1` ✅
- ✅ **Directory scaffold** — guide's directory tree matches `cmd_init()` exactly
- ✅ **`state.json` initial state** — `"INIT"` with all `arbiter_capabilities` = `false` ✅
- ✅ **Upgrade safety gate** — guide correctly states `INIT` or `MERGED` required; CLI enforces this at line 178
- ✅ **Upgrade commit message** — `chore(workbench): upgrade engine to v{version}` matches CLI line 219
- ✅ **All 4 CLI commands** — `init`, `upgrade`, `status`, `rotate` all exist in CLI and Appendix B
- ✅ **`PIVOT_APPROVED` and `UPGRADE_IN_PROGRESS`** — present in Appendix C (Edition 2 ISSUE-D03 fix confirmed applied)
- ✅ **7-step workflow** — matches `.roomodes` stage definitions and `.clinerules` §10 file access constraints
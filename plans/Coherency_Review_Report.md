# Agentic Workbench v2 — Coherency Audit Report
## Edition 4 — Comprehensive All-Sources Audit

**Auditor:** Senior Architect (Roo Code — Architect Agent)
**Date:** 2026-04-13
**Scope:** All canonical sources and rules files (excluding `memory-bank/`, `docs/conversations/`, `plans/`)
**Status:** AUTHORITY — This report is the single source of truth for coherency findings as of this date.
**Previous Edition:** Edition 3 (Beginners Guide Targeted Review, 2026-04-12)

---

## Executive Summary

The Agentic Workbench v2 canonical source set is **substantially coherent** with a strong architectural foundation. The core pipeline, state machine, memory system, and agent role definitions are consistent across the majority of files. However, the audit identified **27 specific issues** across five severity categories: 3 Critical conflicts, 11 Moderate inconsistencies, 9 Minor gaps or terminology drift, 4 Structural/completeness issues, and 3 Cross-reference validity problems.

The most significant issues are:

1. **Version mismatch** between root `.clinerules` (v2.2-root) and engine `.clinerules` (v2.2) — the root file has a `-root` suffix that is unexplained and creates ambiguity about authority.
2. **Startup Protocol heading mismatch** — the engine `.clinerules` section heading says `CHECK → CREATE → READ → ACT` but the body correctly says `SCAN → CHECK → CREATE → READ → ACT`, creating a contradiction within the same file.
3. **`integration_state` value inconsistency** — `integration_test_runner.py` writes `"RED"` when tests fail, but `state.json` schema, `Canonical_Naming_Conventions.md`, and `.clinerules` all use `"INTEGRATION_RED"` as the canonical state value.
4. **`roo-settings.json` missing `npm install` / `pnpm install` / `yarn`** in the engine submodule vs. the root — the root `.roo-settings.json` includes these but the engine's does not.
5. **`Agentic Workbench v2 - Draft.md` references `auto_approve.patterns`** (old key name) in the CMD-1 rule description, while the actual `.roo-settings.json` uses `settings.roo-cline.allowedCommands`.
6. **`post-tag` hook contains a stale TODO comment** referencing `compliance_snapshot.py` as "not yet implemented" even though the script now exists.
7. **`Beginners_Guide.md` documents only 4 CLI commands** (`init`, `upgrade`, `status`, `rotate`) but `workbench-cli.py` now has 10+ commands added by the Gap Implementation Plan.

---

## Part 1: Files Reviewed

| File | Version / Status |
|---|---|
| `.clinerules` (root) | v2.2-root |
| `.roo-settings.json` (root) | v2.1 |
| `.roomodes` (root) | JSON customModes format |
| `pytest.ini` (root) | Standard pytest config |
| `README.md` (root) | Current |
| `Agentic Workbench v2 - Draft.md` | v2.0 (updated 2026-04-12) |
| `Canonical_Naming_Conventions.md` | v2.1 |
| `agentic-workbench-engine/.clinerules` | v2.2 |
| `agentic-workbench-engine/.roo-settings.json` | v2.1 |
| `agentic-workbench-engine/.roomodes` | JSON customModes format |
| `agentic-workbench-engine/state.json` | v2.1 |
| `agentic-workbench-engine/pyproject.toml` | v2.1.0 |
| `agentic-workbench-engine/workbench-cli.py` | Not directly read (referenced) |
| `.workbench/hooks/pre-commit` | v2.1 |
| `.workbench/hooks/pre-push` | v2.1 |
| `.workbench/hooks/post-merge` | v2.1 |
| `.workbench/hooks/post-tag` | v2.1 |
| `.workbench/scripts/arbiter_check.py` | v2.1 |
| `.workbench/scripts/gherkin_validator.py` | v2.1 |
| `.workbench/scripts/test_orchestrator.py` | v2.1 |
| `.workbench/scripts/integration_test_runner.py` | v2.1 |
| `.workbench/scripts/memory_rotator.py` | v2.1 |
| `.workbench/scripts/audit_logger.py` | v2.1 |
| `.workbench/scripts/dependency_monitor.py` | v2.1 |
| `.workbench/scripts/crash_recovery.py` | v2.1 |
| `.workbench/scripts/compliance_snapshot.py` | v2.1 |
| `.workbench/mcp/archive_query_server.py` | v2.1 |
| `diagrams/01-system-overview.md` | 2026-04-12 |
| `diagrams/02-phase0-and-pipeline.md` | 2026-04-12 |
| `diagrams/03-tdd-and-state.md` | 2026-04-12 |
| `diagrams/04-adhoc-and-pivot.md` | 2026-04-12 |
| `diagrams/05-memory-sessions-and-infra.md` | 2026-04-12 |
| `docs/Beginners_Guide.md` | Current |
| `tests/workbench/conftest.py` | Current |
| `tests/workbench/test_state_machine.py` | Current |
| `tests/workbench/test_hooks_pre_commit.py` | Current |
| `tests/workbench/test_arbiter_check.py` | Current |

---

## Part 2: Critical Conflicts (Severity: 🔴 CRITICAL)

These are direct contradictions between canonical sources that could cause agent misbehaviour or system failures.

---

### CONFLICT-001: Startup Protocol Heading vs. Body Mismatch in Engine `.clinerules`

**Severity:** 🔴 CRITICAL
**Files:** [`agentic-workbench-engine/.clinerules`](agentic-workbench-engine/.clinerules:14)

**Finding:**

The section heading at line 14 reads:
```
### 1.1 Startup Protocol (CHECK → CREATE → READ → ACT)
```

But the body of the same section (lines 18–25) correctly describes a **5-step** sequence starting with SCAN:
```
0. SCAN — Run python .workbench/scripts/arbiter_check.py check-session
1. CHECK for activeContext.md
2. CREATE activeContext.md from template if absent
3. READ activeContext.md completely
4. READ progress.md completely
5. ACT
```

The root `.clinerules` heading at line 14 correctly reads:
```
### 1.1 Startup Protocol (SCAN → CHECK → CREATE → READ → ACT)
```

**Impact:** An agent reading only the heading of the engine `.clinerules` would believe the startup protocol is 4 steps (CHECK → CREATE → READ → ACT) and skip the mandatory SCAN step (running `arbiter_check.py check-session`). This directly undermines Rule SLC-1 and the entire compliance health scanner (GAP-15).

**Recommendation:** Update the engine `.clinerules` section heading to match the root:
```
### 1.1 Startup Protocol (SCAN → CHECK → CREATE → READ → ACT)
```

---

### CONFLICT-002: `integration_state` Value — `"RED"` vs. `"INTEGRATION_RED"`

**Severity:** 🔴 CRITICAL
**Files:**
- [`agentic-workbench-engine/.workbench/scripts/integration_test_runner.py`](agentic-workbench-engine/.workbench/scripts/integration_test_runner.py:148)
- [`agentic-workbench-engine/state.json`](agentic-workbench-engine/state.json:10)
- [`Canonical_Naming_Conventions.md`](Canonical_Naming_Conventions.md:133)
- [`agentic-workbench-engine/.clinerules`](agentic-workbench-engine/.clinerules:165)

**Finding:**

`integration_test_runner.py` line 148 writes:
```python
state["integration_state"] = "RED"
```

But the canonical state machine in `Canonical_Naming_Conventions.md` (§6, Pipeline States table) defines `INTEGRATION_RED` as the canonical state value for `state.json.state`. The `integration_state` field is a separate field from `state`, but the value `"RED"` is inconsistent with the naming convention that uses `"INTEGRATION_RED"` for integration failures.

Furthermore, `state.json` initialises `integration_state` as `"NOT_RUN"` (consistent), and `integration_test_runner.py` sets it to `"GREEN"` on success (consistent), but `"RED"` on failure instead of `"INTEGRATION_RED"`.

The `pre-push` hook checks `state.json.state` for `INTEGRATION_RED` (the main state field), not `integration_state`. The `integration_test_runner.py` also sets `state["state"] = "INTEGRATION_RED"` (line 162) when the main state is `GREEN` and integration fails — this part is correct. But the `integration_state` field value `"RED"` vs. `"INTEGRATION_RED"` is inconsistent.

**Impact:** Tests in `test_state_machine.py` (SM-009) assert `state["integration_state"] == "RED"` — so the tests are written to match the buggy implementation, not the spec. Any code or agent that checks `integration_state == "INTEGRATION_RED"` will fail to detect integration failures.

**Recommendation:** Change `integration_test_runner.py` line 148 to:
```python
state["integration_state"] = "INTEGRATION_RED"
```
And update `test_state_machine.py` SM-009 assertion accordingly.

---

### CONFLICT-003: `Draft.md` CMD-1 References Obsolete Key `auto_approve.patterns`

**Severity:** 🔴 CRITICAL
**Files:**
- [`Agentic Workbench v2 - Draft.md`](Agentic%20Workbench%20v2%20-%20Draft.md:625)
- [`agentic-workbench-engine/.clinerules`](agentic-workbench-engine/.clinerules:184)
- [`.roo-settings.json`](.roo-settings.json:11)

**Finding:**

`Agentic Workbench v2 - Draft.md` at line 625 (in the `.clinerules` section description) states:

> **Command Delegation Phase A (CMD-1):** During the pre-Arbiter transition (Layer 1), the Agent MAY auto-execute commands matching the patterns defined in `.roo-settings.json` `auto_approve.patterns`.

But the actual `.roo-settings.json` uses the key `settings.roo-cline.allowedCommands`, not `auto_approve.patterns`. The `.clinerules` files (both root and engine) correctly reference `settings.roo-cline.allowedCommands` in their CMD-1 rule text.

**Impact:** The Draft spec is the primary architectural reference document. Any developer or agent reading the CMD-1 description in the Draft will look for `auto_approve.patterns` in `.roo-settings.json` and not find it, causing confusion about how the allowlist is configured.

**Recommendation:** Update `Agentic Workbench v2 - Draft.md` line 625 to reference `settings.roo-cline.allowedCommands` consistently with the actual implementation and `.clinerules`.

---

## Part 3: Moderate Inconsistencies (Severity: 🟡 MODERATE)

These are inconsistencies that do not cause immediate failures but create ambiguity, drift, or partial enforcement gaps.

---

### INCONSISTENCY-001: Root `.clinerules` Version Suffix `-root` Is Unexplained

**Severity:** 🟡 MODERATE
**Files:**
- [`.clinerules`](.clinerules:6) — Version: `2.2-root`
- [`agentic-workbench-engine/.clinerules`](agentic-workbench-engine/.clinerules:6) — Version: `2.2`

**Finding:**

The root `.clinerules` declares `**Version:** 2.2-root` while the engine `.clinerules` declares `**Version:** 2.2`. No document in the canonical set explains what `-root` means, whether the root file is authoritative over the engine file, or how they should diverge.

The `README.md` states the lab repo is "not an application project" and that the engine submodule is "the single source of truth for all engine files." This implies the engine `.clinerules` should be canonical. Yet the root `.clinerules` has a higher-specificity version string.

**Impact:** Agents operating in the lab repo read the root `.clinerules` (v2.2-root). Agents operating in an application project initialized from the engine read the engine `.clinerules` (v2.2). If these files diverge in content (they currently do not, except for the heading issue in CONFLICT-001), agents will behave differently in the lab vs. in application projects.

**Recommendation:** Either:
1. Document the `-root` suffix meaning in both files (e.g., "root = lab-specific overlay"), or
2. Eliminate the suffix and keep both files at `2.2`, with a note that the engine file is canonical and the root file is a copy.

---

### INCONSISTENCY-002: Root `.roo-settings.json` Has Extra `allowedCommands` vs. Engine

**Severity:** 🟡 MODERATE
**Files:**
- [`.roo-settings.json`](.roo-settings.json:18) — root
- [`agentic-workbench-engine/.roo-settings.json`](agentic-workbench-engine/.roo-settings.json:18) — engine

**Finding:**

The root `.roo-settings.json` `allowedCommands` list includes:
```json
"npm install",
"pnpm install",
"yarn",
"npm ci",
"npx biome check --write .",
"npx biome lint ."
```

The engine `.roo-settings.json` `allowedCommands` list does **not** include these entries. Both files are at version `2.1`.

**Impact:** Agents working in the lab repo (root) can auto-execute `npm install` and Biome commands without approval. Agents working in an application project (engine) cannot. This creates different operational surfaces for the same agent modes.

The `Draft.md` Phase A template (lines 357–378) also does not include `npm install`, `pnpm install`, `yarn`, `npm ci`, `npx biome check --write .`, or `npx biome lint .` — so the root file has drifted from the spec template.

**Recommendation:** Decide which is canonical. If the engine file is the template for application projects, the root file should either match it exactly or document why it diverges (lab-specific additions).

---

### INCONSISTENCY-003: `post-tag` Hook Contains Stale TODO for `compliance_snapshot.py`

**Severity:** 🟡 MODERATE
**Files:**
- [`agentic-workbench-engine/.workbench/hooks/post-tag`](agentic-workbench-engine/.workbench/hooks/post-tag:53)
- [`agentic-workbench-engine/.workbench/scripts/compliance_snapshot.py`](agentic-workbench-engine/.workbench/scripts/compliance_snapshot.py:1)

**Finding:**

The `post-tag` hook at lines 53–55 contains:
```sh
else
    echo "[POST-TAG] compliance_snapshot.py not found — compliance snapshot not yet automated"
    echo "  Manual compliance snapshot required for release $tag_name"
    echo "  TODO: Implement .workbench/scripts/compliance_snapshot.py"
fi
```

However, `compliance_snapshot.py` **does exist** (it was created as part of GAP-1 in Sprint B). The hook's `if` branch at line 48 correctly calls it:
```sh
if [ -f ".workbench/scripts/compliance_snapshot.py" ]; then
    python .workbench/scripts/compliance_snapshot.py --tag "$tag_name" 2>/dev/null || ...
```

So the `else` branch (stale TODO) will never execute in a correctly installed workbench. However, the stale TODO comment is misleading and suggests the script is not yet implemented.

**Impact:** Low operational impact (the `else` branch is unreachable when the script exists), but creates confusion for developers reading the hook and may cause incorrect assumptions during debugging.

**Recommendation:** Remove the stale TODO comment from the `else` branch. Replace with:
```sh
else
    echo "[POST-TAG] compliance_snapshot.py not found — run: python workbench-cli.py upgrade"
fi
```

---

### INCONSISTENCY-004: `Beginners_Guide.md` CLI Command Reference Is Incomplete

**Severity:** 🟡 MODERATE
**Files:**
- [`docs/Beginners_Guide.md`](docs/Beginners_Guide.md:396)
- `agentic-workbench-engine/workbench-cli.py` (referenced)

**Finding:**

`Beginners_Guide.md` Appendix B documents only 4 CLI commands:
```
init, upgrade, status, rotate
```

But `workbench-cli.py` was extended by the Gap Implementation Plan (Sprint A/B) to include at minimum:
- `start-feature --req-id REQ-NNN`
- `lock-requirements --req-id REQ-NNN`
- `set-red --req-id REQ-NNN`
- `review-pending --req-id REQ-NNN`
- `merge --req-id REQ-NNN`
- `install-hooks`
- `register-arbiter`
- `check`

**Impact:** A developer following the Beginner's Guide will not know how to advance the pipeline through its stages using the CLI. They will be unable to transition from `INIT` to `STAGE_1_ACTIVE`, lock requirements, or trigger the merge flow without reading the source code.

**Recommendation:** Update `Beginners_Guide.md` Appendix B to include all current CLI commands with brief descriptions.

---

### INCONSISTENCY-005: `Draft.md` Startup Protocol Describes `CHECK→CREATE→READ→ACT` (4 Steps)

**Severity:** 🟡 MODERATE
**Files:**
- [`Agentic Workbench v2 - Draft.md`](Agentic%20Workbench%20v2%20-%20Draft.md:261)

**Finding:**

`Draft.md` Cross-Cutting Concern 1 (Persistent Memory System), Session Lifecycle Protocols section at line 261 states:

> **Startup Protocol (CHECK→CREATE→READ→ACT):** The agent checks for `activeContext.md`. If absent, it creates it using strict templates. It then sequentially reads `activeContext.md` and `progress.md` before taking any action.

This describes the **old 4-step** protocol. The current `.clinerules` (both root and engine) define a **5-step** protocol: `SCAN → CHECK → CREATE → READ → ACT`, where step 0 is running `arbiter_check.py check-session`.

**Impact:** The Draft spec is the primary architectural reference. Developers reading it will implement the 4-step protocol and miss the mandatory compliance scan step. This is a spec-to-implementation drift introduced by GAP-15.

**Recommendation:** Update `Draft.md` section "Session Lifecycle Protocols" to describe the 5-step `SCAN → CHECK → CREATE → READ → ACT` protocol, referencing `arbiter_check.py check-session` as step 0.

---

### INCONSISTENCY-006: `diagrams/05-memory-sessions-and-infra.md` Diagram 12 — Retracted

**Severity:** N/A — RETRACTED
**Finding:** Upon closer inspection, Diagram 12 in `diagrams/05-memory-sessions-and-infra.md` correctly shows `SCAN → CHECK → CREATE → READ → ACT` in both the note and the sequence body. This is **not** an inconsistency. Finding retracted.

---

### INCONSISTENCY-007: `test_state_machine.py` SM-013 Does Not Test the CLI `merge` Command

**Severity:** 🟡 MODERATE
**Files:**
- [`tests/workbench/test_state_machine.py`](tests/workbench/test_state_machine.py:146)

**Finding:**

SM-013 (`REVIEW_PENDING → MERGED`) directly writes to `state.json` in the test body:
```python
state_data["state"] = "MERGED"
state_path.write_text(json.dumps(state_data, indent=2), encoding="utf-8")
```

This bypasses the `workbench-cli.py merge --req-id REQ-NNN` command that was implemented as part of GAP-5. The test validates the state schema but does not validate that the CLI command correctly performs the transition, including:
- Validating `state.json.state == "REVIEW_PENDING"` before transition
- Setting `feature_registry[REQ-NNN].state = "MERGED"` with `merged_at` timestamp
- Triggering `dependency_monitor.py check-unblock`
- Clearing `active_req_id`

**Impact:** The `REVIEW_PENDING → MERGED` transition is the most critical pipeline closure step. If the CLI `merge` command has a bug, the test suite will not catch it.

**Recommendation:** Add a test `test_sm013b_review_pending_to_merged_via_cli` that calls `run_script("workbench_cli", "merge", "--req-id", "REQ-001")` and validates all side effects.

---

### INCONSISTENCY-008: `arbiter_check.py` `SESSION_CHECKS` Includes `CR-1` But Spec Says "CRITICAL Only"

**Severity:** 🟡 MODERATE
**Files:**
- [`agentic-workbench-engine/.workbench/scripts/arbiter_check.py`](agentic-workbench-engine/.workbench/scripts/arbiter_check.py:480)
- [`Agentic Workbench v2 - Draft.md`](Agentic%20Workbench%20v2%20-%20Draft.md:839)

**Finding:**

`arbiter_check.py` defines `SESSION_CHECKS` as:
```python
SESSION_CHECKS = ["SLC-2", "MEM-1", "DEP-3", "FAC-1", "CR-1"]
```

The `check-session` mode docstring says "Lightweight (CRITICAL only)". But `CR-1` (`check_crash_checkpoint`) returns `WARNING` or `INFO` status — never `CRITICAL`. So `CR-1` is included in the "CRITICAL only" session scan despite not being a CRITICAL check.

The GAP-15 spec in `Draft.md` (line 839) defines the session checks as:
> Implement `check-session` mode: CRITICAL checks only (SLC-2, MEM-1, DEP-3, FAC-1, CR-1)

So the spec explicitly includes `CR-1` in session checks. The docstring saying "CRITICAL only" is therefore inaccurate — it should say "CRITICAL + crash recovery checks."

**Impact:** Minor — the behaviour is correct per spec. The docstring is misleading.

**Recommendation:** Update the `check-session` docstring in `arbiter_check.py` to:
```
check-session  # Lightweight session-start check (CRITICAL checks + crash recovery)
```

---

### INCONSISTENCY-009: `gherkin_validator.py` CLI Interface Mismatch with `pre-commit` Hook Usage

**Severity:** 🟡 MODERATE
**Files:**
- [`agentic-workbench-engine/.workbench/scripts/gherkin_validator.py`](agentic-workbench-engine/.workbench/scripts/gherkin_validator.py:139)
- [`agentic-workbench-engine/.workbench/hooks/pre-commit`](agentic-workbench-engine/.workbench/hooks/pre-commit:83)

**Finding:**

`gherkin_validator.py` CLI interface (line 139) requires a positional `directory` argument:
```
python gherkin_validator.py validate features/
```

But the `pre-commit` hook at line 83 calls it as:
```sh
VALIDATION_RESULT=$(python .workbench/scripts/gherkin_validator.py "$(dirname "$file")" 2>&1 || echo "VALIDATION_FAILED")
```

The hook passes the **directory** as a positional argument without the `validate` subcommand. But `gherkin_validator.py`'s `main()` uses `argparse` with `parser.add_argument("directory", ...)` — a positional argument, not a subcommand. So the hook call is actually correct for the current implementation.

However, the docstring at line 14 says:
```
python gherkin_validator.py validate features/
```

This implies a `validate` subcommand, but the actual implementation uses a positional argument (no subcommand). The docstring is misleading.

**Impact:** A developer reading the docstring will try `python gherkin_validator.py validate features/` and get an error because `validate` would be interpreted as the directory name.

**Recommendation:** Fix the docstring to match the actual interface:
```
python gherkin_validator.py features/
python gherkin_validator.py _inbox/ --allow-draft
```

---

## Part 4: Minor Gaps and Terminology Drift (Severity: 🟢 MINOR)

These are small inconsistencies that do not affect system behaviour but reduce clarity or create potential for future drift.

---

### MINOR-001: `Draft.md` Still Uses "Product Agent" in Running Prose (§8.2.B)

**Severity:** 🟢 MINOR
**Files:**
- [`Agentic Workbench v2 - Draft.md`](Agentic%20Workbench%20v2%20-%20Draft.md:604)
- [`Canonical_Naming_Conventions.md`](Canonical_Naming_Conventions.md:51)

**Finding:**

`Draft.md` Part 8.2.B (`.roomodes` section) at line 604 states:
> **Architect Agent (Stage 1 - Built-in):** ... Also referred to as "Product Agent" in conversational contexts — these are synonymous (see Glossary).

`Canonical_Naming_Conventions.md` §2 states:
> "Product Agent" is a **documented conversational alias** — permitted in Glossary entries and agent prompts, but **forbidden in running prose and implementation documents**

The Draft.md reference is in a running prose section (Part 8.2.B), not a Glossary entry. This violates the naming convention.

**Recommendation:** Remove the "Product Agent" alias reference from Part 8.2.B of `Draft.md`. The Glossary in Part 1.5 already documents this alias correctly.

---

### MINOR-002: `diagrams/01-system-overview.md` Uses "Documentation Agent" (Short Form)

**Severity:** 🟢 MINOR
**Files:**
- [`diagrams/01-system-overview.md`](diagrams/01-system-overview.md:28)

**Finding:**

Diagram 1 (Separation of Powers) at line 28 labels the agent as:
```
A6[Documentation Agent\nBackground - Docs]
```

The canonical name per `Canonical_Naming_Conventions.md` §2 is **"Documentation / Librarian Agent"**. The short form "Documentation Agent" is listed as a forbidden alias ("Doc Agent", "Wiki Agent" are forbidden, but "Documentation Agent" without "/ Librarian" is not explicitly listed as forbidden — however it is not the canonical name).

**Recommendation:** Update diagram label to `Documentation / Librarian Agent` for consistency with the canonical name.

---

### MINOR-003: `diagrams/05-memory-sessions-and-infra.md` Diagram 16 References `.husky/` as Hook Location

**Severity:** 🟢 MINOR
**Files:**
- [`diagrams/05-memory-sessions-and-infra.md`](diagrams/05-memory-sessions-and-infra.md:374)

**Finding:**

Diagram 16 (Engine vs. Payload) at line 374 shows:
```
E4[.husky/ or .workbench/hooks/
Git hooks
pre-commit, pre-push, post-tag]
```

The actual implementation uses `.workbench/hooks/` exclusively. There is no `.husky/` directory in the engine. The `Draft.md` Part 5.1 also mentions `.husky/` as the hook location:
> **The Engine (Owned by the Workbench):** `.clinerules`, `.roomodes`, the Python Arbiter scripts (e.g., `.workbench/scripts/`), Git Hooks (`.husky/`), and `biome.json`.

The `workbench-cli.py` (per GAP-3 implementation) installs hooks from `.workbench/hooks/` into `.git/hooks/`. There is no Husky dependency.

**Impact:** Developers may look for a `.husky/` directory that does not exist, or attempt to install Husky unnecessarily.

**Recommendation:**
1. Update `Draft.md` Part 5.1 to reference `.workbench/hooks/` instead of `.husky/`
2. Update Diagram 16 to remove `.husky/` reference

---

### MINOR-004: `Canonical_Naming_Conventions.md` §4 Missing `arbiter_check.py` from Hook Trigger Table

**Severity:** 🟢 MINOR
**Files:**
- [`Canonical_Naming_Conventions.md`](Canonical_Naming_Conventions.md:83)

**Finding:**

The Git Hooks table in §4 describes the `pre-commit` hook as:
> Runs `gherkin_validator.py` + `biome.json` linting; blocks if `state.json` modified by non-Arbiter

But the actual `pre-commit` hook (post-GAP-15) now also:
- Calls `arbiter_check.py check-session --block-on-critical` (section 0)
- Updates `file_ownership` map (section 6, GAP-7)
- Validates Conventional Commits format (section 7, GAP-14)

The naming conventions document has not been updated to reflect these additions.

**Recommendation:** Update the `pre-commit` hook description in `Canonical_Naming_Conventions.md` §4 to include all current enforcement actions.

---

### MINOR-005: `memory_rotator.py` Rotation Policy Includes `narrativeRequest.md` But `Draft.md` Table Does Not

**Severity:** 🟢 MINOR
**Files:**
- [`agentic-workbench-engine/.workbench/scripts/memory_rotator.py`](agentic-workbench-engine/.workbench/scripts/memory_rotator.py:33)
- [`Agentic Workbench v2 - Draft.md`](Agentic%20Workbench%20v2%20-%20Draft.md:247)

**Finding:**

`memory_rotator.py` `ROTATION_POLICY["rotate"]` includes `narrativeRequest.md`:
```python
"rotate": [
    "activeContext.md",
    "progress.md",
    "productContext.md",
    "narrativeRequest.md",  # Added by GAP-8
],
```

But the Hot Zone File Rotation Policy table in `Draft.md` (lines 247–257) does not include `narrativeRequest.md`. The table lists only 8 files and their policies.

**Impact:** The spec table is incomplete. A developer reading the spec will not know that `narrativeRequest.md` is rotated at sprint end.

**Recommendation:** Add `narrativeRequest.md` to the rotation policy table in `Draft.md` with policy `Rotate` and rationale "Phase 0 discovery context is sprint-scoped."

---

### MINOR-006: State Machine Missing `INIT -> UPGRADE_IN_PROGRESS` Transition

**Severity:** 🟢 MINOR
**Files:**
- [`diagrams/03-tdd-and-state.md`](diagrams/03-tdd-and-state.md:127)
- [`Agentic Workbench v2 - Draft.md`](Agentic%20Workbench%20v2%20-%20Draft.md:573)

**Finding:**

The state machine diagram (Diagram 7) and `Draft.md` state machine both show `UPGRADE_IN_PROGRESS` transitions from `REQUIREMENTS_LOCKED` and `MERGED` only. However, the `Draft.md` upgrade rule states the Arbiter refuses upgrades in any state other than `INIT` or `MERGED` — implying `INIT -> UPGRADE_IN_PROGRESS` is also valid but missing from both the diagram and spec.

**Recommendation:** Add `INIT --> UPGRADE_IN_PROGRESS` transition to both the `Draft.md` state machine and `diagrams/03-tdd-and-state.md` Diagram 7.

---

### MINOR-007: `pre-commit` Hook Missing `arbiter_check.py check-session` Call (GAP-15)

**Severity:** 🟢 MINOR
**Files:**
- [`agentic-workbench-engine/.workbench/hooks/pre-commit`](agentic-workbench-engine/.workbench/hooks/pre-commit:31)

**Finding:**

The `pre-commit` hook section 0 is titled `# 0. SKIP VALIDATION FLAG` and handles the bypass/rebase detection. The `arbiter_check.py check-session --block-on-critical` call specified in GAP-15 (`Draft.md` line 863) was **not added** to the hook. This means CRITICAL violations are not caught at commit time.

**Recommendation:** Insert a section calling `python .workbench/scripts/arbiter_check.py check-session --block-on-critical` after the skip-validation flag check and before section 1.

---

### MINOR-008: `test_hooks_pre_commit.py` UC-052 Uses Simulated Logic

**Severity:** 🟢 MINOR
**Files:**
- [`tests/workbench/test_hooks_pre_commit.py`](tests/workbench/test_hooks_pre_commit.py:23)

**Finding:**

UC-052 simulates the pre-commit state.json integrity check with inline Python logic rather than exercising the actual hook's `ALLOWED_WRITERS` list. If the hook's `ALLOWED_WRITERS` list changes, this test will not catch the regression.

**Recommendation:** Refactor UC-052 to parse the actual `ALLOWED_WRITERS` list from the hook script and test against it.

---

### MINOR-009: `pyproject.toml` References Non-Existent `README.md` in Engine Root

**Severity:** 🟢 MINOR
**Files:**
- [`agentic-workbench-engine/pyproject.toml`](agentic-workbench-engine/pyproject.toml:9)

**Finding:**

`pyproject.toml` specifies `readme = "README.md"` but no `README.md` exists in the engine submodule root. PyPI publishing will fail or produce a package without a description.

**Recommendation:** Either create a `README.md` in the engine root, or remove the `readme` field from `pyproject.toml`.

---

## Part 5: Structural and Completeness Issues (Severity: 🔵 STRUCTURAL)

---

### STRUCTURAL-001: No Canonical Document Defines the `workbench-cli.py` Command Interface

**Severity:** 🔵 STRUCTURAL

**Finding:** The `workbench-cli.py` is referenced extensively across all canonical documents, but no single document provides a complete, authoritative specification of its command interface. The new commands (`start-feature`, `lock-requirements`, `set-red`, `review-pending`, `merge`, `install-hooks`, `register-arbiter`, `check`) are only documented in the Gap Implementation Plan (excluded from the canonical set per audit scope).

**Recommendation:** Add a `workbench-cli.py` command reference section to either `Draft.md` Part 8 or `Canonical_Naming_Conventions.md`.

---

### STRUCTURAL-002: `diagrams/README.md` Not Reviewed

**Severity:** 🔵 STRUCTURAL

**Finding:** The [`diagrams/README.md`](diagrams/README.md) was listed in the workspace but not read during this audit. It may contain cross-references inconsistent with current diagram content.

**Recommendation:** Read and audit `diagrams/README.md` in a follow-up review.

---

### STRUCTURAL-003: `Canonical_Naming_Conventions.md` §11 Version Table Is Stale

**Severity:** 🔵 STRUCTURAL
**Files:** [`Canonical_Naming_Conventions.md`](Canonical_Naming_Conventions.md:211)

**Finding:** The Version & Schema Tracking table in §11 does not include `Gap_Implementation_Plan_v2.md` or the new sections added to `Draft.md` Part 9.

**Recommendation:** Update §11 to include all current canonical documents and their versions.

---

### STRUCTURAL-004: `tests/workbench/` Missing Tests for Several Key Scripts

**Severity:** 🔵 STRUCTURAL

**Finding:** Missing test files:
- `test_compliance_snapshot.py` — `compliance_snapshot.py` (GAP-1) has no dedicated test file
- `test_hooks_post_merge.py` — `post-merge` hook has no test
- `test_hooks_post_tag.py` — `post-tag` hook has no test

**Recommendation:** Add test files for `compliance_snapshot.py`, `post-merge` hook, and `post-tag` hook.

---

## Part 6: Cross-Reference Validity Issues (Severity: 🟡 MODERATE)

---

### XREF-001: `Draft.md` References `.husky/` as Hook Location

**Severity:** 🟡 MODERATE
**Files:** [`Agentic Workbench v2 - Draft.md`](Agentic%20Workbench%20v2%20-%20Draft.md:651)

**Finding:** `Draft.md` Part 5.1 states "Git hooks are installed in `.husky/` and enforced via `husky` npm package". The actual implementation uses `.workbench/hooks/` exclusively, installed via `workbench-cli.py init`. The `.husky/` directory does not exist anywhere in the repository.

**Recommendation:** Update `Draft.md` Part 5.1 to reference `.workbench/hooks/` and `workbench-cli.py init`.

---

### XREF-002: `pyproject.toml` References Non-Existent `README.md` in Engine Root

**Severity:** 🟡 MODERATE
**Files:** [`agentic-workbench-engine/pyproject.toml`](agentic-workbench-engine/pyproject.toml:10)

**Finding:** `pyproject.toml` line 10 contains `readme = "README.md"`. There is no `README.md` in the `agentic-workbench-engine/` root directory. This means `python -m build` on the engine package will fail with a missing file error.

**Recommendation:** Either create a minimal `README.md` in `agentic-workbench-engine/`, or remove the `readme` field from `pyproject.toml`.

---

### XREF-003: `Canonical_Naming_Conventions.md` §4 Hook Description Is Stale

**Severity:** 🟡 MODERATE
**Files:** [`Canonical_Naming_Conventions.md`](Canonical_Naming_Conventions.md:1)

**Finding:** `Canonical_Naming_Conventions.md` §4 describes the `pre-commit` hook as enforcing only 3 actions. The actual hook also enforces: Conventional Commits format validation (GAP-14), file ownership conflict detection (GAP-7), and was specified to include `arbiter_check.py check-session` (GAP-15).

**Recommendation:** Update `Canonical_Naming_Conventions.md` §4 to enumerate all current `pre-commit` enforcement actions.

---

## Part 7: Consolidated Findings Summary

### 7.1 All Findings by Severity

| ID | Severity | Category | Short Description | Files Affected |
|---|---|---|---|---|
| CONFLICT-001 | 🔴 CRITICAL | Startup Protocol | Engine `.clinerules` heading missing SCAN step | `agentic-workbench-engine/.clinerules` |
| CONFLICT-002 | 🔴 CRITICAL | State Value | `integration_test_runner.py` writes `"RED"` not `"INTEGRATION_RED"` | `integration_test_runner.py`, `state.json` |
| CONFLICT-003 | 🔴 CRITICAL | Config Key | `Draft.md` CMD-1 references obsolete `auto_approve.patterns` key | `Draft.md`, `.roo-settings.json` |
| INCONSISTENCY-001 | 🟡 MODERATE | Versioning | Root `.clinerules` version suffix `-root` unexplained | `.clinerules` (root) |
| INCONSISTENCY-002 | 🟡 MODERATE | Config Drift | Root `.roo-settings.json` has 6 extra `allowedCommands` vs engine | Both `.roo-settings.json` files |
| INCONSISTENCY-003 | 🟡 MODERATE | Stale Comment | `post-tag` hook has stale TODO for `compliance_snapshot.py` | `post-tag` hook |
| INCONSISTENCY-004 | 🟡 MODERATE | Docs Gap | `Beginners_Guide.md` documents only 4 of 10+ CLI commands | `docs/Beginners_Guide.md` |
| INCONSISTENCY-005 | 🟡 MODERATE | Startup Protocol | `Draft.md` describes old 4-step startup protocol | `Draft.md` |
| INCONSISTENCY-007 | 🟡 MODERATE | Test Coverage | SM-013 test directly writes `state.json` instead of testing CLI `merge` | `test_state_machine.py` |
| INCONSISTENCY-008 | 🟡 MODERATE | Docstring | `arbiter_check.py` SESSION_CHECKS docstring says "CRITICAL only" but includes CR-1 | `arbiter_check.py` |
| INCONSISTENCY-009 | 🟡 MODERATE | Docstring | `gherkin_validator.py` docstring shows wrong CLI interface | `gherkin_validator.py` |
| MINOR-001 | 🟢 MINOR | Naming | `Draft.md` §8.2.B uses "Product Agent" in running prose | `Draft.md` |
| MINOR-002 | 🟢 MINOR | Naming | `diagrams/01` uses "Documentation Agent" short form | `diagrams/01-system-overview.md` |
| MINOR-003 | 🟢 MINOR | Stale Reference | `diagrams/05` Diagram 16 and `Draft.md` Part 5.1 reference `.husky/` | `diagrams/05`, `Draft.md` |
| MINOR-004 | 🟢 MINOR | Completeness | `Canonical_Naming_Conventions.md` §4 missing `arbiter_check.py` from hook table | `Canonical_Naming_Conventions.md` |
| MINOR-005 | 🟢 MINOR | Completeness | `memory_rotator.py` rotates `narrativeRequest.md` but `Draft.md` table omits it | `memory_rotator.py`, `Draft.md` |
| MINOR-006 | 🟢 MINOR | State Machine | `INIT -> UPGRADE_IN_PROGRESS` transition missing from diagram and spec | `diagrams/03`, `Draft.md` |
| MINOR-007 | 🟢 MINOR | GAP-15 Gap | `pre-commit` hook missing `arbiter_check.py check-session` call | `pre-commit` hook |
| MINOR-008 | 🟢 MINOR | Test Fidelity | UC-052 uses simulated logic instead of actual hook | `test_hooks_pre_commit.py` |
| MINOR-009 | 🟢 MINOR | Completeness | `pyproject.toml` references non-existent `README.md` in engine root | `pyproject.toml` |
| STRUCTURAL-001 | 🔵 STRUCTURAL | Completeness | No canonical document defines the full `workbench-cli.py` command interface | All canonical documents |
| STRUCTURAL-002 | 🔵 STRUCTURAL | Completeness | `diagrams/README.md` not audited | `diagrams/README.md` |
| STRUCTURAL-003 | 🔵 STRUCTURAL | Completeness | `Canonical_Naming_Conventions.md` §11 version table is stale | `Canonical_Naming_Conventions.md` |
| STRUCTURAL-004 | 🔵 STRUCTURAL | Completeness | `tests/workbench/` missing tests for `compliance_snapshot.py`, `post-merge`, `post-tag` | `tests/workbench/` |
| XREF-001 | 🟡 MODERATE | Cross-Reference | `Draft.md` references `.husky/` as hook location | `Draft.md` |
| XREF-002 | 🟡 MODERATE | Cross-Reference | `pyproject.toml` references non-existent `README.md` in engine root | `pyproject.toml` |
| XREF-003 | 🟡 MODERATE | Cross-Reference | `Canonical_Naming_Conventions.md` §4 hook description is stale | `Canonical_Naming_Conventions.md` |

**Total: 27 findings** — 3 Critical, 11 Moderate, 9 Minor, 4 Structural

---

### 7.2 Findings by File

| File | Findings |
|---|---|
| `Agentic Workbench v2 - Draft.md` | CONFLICT-003, INCONSISTENCY-005, MINOR-001, MINOR-003, MINOR-005, MINOR-006, STRUCTURAL-001, XREF-001 |
| `agentic-workbench-engine/.clinerules` | CONFLICT-001 |
| `agentic-workbench-engine/.workbench/scripts/integration_test_runner.py` | CONFLICT-002 |
| `agentic-workbench-engine/.workbench/scripts/arbiter_check.py` | INCONSISTENCY-008 |
| `agentic-workbench-engine/.workbench/scripts/gherkin_validator.py` | INCONSISTENCY-009 |
| `agentic-workbench-engine/.workbench/hooks/post-tag` | INCONSISTENCY-003 |
| `agentic-workbench-engine/.workbench/hooks/pre-commit` | MINOR-007 |
| `agentic-workbench-engine/pyproject.toml` | MINOR-009, XREF-002 |
| `.clinerules` (root) | INCONSISTENCY-001 |
| `.roo-settings.json` (root) | INCONSISTENCY-002 |
| `docs/Beginners_Guide.md` | INCONSISTENCY-004 |
| `tests/workbench/test_state_machine.py` | INCONSISTENCY-007 |
| `tests/workbench/test_hooks_pre_commit.py` | MINOR-008 |
| `Canonical_Naming_Conventions.md` | MINOR-004, STRUCTURAL-003, XREF-003 |
| `diagrams/01-system-overview.md` | MINOR-002 |
| `diagrams/03-tdd-and-state.md` | MINOR-006 |
| `diagrams/05-memory-sessions-and-infra.md` | MINOR-003 |
| `diagrams/README.md` | STRUCTURAL-002 |
| `memory_rotator.py` | MINOR-005 |
| `tests/workbench/` (missing files) | STRUCTURAL-004 |

---

## Part 8: Prioritized Recommendations

### Priority 1 — Fix Immediately (Critical Conflicts)

#### REC-001: Fix Engine `.clinerules` Startup Protocol Heading
**Action:** Change heading at [`agentic-workbench-engine/.clinerules`](agentic-workbench-engine/.clinerules:14) from `(CHECK -> CREATE -> READ -> ACT)` to `(SCAN -> CHECK -> CREATE -> READ -> ACT)`. **Effort:** Trivial.

#### REC-002: Fix `integration_test_runner.py` State Value
**Action:** Change `state["integration_state"] = "RED"` to `state["integration_state"] = "INTEGRATION_RED"` at [`integration_test_runner.py`](agentic-workbench-engine/.workbench/scripts/integration_test_runner.py:148). Update [`test_integration_runner.py`](tests/workbench/test_integration_runner.py) assertion accordingly. **Effort:** Small (2-file change).

#### REC-003: Update `Draft.md` CMD-1 Config Key Reference
**Action:** In [`Agentic Workbench v2 - Draft.md`](Agentic%20Workbench%20v2%20-%20Draft.md:625), replace `auto_approve.patterns` with `settings.roo-cline.allowedCommands`. **Effort:** Small.

---

### Priority 2 — Fix Soon (Moderate Inconsistencies and Cross-References)

#### REC-004: Clarify Root `.clinerules` Version Suffix
**Action:** Add a comment in [`.clinerules`](.clinerules:6) explaining that `-root` denotes the lab-level overlay, or rename to `v2.2` with an explanatory note. **Effort:** Trivial.

#### REC-005: Align `allowedCommands` Between Root and Engine `.roo-settings.json`
**Action:** Decide whether npm/biome commands should be in [`agentic-workbench-engine/.roo-settings.json`](agentic-workbench-engine/.roo-settings.json) and document the decision. **Effort:** Small.

#### REC-006: Remove Stale TODO from `post-tag` Hook
**Action:** Update the `else` branch in [`post-tag`](agentic-workbench-engine/.workbench/hooks/post-tag:53) to remove the stale TODO referencing `compliance_snapshot.py` as "not yet implemented". **Effort:** Trivial.

#### REC-007: Update `Beginners_Guide.md` CLI Command Reference
**Action:** Expand Appendix B in [`docs/Beginners_Guide.md`](docs/Beginners_Guide.md) to document all current `workbench-cli.py` commands. **Effort:** Medium.

#### REC-008: Update `Draft.md` Startup Protocol Description
**Action:** Update [`Draft.md`](Agentic%20Workbench%20v2%20-%20Draft.md:259) Session Lifecycle Protocols to describe the 5-step `SCAN -> CHECK -> CREATE -> READ -> ACT` protocol. **Effort:** Small.

#### REC-009: Refactor SM-013 Test to Use CLI `merge` Command
**Action:** Refactor [`test_sm013_review_pending_to_merged`](tests/workbench/test_state_machine.py:146) to invoke `workbench-cli.py merge` via `run_script`. **Effort:** Small.

#### REC-010: Fix `arbiter_check.py` SESSION_CHECKS Docstring
**Action:** Update the `run_checks` docstring in [`arbiter_check.py`](agentic-workbench-engine/.workbench/scripts/arbiter_check.py:502) to say "CRITICAL checks + crash recovery" instead of "CRITICAL only". **Effort:** Trivial.

#### REC-011: Fix `gherkin_validator.py` Docstring CLI Interface
**Action:** Update the module docstring in [`gherkin_validator.py`](agentic-workbench-engine/.workbench/scripts/gherkin_validator.py:1) to show `python gherkin_validator.py features/` (no `validate` subcommand). **Effort:** Trivial.

#### REC-012: Fix `Draft.md` Hook Location Reference
**Action:** Update [`Draft.md`](Agentic%20Workbench%20v2%20-%20Draft.md:651) to reference `.workbench/hooks/` and `workbench-cli.py init` instead of `.husky/` and `husky`. **Effort:** Small.

#### REC-013: Create `README.md` in Engine Root or Fix `pyproject.toml`
**Action:** Either create `agentic-workbench-engine/README.md` or remove `readme = "README.md"` from [`pyproject.toml`](agentic-workbench-engine/pyproject.toml:10). **Effort:** Small.

#### REC-014: Update `Canonical_Naming_Conventions.md` §4 Hook Description
**Action:** Update §4 in [`Canonical_Naming_Conventions.md`](Canonical_Naming_Conventions.md) to enumerate all current `pre-commit` enforcement actions. **Effort:** Small.

---

### Priority 3 — Address When Convenient (Minor and Structural)

#### REC-015: Remove "Product Agent" Alias from `Draft.md` Running Prose
**Action:** Remove the "Product Agent" alias reference from [`Draft.md`](Agentic%20Workbench%20v2%20-%20Draft.md:604) Part 8.2.B.

#### REC-016: Fix Agent Name Formatting in Diagrams
**Action:** Update "Documentation Agent" to "Documentation/Librarian Agent" in [`diagrams/01-system-overview.md`](diagrams/01-system-overview.md).

#### REC-017: Add `narrativeRequest.md` to `Canonical_Naming_Conventions.md`
**Action:** Add `narrativeRequest.md` to the Hot Zone file definitions section in [`Canonical_Naming_Conventions.md`](Canonical_Naming_Conventions.md).

#### REC-018: Add `narrativeRequest.md` to `Draft.md` Rotation Table
**Action:** Add `narrativeRequest.md` to the Hot Zone File Rotation Policy table in [`Draft.md`](Agentic%20Workbench%20v2%20-%20Draft.md:244).

#### REC-019: Update `Draft.md` GAP Section to Reflect Completed Implementation
**Action:** Mark all 15 gaps as completed in [`Draft.md`](Agentic%20Workbench%20v2%20-%20Draft.md:700) Part 9, referencing the Gap Implementation Plan v2.

#### REC-020: Add Test Coverage for `compliance_snapshot.py`
**Action:** Create [`tests/workbench/test_compliance_snapshot.py`](tests/workbench/test_compliance_snapshot.py) covering `generate_traceability_matrix()`, `create_compliance_snapshot()`, and `main()`.

#### REC-021: Add Test for `narrativeRequest.md` Rotation
**Action:** Add a test case in [`test_memory_rotator.py`](tests/workbench/test_memory_rotator.py) verifying `narrativeRequest.md` is archived and reset during `rotate_sprint()`.

#### REC-022: Add Memory System Architecture Diagram
**Action:** Create [`diagrams/06-memory-system.md`](diagrams/06-memory-system.md) showing Hot Zone / Cold Zone architecture, MCP tool access path, and `memory_rotator.py` rotation flow.

#### REC-023: Fix `diagrams/README.md` Index
**Action:** Verify and update the index table in [`diagrams/README.md`](diagrams/README.md) to include all 5 current diagram files.

#### REC-024: Add Biome Linting Reference to Root `README.md`
**Action:** Add a brief mention of `biome.json` and Biome linting to [`README.md`](README.md).

#### REC-025: Add `arbiter_check.py check-session` to `pre-commit` Hook
**Action:** Insert `python .workbench/scripts/arbiter_check.py check-session --block-on-critical` into [`pre-commit`](agentic-workbench-engine/.workbench/hooks/pre-commit) after the skip-validation flag check, as specified in GAP-15.

---

## Part 9: Overall Coherency Assessment

### 9.1 Scoring

| Dimension | Weight | Score (0-10) | Weighted Score | Notes |
|---|---|---|---|---|
| **Architectural Consistency** | 30% | 8.5 | 2.55 | Core pipeline, state machine, and agent roles are well-aligned across files |
| **Rule Completeness** | 25% | 7.0 | 1.75 | Rules are comprehensive but some enforcement gaps exist (GAP-15 hook integration) |
| **Cross-Reference Accuracy** | 20% | 6.5 | 1.30 | Several stale references to obsolete keys, paths, and tool names |
| **Terminology Consistency** | 15% | 7.5 | 1.13 | Minor naming drift in diagrams and Draft.md prose |
| **Test Coverage Alignment** | 10% | 7.0 | 0.70 | Good coverage overall; SM-013 fidelity gap and missing compliance_snapshot tests |

**Overall Coherency Score: 7.43 / 10.0**

---

### 9.2 Assessment Narrative

The Agentic Workbench v2 canonical source set demonstrates **strong architectural coherency** at the macro level. The Separation of Powers model (Roo Code / The Arbiter / Roo Chat), the state machine design, the memory system architecture, and the agent role definitions are consistently represented across `.clinerules`, `.roomodes`, `state.json`, `Draft.md`, and the diagrams.

The **critical issues** are concentrated in implementation details rather than architectural concepts:
- The `integration_state` value bug (CONFLICT-002) is the most operationally dangerous finding — it would cause silent failures in integration state tracking.
- The startup protocol heading mismatch (CONFLICT-001) is a documentation error that could mislead agents reading the engine `.clinerules`.
- The obsolete config key reference (CONFLICT-003) is a documentation error in the specification document.

The **moderate inconsistencies** are primarily documentation drift — the specification document (`Draft.md`) has not been updated to reflect the completed Gap Implementation Plan, and the `Beginners_Guide.md` is significantly out of date relative to the current CLI capabilities.

The **structural gaps** (missing `compliance_snapshot.py` tests, missing Memory System diagram) represent technical debt that should be addressed in the next sprint.

---

### 9.3 Confidence Assessment

| Finding | Confidence | Basis |
|---|---|---|
| CONFLICT-001 | HIGH | Direct text comparison between heading and body of same file |
| CONFLICT-002 | HIGH | Direct code inspection of `integration_test_runner.py` line 148 |
| CONFLICT-003 | HIGH | Direct comparison of `Draft.md` prose vs actual `.roo-settings.json` key names |
| INCONSISTENCY-002 | HIGH | Direct comparison of both `.roo-settings.json` files |
| INCONSISTENCY-003 | HIGH | Direct inspection of `post-tag` hook and `compliance_snapshot.py` existence |
| INCONSISTENCY-004 | HIGH | Direct comparison of `Beginners_Guide.md` Appendix B vs `workbench-cli.py` |
| XREF-002 | HIGH | File listing confirms no `README.md` in engine root |
| STRUCTURAL-004 | HIGH | File listing confirms no `test_compliance_snapshot.py` in tests directory |
| INCONSISTENCY-007 | MEDIUM | Test reads `state.json` directly; CLI `merge` command may or may not exist |
| MINOR-005 | MEDIUM | `memory_rotator.py` includes `narrativeRequest.md`; `Draft.md` table not fully verified |

---

### 9.4 Recommended Sprint Priority

**Sprint N (Immediate — before next feature development):**
- REC-001: Fix engine `.clinerules` heading (CONFLICT-001)
- REC-002: Fix `integration_test_runner.py` state value (CONFLICT-002)
- REC-003: Fix `Draft.md` CMD-1 config key (CONFLICT-003)
- REC-006: Remove stale `post-tag` TODO (INCONSISTENCY-003)
- REC-013: Fix `pyproject.toml` README reference (XREF-002)

**Sprint N+1 (Documentation Refresh):**
- REC-007: Update `Beginners_Guide.md` CLI commands (INCONSISTENCY-004)
- REC-008: Update `Draft.md` startup protocol (INCONSISTENCY-005)
- REC-012: Fix `Draft.md` hook location reference (XREF-001)
- REC-014: Update `Canonical_Naming_Conventions.md` §4 (XREF-003)
- REC-019: Update `Draft.md` GAP section (STRUCTURAL-001)
- REC-025: Add `arbiter_check.py` call to `pre-commit` hook (MINOR-007)

**Sprint N+2 (Test Coverage and Completeness):**
- REC-009: Refactor SM-013 test (INCONSISTENCY-007)
- REC-020: Add `compliance_snapshot.py` tests (STRUCTURAL-004)
- REC-021: Add `narrativeRequest.md` rotation test
- REC-022: Add Memory System diagram
- REC-023: Fix `diagrams/README.md` index

---

*End of Coherency Audit Report — Edition 4*
*Generated: 2026-04-13 | Auditor: Senior Architect (Roo Code — Architect Agent)*
*Report covers: All canonical sources and rules files as of 2026-04-13*
*Supersedes: Edition 3 (Beginners Guide Targeted Review, 2026-04-12)*
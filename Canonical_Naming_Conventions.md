# Agentic Workbench v2 — Canonical Naming Conventions

**Author:** Senior Architect (Roo)
**Date:** 2026-04-12
**Status:** AUTHORITY — This document is the single source of truth for all named entities. When in doubt, this document wins.

---

## Purpose

This document eliminates all ambiguity about what things are called across the Agentic Workbench v2 documentation suite. Every named entity has exactly **one canonical form** used everywhere, and **zero alias forms** in any specification or implementation document.

---

## 1. System Actors (The Triad)

These are the three top-level entities in the architecture. They are mutually exclusive and collectively exhaustive.

| Canonical Name | Role Subtitle | What It Is NOT Called | Notes |
|---|---|---|---|
| **Roo Code** | The Agent | "The AI", "The LLM", "Cline", "Roo" (standalone) | VS Code extension. Probabilistic. |
| **The Arbiter** | The Governor | "The Orchestrator", "The State Manager", "Python scripts" (as a name) | Python scripts + Git hooks. Deterministic. |
| **Roo Chat** | The HITL Cockpit / The Director | "The Chat", "The Human", "The Cockpit", "HITL", "Roo" (standalone) | VS Code chat panel. Human interface only. |

### Canonical Usage Rules

- **Roo Code** is the entity that *acts* (writes code, runs modes)
- **The Arbiter** is the entity that *enforces* (runs gates, writes state)
- **Roo Chat** is the entity that *decides* (approves, injects intent)
- Never refer to "The Orchestrator" as a system actor — that is a Roo Code agent mode (see §2)

---

## 2. Agent Modes (Roo Code Roles)

Agent modes are specialized operational states of **Roo Code** (the Agent). Each mode has exactly one canonical name.

| Canonical Mode Name | Pipeline Stage | Aliases (Forbidden) | Primary Responsibility |
|---|---|---|---|
| **Architect Agent** | Stage 1 | "Product Agent", "Stage 1 Agent", "Intent Agent" | Translates human narrative → Gherkin `.feature` files |
| **Test Engineer Agent** | Stage 2 / 2b | "Test Agent", "QA Agent", "Testing Agent" | Writes failing `.spec.ts` test suites from Gherkin |
| **Developer Agent** | Stage 3 | "Code Agent", "Implementation Agent", "Stage 3 Agent" | Writes feature source code to satisfy tests |
| **Orchestrator Agent** | Stage 4 + Lifecycle | "Review Agent", "Stage 4 Agent" | Read-only oversight; dependency monitoring when blocked |
| **Reviewer / Security Agent** | Stage 4 | "Security Agent", "PR Reviewer" | Static analysis + security scans on PRs |
| **Documentation / Librarian Agent** | Background | "Doc Agent", "Wiki Agent" | Auto-generates OpenAPI, topology graphs, executive summaries |

### Canonical Usage Rules

- Always use the **full canonical name** when first introducing a mode
- Use the **canonical short form** after introduction (e.g., "the Architect" not "the Product Agent")
- "Product Agent" is a **documented conversational alias** — permitted in Glossary entries and agent prompts, but forbidden in running prose and implementation documents

---

## 3. Python Arbiter Scripts

These are deterministic programs owned by **The Arbiter**. Each script has exactly one canonical name.

| Canonical Script Name | What It Is NOT Called | Purpose |
|---|---|---|
| **`test_orchestrator.py`** | "test_runner.py", "Test Orchestrator" (as a Roo mode) | Two-phase test execution (feature scope + full regression) |
| **`integration_test_runner.py`** | "integration.py", "Integration Runner" (as a Roo mode) | Runs `*.integration.spec.ts` files; writes `integration_state` |
| **`dependency_monitor.py`** | "dep_monitor.py", "Dependency Checker" | Polls `feature_registry`; auto-unblocks `DEPENDENCY_BLOCKED` features |
| **`gherkin_validator.py`** | "gherkin_lint.py", "Feature Validator" | Validates Gherkin syntax; parses `@depends-on` tags |
| **`memory_rotator.py`** | "rotation.py", "Memory Rotator script" | Applies per-file rotation policy at sprint end |
| **`audit_logger.py`** | "logger.py", "Audit Trail" | Saves immutable session metadata to `docs/conversations/` |
| **`crash_recovery.py`** | "heartbeat.py", "Recovery Daemon" | Writes 5-minute heartbeat to `session-checkpoint.md` |
| **`arbiter_check.py`** | "compliance_check.py", "Health Check" | Runs session startup compliance scan; checks for violations of `.clinerules` rules |
| **`compliance_snapshot.py`** | "snapshot.py", "Compliance Report" | Generates compliance documentation (PDFs + Traceability Matrix) on tag events |

### Canonical Usage Rules

- Always prefix with **"The Arbiter's"** when referring to script actions: *"The Arbiter's `test_orchestrator.py` runs..."*
- Never refer to a script as "the Orchestrator" — that refers to the Orchestrator Agent mode
- Scripts are **lowercase with underscores**; mode names are **Title Case**

---

## 4. Git Hooks

| Canonical Hook Name | What It Is NOT Called | Trigger | Purpose |
|---|---|---|---|
| **`pre-commit`** | "Commit hook", "precommit" | Before `git commit` | Runs `arbiter_check.py check-session` (GAP-15) + `gherkin_validator.py` + `biome.json` linting; blocks if `state.json` modified by non-Arbiter |
| **`pre-push`** | "Push hook", "prepush" | Before `git push` | Blocks push if state is `RED/REGRESSION_RED/INTEGRATION_RED/PIVOT_IN_PROGRESS`; blocks direct push to `main` |
| **`post-merge`** | "Merge hook", "postmerge" | After PR merge | Runs `dependency_monitor.py check-unblock`; auto-unblocks blocked features |
| **`post-tag`** | "Tag hook", "posttag" | After `git tag` | Triggers compliance snapshot (PDFs + Traceability Matrix) |

**Hook Implementation:** Hooks are installed in `.workbench/hooks/` (not `.husky/`). Installation via `workbench-cli.py install-hooks`.

### Canonical Usage Rules

- Hook names are ** hyphenated** (not camelCase, not underscore)
- Always refer to hooks as **owned by The Arbiter**, not Roo Code

---

## 5. Key Artifacts & Files

| Canonical Artifact | Location | Owner | What It Is NOT Called |
|---|---|---|---|
| **`state.json`** | Repo root | The Arbiter | "the state file", "state", "json state" |
| **`handoff-state.md`** | `memory-bank/hot-context/` | Agents + Arbiter | "handoff.md", "hand-off.md", "state-handoff.md" |
| **`activeContext.md`** | `memory-bank/hot-context/` | Agents | "context.md", "active-context.md", "session-context.md" |
| **`.feature` files** | `/features/` or `_inbox/` | Architect Agent | "feature files", "gherkin files", "requirement files" |
| **`feature_registry`** | `state.json` key | The Arbiter | "feature map", "requirement registry", "dependency registry" |
| **`file_ownership`** | `state.json` key | The Arbiter | "ownership map", "file map" |
| **`arbiter_capabilities`** | `state.json` key | The Arbiter | "capabilities map", "permission map" |
| **`.clinerules`** | Repo root | The Workbench | "rules", "cursorrules" (as primary name), "clinerules file" |
| **`.roomodes`** | Repo root | The Workbench | "modes", "role definitions" |
| **`workbench-cli.py`** | Global install (not in app repo) | The Workbench | "cli.py", "workbench.py", "bootstrapper.py" |
| **`biome.json`** | Repo root | The Workbench | "linter config", "linting rules" |

### Canonical Usage Rules

- **`state.json` keys** are always referred to with the `state.json.` prefix: `state.json.feature_registry`, `state.json.regression_state`
- **`.clinerules`** is the canonical guardrail file; `.cursorrules` is a Cursor IDE alias only
- **Locations** are always path-formatted: `/src`, `/tests/unit/`, `/tests/integration/` (no trailing slash, no backslash)

---

## 6. Pipeline States

All states in `state.json.state`. Each state has exactly one meaning.

| Canonical State | Meaning | Blocking? | What It Is NOT Called |
|---|---|---|---|
| `INIT` | Workbench initialized, no active feature | No | "Initial", "Start" |
| `STAGE_1_ACTIVE` | Feature in Stage 1 (Architect Agent iterating Gherkin) | No | "Stage 1", "Architecting" |
| `REQUIREMENTS_LOCKED` | `.feature` files approved by human (HITL 1) | No | "Requirements Approved", "Spec Locked" |
| `DEPENDENCY_BLOCKED` | Feature blocked on unmet `@depends-on` dependency | Yes (Stage 3) | "Blocked", "Waiting on Dependency" |
| `RED` | Unit tests failing (initial or after pivot) | No | "Test Failing", "Red State" |
| `FEATURE_GREEN` | Phase 1 (feature-scope) tests pass | No | "Feature Green", "Local Green" |
| `REGRESSION_RED` | Phase 2 (full regression) found broken test(s) | **Yes** | "Regression", "Full Suite Failing" |
| `GREEN` | Phase 1 + Phase 2 both pass | No | "All Green", "Suite Clean" |
| `CLEAN` | Phase 2 full regression passed | No | Value of `regression_state` field (not a `state.json.state` value) |
| `INTEGRATION_CHECK` | Arbiter running integration test suite | No | "Running Integration Tests" |
| `INTEGRATION_RED` | Integration tests failing | **Yes** | "Integration Failing" |
| `REVIEW_PENDING` | All gates passed; awaiting HITL 2 approval | No | "Ready for Review", "Pending Approval" |
| `MERGED` | Feature merged to `develop` | No | "Done", "Complete", "Shipped" |
| `PIVOT_IN_PROGRESS` | Mid-stage requirement change in progress | **Yes** | "Pivot", "Delta In Progress" |
| `PIVOT_APPROVED` | Delta approved by human (HITL 1.5); merge pending | No | "Delta Approved" |
| `UPGRADE_IN_PROGRESS` | Workbench engine upgrade in progress | **Yes** | "Upgrading", "Engine Upgrade" |

### Canonical Usage Rules

- States are **UPPER_SNAKE_CASE** in `state.json` and in prose when referring to the exact value
- Never use "Green" or "Red" alone — always qualify: `FEATURE_GREEN` vs. `GREEN` vs. `INTEGRATION_CHECK`
- `REGRESSION_RED` and `INTEGRATION_RED` are the only **blocking** states besides `DEPENDENCY_BLOCKED` and `PIVOT_IN_PROGRESS`

---

## 7. Pipeline Stages

| Canonical Stage Name | Aliases (Forbidden) | Agent Active |
|---|---|---|
| **Stage 1: Intent to Contract** | "Stage 1", "Architect Stage", "Gherkin Stage" | Architect Agent |
| **Stage 2: Test Suite Authoring** | "Stage 2", "TDD Stage", "Test Stage" | Test Engineer Agent |
| **Stage 2b: Integration Contract Scaffolding** | "Stage 2b", "Integration Stage" | Test Engineer Agent |
| **Stage 3: The Autonomous Execution Engine** | "Stage 3", "Code Stage", "Implementation Stage" | Developer Agent |
| **Stage 4: Validation and Delivery** | "Stage 4", "Review Stage", "Delivery Stage" | Orchestrator Agent / Reviewer/Security Agent |

---

## 8. HITL Gates

| Canonical Gate Name | Trigger | Who Approves |
|---|---|---|
| **HITL 1** (The Requirement Gate) | `.feature` files ready for approval | Product Owner |
| **HITL 1.5** (The Delta Approval) | Pivot branch Git diff ready for review | Human (any role) |
| **HITL 2** (The Delivery Gate) | PR ready for merge approval | Lead Engineer / Architect |

---

## 9. Test Naming Conventions

| Test Type | File Pattern | ID Prefix | Scope |
|---|---|---|---|
| **Unit / Acceptance Test** | `/tests/unit/{REQ-NNN}-*.spec.ts` | `REQ-NNN` | Single feature |
| **Integration Test** | `/tests/integration/{FLOW-NNN}-{slug}.integration.spec.ts` | `FLOW-NNN` | Cross-feature flow |
| **Regression Run** | All `/tests/unit/**/*.spec.ts` + all `/tests/integration/**/*.spec.ts` | N/A | Full suite |

### Canonical Usage Rules

- Never call an integration test a "unit test" or vice versa
- `REQ-NNN` = single requirement; `FLOW-NNN` = cross-boundary flow (distinct namespaces)
- Phase 1 = feature-scope only; Phase 2 = full regression suite

---

## 10. Forbidden Terminology

The following terms are **forbidden** in all specification and implementation documents. They cause ambiguity and must be replaced with canonical terms:

| Forbidden Term | Replace With |
|---|---|
| "The Orchestrator" (when referring to scripts) | The Arbiter's `{script_name}.py` |
| "The Orchestrator" (when referring to a system actor) | **Roo Code in Orchestrator Agent mode** |
| "Product Agent" | **Architect Agent** |
| "Workbench Orchestrator" | **Python Arbiter's `test_orchestrator.py`** |
| "clinerules / cursorrules" (as a slash notation) | **`.clinerules`** (canonical) |
| "state" (when referring to `state.json`) | **`state.json`** |
| "Stage 1/2/3/4" (as standalone nouns) | **Stage 1: Intent to Contract**, etc. |
| "Green" / "Red" (unqualified) | **`FEATURE_GREEN`**, `RED`, `REGRESSION_RED`, `INTEGRATION_RED` |
| "wild mainline" (for `develop`) | **primary integration mainline** |
| "the memory rotator" (as agent name) | **The Arbiter's `memory_rotator.py`** |
| "develop branch" | **`develop` branch** (backticks for code literals) |

---

## 11. Version & Schema Tracking

| Document | Version | Tracks |
|---|---|---|
| `Agentic Workbench v2 - Draft.md` | v2.0 (updated 2026-04-13) | Architectural specification |
| `Agentic_Workbench_v2_Implementation_Strategy.md` | v2.1 | Implementation sequence (Sprint 0–3) |
| `Spec_Gap_Fix_Plan_Integration_NonRegression_CrossFeature.md` | v2.1 | Gap fixes incorporated into spec |
| `Canonical_Naming_Conventions.md` | v2.2 | This document — single source of truth (self-referential) |
| `plans/Coherency_Review_Report.md` | v1.0 (2026-04-13) | Coherency audit report |

Whenever a new feature or gap fix is incorporated into the spec, this naming conventions document should be updated to reflect any new named entities introduced.

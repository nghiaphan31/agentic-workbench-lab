# Workbench Lifecycle Test Plan

**Author:** Senior Tester / Test Engineer Agent
**Scope:** Project Initiation → Code Merge
**Reference:** `Agentic Workbench v2 - Draft.md`, existing test suite at `tests/workbench/`

---

## 1. Executive Summary

This plan defines test coverage for the complete Agentic Workbench v2 lifecycle, from `workbench-cli.py init` through feature code merged into `main`. The existing test suite (`tests/workbench/`) covers ~40% of required scenarios — primarily unit-level arbiter script tests. Significant gaps exist in Phase 0, Stage 1 (Architect Agent), Stage 2 (Test Engineer Agent), and cross-stage integration scenarios.

---

## 2. Test Scope

### 2.1 In-Scope

| Pipeline Phase | Description | Status |
|---|---|---|
| **Bootstrap** | `workbench-cli.py init`, hook installation, `workbench-cli.py upgrade` | Partially tested |
| **Phase 0** | Ideation pipeline — narrativeRequest.md creation, Socratic interrogation | **NOT TESTED** |
| **Stage 1** | Architect Agent — `.feature` creation, REQ-ID assignment, HITL 1 gate | **NOT TESTED** |
| **Stage 2** | Test Engineer Agent — unit test authoring, RED state confirmation | **NOT TESTED** |
| **Stage 2b** | Integration scaffolding — `.integration.spec.ts` authoring | **NOT TESTED** |
| **Stage 3** | Developer Agent — RED→GREEN loop, two-phase test execution | Partially tested (state machine SM-001–SM-014) |
| **Stage 4** | Integration gate, review, merge | Partially tested (merge command GAP-5d) |
| **Arbiter Scripts** | test_orchestrator, integration_test_runner, dependency_monitor, arbiter_check, gherkin_validator, memory_rotator, audit_logger, crash_recovery, compliance_snapshot | ~60% coverage |
| **Git Hooks** | pre-commit, pre-push, post-merge, post-tag | Partially tested |
| **Phase 2A Inbox** | Draft feature capture, `@draft` tagging | **NOT TESTED** |
| **Phase 2B Pivot** | Delta injection, HITL 1.5, test invalidation | **NOT TESTED** |

### 2.2 Out of Scope

- Security penetration testing (owned by Reviewer/Security Agent)
- Performance/load testing of arbiter scripts
- IDE integration testing (Roo Code extension itself)

---

## 3. Existing Test Coverage Map

| Test File | Coverage | Gap |
|---|---|---|
| `test_workbench_cli.py` | UC-041–050, GAP-3d, GAP-5d, GAP-6f | Missing `init` with existing remote, `upgrade` rollback |
| `test_state_machine.py` | SM-001–SM-014 | Missing DEPENDENCY_BLOCKED→RED auto-transitions |
| `test_test_orchestrator.py` | UC-015–021 | Missing Phase 2 regression failure capture |
| `test_integration_runner.py` | UC-022–027 | Missing syntax-only validation on Stage 2b input |
| `test_dependency_monitor.py` | UC-004–006 | Missing auto-unblock when dependency merges |
| `test_arbiter_check.py` | GAP-15u | Covers check functions; missing `check-session` integration |
| `test_gherkin_validator.py` | UC-007–014, GAP-13b/c/d | Complete |
| `test_hooks_pre_commit.py` | UC-051–056 | Missing Conventional Commits validation |
| `test_hooks_pre_push.py` | UC-057–064 | Missing arbiter_capabilities enforcement |
| `test_hooks_post_merge.py` | UC-PM-001–004 | Missing state transitions on merge |
| `test_hooks_post_tag.py` | UC-PT-001–005 | Complete |
| `test_memory_rotator.py` | UC-028–032 | Complete |
| `test_audit_logger.py` | UC-033–036 | Complete |
| `test_crash_recovery.py` | UC-037–040 | Missing daemon heartbeat race conditions |
| `test_compliance_snapshot.py` | UC-CS-001–006 | Complete |
| `test_archive_query_server.py` | GAP-11e | Complete |
| `test_roomodes_format.py` | GAP-12d | Complete |
| `test_e2e_pipeline.py` | UC-065–069 | Missing full HITL simulation |

---

## 4. Phase-by-Phase Test Requirements

### 4.1 Bootstrap — `workbench-cli.py init` / `upgrade`

| ID | Scenario | Type | Status |
|---|---|---|---|
| B-001 | `init` creates full scaffold (`.clinerules`, `.roomodes`, `.roo-settings.json`, `state.json`, `memory-bank/`, `features/`, `tests/`) | Unit | ✅ Covered (UC-041) |
| B-002 | `init` fails gracefully when target directory is not empty | Unit | ✅ Covered (UC-042) |
| B-003 | `init` installs hooks as executable files | Unit | ✅ Covered (GAP-3d) |
| B-004 | `init` skips hook installation with `--no-hooks` flag | Unit | **GAP** |
| B-005 | `upgrade` safe state (INIT) — full upgrade | Unit | ✅ Covered (UC-043) |
| B-006 | `upgrade` safe state (MERGED) — full upgrade | Unit | ✅ Covered (UC-044) |
| B-007 | `upgrade` unsafe state (RED) — aborts | Unit | ✅ Covered (UC-045) |
| B-008 | `upgrade` unsafe state (REGRESSION_RED) — aborts | Unit | ✅ Covered (UC-046) |
| B-009 | `upgrade` unsafe state (DEPENDENCY_BLOCKED) — aborts | Unit | **GAP** |
| B-010 | `upgrade` unsafe state (PIVOT_IN_PROGRESS) — aborts | Unit | **GAP** |
| B-011 | `status` displays all state.json fields | Unit | ✅ Covered (UC-047) |
| B-012 | `status` fails gracefully when state.json missing | Unit | ✅ Covered (UC-048) |
| B-013 | `rotate` delegates to memory_rotator | Unit | ✅ Covered (UC-049) |
| B-014 | `rotate` fails gracefully when memory_rotator not found | Unit | ✅ Covered (UC-050) |
| B-015 | `install-hooks` can be re-run safely (idempotent) | Unit | **GAP** |

---

### 4.2 Phase 0 — Ideation & Discovery Pipeline

| ID | Scenario | Type | Status |
|---|---|---|---|
| P0-001 | Human submits unstructured prompt; `narrativeRequest.md` created in `memory-bank/hot-context/` | Integration | **GAP** |
| P0-002 | Architect Agent performs Socratic interrogation via questions | Manual/Simulation | **GAP** |
| P0-003 | "Five Whys" deep dive produces refined narrative | Manual/Simulation | **GAP** |
| P0-004 | Architect Agent synthesizes multi-turn dialogue into `narrativeRequest.md` | Integration | **GAP** |
| P0-005 | Human approves/rejects/modifies `narrativeRequest.md` | Manual | **GAP** |
| P0-006 | Approved `narrativeRequest.md` triggers Stage 1 via HITL 0 gate | Integration | **GAP** |

**Note:** Phase 0 is primarily a human-driven workflow. Testing requires simulation of the human agent via mock Roo Chat responses.

---

### 4.3 Stage 1 — Architect Agent (`.feature` Creation)

| ID | Scenario | Type | Status |
|---|---|---|---|
| S1-001 | REQ-ID assigned to new `.feature` file in `/features/` | Unit | **GAP** |
| S1-002 | Filename format is `{REQ-NNN}-{slug}.feature` | Unit | **GAP** |
| S1-003 | `@REQ-NNN` tag present as first tag in every `.feature` file | Unit | **GAP** |
| S1-004 | `@depends-on` tag validated against `feature_registry` | Unit | ✅ Covered (UC-007–014, GAP-13) |
| S1-005 | Draft feature in `_inbox/` has `@draft` tag, no REQ-ID | Unit | **GAP** |
| S1-006 | Feature promoted from `_inbox/` to `/features/` receives REQ-ID | Integration | **GAP** |
| S1-007 | Gherkin syntax validated by `gherkin_validator.py` | Unit | ✅ Covered (UC-007–014) |
| S1-008 | HITL 1: Human reviews PR, approves, triggers `start-feature` | Manual | **GAP** |
| S1-009 | HITL 1 rejection: Human requests changes, stage stays `STAGE_1_ACTIVE` | Manual | **GAP** |
| S1-010 | `cmd_start_feature` sets `state.json.state = STAGE_1_ACTIVE` | Unit | **GAP** |
| S1-011 | `cmd_lock_requirements` transitions `STAGE_1_ACTIVE` → `RED` | Unit | **GAP** |

---

### 4.4 Stage 2 — Test Engineer Agent (Unit Test Authoring)

| ID | Scenario | Type | Status |
|---|---|---|---|
| S2-001 | Unit test file created at `/tests/unit/{REQ-NNN}-*.spec.ts` | Integration | **GAP** |
| S2-002 | Test file contains import of `.feature` file for traceability | Unit | **GAP** |
| S2-003 | Tests are initially failing (RED state confirmed by arbiter) | Integration | **GAP** |
| S2-004 | `state.json.state = RED` after test run | Unit | ✅ Covered (SM-001) |
| S2-005 | `state.json.active_req_id` set to active feature | Unit | **GAP** |
| S2-006 | Test Engineer Agent cannot write to `/src` | Unit | **GAP** |
| S2-007 | Parallel Stage 2: Second feature can enter Stage 2 while first is in Stage 2 | Integration | **GAP** |
| S2-008 | Parallel Stage 2: Second feature blocked from Stage 3 until first completes | Integration | **GAP** |

---

### 4.5 Stage 2b — Integration Contract Scaffolding

| ID | Scenario | Type | Status |
|---|---|---|---|
| S2B-001 | Integration skeleton created at `/tests/integration/*.integration.spec.ts` | Integration | **GAP** |
| S2B-002 | Integration tests tagged with `FLOW-NNN` ID | Unit | **GAP** |
| S2B-003 | Integration test reads from `feature_registry` for already-merged features | Unit | **GAP** |
| S2B-004 | Integration tests are intentionally failing (contracts, not implementations) | Integration | **GAP** |
| S2B-005 | Syntax-only validation by `integration_test_runner.py` (no execution) | Unit | ✅ Covered (UC-022–027) |
| S2B-006 | Stage 2b skipped when `/tests/integration/` does not exist | Integration | **GAP** |
| S2B-007 | `cmd_start_feature --integration` sets `state.json.integration_state = STAGE_2B_ACTIVE` | Unit | **GAP** |

---

### 4.6 Stage 3 — Developer Agent (RED→GREEN Loop)

| ID | Scenario | Type | Status |
|---|---|---|---|
| S3-001 | Dependency Gate: Stage 3 blocked when `@depends-on` not MERGED | Integration | ✅ Covered (SM-003) |
| S3-002 | `DEPENDENCY_BLOCKED` state set when dependency not met | Unit | ✅ Covered (SM-003) |
| S3-003 | Orchestrator Agent activates on DEPENDENCY_BLOCKED for monitoring | Integration | **GAP** |
| S3-004 | Auto-unblock: Stage 3 resumes when dependency reaches MERGED | Integration | **GAP** |
| S3-005 | Test Phase 1: Only `{REQ-NNN}` scoped tests run | Unit | ✅ Covered (UC-015) |
| S3-006 | Test Phase 2: All unit + all integration tests run after Phase 1 GREEN | Unit | ✅ Covered (UC-016–018) |
| S3-007 | `REGRESSION_RED`: Previously passing test fails after new feature | Integration | ✅ Covered (SM-005) |
| S3-008 | `REGRESSION_RED` is blocking — pipeline cannot advance to Stage 4 | Unit | ✅ Covered (SM-005) |
| S3-009 | Regression fix: Developer addresses regression, Phase 2 passes | Integration | ✅ Covered (SM-006) |
| S3-010 | `FEATURE_GREEN` achieved when Phase 1 passes | Unit | ✅ Covered (SM-002) |
| S3-011 | `GREEN` achieved when Phase 2 passes (regression_state = CLEAN) | Unit | ✅ Covered (SM-004) |
| S3-012 | Developer Agent cannot self-declare GREEN — Arbiter confirms | Unit | ✅ Covered (GAP-15u) |
| S3-013 | `file_ownership` map updated after every commit | Unit | **GAP** |
| S3-014 | File conflict detected when two features touch same source file | Integration | **GAP** |
| S3-015 | `cmd_set_red` manually sets RED state | Unit | ✅ Covered (UC-046 context) |

---

### 4.7 Stage 4 — Review & Merge

| ID | Scenario | Type | Status |
|---|---|---|---|
| S4-001 | `GREEN` + `integration_state = GREEN` required before review | Integration | ✅ Covered (SM-007–SM-010) |
| S4-002 | Integration tests execute (not just syntax-validate) at Stage 4 | Integration | ✅ Covered (SM-008–SM-010) |
| S4-003 | `INTEGRATION_RED`: Developer Agent re-activated to fix integration failure | Integration | ✅ Covered (SM-009) |
| S4-004 | `INTEGRATION_RED` → `GREEN` loop until all integration tests pass | Integration | ✅ Covered (SM-010) |
| S4-005 | Reviewer/Security Agent performs static analysis | Manual | **GAP** |
| S4-006 | HITL 2: Human approves PR for merge | Manual | **GAP** |
| S4-007 | `cmd_review_pending` validates all gates before human review | Unit | **GAP** |
| S4-008 | `cmd_merge` transitions `REVIEW_PENDING` → `MERGED` | Unit | ✅ Covered (GAP-5d) |
| S4-009 | `MERGED`: `feature_registry` entry updated, `file_ownership` cleared | Unit | ✅ Covered (SM-013) |
| S4-010 | Merge blocked when state ≠ REVIEW_PENDING | Unit | ✅ Covered (GAP-5d) |
| S4-011 | Post-merge hook triggers — state.json reset, memory rotation | Integration | **GAP** |

---

### 4.8 Phase 2A — Inbox (Non-Blocking Ideas)

| ID | Scenario | Type | Status |
|---|---|---|---|
| IN-001 | Human submits shower-thought prompt to `_inbox/` | Manual | **GAP** |
| IN-002 | Architect Agent lightweight chunking with `@draft` tag | Integration | **GAP** |
| IN-003 | No REQ-ID assigned while in `_inbox/` | Unit | **GAP** |
| IN-004 | Gherkin syntax check runs on `@draft` files but no REQ-ID enforcement | Unit | **GAP** |
| IN-005 | Product Owner reviews `_inbox/`, approves for promotion | Manual | **GAP** |
| IN-006 | Feature promoted: REQ-ID assigned, moved to `/features/`, `state = STAGE_1_ACTIVE` | Integration | **GAP** |
| IN-007 | Feature rejected: remains in `_inbox/` | Manual | **GAP** |

---

### 4.9 Phase 2B — Pivot (Mid-Stage Change)

| ID | Scenario | Type | Status |
|---|---|---|---|
| PV-001 | Human submits Delta Prompt during Stage 1; state → `PIVOT_IN_PROGRESS` | Integration | **GAP** |
| PV-002 | Human submits Delta Prompt during Stage 3; state → `PIVOT_IN_PROGRESS` | Integration | **GAP** |
| PV-003 | `pivot/{ticket-id}` branch created from current working branch | Unit | **GAP** |
| PV-004 | Architect Agent modifies `.feature` scenarios on pivot branch | Integration | **GAP** |
| PV-005 | HITL 1.5: Human approves pivot via Roo Chat | Manual | **GAP** |
| PV-006 | `PIVOT_APPROVED` → Arbiter invalidates tests → `RED` | Integration | **GAP** |
| PV-007 | Test Engineer Agent rewrites invalidated tests | Integration | **GAP** |
| PV-008 | Developer Agent refactors source until GREEN | Integration | **GAP** |
| PV-009 | Pivot blocked during `REGRESSION_RED`, `INTEGRATION_RED` states | Integration | **GAP** |
| PV-010 | Only Architect Agent can initiate pivot during Stage 1 | Unit | **GAP** |

---

## 5. Arbiter Script Coverage Gaps

| Script | Gap | Priority |
|---|---|---|
| `arbiter_check.py` | `check-session` integration test (not just unit functions) | HIGH |
| `test_orchestrator.py` | Regression failure log population | HIGH |
| `integration_test_runner.py` | Stage 2b syntax-only vs Stage 4 execution mode distinction | HIGH |
| `dependency_monitor.py` | Auto-unblock on dependency MERGED | MEDIUM |
| `crash_recovery.py` | Daemon heartbeat race conditions | MEDIUM |
| `gherkin_validator.py` | Full `@depends-on` registry lookup | LOW (GAP-13 complete) |
| `pre-commit` hook | Conventional Commits validation enforcement | HIGH |
| `pre-push` hook | `arbiter_capabilities` enforcement | HIGH |

---

## 6. Test Execution Strategy

### 6.1 Phase 1 — Unit Tests (Arbiter Scripts)

Run via: `pytest tests/workbench/ -v`

| Order | Focus | Target |
|---|---|---|
| 1 | `test_gherkin_validator.py` | Fastest feedback, no external deps |
| 2 | `test_arbiter_check.py` | Session startup compliance |
| 3 | `test_workbench_cli.py` | Bootstrap operations |
| 4 | `test_state_machine.py` | Core state transitions |
| 5 | `test_test_orchestrator.py` | Test execution flow |
| 6 | `test_integration_runner.py` | Integration gate |
| 7 | `test_dependency_monitor.py` | Dependency tracking |
| 8 | Remaining arbiter tests | Lower priority |

### 6.2 Phase 2 — Integration Tests

Run via: `pytest tests/integration/ -v` (after Stage 2b scaffolding exists)

| Order | Focus | Target |
|---|---|---|
| 1 | Single feature RED→GREEN flow | End-to-end UC-065–069 |
| 2 | Two-feature dependency flow | S3-001, S3-004 |
| 3 | Regression detection and fix | SM-005, SM-006 |
| 4 | Integration gate | SM-007–SM-010 |
| 5 | Full merge lifecycle | GAP-6f |

### 6.3 Phase 3 — E2E Pipeline Simulation

Run via: `python tests/workbench/test_e2e_pipeline.py`

Requires mock Roo Chat responses to simulate human approvals (HITL 0, HITL 1, HITL 1.5, HITL 2).

---

## 7. Test Gap Prioritization

| Priority | Gap | Reason |
|---|---|---|
| **P0 — Critical** | Stage 1 `.feature` creation and REQ-ID assignment | Core traceability infrastructure |
| **P0 — Critical** | Two-phase test execution (Phase 1 + Phase 2) | Core development loop |
| **P0 — Critical** | Dependency Gate (DEPENDENCY_BLOCKED + auto-unblock) | Cross-feature safety |
| **P0 — Critical** | Integration gate (Stage 4) | Pre-merge validation |
| **P1 — High** | Inbox flow (draft features) | Backlog hygiene |
| **P1 — High** | Pivot flow | Change management |
| **P1 — High** | Conventional Commits in pre-commit hook | Commit discipline |
| **P2 — Medium** | Phase 0 (ideation pipeline) | Human-driven, harder to automate |
| **P2 — Medium** | `check-session` integration test | Session startup safety |
| **P3 — Low** | Crash recovery daemon race conditions | Edge case |

---

## 8. Deliverables

| Deliverable | File | Owner |
|---|---|---|
| Phase 0 test stubs | `tests/unit/test_phase0_ideation.py` | Test Engineer Agent |
| Stage 1 test stubs | `tests/unit/test_stage1_architect.py` | Test Engineer Agent |
| Stage 2 test stubs | `tests/unit/test_stage2_test_engineer.py` | Test Engineer Agent |
| Stage 2b test stubs | `tests/unit/test_stage2b_integration_scaffold.py` | Test Engineer Agent |
| Inbox flow tests | `tests/unit/test_inbox_flow.py` | Test Engineer Agent |
| Pivot flow tests | `tests/unit/test_pivot_flow.py` | Test Engineer Agent |
| E2E pipeline simulation | `tests/workbench/test_e2e_pipeline.py` (enhance) | Test Engineer Agent |
| Arbiter integration tests | `tests/integration/test_arbiter_integration.py` | Test Engineer Agent |

---

## 9. References

- Specification: [`Agentic Workbench v2 - Draft.md`](Agentic%20Workbench%20v2%20-%20Draft.md)
- State machine: [`plans/Coherency_Review_Report.md`](plans/Coherency_Review_Report.md)
- Existing tests: [`tests/workbench/`](tests/workbench/)
- CLI coverage: UC-041–050 (`test_workbench_cli.py`)
- State machine: SM-001–SM-014 (`test_state_machine.py`)

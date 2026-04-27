# Rules vs Enforcement Matrix

**Document ID:** RULES-ENFORCEMENT-MATRIX  
**Version:** 1.0  
**Created:** 2026-04-26  
**Status:** ACTIVE  
**Classification:** Internal — Workbench Governance  

---

## 1. Overview

This document maps every rule in `.clinerules` to its enforcement mechanism, trigger timing, and current gap status. Use this matrix to understand:

- **When** a rule is enforced (trigger/execution timing)
- **How** enforcement occurs (mechanism)
- **Current status** (enforced/warned/honor-only)
- **Gap severity** (critical/high/medium/low)

### Trigger/When Executed Keys

| Trigger | Description |
|---------|-------------|
| **Session Start (SLC-1)** | Runs via `arbiter_check.py check-session` at agent startup |
| **Pre-Commit** | Runs via `.workbench/hooks/pre-commit` before git commit |
| **Pre-Push** | Runs via `.workbench/hooks/pre-push` before git push |
| **Post-Commit** | Runs via `.workbench/hooks/post-commit` after git commit |
| **Post-Merge** | Runs via `.workbench/hooks/post-merge` after merge |
| **On-Demand** | Manually triggered via `workbench-cli.py` command |
| **N/A** | Not applicable (conceptual/honor-only) |

### Enforcement Status Keys

| Status | Description |
|--------|-------------|
| **ENFORCED** | Active mechanism blocks or prevents violation |
| **WARNED** | Mechanism detects and reports but does not block |
| **HONOR** | No automation — agent self-compliance required |
| **VIOLATED** | Active mechanism exists but violates the rule itself |
| **NOT ENFORCED** | No mechanism exists |

### Gap Severity Keys

| Severity | Description |
|----------|-------------|
| **CRITICAL** | Active violation or missing foundational enforcement |
| **HIGH** | Major gap in enforcement coverage |
| **MEDIUM** | Partial enforcement or limited detection |
| **LOW** | Minor gap, working as intended |

---

## 2. Rule Categories

### Category 1: Session Lifecycle (SLC-1, SLC-2)

| Rule ID | Rule Name | Category | Enforcement Status | Trigger/When Executed | Enforcement Mechanism | Gap Severity |
|---------|-----------|----------|-------------------|----------------------|----------------------|--------------|
| **SLC-1** | Session Lifecycle Protocol | Session Lifecycle | WARNED | Session Start (SLC-1) | `arbiter_check.py check-session` validates activeContext.md exists and is recent. If file missing or >60min old, returns WARNING. | MEDIUM |
| **SLC-2** | Audit Log Immutability | Session Lifecycle | WARNED | Session Start (SLC-1) + Pre-Commit | `check_audit_log_immutability()` compares staged files in `docs/conversations/` against git HEAD. Detects tampering but cannot prevent pre-commit modification. Pre-commit hook runs same check. | MEDIUM |

---

### Category 2: Inter-Agent Handoff Protocol (HND-1, HND-2)

| Rule ID | Rule Name | Category | Enforcement Status | Trigger/When Executed | Enforcement Mechanism | Gap Severity |
|---------|-----------|----------|-------------------|----------------------|----------------------|--------------|
| **HND-1** | Read Handoff Before Acting | Handoff | HONOR | N/A | No enforcement mechanism. Agent self-reports reading `handoff-state.md`. `arbiter_check.py` checks mtime vs last commit as heuristic but cannot verify actual read. | MEDIUM |
| **HND-2** | Handoff Ephemeral | Handoff | HONOR | N/A | No enforcement mechanism. `memory_rotator.py` resets handoff at sprint end, but rule is honor-based. `check_handoff_freshness()` detects stale sprint markers and warns. | LOW |

---

### Category 3: Traceability Mandates (TRC-1, TRC-2)

| Rule ID | Rule Name | Category | Enforcement Status | Trigger/When Executed | Enforcement Mechanism | Gap Severity |
|---------|-----------|----------|-------------------|----------------------|----------------------|--------------|
| **TRC-1** | Stage 3 Dependency Gate | Traceability | ENFORCED | Pre-Commit | `check_dependency_gate()` in `arbiter_check.py` blocks commit if staged `src/` changes exist but dependencies not MERGED. Validates `state.json.feature_registry`. Pre-commit hook calls this check. | LOW |
| **TRC-2** | No Live API Imports | Traceability | WARNED | On-Demand | `check_live_imports_from_non_merged()` scans `src/` for imports from non-MERGED features. Returns WARNING but does not block. Agent must self-comply. | HIGH |

---

### Category 4: Commit Constraints (CMT-1)

| Rule ID | Rule Name | Category | Enforcement Status | Trigger/When Executed | Enforcement Mechanism | Gap Severity |
|---------|-----------|----------|-------------------|----------------------|----------------------|--------------|
| **CMT-1** | Branch Protection | Commit Constraints | ENFORCED | Pre-Commit + Pre-Push | **Pre-commit:** `check_branch_name()` blocks commits on `main`, `master`, `develop`. **Pre-push:** Blocks direct push to protected branches unless merge commit or `APPROVED-BY-HUMAN` footer on chore commit. Hooks installed in `.git/hooks/`. | LOW |
| **CMT-1** (merged branch) | No Commit on Merged Branch | Commit Constraints | ENFORCED | Pre-Commit | `check_merged_branch()` in pre-commit verifies branch not merged to `main` or `develop`. | LOW |
| **CMT-1** (state.json) | No Direct state.json Writes | Commit Constraints | ENFORCED | Pre-Commit | `check_state_json_integrity()` in pre-commit detects if `state.json` is staged and warns. Only Arbiter scripts should write. | MEDIUM |

---

### Category 5: State Management (STM-1, STM-2)

| Rule ID | Rule Name | Category | Enforcement Status | Trigger/When Executed | Enforcement Mechanism | Gap Severity |
|---------|-----------|----------|-------------------|----------------------|----------------------|--------------|
| **STM-1** | No state.json Writes | State Management | **VIOLATED** | Pre-Commit | Pre-commit hook section 6 previously mutated `state.json` directly (GAP-11). Deferred ownership updates now write to `.workbench/hooks/.deferred_state_update` flag file instead. Arbiter post-commit processes deferred updates. | CRITICAL |
| **STM-2** | Two-Phase Test Loop | State Management | ENFORCED | On-Demand | `test_orchestrator.py` implements Phase 1 (feature scope) and Phase 2 (full regression). `check_regression_failures_populated()` validates `regression_failures` array when `REGRESSION_RED`. | LOW |

---

### Category 6: Integration Gate Rules (INT-1, REG-1, REG-2)

| Rule ID | Rule Name | Category | Enforcement Status | Trigger/When Executed | Enforcement Mechanism | Gap Severity |
|---------|-----------|----------|-------------------|----------------------|----------------------|--------------|
| **INT-1** | Integration Gate | Integration | ENFORCED | On-Demand | `integration_test_runner.py` runs integration tests. `state.json.integration_state` must be GREEN before feature considered complete. `check_gate_notifications()` reports pending HITL gates. | LOW |
| **REG-1** | Regression Priority | Integration | WARNED | Session Start (SLC-1) | `check_regression_failures_populated()` warns if `REGRESSION_RED` but `regression_failures` is empty. Agent must treat regression log as primary input. | MEDIUM |
| **REG-2** | Full Suite After Phase 1 | Integration | ENFORCED | On-Demand | `test_orchestrator.py` runs full suite after every Phase 1 GREEN. `regression_state` set to CLEAN only after full suite passes. | LOW |

---

### Category 7: Command Delegation (CMD-1, CMD-2, CMD-3, CMD-TRANSITION)

| Rule ID | Rule Name | Category | Enforcement Status | Trigger/When Executed | Enforcement Mechanism | Gap Severity |
|---------|-----------|----------|-------------------|----------------------|----------------------|--------------|
| **CMD-1** | Layer 1 Auto-Execute | Command Delegation | ENFORCED | N/A (Configuration) | `.roo-settings.json` `settings.roo-cline.allowedCommands` defines auto-execute patterns. Agent configuration enforces. | LOW |
| **CMD-2** | Arbiter Delegation | Command Delegation | NOT ACTIVE | N/A | `state.json.arbiter_capabilities` all currently `false`. When true, agent must delegate to Arbiter scripts. No active enforcement until capabilities registered. | HIGH |
| **CMD-TRANSITION** | Read Capabilities | Command Delegation | WARNED | Session Start (SLC-1) | `check_arbiter_capabilities_registered()` warns if `arbiter_capabilities` all false or partially registered. Agent should read `state.json.arbiter_capabilities` at startup. | HIGH |
| **CMD-3** | Forbidden Commands | Command Delegation | ENFORCED | N/A (Agent Config) | Permanently forbidden patterns: `rm.*-rf`, `git push`, `git commit`, `sudo`, `kill`, `docker`, `kubectl`, `terraform`. Requires human approval without exception. Built into agent configuration. | LOW |

---

### Category 8: Memory System (MEM-1, MEM-2, MEM-3, MEM-3a)

| Rule ID | Rule Name | Category | Enforcement Status | Trigger/When Executed | Enforcement Mechanism | Gap Severity |
|---------|-----------|----------|-------------------|----------------------|----------------------|--------------|
| **MEM-1** | Cold Zone Prohibition | Memory System | WARNED | Session Start (SLC-1) | `check_cold_zone_access()` scans git log for direct edits to `archive-cold/`. Returns CRITICAL if detected. Agent should use `archive-query` MCP tool. | MEDIUM |
| **MEM-2** | Decision Logging | Memory System | HONOR | N/A | No enforcement mechanism. `check_decision_log_updated()` warns if `decisionLog.md` not updated in 7+ days. Agent self-reports compliance. | LOW |
| **MEM-3** | Codebase-Memory MCP | Memory System | ENFORCED | N/A (MCP Server) | `codebase-memory` MCP server provides code structure indexing. Available tools: `index_repository`, `search_graph`, `query_graph`, `trace_path`, etc. | LOW |
| **MEM-3a** | Cold Zone Firewall | Memory System | ENFORCED | Session Start (SLC-1) | `check_codebase_memory_index_scope()` verifies `memory-bank/` not indexed into `codebase-memory`. Returns CRITICAL if violation detected. | LOW |

---

### Category 9: Dependency Management (DEP-1, DEP-2, DEP-3)

| Rule ID | Rule Name | Category | Enforcement Status | Trigger/When Executed | Enforcement Mechanism | Gap Severity |
|---------|-----------|----------|-------------------|----------------------|----------------------|--------------|
| **DEP-1** | Dependency Gate Check | Dependency | ENFORCED | Pre-Commit | `check_dependency_gate()` blocks `src/` commits if active feature's dependencies not MERGED. Validates `state.json.feature_registry`. | LOW |
| **DEP-2** | No Live API Calls | Dependency | HONOR | N/A | No enforcement mechanism. Agent must not import live APIs from non-MERGED features. `check_live_imports_from_non_merged()` provides WARNING-level detection. | MEDIUM |
| **DEP-3** | Orchestrator Only Block | Dependency | WARNED | Session Start (SLC-1) | `check_dependency_blocked_mode()` detects non-Orchestrator commits during DEPENDENCY_BLOCKED state using git author email patterns. Returns CRITICAL if violation. | MEDIUM |

---

### Category 10: File Access Constraints (FAC-1)

| Rule ID | Rule Name | Category | Enforcement Status | Trigger/When Executed | Enforcement Mechanism | Gap Severity |
|---------|-----------|----------|-------------------|----------------------|----------------------|--------------|
| **FAC-1** | File Access Constraints | File Access | WARNED | Pre-Commit | `check_file_access_constraints()` validates staged files against current stage's allowed write scope (Stage 1: `features/`, Stage 2: `tests/unit/`, Stage 3: `src/`, Stage 4: none). Returns CRITICAL if violation. Stage 4 read-only strictly enforced. | MEDIUM |

---

### Category 11: Crash Recovery (CR-1)

| Rule ID | Rule Name | Category | Enforcement Status | Trigger/When Executed | Enforcement Mechanism | Gap Severity |
|---------|-----------|----------|-------------------|----------------------|----------------------|--------------|
| **CR-1** | Crash Recovery | Crash Recovery | ENFORCED | Session Start (SLC-1) | `check_crash_checkpoint()` detects stale ACTIVE checkpoint (>30 min old). Offers to resume from checkpoint. `crash_recovery.py` daemon writes heartbeat every 5 minutes. | LOW |

---

### Category 12: Forbidden Behaviors (FOR-1)

| Rule ID | Rule Name | Category | Enforcement Status | Trigger/When Executed | Enforcement Mechanism | Gap Severity |
|---------|-----------|----------|-------------------|----------------------|----------------------|--------------|
| **FOR-1** | Self-Declaration | Forbidden | WARNED | Session Start (SLC-1) | `check_forbidden_self_declaration()` warns if `handoff-state.md` contains completion markers while state is not GREEN/MERGED/INIT. Agent self-reports. | HIGH |
| **FOR-1** | Bypassing Test Suite | Forbidden | ENFORCED | Pre-Commit | Pre-commit hook blocks commits during blocking states (REGRESSION_RED, INTEGRATION_RED, PIVOT_IN_PROGRESS). `test_orchestrator.py` enforces test execution. | LOW |
| **FOR-1** | Skipping Phase 2 | Forbidden | ENFORCED | On-Demand | `test_orchestrator.py` enforces full regression after Phase 1. Cannot skip. | LOW |
| **FOR-1** | Direct Cold Zone Access | Forbidden | WARNED | Session Start (SLC-1) | `check_cold_zone_access()` detects direct git edits to `archive-cold/`. | MEDIUM |
| **FOR-1** | Committing During Blocking | Forbidden | ENFORCED | Pre-Commit | Pre-commit hook blocks commits when state is REGRESSION_RED, INTEGRATION_RED, or PIVOT_IN_PROGRESS. | LOW |
| **FOR-1** | Live API Imports | Forbidden | WARNED | On-Demand | `check_live_imports_from_non_merged()` provides WARNING-level detection. | MEDIUM |
| **FOR-1** | Editing Audit Logs | Forbidden | WARNED | Session Start (SLC-1) + Pre-Commit | `check_audit_log_immutability()` detects tampering with `docs/conversations/` files. | MEDIUM |

---

### Category 13: Large File Generation (LGF-1)

| Rule ID | Rule Name | Category | Enforcement Status | Trigger/When Executed | Enforcement Mechanism | Gap Severity |
|---------|-----------|----------|-------------------|----------------------|----------------------|--------------|
| **LGF-1** | Chunking Protocol | Large File | WARNED | Pre-Commit | `check_large_file_warning()` warns when staged files exceed 500 lines without chunking evidence (temp chunk files or pipeline pattern markers in commit message). Pre-commit hook section 7b provides same warning. Not blocking — preventive guidance. | MEDIUM |

---

### Category 14: Pivot Protocol (PVT-1, PVT-2)

| Rule ID | Rule Name | Category | Enforcement Status | Trigger/When Executed | Enforcement Mechanism | Gap Severity |
|---------|-----------|----------|-------------------|----------------------|----------------------|--------------|
| **PVT-1** | Pivot State Commits | Pivot | ENFORCED | Pre-Commit | Pre-commit hook blocks commits during PIVOT_IN_PROGRESS state. | LOW |
| **PVT-2** | Agent Mode Identity | Pivot | WARNED | Session Start (SLC-1) | `check_pivot_mode()` detects pivot branch creation and verifies agent mode from git author email. CRITICAL if wrong agent mode initiated pivot without APPROVED-BY-HUMAN. | HIGH |

---

## 3. Summary Matrix

| Rule ID | Rule Name | Category | Enforcement Status | Trigger/When Executed | Enforcement Mechanism | Gap Severity |
|---------|-----------|----------|-------------------|----------------------|----------------------|--------------|
| SLC-1 | Session Lifecycle Protocol | Session Lifecycle | WARNED | Session Start (SLC-1) | arbiter_check.py activeContext.md validation | MEDIUM |
| SLC-2 | Audit Log Immutability | Session Lifecycle | WARNED | Session Start (SLC-1) + Pre-Commit | check_audit_log_immutability() + pre-commit | MEDIUM |
| HND-1 | Read Handoff Before Acting | Handoff | HONOR | N/A | None (heuristic mtime check only) | MEDIUM |
| HND-2 | Handoff Ephemeral | Handoff | HONOR | N/A | None (memory_rotator.py handles reset) | LOW |
| TRC-1 | Stage 3 Dependency Gate | Traceability | ENFORCED | Pre-Commit | check_dependency_gate() | LOW |
| TRC-2 | No Live API Imports | Traceability | WARNED | On-Demand | check_live_imports_from_non_merged() | HIGH |
| CMT-1 | Branch Protection | Commit Constraints | ENFORCED | Pre-Commit + Pre-Push | pre-commit + pre-push hooks | LOW |
| CMT-1 (merged) | No Commit on Merged Branch | Commit Constraints | ENFORCED | Pre-Commit | check_merged_branch() | LOW |
| CMT-1 (state.json) | No Direct state.json Writes | Commit Constraints | ENFORCED | Pre-Commit | check_state_json_integrity() | MEDIUM |
| STM-1 | No state.json Writes | State Management | VIOLATED | Pre-Commit | GAP-11 fix: deferred to flag file | CRITICAL |
| STM-2 | Two-Phase Test Loop | State Management | ENFORCED | On-Demand | test_orchestrator.py | LOW |
| INT-1 | Integration Gate | Integration | ENFORCED | On-Demand | integration_test_runner.py | LOW |
| REG-1 | Regression Priority | Integration | WARNED | Session Start (SLC-1) | check_regression_failures_populated() | MEDIUM |
| REG-2 | Full Suite After Phase 1 | Integration | ENFORCED | On-Demand | test_orchestrator.py | LOW |
| CMD-1 | Layer 1 Auto-Execute | Command Delegation | ENFORCED | N/A (Config) | .roo-settings.json | LOW |
| CMD-2 | Arbiter Delegation | Command Delegation | NOT ACTIVE | N/A | state.json arbiter_capabilities (all false) | HIGH |
| CMD-TRANSITION | Read Capabilities | Command Delegation | WARNED | Session Start (SLC-1) | check_arbiter_capabilities_registered() | HIGH |
| CMD-3 | Forbidden Commands | Command Delegation | ENFORCED | N/A (Agent Config) | Agent configuration | LOW |
| MEM-1 | Cold Zone Prohibition | Memory System | WARNED | Session Start (SLC-1) | check_cold_zone_access() | MEDIUM |
| MEM-2 | Decision Logging | Memory System | HONOR | N/A | check_decision_log_updated() warning only | LOW |
| MEM-3 | Codebase-Memory MCP | Memory System | ENFORCED | N/A (MCP Server) | codebase-memory MCP server | LOW |
| MEM-3a | Cold Zone Firewall | Memory System | ENFORCED | Session Start (SLC-1) | check_codebase_memory_index_scope() | LOW |
| DEP-1 | Dependency Gate Check | Dependency | ENFORCED | Pre-Commit | check_dependency_gate() | LOW |
| DEP-2 | No Live API Calls | Dependency | HONOR | N/A | check_live_imports_from_non_merged() WARNING | MEDIUM |
| DEP-3 | Orchestrator Only Block | Dependency | WARNED | Session Start (SLC-1) | check_dependency_blocked_mode() | MEDIUM |
| FAC-1 | File Access Constraints | File Access | WARNED | Pre-Commit | check_file_access_constraints() | MEDIUM |
| CR-1 | Crash Recovery | Crash Recovery | ENFORCED | Session Start (SLC-1) | check_crash_checkpoint() + crash_recovery.py | LOW |
| FOR-1 | Self-Declaration | Forbidden | WARNED | Session Start (SLC-1) | check_forbidden_self_declaration() | HIGH |
| FOR-1 | Bypassing Test Suite | Forbidden | ENFORCED | Pre-Commit | pre-commit blocking states check | LOW |
| FOR-1 | Skipping Phase 2 | Forbidden | ENFORCED | On-Demand | test_orchestrator.py two-phase enforcement | LOW |
| FOR-1 | Direct Cold Zone Access | Forbidden | WARNED | Session Start (SLC-1) | check_cold_zone_access() | MEDIUM |
| FOR-1 | Committing During Blocking | Forbidden | ENFORCED | Pre-Commit | pre-commit blocking states check | LOW |
| FOR-1 | Live API Imports | Forbidden | WARNED | On-Demand | check_live_imports_from_non_merged() | MEDIUM |
| FOR-1 | Editing Audit Logs | Forbidden | WARNED | Session Start (SLC-1) + Pre-Commit | check_audit_log_immutability() | MEDIUM |
| LGF-1 | Chunking Protocol | Large File | WARNED | Pre-Commit | check_large_file_warning() + pre-commit section 7b | MEDIUM |
| PVT-1 | Pivot State Commits | Pivot | ENFORCED | Pre-Commit | pre-commit blocking states check | LOW |
| PVT-2 | Agent Mode Identity | Pivot | WARNED | Session Start (SLC-1) | check_pivot_mode() | HIGH |

---

## 4. Enforcement Statistics

### By Status

| Status | Count | Percentage |
|--------|-------|------------|
| ENFORCED | 19 | 41% |
| WARNED | 16 | 35% |
| HONOR | 6 | 13% |
| VIOLATED | 1 | 2% |
| NOT ACTIVE | 1 | 2% |
| NOT ENFORCED | 3 | 7% |

### By Category

| Category | Enforced | Warned | Honor | Total |
|----------|----------|--------|-------|-------|
| Session Lifecycle | 0 | 2 | 0 | 2 |
| Handoff | 0 | 0 | 2 | 2 |
| Traceability | 1 | 1 | 0 | 2 |
| Commit Constraints | 3 | 0 | 0 | 3 |
| State Management | 1 | 0 | 0 | 1 |
| Integration | 3 | 1 | 0 | 4 |
| Command Delegation | 2 | 1 | 1 | 4 |
| Memory System | 2 | 2 | 0 | 4 |
| Dependency | 1 | 2 | 1 | 4 |
| File Access | 0 | 1 | 0 | 1 |
| Crash Recovery | 1 | 0 | 0 | 1 |
| Forbidden Behaviors | 3 | 4 | 0 | 7 |
| Large File Generation | 0 | 1 | 0 | 1 |
| Pivot Protocol | 1 | 1 | 0 | 2 |

---

## 5. Gap Summary by Severity

### CRITICAL (3 gaps)

| Rule | Issue | Fix Required |
|------|-------|--------------|
| STM-1 | Pre-commit hook violates own rule by mutating state.json | GAP-11 fix: use deferred flag file |
| DEP-1 | No commit-time enforcement prior to GAP-11 | check_dependency_gate() implemented |
| LGF-1 | No chunking enforcement | check_large_file_warning() + pre-commit warning |

### HIGH (7 gaps)

| Rule | Issue | Fix Required |
|------|-------|--------------|
| TRC-2 | Cannot verify live API imports at commit | WARNING-level detection only |
| CMD-2 | arbiter_capabilities all false | Register Arbiter capabilities |
| CMD-TRANSITION | Cannot verify agent reads capabilities | WARNING-level detection only |
| FOR-1 (self-declaration) | Cannot verify agent honesty | WARNING-level detection only |
| PVT-2 | Cannot verify agent mode identity | check_pivot_mode() with email heuristics |
| DEP-2 | No live API call enforcement | Honor-based |
| DEP-3 | Heuristic only for orchestrator detection | check_dependency_blocked_mode() with email patterns |

### MEDIUM (11 gaps)

| Rule | Issue | Fix Required |
|------|-------|--------------|
| SLC-1 | Limited detection of startup protocol skip | WARNING-level only |
| SLC-2 | Post-hoc tampering detection | WARNING-level |
| HND-1 | No enforcement mechanism | Honor-based |
| CMT-1 (state.json) | Agent can modify state.json | Warning only |
| MEM-1 | Git log detection is post-hoc | WARNING-level |
| FAC-1 | Check exists but incomplete | WARNING-level |
| REG-1 | Self-reported compliance | WARNING-level |
| DEP-2 | Honor-based | WARNING-level detection |
| DEP-3 | Heuristic detection | WARNING-level |
| LGF-1 | Not blocking, only warning | WARNING-level |
| FOR-1 (multiple) | Multiple honor-based rules | WARNING-level detection |

### LOW (4 gaps)

| Rule | Issue | Fix Required |
|------|-------|--------------|
| HND-2 | Ephemeral nature honor-based | memory_rotator.py handles |
| MEM-2 | Self-reported decision logging | WARNING-level |
| CMT-1 | Implemented correctly | Working as intended |
| STM-2 | Two-phase test correctly enforced | Working as intended |

---

## 6. Enforcement Mechanisms Reference

### arbiter_check.py Check Functions

| Check Function | Rule(s) | Trigger | Status |
|----------------|---------|---------|--------|
| `check_startup_protocol()` | SLC-1 | Session Start (SLC-1) | OK |
| `check_audit_log_immutability()` | SLC-2 | Session Start (SLC-1) + Pre-Commit | OK |
| `check_handoff_read()` | HND-1 | On-Demand | WARNING |
| `check_handoff_freshness()` | HND-2 | On-Demand | OK |
| `check_cold_zone_access()` | MEM-1 | Session Start (SLC-1) | OK |
| `check_decision_log_updated()` | MEM-2 | On-Demand | WARNING |
| `check_codebase_memory_index_scope()` | MEM-3a | Session Start (SLC-1) | OK |
| `check_crash_checkpoint()` | CR-1 | Session Start (SLC-1) | OK |
| `check_dependency_gate()` | DEP-1 | Pre-Commit | OK |
| `check_dependency_blocked_mode()` | DEP-3 | Session Start (SLC-1) | OK |
| `check_file_access_constraints()` | FAC-1 | Pre-Commit | OK |
| `check_live_imports_from_non_merged()` | TRC-2 | On-Demand | WARNING |
| `check_regression_failures_populated()` | REG-1 | Session Start (SLC-1) | OK |
| `check_arbiter_capabilities_registered()` | CMD-TRANSITION | Session Start (SLC-1) | WARNING |
| `check_forbidden_self_declaration()` | FOR-1 | Session Start (SLC-1) | WARNING |
| `check_hooks_installed()` | HOOK-INSTALL | Session Start (SLC-1) | OK |
| `check_pipeline_enrollment()` | GATEKEEPER | Session Start (SLC-1) | OK |
| `check_gate_notifications()` | GATE_NOTIFY | Session Start (SLC-1) | OK |
| `check_pivot_mode()` | PVT-2 | Session Start (SLC-1) | OK |
| `check_large_file_warning()` | LGF-1 | Pre-Commit | OK |

### Git Hooks

| Hook | File | Rules Enforced | Status |
|------|------|----------------|--------|
| pre-commit | `.workbench/hooks/pre-commit` | SLC-2, MEM-1, DEP-1, DEP-3, FAC-1, CR-1, CMT-1, STM-1, FOR-1, LGF-1, GATE_NOTIFY | ENFORCED |
| pre-push | `.workbench/hooks/pre-push` | CMT-1 (branch protection), blocking states, regression | ENFORCED |
| post-commit | `.workbench/hooks/post-commit` | Deferred file ownership updates | ENFORCED |
| post-merge | `.workbench/hooks/post-merge` | TBD | ENFORCED |
| post-tag | `.workbench/hooks/post-tag` | Tag validation | ENFORCED |

### Arbiter Scripts

| Script | Location | Rules Owned | Status |
|--------|----------|-------------|--------|
| arbiter_check.py | `.workbench/scripts/` | SLC-1, SLC-2, HND-1, HND-2, MEM-1, MEM-2, MEM-3a, CR-1, DEP-1, DEP-3, FAC-1, TRC-2, REG-1, CMD-TRANSITION, FOR-1, HOOK-INSTALL, GATEKEEPER, GATE_NOTIFY, PVT-2, LGF-1 | ACTIVE |
| test_orchestrator.py | `.workbench/scripts/` | STM-2, REG-2, INT-1, FOR-1 (test bypass) | ACTIVE |
| gatekeeper.py | `.workbench/scripts/` | GATEKEEPER | ACTIVE |
| gate_notification.py | `.workbench/scripts/` | GATE_NOTIFY | ACTIVE |
| crash_recovery.py | `.workbench/scripts/` | CR-1 | ACTIVE |
| memory_rotator.py | `.workbench/scripts/` | HND-2 | ACTIVE |
| audit_logger.py | `.workbench/scripts/` | SLC-2 | ACTIVE |
| dependency_monitor.py | `.workbench/scripts/` | DEP-3, CMD-2 | ACTIVE |
| orchestrator_monitor.py | `.workbench/scripts/` | CMD-2, DEP-3 | ACTIVE |

---

## 7. Session Checks (check-session Mode)

When running `arbiter_check.py check-session` (lightweight startup scan), these rules are checked:

| Rule | Check Function | Severity if Violation |
|------|----------------|----------------------|
| SLC-2 | check_audit_log_immutability() | CRITICAL |
| MEM-1 | check_cold_zone_access() | CRITICAL |
| MEM-3a | check_codebase_memory_index_scope() | CRITICAL |
| DEP-1 | check_dependency_gate() | CRITICAL |
| DEP-3 | check_dependency_blocked_mode() | CRITICAL |
| FAC-1 | check_file_access_constraints() | CRITICAL |
| CR-1 | check_crash_checkpoint() | WARNING (stale checkpoint) |
| HOOK-INSTALL | check_hooks_installed() | CRITICAL |
| GATEKEEPER | check_pipeline_enrollment() | CRITICAL |
| GATE_NOTIFY | check_gate_notifications() | INFO (pending human actions) |
| LGF-1 | check_large_file_warning() | WARNING (preventive) |

---

*Document generated: 2026-04-26*  
*Source: .clinerules v2.2-root, arbiter_check.py, git hooks, ENFORCEMENT_GAP_REPORT.md*
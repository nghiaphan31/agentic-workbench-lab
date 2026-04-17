# decisionLog.md — Architecture Decision Records

**Template Version:** 2.1
**Owner:** All Agents
**Rotation Policy:** Persist (never rotate) — ADRs accumulate across sprints as permanent architectural records

---

## ADR-001: Two-Repository Strategy for Workbench vs. Specs

- **Date:** 2026-04-12
- **Context:** The workbench requires two distinct concerns: (1) the template/repo containing engine files (.clinerules, .roomodes, Arbiter scripts) that gets injected into application repos, and (2) a specs/documentation repo containing architectural diagrams, implementation plans, and design documents. Placing both in one repo creates ambiguity about which is the "canonical" workbench.
- **Decision:** Create two separate Git repositories:
  - `agentic-workbench-template` — the canonical template repo at `AGENTIC_DEVELOPMENT_PROJECTS/agentic-workbench-template`. Contains all Engine files (.clinerules, .roomodes, .workbench/scripts/, state.json, memory-bank templates). This is what gets consumed by `workbench-cli.py init/upgrade`.
  - `agentic-workbench-v2-specs` — the specs/documentation repo at `AGENTIC_DEVELOPMENT_PROJECTS/agentic-workbench-v2-specs`. Contains `Agentic Workbench v2 - Draft.md`, implementation plans, diagrams, and architectural reviews.
- **Consequences:** Clear separation of concerns. The template repo is versioned, reusable, and consumable by multiple application repos. The specs repo is for human readers planning or reviewing the workbench design. The `workbench-cli.py` tool (Sprint 2) will only interact with `agentic-workbench-template`.

---

## ADR-002: Phase B Command Delegation via .roo-settings.json

- **Date:** 2026-04-12
- **Context:** During Layer 2 migration (Phase A → B → C), each Arbiter script delivered permanently revokes a command permission from Roo Code's auto-approve allowlist. The allowlist lives in `.roo-settings.json` but the authoritative record of what is "owned" lives in `state.json.arbiter_capabilities`. We need a single source of truth for the mapping between scripts and commands.
- **Decision:** Store the mapping in `.roo-settings.json` under an `arbiter_owned` key. This allows Roo Code to read both the allowlist AND the ownership mapping in one file. `state.json.arbiter_capabilities` remains the Arbiter's internal record. On script delivery, both files are updated atomically via a commit.
- **Consequences:** The `.roo-settings.json` `arbiter_owned` section serves as the "contract" between Roo Code's permission system and the Arbiter's capability system.

---

## ADR-003: Distributed State Management — No Central state_manager.py

- **Date:** 2026-04-12
- **Context:** The spec and diagrams listed `state_manager.py` as a dedicated Arbiter script owning all `state.json` writes. The script was never implemented. State transitions are handled by individual scripts writing their own domain fields directly.
- **Decision:** Remove `state_manager.py` from all spec, diagram, and naming references. Document that state management is distributed across individual Arbiter scripts. Each script is responsible for writing only its own domain fields in `state.json`.
- **Consequences:** Simpler implementation with no central bottleneck. Risk: no single enforcement point for `state.json` schema validation. Mitigation: `pre-commit` hook validates `state.json` integrity via `last_updated_by` field inspection. `pre-push` hook blocks pushes in `RED`/`REGRESSION_RED`/`INTEGRATION_RED`/`PIVOT_IN_PROGRESS` states.

---

## ADR-004: Repo Naming — agentic-workbench-lab + agentic-workbench-engine

- **Date:** 2026-04-12
- **Context:** The two-repo ecosystem needed clear, non-confusing names. `agentic-workbench-v2-specs` undersold the repo's value (it contains specs + design + validation). `agentic-workbench-template` was confusing because "template" implied the repo was a project template to clone, when it's actually the canonical engine repo that gets injected into application repos.
- **Decision:** Rename both repos:
  - `agentic-workbench-v2-specs` → `agentic-workbench-lab` — this repo is the lab environment where specs, design, and engine validation happen. It contains `Agentic Workbench v2 - Draft.md`, implementation plans, diagrams, and the `tests/workbench/` validation suite.
  - `agentic-workbench-template` → `agentic-workbench-engine` — this repo is the canonical source of truth for all engine files (.clinerules, .roomodes, Arbiter scripts, workbench-cli.py). It gets injected into application repos via `workbench-cli.py init/upgrade`. The embedded copy in the lab repo should be a git submodule pinned to a specific commit.
- **Consequences:** Clear naming. The engine repo is clearly the "engine" (not a template). The lab repo is clearly where development/experimentation happens (not just specs).

---

## ADR-005: Lab Repo Cleanup — Canonical vs. Runtime Artifacts

- **Date:** 2026-04-12
- **Context:** The lab repo (agentic-workbench-lab) contained runtime artifacts (`state.json`, `_inbox/`, `features/`, `src/`, `tests/unit/`, `tests/integration/`) that belong in application repos, not in a specs/design/validation repo. This created confusion about the repo's purpose and risked the embedded engine copy drifting from the canonical engine repo.
- **Decision:**
  1. Remove all runtime artifacts from the lab repo root: `state.json`, `_inbox/`, `features/`, `src/`, `tests/unit/`, `tests/integration/`, `.workbench/`.
  2. Convert `agentic-workbench-engine/` (the embedded engine copy) to a git submodule pointing to the canonical `agentic-workbench-engine` repo.
  3. Keep `memory-bank/hot-context/` (active context for the lab's own agent sessions), `tests/workbench/` (validation suite), `docs/`, `diagrams/`, `plans/`.
- **Consequences:** The lab repo now has a single, clear purpose: specs + design + validation. The embedded engine is always in sync with the canonical engine via git submodule pinning. No more silent drift risk.

---

## ADR-006: Submodule Restoration

- **Date:** 2026-04-17
- **Context:** On 2026-04-17, the submodule was removed in favor of standalone clone (Option A). After further consideration, the user wants to restore the submodule pattern for better version pinning and alignment with ADR-005.
- **Decision:** Add `agentic-workbench-engine` as a git submodule at `agentic-workbench-engine/`.
- **Original pinned commit:** 54b4d0a (fix(memory_rotator): move narrativeRequest.md from rotate to persist policy)
- **URL:** git@github.com:nghiaphan31/agentic-workbench-engine.git
- **Consequences:** Engine changes now require two-step commit: one in engine repo, one to update submodule pointer in lab repo.

---

## Adding New ADRs

When a significant architectural decision is made:

1. Assign the next sequential ADR number (ADR-001, ADR-002, etc.)
2. Fill in all four fields completely
3. Do NOT edit or delete existing ADRs — they are immutable records
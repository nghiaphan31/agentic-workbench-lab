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

## Adding New ADRs

When a significant architectural decision is made:

1. Assign the next sequential ADR number (ADR-001, ADR-002, etc.)
2. Fill in all four fields completely
3. Do NOT edit or delete existing ADRs — they are immutable records
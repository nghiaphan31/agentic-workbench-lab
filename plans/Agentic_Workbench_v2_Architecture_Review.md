# Architectural Review: Agentic Workbench v2.0 — Draft

**Reviewer:** Senior Architect (Roo)  
**Document Under Review:** [`Agentic Workbench v2 - Draft.md`](../Agentic%20Workbench%20v2%20-%20Draft.md)  
**Review Date:** 2026-04-11  
**Status:** DRAFT — Pending Author Response

---

## Executive Summary

The document is architecturally ambitious and conceptually sound. The core triad (Agent / Arbiter / HITL), the file-system-as-database synchronization pattern, and the TDD-gated pipeline are well-conceived and internally motivated. However, the document suffers from **three categories of defects** that must be resolved before it can serve as an authoritative specification:

1. **Structural defects** — The document is actually two documents merged without a clear boundary, causing heading-level collisions and numbering inconsistencies.
2. **Terminology drift** — Several key actors and artifacts are named inconsistently across sections, which would cause ambiguity during implementation.
3. **Logical gaps and contradictions** — Several rules contradict each other or leave critical operational questions unanswered.

---

## Category 1: Structural Defects

### 1.1 — Two Documents, One File (Critical)

The file contains **two distinct documents** that are concatenated without a separator or explicit boundary:

- **Document A** (lines 1–197): `The Agentic Workbench Architecture v2.0: Complete Specification`
- **Document B** (lines 199–316): `The Agentic Workbench Architecture v2.0: Implementation Mapping & Topology`

Document B begins with a new `# H1` heading at line 199 but shares the same H1 title prefix. This creates a document that has **two root headings**, which is invalid for a specification. A reader cannot determine which document is authoritative when they conflict.

**Recommendation:** Either merge them into a single coherent document with a unified section hierarchy, or explicitly split them into two separate files (`v2-specification.md` and `v2-implementation.md`) with cross-references between them.

---

### 1.2 — Heading Hierarchy Collision in Section 5 (Critical)

In Document B, Section 5 ("Lifecycle & Upgrades") has a **broken heading hierarchy**:

```
### 5\. Lifecycle & Upgrades        ← H3 (should be H2, like sections 1–4)
### 1\. The Core Principle...        ← H3 sub-section numbered "1"
### 2\. Initialization...            ← H3 sub-section numbered "2"
### 3\. The Upgrade Protocol...      ← H3 sub-section numbered "3"
### 4\. How to Implement This Next   ← H3 sub-section numbered "4"
```

Section 5 is rendered as an `H3` (`###`) while all preceding sections (1–4) are `H2` (`##`). This is a copy-paste error. Additionally, the sub-sections within Section 5 are also `H3`, making them visually indistinguishable from the parent section.

**Recommendation:** Promote `### 5\. Lifecycle & Upgrades` to `## 5\. Lifecycle & Upgrades`, and promote its sub-sections to `### H3`.

---

### 1.3 — Phase Numbering Inconsistency (Moderate)

The document uses an inconsistent phase/part numbering scheme:

| Label in Document | Actual Content |
|---|---|
| Part 1 | Separation of Powers (cross-cutting concern, not a phase) |
| Part 2 | **Phase 0** — Ideation |
| Part 3 | **Phase 1** — Standard Execution |
| Part 4 | **Phase 2** — Ad Hoc Ideas |
| Part 5 | **Phase 3** — Documentation |
| Part 6 | Persistent Memory System |
| Part 7 | GitFlow |

The "Part N" numbering and the "Phase N" numbering are **parallel but offset by 2**, which is confusing. Parts 1, 6, and 7 are cross-cutting concerns, not phases, yet they are numbered in the same sequence as the phases. A reader cannot easily map "Part 4" to "Phase 2" without re-reading.

**Recommendation:** Restructure the document into two explicit top-level sections: **"Pipeline Phases"** (containing Phase 0 through Phase 3 in sequence) and **"Cross-Cutting Concerns"** (containing the Separation of Powers, Memory System, and GitFlow). Remove the "Part N" numbering from phases entirely.

---

## Category 2: Terminology Drift

### 2.1 — The Third Entity: Three Names for One Role (Critical)

The human-facing interface is referred to by **three different names** across the document with no explicit statement that they are synonymous:

| Location | Name Used |
|---|---|
| Part 1 (line 13) | **Roo Chat (The HITL Cockpit)** |
| Document B, Section 1 (line 209) | **The HITL Cockpit (The Director)** |
| Document B, Section 4 (line 265) | **Roo Chat** (inside VS Code shell) |

The subtitle also changes: "The HITL Cockpit" is subtitled "The Governor" in Part 1 but "The Director" in Document B, Section 1.

> **Part 1:** `Roo Chat (The HITL Cockpit)` — no subtitle  
> **Doc B, §1:** `The HITL Cockpit (The Director)`

**Recommendation:** Standardize to a single canonical name throughout. Suggested: **`Roo Chat (The HITL Cockpit)`** as the proper noun, with `The Director` as its role subtitle, used consistently everywhere.

---

### 2.2 — "Product Agent" vs. "Architect Agent" (Moderate)

Stage 1 of the pipeline is described as being driven by the **"Architect"** mode in the Feature Stage Execution Matrix (line 19) and in Document B's `.roomodes` section (line 239). However, in Part 3 (the narrative description of Stage 1) and Part 4 (the Ad Hoc pipeline), the same agent is called the **"Product Agent"**:

> *"This is an active, multi-turn dialogue driven by the **Product Agent** collaborating with the Product Owner."* (line 66)  
> *"The **Product Agent** asynchronously ingests this idea."* (line 112)

These appear to be the same agent. If they are, the document must use one name. If they are distinct agents (e.g., the Product Agent is a sub-role of the Architect mode), this distinction must be explicitly defined.

**Recommendation:** Clarify whether "Product Agent" is an alias for the Architect mode or a separate custom mode. If an alias, standardize to "Architect Agent." If distinct, add it to the `.roomodes` mapping in Document B, Section 3B.

---

### 2.3 — "Workbench Orchestrator" vs. "Orchestrator" (Moderate)

In Stage 2 (line 84), the entity that runs the tests is called the **"Workbench Orchestrator"**:

> *"The **Workbench Orchestrator** automatically runs these tests against the codebase."*

Everywhere else, this role is simply called **"The Orchestrator"** or the **"Orchestrator mode"**. The prefix "Workbench" implies it might be the Python Arbiter scripts rather than the Roo Code Orchestrator mode. This is a critical ambiguity: is the test runner the **Python Arbiter** (deterministic) or the **Roo Orchestrator** (probabilistic)?

**Recommendation:** Clarify and standardize. If the test runner is the Python Arbiter's `Test Orchestrator` script (as defined in Document B, §3A), call it that. Reserve "Orchestrator" exclusively for the Roo Code agent mode.

---

### 2.4 — `.clinerules` vs. `.cursorrules` (Minor)

The document references both `.clinerules` and `.cursorrules` as the system guardrail file:

- Part 3, Stage 2 (line 82): `".cursorrules, biome.json"`
- Document B, §3C (line 246): `".clinerules / .cursorrules (System Guardrails)"`
- Document B, §5.1 (line 279): `".clinerules, .roomodes"`

The document never explicitly states whether these are the same file, two separate files, or whether `.cursorrules` is a legacy alias. In the Roo Code ecosystem, `.clinerules` is the canonical file.

**Recommendation:** Declare `.clinerules` as the canonical file. If `.cursorrules` is supported for Cursor IDE compatibility, note it explicitly as an alias. Remove the ambiguous slash notation `/.cursorrules`.

---

## Category 3: Logical Gaps and Contradictions

### 3.1 — Stage 2 File Access Contradiction (Critical)

The **Feature Stage Execution Matrix** (line 20) states that the Test Engineer in Stage 2 has:

> `File Access Constraints: /src (RW)`

However, Document B's `.roomodes` definition (line 240) states:

> *"**Test Engineer (Stage 2):** Read/Write access to `/src` to generate failing test suites based on the Gherkin scenarios."*

This is **logically incorrect**. Test files (`.spec.ts`) should be written to `/tests`, not `/src`. The Test Engineer should have **RW access to `/tests`** and **Read-Only access to `/src`** (to understand the existing code structure). Writing test files into `/src` would violate the separation of source code and test code.

**Recommendation:** Correct the Matrix row for Stage 2 to: `/tests` (RW), `/src` (R). Update the `.roomodes` description accordingly.

---

### 3.2 — Stage 3 File Access Contradiction (Critical)

The **Feature Stage Execution Matrix** (line 21) states that the Developer in Stage 3 has:

> `File Access Constraints: All (Read-Only)`

This is **directly contradictory** to the stage's purpose. Stage 3 is "The Autonomous Execution Engine" — the Developer Agent must **write** feature source code to `/src`. A Read-Only constraint would make the entire stage impossible to execute.

**Recommendation:** Correct the Matrix row for Stage 3 to: `/src` (RW), `/tests` (R), `.feature` (R). The Developer should not be able to modify test files or feature contracts.

---

### 3.3 — The "Inbox" Gherkin Tagging Contradiction (Moderate)

Part 4, Case A (line 112) states that inbox items are formatted into Gherkin syntax but tagged `@draft` and stored without a Traceability ID. However, Part 3, Stage 1 (line 69) states:

> *"Every requirement in the initial narrative is assigned a unique Traceability ID."*

The Inbox flow bypasses Stage 1's Iterative Chunking Loop entirely, yet produces Gherkin output. This raises the question: **which agent produces the Inbox Gherkin, and under what mode?** The document implies it is the "Product Agent" but does not specify the mode, the file access constraints, or whether the Arbiter's Gherkin Syntax Check gate applies.

**Recommendation:** Add an explicit sub-section defining the Inbox agent's mode, file access scope, and whether the Arbiter validates `@draft` Gherkin syntax. Clarify that the Backlog Gate (not the Requirement Gate HITL 1) is the approval mechanism for inbox items.

---

### 3.4 — The "Pivot" Flow Missing State Transition (Moderate)

Part 4, Case B (line 115–121) describes the Pivot flow but does not specify what happens to `state.json` during the pivot. The document states the Orchestrator "flags test files" and the state shifts to Red, but:

- Does the Arbiter explicitly write a `PIVOT_IN_PROGRESS` state to `state.json`?
- Is the current Stage 3 loop interrupted, or does it complete before the pivot takes effect?
- What happens to the Git branch — is a new branch created, or does the pivot happen in-place?

**Recommendation:** Add a state transition diagram or explicit bullet points describing the `state.json` values during a Pivot, and clarify the branch strategy for mid-stage requirement changes.

---

### 3.5 — The Compliance Snapshot Trigger is Ambiguous (Moderate)

Part 5, Stage 2 (line 135) states:

> *"When the Orchestrator detects a major release tag triggered at the Delivery Gate..."*

This conflates two distinct actors. The **Delivery Gate** is a human approval action (HITL 2), but the entity that "detects" the release tag is described as "the Orchestrator." It is unclear whether this is:

- The **Roo Orchestrator agent** (probabilistic, unreliable for compliance triggers), or
- The **Python Arbiter** (deterministic, the correct choice for compliance triggers)

Given that compliance snapshots are immutable legal artifacts, they must be triggered deterministically.

**Recommendation:** Explicitly assign the compliance snapshot trigger to the **Python Arbiter** (specifically, a Git hook on release tag creation), not the Orchestrator agent.

---

### 3.6 — Memory Rotation Scope Undefined (Minor)

Part 6 (line 160) states that at sprint end, "hot-context files are rotated here using a script." Document B, §3A names this the **Memory Rotator** script. However, the document does not specify:

- Which specific files are rotated (all of them, or only `activeContext.md` and `progress.md`)?
- Whether `handoff-state.md` and `session-checkpoint.md` are rotated or reset?
- Whether `RELEASE.md` is ever rotated (it is described as a "single source of truth," implying it should persist).

**Recommendation:** Add a table in Part 6 explicitly listing each Hot Zone file and its rotation policy (Rotate / Reset / Persist).

---

### 3.7 — `develop` Branch Description is Imprecise (Minor)

Part 7 (line 182) describes the `develop` branch as:

> *"Wild mainline for ad-hoc features and experiments."*

The word "Wild" is informal and contradicts the document's overall tone of rigorous determinism. More importantly, it implies `develop` is an uncontrolled branch, yet the document also states all new development must target `develop`. If `develop` is the integration target for all feature branches, it is not "wild" — it is the primary integration branch.

**Recommendation:** Replace "Wild mainline" with "Primary integration mainline." Clarify that direct commits to `develop` are also forbidden (only PR merges from feature branches are permitted), or explicitly state that direct commits to `develop` are allowed (unlike `main`).

---

### 3.8 — `workbench-cli.py` Source Location Undefined (Minor)

Section 5.2 (line 284) introduces `workbench-cli.py` as the deterministic bootstrapper but does not specify where this script lives before it is used to initialize a new project. It cannot live inside the project it is initializing. Section 5.4 (line 310) implies it is a "global Python script," but the installation mechanism is never described.

**Recommendation:** Add a brief note specifying that `workbench-cli.py` is installed globally (e.g., via `pip install agentic-workbench-cli` or by cloning the template repo and adding it to `PATH`), and that it is maintained in the `agentic-workbench-template` repository.

---

## Summary Table of Findings

| # | Severity | Category | Section | Issue |
|---|---|---|---|---|
| 1.1 | 🔴 Critical | Structure | Entire doc | Two documents merged under one H1 |
| 1.2 | 🔴 Critical | Structure | Doc B, §5 | Section 5 is H3 instead of H2; sub-sections collide |
| 1.3 | 🟡 Moderate | Structure | Parts 1–7 | Part N and Phase N numbering are offset and confusing |
| 2.1 | 🔴 Critical | Terminology | Parts 1, Doc B §1, §4 | HITL entity has 3 names and 2 subtitles |
| 2.2 | 🟡 Moderate | Terminology | Parts 3, 4, Doc B §3B | "Product Agent" vs. "Architect Agent" undefined |
| 2.3 | 🟡 Moderate | Terminology | Part 3, Doc B §3A | "Workbench Orchestrator" vs. "Orchestrator" ambiguous |
| 2.4 | 🟢 Minor | Terminology | Parts 3, Doc B §3C, §5 | `.clinerules` vs. `.cursorrules` not reconciled |
| 3.1 | 🔴 Critical | Logic | Matrix, Doc B §3B | Stage 2 Test Engineer has RW on `/src` instead of `/tests` |
| 3.2 | 🔴 Critical | Logic | Matrix | Stage 3 Developer has Read-Only access — cannot write code |
| 3.3 | 🟡 Moderate | Logic | Part 4, Case A | Inbox Gherkin production flow is underspecified |
| 3.4 | 🟡 Moderate | Logic | Part 4, Case B | Pivot flow missing `state.json` transitions and branch strategy |
| 3.5 | 🟡 Moderate | Logic | Part 5, Stage 2 | Compliance snapshot trigger assigned to wrong actor |
| 3.6 | 🟢 Minor | Logic | Part 6 | Memory rotation policy per-file not defined |
| 3.7 | 🟢 Minor | Logic | Part 7 | `develop` branch described as "Wild" — imprecise and contradictory |
| 3.8 | 🟢 Minor | Logic | Doc B, §5.2 | `workbench-cli.py` global installation mechanism undefined |

---

## Corrected Feature Stage Execution Matrix

The matrix as written contains two critical errors (findings 3.1 and 3.2). The corrected version:

| Stage | Roo Mode | File Access Constraints | Arbiter's Gate | Memory Sync Actions |
| :---- | :---- | :---- | :---- | :---- |
| **Stage 1: Architect** | Architect | `.feature` (RW) / `/tests` (RW) / `/src` (R) | Gherkin Syntax Check | REQ-ID assigned |
| **Stage 2: Test Engineer** | Test Engineer | `/tests` (RW) / `/src` (R) | Confirmed Red State | Traceability Map updated |
| **Stage 3: Developer** | Developer/Code | `/src` (RW) / `/tests` (R) / `.feature` (R) | Confirmed Green State | Git Commit (REQ-ID) |
| **Stage 4: Review** | Orchestrator | All (Read-Only) | Human Approval | `current_state_summary` updated |

> **Note on Stage 1:** The original matrix lists `/tests` (RW) for the Architect. This is unusual — the Architect should be generating `.feature` files, not test files. Clarify whether the Architect writes skeleton test stubs (as a contract scaffold) or whether `/tests` access is a carry-over error. If the Architect does not write to `/tests`, remove that permission.

---

## Recommended Next Steps

1. **Resolve the two-document structure** — decide on merge vs. split and apply consistently.
2. **Fix the four Critical findings** (1.1, 1.2, 2.1, 3.1, 3.2) before any implementation work begins.
3. **Add a Glossary section** defining all named actors (Arbiter, Orchestrator, Product Agent, HITL Cockpit, etc.) with their canonical names, roles, and tool implementations. This single addition would prevent most of the terminology drift found in this review.
4. **Add a State Transition Diagram** for `state.json` covering all states: `INIT → RED → GREEN → REVIEW → MERGED`, plus `PIVOT_IN_PROGRESS` and `UPGRADE_IN_PROGRESS`.
5. **Add a per-file Memory Rotation Policy table** to Part 6.

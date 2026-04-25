# Agentic Workbench v2 â€” Mermaid Diagram Suite

**Source:** [`Agentic Workbench v2 - Draft.md`](../Agentic%20Workbench%20v2%20-%20Draft.md)  
**Generated:** 2026-04-12  
**Purpose:** Visual reference for all sequences, workflows, state machines, stages, roles, journeys, GitFlow, naming conventions, and domain separations defined in the v2 specification.

> **Note:** This diagram suite has been split into smaller files for better Mermaid preview performance. Each file contains logically grouped diagrams (~3â€“4 per file).

---

## Diagram Index

### [ðŸ“ System Overview](01-system-overview.md)
Covers the big-picture architecture and human-facing views.

| # | Diagram | Theme |
|---|---------|-------|
| 1 | [Separation of Powers: The Operational Triad](01-system-overview.md#diagram-1--separation-of-powers-the-operational-triad) | The constitutional triad: Human, Agent, Arbiter |
| 2 | [Full Human Journey: Ideation to Merged Code](01-system-overview.md#diagram-2--full-human-journey-ideation-to-merged-code) | End-to-end human touchpoints |
| 20 | [Full System Topology: All Components](01-system-overview.md#diagram-20--full-system-topology-all-components) | Complete bird's-eye system view |

---

### [âš™ï¸ Phase 0 & Execution Pipeline](02-phase0-and-pipeline.md)
Covers the ideation pipeline and the four-stage execution flow.

| # | Diagram | Theme |
|---|---------|-------|
| 3 | [Phase 0: Ideation and Discovery Pipeline](02-phase0-and-pipeline.md#diagram-3--phase-0-ideation-and-discovery-pipeline) | Socratic interview and narrative drafting |
| 4 | [Phase 1: Standard Execution Pipeline Overview](02-phase0-and-pipeline.md#diagram-4--phase-1-standard-execution-pipeline-overview) | Four-stage pipeline at a glance |
| 5 | [Stage 1: Iterative Chunking Loop](02-phase0-and-pipeline.md#diagram-5--stage-1-iterative-chunking-loop) | Decomposing narratives into Gherkin contracts |

---

### [ðŸ”´ TDD, State Machine & Memory Rotation](03-tdd-and-state.md)
Covers the TDD red/green cycle, the state machine, and development cycle-end memory rotation.

| # | Diagram | Theme |
|---|---------|-------|
| 6 | [Stage 2 and 3: TDD Red/Green Execution Loop](03-tdd-and-state.md#diagram-6--stage-2-and-3-tdd-redgreen-execution-loop) | Test Engineer â†’ Developer closed loop |
| 7 | [state.json State Machine](03-tdd-and-state.md#diagram-7--statejson-state-machine) | All valid states and transitions |
| 19 | [Memory Rotation Policy at Development Cycle End](03-tdd-and-state.md#diagram-19--memory-rotation-policy-at-development-cycle-end) | Rotate / Persist / Reset policies |

---

### [ðŸ”€ Ad Hoc Ideas, Pivot & HITL Gates](04-adhoc-and-pivot.md)
Covers the inbox quarantine, mid-stage pivots, documentation engine, and human decision gates.

| # | Diagram | Theme |
|---|---------|-------|
| 8 | [Phase 2: Ad Hoc Ideas Pipeline â€” Inbox vs Pivot](04-adhoc-and-pivot.md#diagram-8--phase-2-ad-hoc-ideas-pipeline--inbox-vs-pivot) | Low-priority inbox vs urgent pivot |
| 9 | [Phase 2 Case B: The Pivot Flow in Detail](04-adhoc-and-pivot.md#diagram-9--phase-2-case-b-the-pivot-flow-in-detail) | Step-by-step pivot sequence |
| 10 | [Phase 3: Documentation and Compliance Engine](04-adhoc-and-pivot.md#diagram-10--phase-3-documentation-and-compliance-engine) | Continuous docs and compliance snapshots |
| 18 | [HITL Gates: Human Decision Points Journey](04-adhoc-and-pivot.md#diagram-18--hitl-gates-human-decision-points-journey) | Every human decision gate in the system |

---

### [ðŸ§  Memory, Sessions & Infrastructure](05-memory-sessions-and-infra.md)
Covers the hot/cold memory architecture, session lifecycle, agent handoffs, GitFlow, naming conventions, engine vs payload separation, and the CLI.

| # | Diagram | Theme |
|---|---------|-------|
| 11 | [Persistent Memory System: Hot/Cold Architecture](05-memory-sessions-and-infra.md#diagram-11--persistent-memory-system-hotcold-architecture) | Hot zone, cold zone, and rotation policies |
| 12 | [Session Lifecycle: Startup and Close Protocols](05-memory-sessions-and-infra.md#diagram-12--session-lifecycle-startup-and-close-protocols) | CHECK-CREATE-READ-ACT and close protocol |
| 13 | [Inter-Agent Handoff Protocol](05-memory-sessions-and-infra.md#diagram-13--inter-agent-handoff-protocol) | handoff-state.md as inter-agent message bus |
| 14 | [GitFlow and Branch Strategy](05-memory-sessions-and-infra.md#diagram-14--gitflow-and-branch-strategy) | All branch types and forbidden actions |
| 15 | [Naming Conventions and File Taxonomy](05-memory-sessions-and-infra.md#diagram-15--naming-conventions-and-file-taxonomy) | Branch, commit, file, and directory naming |
| 16 | [Separation of Domains: Engine vs Payload](05-memory-sessions-and-infra.md#diagram-16--separation-of-domains-engine-vs-payload) | What the workbench owns vs what the app owns |
| 17 | [workbench-cli.py Init and Upgrade Sequences](05-memory-sessions-and-infra.md#diagram-17--workbench-clipy-init-and-upgrade-sequences) | Deterministic bootstrap and upgrade flows |

---

## Summary

| File | Diagrams | Approx. Lines |
|------|----------|---------------|
| [`01-system-overview.md`](01-system-overview.md) | 1, 2, 20 | ~250 |
| [`02-phase0-and-pipeline.md`](02-phase0-and-pipeline.md) | 3, 4, 5 | ~250 |
| [`03-tdd-and-state.md`](03-tdd-and-state.md) | 6, 7, 19 | ~200 |
| [`04-adhoc-and-pivot.md`](04-adhoc-and-pivot.md) | 8, 9, 10, 18 | ~350 |
| [`05-memory-sessions-and-infra.md`](05-memory-sessions-and-infra.md) | 11â€“17 | ~500 |

**Total diagrams:** 20  
**Coverage:** Separation of Powers, Human Journey, Ideation Pipeline, Standard Execution Pipeline, Iterative Chunking Loop, TDD Red/Green Loop, state.json State Machine, Ad Hoc Ideas Pipeline, Pivot Flow, Documentation Engine, Memory Hot/Cold Architecture, Session Lifecycle, Inter-Agent Handoff, GitFlow, Naming Conventions, Engine vs Payload Domains, CLI Init/Upgrade, Memory Rotation Policy, Full System Topology.

---

*This diagram suite was migrated from the monolithic `plans/Agentic_Workbench_v2_Mermaid_Diagrams.md` into individual logical files for better Mermaid preview performance.*

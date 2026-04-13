# Agentic Workbench v2 — Memory, Sessions & Infrastructure Diagrams

**Source:** [`Agentic Workbench v2 - Draft.md`](../Agentic%20Workbench%20v2%20-%20Draft.md)  
**Generated:** 2026-04-12  
**Coverage:** Memory Architecture, Session Lifecycle, Inter-Agent Handoff, GitFlow, Naming Conventions, Engine vs Payload, CLI Init/Upgrade

---

## Diagram 11 — Persistent Memory System: Hot/Cold Architecture

> The Hot/Cold memory architecture that counters AI drift and context-window flooding. Git is the single source of truth; every piece of memory is versioned.

```mermaid
graph TB
    subgraph HOT["Hot Zone — memory-bank/hot-context/ — Read directly by agent at session start"]
        direction TB
        H1[activeContext.md — current task & ROTATE]
        H2[progress.md — project checkbox & ROTATE]
        H3[decisionLog.md — ADRs & PERSIST]
        H4[systemPatterns.md — conventions & PERSIST]
        H5[productContext.md — sprint stories & ROTATE]
        H6[RELEASE.md — release tracking & PERSIST]
        H7[handoff-state.md — inter-agent bus & RESET]
        H8[session-checkpoint.md — crash recovery & RESET]
    end

    subgraph COLD["Cold Zone — memory-bank/archive-cold/ — NEVER read directly by agent"]
        direction TB
        C1[archived-activeContext — timestamped]
        C2[archived-progress — timestamped]
        C3[archived-productContext — timestamped]
    end

    subgraph MCP_TOOL["MCP Tool — Controlled Cold Access"]
        M1[Semantic search over cold archive]
        M2[Targeted retrieval by REQ-ID or date]
    end

    subgraph AGENTS["Agents"]
        AG1[All Agents except Librarian]
        AG2[Documentation / Librarian Agent]
    end

    subgraph ARBITER_MEM["Arbiter — memory_rotator.py"]
        AR1[Sprint-end rotation trigger]
        AR2[ROTATE: archive then reset to template]
        AR3[PERSIST: never moved]
        AR4[RESET: overwrite to empty template]
    end

    AG1 -->|reads at session start| HOT
    AG1 -->|writes updates during session| HOT
    AG2 -->|reads all zones directly| HOT
    AG2 -->|reads all zones directly| COLD
    AG1 -->|cold access only via| MCP_TOOL
    MCP_TOOL -->|queries| COLD

    AR1 -->|ROTATE H1 H2 H5| COLD
    AR1 -->|PERSIST H3 H4 H6 stays in| HOT
    AR1 -->|RESET H7 H8 overwrite in| HOT

    HOT -->|all changes versioned| GIT[Git History
Immutable record
Sessions ephemeral - Git is eternal]

    style HOT fill:#d8f3dc,color:#1b4332,stroke:#2d6a4f
    style COLD fill:#e6dcc8,color:#3d2b1f,stroke:#8b5e3c
    style MCP_TOOL fill:#d0e1f2,color:#1d3557,stroke:#457b9d
    style ARBITER_MEM fill:#f8d7da,color:#6d2b3d,stroke:#c1121f
    style H3 fill:#d8f3dc,color:#1b4332
    style H4 fill:#d8f3dc,color:#1b4332
    style H6 fill:#d8f3dc,color:#1b4332
    style H7 fill:#f8d7da,color:#6d2b3d
    style H8 fill:#f8d7da,color:#6d2b3d

    subgraph LEGEND["File Legend — memory-bank/hot-context/"]
        direction LR
        L1[activeContext.md]:::rotate
        L2[progress.md]:::rotate
        L3[decisionLog.md]:::persist
        L4[systemPatterns.md]:::persist
        L5[productContext.md]:::rotate
        L6[RELEASE.md]:::persist
        L7[handoff-state.md]:::reset
        L8[session-checkpoint.md]:::reset
    end
    classDef rotate fill:#f8d7da,color:#6d2b3d,stroke:#c1121f
    classDef persist fill:#d8f3dc,color:#1b4332,stroke:#2d6a4f
    classDef reset fill:#e6dcc8,color:#3d2b1f,stroke:#8b5e3c
```

---

## Diagram 12 — Session Lifecycle: Startup and Close Protocols

> The mandatory startup sequence and the Close Protocol that every agent must follow, enforced by `.clinerules`.

```mermaid
sequenceDiagram
    autonumber
    participant Agent as Any Agent
    participant HotZone as memory-bank/hot-context/
    participant StateJSON as state.json
    participant Arbiter as Arbiter
    participant Git as Git
    participant Docs as docs/conversations/

    Note over Agent,Docs: STARTUP PROTOCOL —
    SCAN → CHECK → CREATE → READ → ACT

    Agent->>Arbiter: SCAN: Run arbiter_check.py check-session
    alt CRITICAL violation found
        Agent->>Agent: RESOLVE before proceeding
    end

    Agent->>HotZone: CHECK: Does activeContext.md exist?

    alt activeContext.md absent
        Agent->>HotZone: CREATE: Generate from strict template
    end

    Agent->>HotZone: READ: Load activeContext.md
    Agent->>HotZone: READ: Load progress.md
    Agent->>StateJSON: READ: Load state.json and determine operational constraints

    alt session-checkpoint.md status = ACTIVE
        Agent->>Agent: DETECT: Previous session crashed
        Agent->>Agent: Offer to resume from checkpoint\nSession ID, branch, commit hash, task
    end

    Note over Agent,Docs: ACT —
    Agent performs its pipeline stage work

    Agent->>Agent: Execute pipeline stage task

    Note over Agent,Docs: CLOSE PROTOCOL — Before completing task

    Agent->>HotZone: UPDATE activeContext.md\nCurrent task, last result, next steps
    Agent->>HotZone: UPDATE progress.md\nCheckbox state
    Agent->>HotZone: UPDATE handoff-state.md\nCompletion status, artifacts, recommendations
    Agent->>HotZone: UPDATE RELEASE.md if release occurred

    Agent->>Arbiter: Signal: Close Protocol executing
    Arbiter->>Docs: SAVE immutable session metadata\ntimestamped file in docs/conversations/
    Note over Arbiter,Docs: Conversation logs NEVER edited after creation

    Agent->>Git: Commit Hot Zone updates\ndocs-memory: session-close

    Note over Agent,Docs: CRASH RECOVERY — Background daemon

    loop Every 5 minutes during active work
        Arbiter->>HotZone: HEARTBEAT: Write session-checkpoint.md\nSession ID, branch, commit hash, current task
    end
```

---

## Diagram 13 — Inter-Agent Handoff Protocol

> How agents pass the baton between pipeline stages using `handoff-state.md` as the message bus, with the Orchestrator Agent as the traffic controller.

```mermaid
sequenceDiagram
    autonumber
    participant PrevAgent as Completing Agent
    participant HandoffFile as handoff-state.md
    participant Orchestrator as Orchestrator Agent
    participant Arbiter as Arbiter
    participant StateJSON as state.json
    participant NextAgent as Next Agent

    Note over PrevAgent,NextAgent: Agent completes its pipeline stage task

    PrevAgent->>HandoffFile: LOG completion data\nCompletion status\nArtifacts created\nRecommendations for next agent\nAny blockers or warnings

    PrevAgent->>Arbiter: Signal: Stage complete

    Arbiter->>StateJSON: Read current state
    Arbiter->>StateJSON: Write next state e.g. REQUIREMENTS_LOCKED

    Arbiter->>Orchestrator: Activate for handoff management

    Orchestrator->>HandoffFile: READ: Acknowledge receipt of handoff data
    Orchestrator->>StateJSON: READ: Confirm new state
    Orchestrator->>Orchestrator: Determine subsequent workflow\nbased on state and handoff data

    alt Normal progression
        Orchestrator->>NextAgent: Activate with context\nhandoff-state.md contents\nstate.json constraints\nRelevant artifacts
        NextAgent->>HandoffFile: READ: Ingest previous agent recommendations
        NextAgent->>NextAgent: Execute startup protocol SCAN-CHECK-CREATE-READ-ACT
    else Blocker detected
        Orchestrator->>Arbiter: Report blocker
        alt Blocker requires human
            Arbiter->>Arbiter: Generate report for HITL review
        else Blocker is auto-resolvable
            Orchestrator->>PrevAgent: Re-activate with blocker details
        end
    end

    Note over PrevAgent,NextAgent: After handoff complete
    Arbiter->>HandoffFile: RESET: Clear for next handoff cycle
```

---

## Diagram 14 — GitFlow and Branch Strategy

> The absolute branching strategy. Every branch type, its lifecycle, merge direction, and forbidden actions.

```mermaid
gitGraph
   commit id: "chore: initialize Agentic Workbench v2.0" tag: "v0.0.1"

   branch develop
   checkout develop
   commit id: "chore: setup project scaffold"

   branch feature/Sprint1/REQ-001-user-auth
   checkout feature/Sprint1/REQ-001-user-auth
   commit id: "feat: REQ-001 Gherkin contracts"
   commit id: "test: REQ-001 failing test suite"
   commit id: "feat: REQ-001 implement auth logic"
   commit id: "feat: REQ-001 all tests GREEN"

   checkout develop
   merge feature/Sprint1/REQ-001-user-auth id: "merge: REQ-001 via PR no-ff"

   branch feature/Sprint1/REQ-002-reporting
   checkout feature/Sprint1/REQ-002-reporting
   commit id: "feat: REQ-002 Gherkin contracts"

   branch lab/Sprint1/pdf-export-spike
   checkout lab/Sprint1/pdf-export-spike
   commit id: "lab: explore PDF generation options"
   commit id: "lab: prototype approach"

   checkout feature/Sprint1/REQ-002-reporting
   merge lab/Sprint1/pdf-export-spike id: "merge: lab findings into feature"
   commit id: "feat: REQ-002 implement reporting"

   checkout develop
   merge feature/Sprint1/REQ-002-reporting id: "merge: REQ-002 via PR no-ff"

   branch stabilization/v1.0
   checkout stabilization/v1.0
   commit id: "fix: polish release candidate"
   commit id: "docs: update release notes"

   checkout main
   merge stabilization/v1.0 id: "release: v1.0.0" tag: "v1.0.0"

   checkout develop
   merge main id: "chore: fast-forward develop to main"

   branch hotfix/TICKET-042
   checkout hotfix/TICKET-042
   commit id: "fix: critical auth bypass patch"

   checkout main
   merge hotfix/TICKET-042 id: "hotfix: TICKET-042 to main" tag: "v1.0.1"

   checkout develop
   merge hotfix/TICKET-042 id: "hotfix: TICKET-042 to develop"
```

> **Forbidden Actions:** Never commit directly to `main` after a release tag. Never commit on a branch already merged to `main`. Never use `--delete-branch` when merging PRs. All new development must target `develop`, a stabilization branch, or a feature branch.

---

## Diagram 15 — Naming Conventions and File Taxonomy

> Every naming pattern used in the system: branches, commits, files, REQ-IDs, and directories.

```mermaid
mindmap
  root((Naming Conventions))
    Branch Names
      main
        Production state
        Frozen - never commit directly
      develop
        Primary integration mainline
        Long-lived - never deleted
      feature/Timebox/REQ-NNN-slug
        e.g. feature/Sprint1/REQ-042-user-auth
        Merges via PR with no-ff
        Never deleted after merge
      lab/Timebox/slug
        e.g. lab/Sprint1/pdf-export-spike
        Ad-hoc experimental exploration
      stabilization/vX.Y
        e.g. stabilization/v1.2
        Permanent artifact for traceability
      hotfix/Ticket
        e.g. hotfix/TICKET-042
        Branched from production tag on main
      pivot/ticket-id
        e.g. pivot/TICKET-099
        Mid-stage requirement change isolation
    Commit Messages
      Conventional Commits format
        feat-scope - new feature
        fix-scope - bug fix
        docs-memory - memory bank update
        chore-config - configuration change
        chore-workbench - workbench engine change
        test-scope - test additions
      REQ-ID in feat commits
        e.g. feat-auth: REQ-001 implement login flow
    File Names
      Feature Files
        REQ-NNN-slug.feature
        e.g. REQ-042-user-authentication.feature
        Stored in /features/ when active
        Stored in _inbox/ when @draft
      Unit Test Files
        REQ-NNN-slug.spec.ts
        e.g. REQ-042-user-authentication.spec.ts
        Stored in /tests/unit/
        REQ-NNN scoped
      Integration Test Files
        FLOW-NNN-slug.integration.spec.ts
        e.g. FLOW-001-auth-checkout-flow.integration.spec.ts
        Stored in /tests/integration/
        FLOW-NNN tagged
      Session Logs
        YYYY-MM-DD-session-id.md
        Stored in docs/conversations/
        Immutable after creation
    Internal File Tags
      @REQ-NNN
        Traceability tag inside .feature files
        Links to REQ-ID
      @draft
        Inbox items without REQ-ID
        Not yet promoted to pipeline
      @depends-on: REQ-NNN
        Dependency declaration in .feature files
        Parsed by Arbiter Gherkin Validator
    Directory Structure
      /src - Application source code
      /tests/unit - Unit and acceptance tests REQ-NNN scoped
      /tests/integration - Cross-boundary tests FLOW-NNN tagged
      /features - Active Gherkin contracts
      /_inbox - Draft ideas quarantine
      /memory-bank/hot-context - Active memory
      /memory-bank/archive-cold - Rotated memory
      /.workbench/scripts - Arbiter Python scripts
      /docs/conversations - Immutable audit trail
      /compliance-vault - Read-only compliance artifacts
```

---

## Diagram 16 — Separation of Domains: Engine vs Payload

> The rigid boundary between what the Workbench owns and what the Application owns. Engine files can be overwritten during upgrades; Payload files are never touched.

```mermaid
graph TB
    subgraph ENGINE["ENGINE — Owned by the Workbench — CAN be overwritten during upgrade"]
        direction TB
        E1[.clinerules
Behavioral constitution
Session protocols, handoff rules, traceability mandates]
        E2[.roomodes
Agent role definitions
System prompts and file access constraints]
        E3[.workbench/scripts/
Python Arbiter scripts
test_orchestrator.py, integration_test_runner.py
dependency_monitor.py, gherkin_validator.py
memory_rotator.py, audit_logger.py
crash_recovery.py]
        E4[.husky/ or .workbench/hooks/
Git hooks
pre-commit, pre-push, post-tag]
        E5[biome.json
Root-level linting and formatting
Configured for JS/TS projects — see pyproject.toml for Python]
        E6[.workbench-version
Engine version tracking]
    end

    subgraph PAYLOAD["PAYLOAD — Owned by the Application — NEVER touched by workbench upgrade"]
        direction TB
        P1[src/
Application source code]
        P2[tests/
Unit tests in tests/unit/
Integration tests in tests/integration/]
        P3[features/
Active Gherkin contracts]
        P4[_inbox/
Draft ideas quarantine]
        P5[memory-bank/
Hot and Cold zones
except core templates]
        P6[package.json and docker-compose.yml
Application configuration]
        P7[docs/conversations/
Immutable audit trail]
        P8[compliance-vault/
Compliance artifacts]
    end

    subgraph TEMPLATE["agentic-workbench-engine repo
Source of truth for Engine files"]
        T1[Latest .clinerules]
        T2[Latest .roomodes]
        T3[Latest Arbiter scripts]
        T4[Latest Git hooks]
    end

    subgraph CLI["workbench-cli.py — Global install — not in app repo"]
        C1[init command
Scaffolds new project]
        C2[upgrade command
Patches Engine only]
        C3[status command
Reads state.json]
        C4[rotate command
Sprint-end memory rotation]
    end

    TEMPLATE -->|init: copies Engine files into| ENGINE
    TEMPLATE -->|upgrade: overwrites Engine files in| ENGINE
    CLI -->|orchestrates| TEMPLATE
    CLI -->|never touches| PAYLOAD
    ENGINE -.->|governs behavior of agents working on| PAYLOAD

    style ENGINE fill:#f8d7da,color:#6d2b3d,stroke:#c1121f
    style PAYLOAD fill:#d8f3dc,color:#1b4332,stroke:#2d6a4f
    style TEMPLATE fill:#d0e1f2,color:#1d3557,stroke:#457b9d
    style CLI fill:#e6dcc8,color:#3d2b1f,stroke:#8b5e3c
```

---

## Diagram 17 — workbench-cli.py Init and Upgrade Sequences

> The deterministic bootstrapper sequences. AI must NOT be used for initialization or upgrades — only the Python CLI handles these foundational operations.

```mermaid
sequenceDiagram
    autonumber
    actor Dev as Developer
    participant CLI as workbench-cli.py
    participant Template as agentic-workbench-engine repo
    participant NewRepo as New Application Repository
    participant Arbiter as Arbiter scripts
    participant StateJSON as state.json
    participant Git as Git

    Note over Dev,Git: INIT SEQUENCE — python workbench-cli.py init my-new-app

    Dev->>CLI: python workbench-cli.py init my-new-app

    CLI->>NewRepo: Step 1 - Repository Generation\nCreate target folder\ngit init\nConfigure initial branch to main

    CLI->>NewRepo: Step 2 - Directory Scaffolding\nCreate /src /tests /features /_inbox\nmemory-bank/hot-context/\n.workbench/scripts/\ndocs/conversations/

    CLI->>Template: Fetch latest Engine files
    Template->>CLI: Return .clinerules .roomodes\nArbiter scripts Git hooks biome.json

    CLI->>NewRepo: Step 3 - Engine Injection\nCopy .clinerules .roomodes\nCopy Arbiter scripts to .workbench/scripts/\nCopy Git hooks to .husky/

    CLI->>StateJSON: Step 4 - State Initialization\nGenerate fresh state.json\nstate = INIT, version = 2.0

    CLI->>Git: Step 5 - Initial Commit\nchore-workbench: initialize Agentic Workbench v2.0

    CLI->>Dev: Scaffold complete - Project ready for Phase 0 ideation

    Note over Dev,Git: UPGRADE SEQUENCE — python workbench-cli.py upgrade --version v3.0

    Dev->>CLI: python workbench-cli.py upgrade --version v3.0

    CLI->>Arbiter: Step 1 - Safety Check\nRead state.json and handoff-state.md

    alt State is INIT or MERGED
        Arbiter->>CLI: SAFE: Proceed with upgrade

        CLI->>Template: Fetch v3.0 Engine files
        Template->>CLI: Return updated Engine files

        CLI->>NewRepo: Step 2 - Engine Overwrite\nForce-overwrite .clinerules\nForce-overwrite .roomodes\nForce-overwrite .workbench/scripts/\nForce-overwrite Git hooks

        CLI->>NewRepo: Step 3 - Memory Migration\nProvision new memory templates if required\nDo NOT delete existing memory files

        CLI->>NewRepo: Step 4 - Version Bumping\nUpdate .workbench-version to v3.0

        CLI->>Git: Step 5 - Commit\nchore-workbench: upgrade engine to v3.0

        CLI->>Dev: Upgrade complete

    else State is active
        Arbiter->>CLI: REFUSED: Active development in progress
        CLI->>Dev: ERROR: Cannot upgrade during active development\nComplete or pause current work first
    end

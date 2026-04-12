# Agentic Workbench Lab — `agentic-workbench-lab`

**Purpose:** Specs + Design + Validation for the Agentic Workbench v2

This repository is the development and validation environment for the Agentic Workbench v2 engine. It is **not** an application project template — it does not contain `src/`, `features/`, `tests/unit/`, or `tests/integration/` directories. Those belong in application repos that use the workbench.

---

## What This Repo Contains

| Directory | Purpose |
|---|---|
| [`agentic-workbench-engine/`](./agentic-workbench-engine/) | Git submodule — pinned reference to the canonical `agentic-workbench-engine` repo. This is the single source of truth for all engine files. |
| [`tests/workbench/`](./tests/workbench/) | Validation test suite — runs against the engine submodule to verify engine correctness |
| [`docs/`](./docs/) | Human-readable documentation including the Beginner's Guide |
| [`diagrams/`](./diagrams/) | Architecture diagrams (Mermaid .md files) |
| [`plans/`](./plans/) | Implementation plans, strategy documents, and gap analyses |
| [`memory-bank/hot-context/`](./memory-bank/hot-context/) | Active context for agent sessions working on the workbench itself |
| `Agentic Workbench v2 - Draft.md` | Master specification document |
| `Canonical_Naming_Conventions.md` | Naming reference |

---

## The Two-Repo Architecture

```
agentic-workbench-engine  (canonical engine repo)
  └── The Workbench (Layer 3) — .clinerules, .roomodes, .workbench/scripts/, workbench-cli.py
  └── Consumed by: workbench-cli.py init / upgrade

agentic-workbench-lab  (this repo — specs + design + validation)
  └── agentic-workbench-engine/ as git submodule (pinned)
  └── tests/workbench/ validation suite
  └── Specs, diagrams, implementation plans
  └── NOT an application project
```

---

## How the Engine Submodule Works

The `agentic-workbench-engine/` subdirectory is a **git submodule** — it points to a specific commit of the canonical engine repo. This means:

- **Zero drift** — the embedded engine is always a known, pinned version
- **Explicit updates** — updating the engine is a deliberate `git submodule update` + commit in this repo
- **CI-safe** — `git submodule update --init` in CI always gets the right version

To update the embedded engine to the latest canonical version:

```bash
cd agentic-workbench-engine
git pull origin main
cd ..
git add agentic-workbench-engine
git commit -m "chore: update engine submodule to latest"
```

To run the validation suite:

```bash
pytest tests/workbench/ -v
```

---

## How to Use This Repo

### As a Workbench Developer

1. Clone this repo with submodules:
   ```bash
   git clone --recurse-submodules git@github.com:your-org/agentic-workbench-lab.git
   ```

2. If you cloned without submodules, initialize them:
   ```bash
   git submodule update --init --recursive
   ```

3. Open in VS Code with Roo Code extension

4. Run the validation suite:
   ```bash
   pytest tests/workbench/ -v
   ```

### As an Application Developer

You do **not** need this repo. You need the `agentic-workbench-engine` repo and the `workbench-cli.py`:

```bash
# Clone the engine repo
git clone git@github.com:your-org/agentic-workbench-engine.git ~/agentic-workbench-engine
export PATH="$PATH:~/agentic-workbench-engine"

# Initialize a new application project
python workbench-cli.py init my-new-app
```

---

## Key Files

| File | Purpose |
|---|---|
| `.clinerules` | System guardrails — governs agent behavior in this repo |
| `.workbench-version` | Version of the engine this lab repo currently references |
| `.roomodes` | Custom agent modes |
| `memory-bank/hot-context/decisionLog.md` | Architecture Decision Records (ADRs) |
| `memory-bank/hot-context/systemPatterns.md` | Technical conventions |
| `plans/Repo_Cleanup_and_Deployment_Strategy.md` | This repo's own architecture plan |

---

## Versioning

The lab repo does **not** have its own version number. It tracks the version of the engine it references via the `agentic-workbench-engine` submodule. Check the engine version with:

```bash
cat agentic-workbench-engine/.workbench-version
```

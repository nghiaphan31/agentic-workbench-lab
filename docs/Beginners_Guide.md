# Agentic Workbench v2 — Beginner's Guide

This guide provides clear, step-by-step instructions for two scenarios:
1. **Starting a new application project** with the Agentic Workbench
2. **Upgrading an existing project** to a newer version of the workbench

---

## Prerequisites

Before using the Agentic Workbench, you need:

- **Python 3.10+** installed and accessible from command line
- **Git** installed and configured (with your name and email)
- **VS Code** installed (recommended)
- **Roo Code extension** installed in VS Code
- Access to the `agentic-workbench-engine` repository (canonical engine)

---

## Part 1: Starting a New Application Project

This section walks you through creating a brand new application from scratch using the Agentic Workbench.

### Step 1.1: Install the Workbench CLI

The Workbench Command-Line Interface (CLI) is the bootstrapper that sets up new projects and upgrades existing ones.

**Option A: Clone the template repository (recommended)**

```bash
# Clone the template repository to a convenient location
git clone https://github.com/your-org/agentic-workbench-engine.git ~/agentic-workbench-engine

# Verify the clone succeeded
cd ~/agentic-workbench-engine
ls -la
```

You should see these key files:
- `workbench-cli.py` — the main CLI tool
- `.clinerules` — system guardrails
- `.roomodes` — custom agent modes
- `.workbench/` — Arbiter scripts directory

**Option B: pip install — Local install supported**

```bash
# Local install via pyproject.toml in agentic-workbench-engine/
# PyPI publishing pending — coming soon
pip install -e agentic-workbench-engine/
```

### Step 1.2: Add the CLI to your system PATH

For the `workbench-cli.py` command to work from any directory, add it to your PATH:

**On macOS/Linux — Add to ~/.bashrc or ~/.zshrc:**

```bash
# Add this line to your shell config file
export PATH="$PATH:~/agentic-workbench-engine"

# Reload your shell config
source ~/.bashrc   # or: source ~/.zshrc
```

**On Windows:**

1. Press `Win + R`, type `sysdm.cpl`, press Enter
2. Go to **Advanced** → **Environment Variables**
3. Under **User variables**, find **Path** and click **Edit**
4. Click **New** and add: `C:\Users\YourUsername\agentic-workbench-engine`
5. Click **OK** on all dialogs

**Verify the CLI is accessible:**

```bash
# Open a new terminal and run:
python workbench-cli.py --version
```

You should see output like: `Agentic Workbench CLI v2.1`

### Step 1.3: Create your new project directory

Decide where you want your new application to live. For this guide, we'll create a project called `my-first-workbench-app`.

```bash
# Navigate to where you keep your projects
cd ~/projects

# Create the project directory (don't cd into it yet — the CLI does that)
# The CLI will create this directory if it doesn't exist
```

### Step 1.4: Initialize the project

Now run the initialization command. This is the most important step — it sets up the entire project scaffold.

```bash
# Run the initialization command
# Replace "my-first-workbench-app" with your desired project name
python workbench-cli.py init my-first-workbench-app
```

**What happens during initialization:**

1. **Directory Creation** — Creates `my-first-workbench-app/` folder and `cd`s into it
2. **Git Initialization** — Runs `git init` and sets branch to `main`
3. **Directory Scaffolding** — Creates the required folder structure:
   ```
   my-first-workbench-app/
   ├── .workbench/
   │   ├── hooks/          # Git hooks (pre-commit, pre-push, etc.)
   │   └── scripts/        # Arbiter Python scripts
   ├── docs/
   │   └── conversations/  # Audit trail for sessions
   ├── features/           # Gherkin feature files
   ├── memory-bank/
   │   ├── archive-cold/   # Rotated-out memory files
   │   └── hot-context/    # Active memory files
   ├── src/                # Your application source code
   ├── tests/
   │   ├── integration/    # Integration tests
   │   └── unit/          # Unit/acceptance tests
   ├── _inbox/             # Draft feature ideas (not yet official)
   ├── .clinerules         # System guardrails (copied from template)
   ├── .roomodes           # Custom agent modes (copied from template)
   ├── .roo-settings.json  # Roo Code settings
   ├── .workbench-version  # Workbench version file
   └── state.json          # Master state file
   ```
4. **Engine Injection** — Copies `.clinerules`, `.roomodes`, and scripts from the template
5. **State Initialization** — Creates `state.json` with initial state:
   ```json
   {
     "state": "INIT",
     "arbiter_capabilities": { ... }
   }
   ```
6. **Initial Commit** — Automatically commits everything as:
   ```
   chore(workbench): initialize Agentic Workbench v2.1
   ```

**If initialization succeeds, you'll see:**
```
[WORKBENCH-CLI] Project initialized successfully!
  Navigate to: cd my-first-workbench-app
  Next: Open in VS Code with Roo Code extension
```

### Step 1.5: Open the project in VS Code

```bash
# Navigate into your new project
cd my-first-workbench-app

# Open it in VS Code
code .
```

**Alternative — without using the `code` command:**
1. Open VS Code
2. File → Open Folder
3. Navigate to `~/projects/my-first-workbench-app`
4. Click "Open"

### Step 1.6: Configure Roo Code settings

The `.roo-settings.json` file contains auto-approve rules for Roo Code. These rules define which commands Roo Code can run without asking for human approval.

**For a brand new project in Phase A (pre-Arbiter), the default settings are already configured.**

To import the settings into Roo Code:
1. Open the Command Palette: `Ctrl + Shift + P` (Windows/Linux) or `Cmd + Shift + P` (Mac)
2. Type: `Roo Code: Import Settings`
3. Press Enter
4. Select the `.roo-settings.json` file from your project root

**What the settings mean:**
- `allowedCommands` — Commands Roo can run without asking (e.g., `git status`, `git diff`)
- `deniedCommands` — Commands that always require approval (e.g., `git push`, `git commit`, `docker`)

### Step 1.7: Understand the key files

Before you start developing, familiarize yourself with these key files in your project:

| File | Purpose |
|------|---------|
| **`state.json`** | The master state file. Tracks what stage the pipeline is in, which feature is active, and test results. **Read this before every session.** |
| **`memory-bank/hot-context/activeContext.md`** | What you're working on right now. Updated every session. |
| **`memory-bank/hot-context/progress.md`** | Checklist of all features and their status. |
| **`memory-bank/hot-context/decisionLog.md`** | Architectural decisions made along the way. |
| **`.clinerules`** | The rules Roo Code follows. **Read this before every session.** |
| **`features/`** | Where your feature specifications live (Gherkin files). |

### Step 1.8: Start your first feature

You're now ready to start developing. Here's the workflow:

1. **Inject intent** — Tell Roo Code (via Roo Chat) what you want to build. Example:
   > "I want a user login system with email and password"

2. **Architect Agent activates** (Stage 1) — Roo Code asks clarifying questions to understand the requirements. This is the Socratic interrogation phase.

3. **Gherkin files created** — Roo Code translates your requirements into structured `.feature` files in `/features/`.

4. **Human approval (HITL 1)** — You review the generated `.feature` files and approve them.

5. **Test Engineer Agent activates** (Stage 2) — Roo Code writes failing tests for your features.

6. **Developer Agent activates** (Stage 3) — Roo Code writes the actual code to make tests pass.

7. **Review and merge** (Stage 4) — Human reviews the PR and approves merge.

**For your first feature, start simple!** Try a small feature like "show current date" rather than a complex payment system.

---

## Part 2: Upgrading an Existing Project

This section walks you through upgrading a project that's already using an older version of the Agentic Workbench to a newer version.

### Step 2.1: Check your current workbench version

```bash
# Navigate to your existing project
cd ~/projects/my-existing-workbench-app

# Check the current version
cat .workbench-version
```

You should see something like: `2.0`

Also check `state.json` to understand the current project state:
```bash
cat state.json
```

**Important: The upgrade will be blocked if the project is in an active development state.**

### Step 2.2: Ensure the project is in a safe state

The Arbiter will refuse to upgrade if:
- `state.json.state` is NOT `INIT` or `MERGED`
- Tests are failing
- An agent is mid-task

**To prepare for upgrade:**

1. **Wait for any active work to complete** — Let the current pipeline finish (feature reaches `MERGED`)
2. **Or, reset to INIT if you want to force upgrade:**
   ```bash
   # Edit state.json and set:
   # "state": "INIT"
   ```
   ⚠️ Only do this if you understand the consequences — it abandons any in-progress work.

3. **Verify no one is working:**
   ```bash
   cat memory-bank/hot-context/session-checkpoint.md
   ```
   If you see `status: ACTIVE`, someone is mid-session. Wait for them to finish.

### Step 2.3: Update your local template copy

Before upgrading, sync your local template repository to get the latest workbench version:

```bash
# Navigate to where you cloned the template
cd ~/agentic-workbench-engine

# Pull the latest changes
git pull origin main

# Verify the version
cat .workbench-version
```

You should see the newer version number.

### Step 2.4: Run the upgrade command

Now run the upgrade command from inside your project:

```bash
# Navigate to your project
cd ~/projects/my-existing-workbench-app

# Run the upgrade (replace 2.1 with your target version)
python workbench-cli.py upgrade --version 2.1
```

### Step 2.5: Understand the upgrade process

When you run `upgrade`, the CLI performs these steps:

1. **Safety Check** — Confirms `state.json` is in `INIT` or `MERGED`
2. **Engine Overwrite** — Replaces these files with the new version:
   - `.clinerules`
   - `.roomodes`
   - `.workbench/scripts/` (all Arbiter scripts)
   - `.workbench/hooks/` (all Git hooks)
   - `.roo-settings.json`
3. **Memory Migration** — If the new version adds new memory-bank files, they are created. **Existing memory files are preserved.**
4. **Version Bump** — Updates `.workbench-version` to the new version
5. **Auto-Commit** — Creates a commit:
   ```
   chore(workbench): upgrade engine to v2.1
   ```

### Step 2.6: Verify the upgrade succeeded

```bash
# Check the new version
cat .workbench-version

# Should output: 2.1 (or whatever version you upgraded to)
```

Check the git log to see the upgrade commit:
```bash
git log --oneline -n 5
```

You should see the upgrade commit at the top.

### Step 2.7: Review the upgrade changes

Before continuing work, review what changed:

```bash
# See what files changed
git diff HEAD~1 --stat

# See the actual changes
git diff HEAD~1
```

**Common changes you might see:**
- New rules in `.clinerules`
- New agent modes in `.roomodes`
- New or updated Arbiter scripts
- Updated `.roo-settings.json` (Roo Code permission changes)

### Step 2.8: Update your local template periodically

Whenever you want to upgrade, make sure your local template clone is up-to-date:

```bash
cd ~/agentic-workbench-engine
git pull origin main
```

---

## Appendix A: Troubleshooting

### "command not found: workbench-cli"

The CLI is not in your PATH. See [Step 1.2](#step-12-add-the-cli-to-your-system-path).

### "Error: state is not INIT or MERGED — upgrade blocked"

Your project is in an active development state. See [Step 2.2](#step-22-ensure-the-project-is-in-a-safe-state).

### "Error: Permission denied" during init

The directory might already exist. Try a different project name or delete the existing directory:
```bash
rm -rf my-first-workbench-app
python workbench-cli.py init my-first-workbench-app
```

### "Error: git configuration missing"

Set your Git name and email:
```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

### Roo Code isn't responding to `.clinerules`

Make sure `.clinerules` is in the **root** of your project (not in a subdirectory), and that you've opened that folder in VS Code.

---

## Appendix B: Key Commands Reference

The `workbench-cli.py` is the deterministic bootstrapper and state manager for the workbench.

### Initialization & Upgrades

| Command | Purpose |
|---------|---------|
| `python workbench-cli.py init <project-name>` | Create a new project with workbench scaffold |
| `python workbench-cli.py upgrade --version <vX.Y>` | Upgrade existing project to new workbench version |
| `python workbench-cli.py install-hooks` | (Re)install Arbiter hooks into `.git/hooks/` |
| `python workbench-cli.py register-arbiter` | Register all Arbiter script capabilities in `state.json` |
| `python workbench-cli.py check` | Run Arbiter compliance health scan |

### Feature Lifecycle

| Command | Purpose |
|---------|---------|
| `python workbench-cli.py start-feature --req-id REQ-NNN` | Transition INIT/MERGED → STAGE_1_ACTIVE |
| `python workbench-cli.py lock-requirements --req-id REQ-NNN` | Transition STAGE_1_ACTIVE → REQUIREMENTS_LOCKED |
| `python workbench-cli.py set-red --req-id REQ-NNN` | Transition REQUIREMENTS_LOCKED → RED |
| `python workbench-cli.py review-pending --req-id REQ-NNN` | Transition GREEN → REVIEW_PENDING |
| `python workbench-cli.py merge --req-id REQ-NNN` | Mark feature as MERGED, close pipeline cycle |

### Operations

| Command | Purpose |
|---------|---------|
| `python workbench-cli.py status` | Display `state.json` in human-readable format |
| `python workbench-cli.py rotate` | Trigger memory rotator for sprint end |

---

## Appendix C: Understanding the State Machine

Your project's progress is tracked in `state.json.state`. Here's what each state means:

| State | Meaning |
|-------|---------|
| `INIT` | Fresh start, no active feature |
| `STAGE_1_ACTIVE` | Architect is writing feature files |
| `REQUIREMENTS_LOCKED` | Feature files approved, waiting for tests |
| `DEPENDENCY_BLOCKED` | Waiting for a dependent feature to reach `MERGED` |
| `RED` | Tests are failing (expected initially) |
| `FEATURE_GREEN` | Current feature's unit tests pass (Phase 1 only — full regression not yet run) |
| `REGRESSION_RED` | A regression was introduced (other tests fail) |
| `GREEN` | Phase 1 + Phase 2 (full regression) both pass |
| `INTEGRATION_CHECK` | Running integration tests |
| `INTEGRATION_RED` | Integration tests failing |
| `REVIEW_PENDING` | Awaiting human review |
| `MERGED` | Feature successfully merged |
| `PIVOT_IN_PROGRESS` | Mid-feature change in progress |
| `PIVOT_APPROVED` | Pivot approved, re-running tests |
| `UPGRADE_IN_PROGRESS` | Engine upgrade in progress |

---

## Appendix D: Getting Help

If you're stuck:

1. **Read the spec:** `Agentic Workbench v2 - Draft.md` — comprehensive architectural documentation
2. **Check decision log:** `memory-bank/hot-context/decisionLog.md` — architectural decisions
3. **Ask Roo Code:** Use Roo Chat to ask questions about the workbench
4. **Review the template:** Browse `~/agentic-workbench-engine` for examples

# Agentic Workbench v2 — Beginner's Guide

**Last updated:** 2026-04-17  
**Architecture:** Ubuntu Server (main dev host) + Windows PC (thin interface via Remote SSH)

---

## Table of Contents

1. [Understanding the Architecture](#part-1-understanding-the-architecture)
2. [One-Time Setup](#part-2-one-time-setup-both-machines)
3. [Starting Your First Project](#part-3-starting-your-first-project)
4. [Configuration Sync Workflow](#part-4-configuration-sync-workflow)
5. [Backup & Disaster Recovery](#part-5-backup--disaster-recovery)
6. [Continuing Development](#part-6-continuing-development)
7. [Upgrading](#part-7-upgrading)
8. [Developing the Workbench](#part-8-developing-the-workbench-itself)
9. [Troubleshooting](#appendix-a-troubleshooting)
10. [Key Commands Reference](#appendix-b-key-commands-reference)
11. [State Machine Reference](#appendix-c-understanding-the-state-machine)

---

## Part 1: Understanding the Architecture

### Overview

The Agentic Workbench is designed for a **two-machine setup**:

| Machine | Role | Notes |
|---------|------|-------|
| **Ubuntu Server** | Main development host | 24/7 uptime, GPU available, runs VS Code Server |
| **Windows PC** | Thin interface only | Connects via VS Code Remote SSH, no local dev |

### Why This Architecture?

- **Token efficiency:** All heavy processing (bash, Python, GPU) runs on Ubuntu
- **Windows avoidance:** Bash on Ubuntu is cleaner than PowerShell
- **Consistency:** Same folder structure and configs on all machines
- **Persistence:** Ubuntu server is always on, so agents can run 24/7

### Folder Structure (Same on ALL Machines)

```
AGENTIC_DEVELOPMENT_PROJECTS/
└── agentic-workbench-lab/        # Main repo with engine as submodule
    └── agentic-workbench-engine/ # Canonical engine (git submodule)
├── APPLICATION-PROJECTS/         # Your application projects
│   ├── my-app-1/
│   └── my-app-2/
└── archive/                      # Archived projects
```

### How Machines Connect

```
Windows PC  ←→  Tailscale VPN  ←→  Ubuntu Server (24/7)
     ↓                              ↓
VS Code Remote SSH            VS Code Server
     ↓                              ↓
   (Display only)            (All development work)
```

### What Gets Synced

| Config | Path | Sync Method |
|--------|------|-------------|
| VS Code Settings | `~/.config/Code/User/settings.json` | Git + symlink |
| VS Code Keybindings | `~/.config/Code/User/keybindings.json` | Git + symlink |
| Roo Code Settings | `~/.roo-settings.json` | Git + symlink |
| Git Config | `~/.gitconfig` | Git + symlink |
| SSH Config | `~/.ssh/config` | Git + symlink |
| Shell Profile | `~/.bashrc` | Git + symlink |

All configs live in `CONFIG-DOTFILES/` repo on GitHub, symlinked to their proper locations on each machine.

### Prerequisites

Before setting up, ensure you have:

- **GitHub account** with access to `nghiaphan31` repos
- **Ubuntu server** with:
  - Ubuntu 20.04+ installed
  - SSH server running
  - Python 3.10+
  - Git installed
  - Tailscale installed and joined to your tailnet
- **Windows PC** with:
  - VS Code installed
  - Tailscale installed and joined to your tailnet
  - Git installed (for bash/git operations)

---

## Part 2: One-Time Setup (Both Machines)

### Step 2.1: Install Tailscale on Both Machines

Tailscale provides the VPN between your machines.

**On Ubuntu Server:**
```bash
# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Authenticate (one-time)
sudo tailscale up --accept-dns

# Note the machine name for SSH
hostname  # e.g., "ubuntu-server"
tailscale ip  # e.g., "100.64.1.2"
```

**On Windows PC:**
1. Download Tailscale from https://tailscale.com/download
2. Install and authenticate with the same Google/GitHub account
3. Verify both machines appear in the Tailscale admin console

### Step 2.2: Enable SSH on Ubuntu Server

```bash
# Install OpenSSH if not present
sudo apt update && sudo apt install -y openssh-server

# Enable and start SSH
sudo systemctl enable ssh
sudo systemctl start ssh

# Test from Windows: open PowerShell
ssh nghia@<ubuntu-ip>
```

### Step 2.3: Create CONFIG-DOTFILES Repo on GitHub

On **Ubuntu Server**:

```bash
# Create the repo on GitHub first:
# 1. Go to https://github.com/new
# 2. Name it "dotfiles" or "config-dotfiles"
# 3. Make it PRIVATE
# 4. Don't add README (start empty)

# Then clone it locally
git clone https://github.com/nghiaphan31/dotfiles.git ~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES
cd ~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES

# Create folder structure
mkdir -p .config/VS\ Code .ssh

# Copy existing configs (if they exist)
cp ~/.config/Code/User/settings.json .config/VS\ Code/ 2>/dev/null || true
cp ~/.config/Code/User/keybindings.json .config/VS\ Code/ 2>/dev/null || true
cp ~/.roo-settings.json . 2>/dev/null || true
cp ~/.gitconfig . 2>/dev/null || true
cp ~/.ssh/config .ssh/ 2>/dev/null || true
cp ~/.bashrc . 2>/dev/null || true

# Initial commit and push
git add .
git commit -m "Initial config from Ubuntu"
git push -u origin main
```

### Step 2.4: Clone dotfiles on Windows PC

Open **PowerShell** (or Git Bash):

```bash
# Clone the dotfiles repo to the same path structure
git clone https://github.com/nghiaphan31/dotfiles.git C:\Users\nghia\CONFIG-DOTFILES

# Navigate to it
cd C:\Users\nghia\CONFIG-DOTFILES

# Create symlinks for each config
# (Requires admin or use Git Bash)

# For Git Bash (easier):
cd ~  # Go home

# Create symlinks
ln -s /c/Users/nghia/CONFIG-DOTFILES/.roo-settings.json .roo-settings.json
ln -s /c/Users/nghia/CONFIG-DOTFILES/.gitconfig .gitconfig
mkdir -p ~/.config/Code/User
ln -s /c/Users/nghia/CONFIG-DOTFILES/.config/VS\ Code/settings.json ~/.config/Code/User/settings.json
ln -s /c/Users/nghia/CONFIG-DOTFILES/.config/VS\ Code/keybindings.json ~/.config/Code/User/keybindings.json
ln -s /c/Users/nghia/CONFIG-DOTFILES/.bashrc .bashrc
```

### Step 2.5: Install VS Code Server on Ubuntu

On **Windows PC**, open VS Code and connect to Ubuntu:

1. Install the **Remote - SSH** extension in VS Code
2. Press `Ctrl+Shift+P`, type "Remote-SSH: Connect to Host"
3. Enter `nghia@<ubuntu-ip>` (e.g., `nghia@100.64.1.2`)
4. Enter your password (or setup SSH key)

VS Code Server will be installed on Ubuntu automatically.

### Step 2.6: Install Roo Code Extension

Once connected to Ubuntu via Remote SSH:

1. Go to Extensions in VS Code (left sidebar)
2. Search for "Roo Code"
3. Install the extension

### Step 2.7: Clone Workbench Repos on Ubuntu

On **Ubuntu Server** (via VS Code Remote SSH):

```bash
# Navigate to your home directory
cd ~

# Create the main projects folder
mkdir -p AGENTIC_DEVELOPMENT_PROJECTS
cd AGENTIC_DEVELOPMENT_PROJECTS

# Clone the workbench lab repo (engine is included as a git submodule)
git clone https://github.com/nghiaphan31/agentic-workbench-lab.git

# Initialize and update the engine submodule
cd agentic-workbench-lab
git submodule update --init --recursive

# Create application projects folder (empty for now)
mkdir ../APPLICATION-PROJECTS
mkdir ../archive

# Verify the structure
ls -la
```

Expected output:
```
AGENTIC_DEVELOPMENT_PROJECTS/
└── agentic-workbench-lab/        # Main repo
    └── agentic-workbench-engine/ # Submodule (auto-initialized)
    └── ... (other workbench files)
```

### Step 2.8: Sync dotfiles on Ubuntu

On **Ubuntu Server**:

```bash
# Navigate to dotfiles
cd ~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES

# Create symlinks
cd ~

# Link dotfiles to their proper locations
ln -s ~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES/.roo-settings.json .roo-settings.json
ln -s ~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES/.gitconfig .gitconfig
ln -s ~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES/.bashrc .bashrc
mkdir -p .config/Code/User
ln -s ~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES/.config/VS\ Code/settings.json .config/Code/User/settings.json
ln -s ~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES/.config/VS\ Code/keybindings.json .config/Code/User/keybindings.json
mkdir -p .ssh
ln -s ~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES/.ssh/config .ssh/config

# Verify
ls -la ~
ls -la .config/Code/User/
```

### Step 2.9: Verify Setup

On **Ubuntu Server**, open VS Code (`code .`) and verify:

1. **Roo Code extension** is active (green icon in sidebar)
2. **`.clinerules`** file is visible in the root
3. **`state.json`** exists
4. The workbench scripts are present in `.workbench/`

Test the CLI:
```bash
cd AGENTIC_DEVELOPMENT_PROJECTS/agentic-workbench-lab/agentic-workbench-engine
python workbench-cli.py --version
```

You should see: `Agentic Workbench CLI v2.2` or similar.

---

## Part 3: Starting Your First Project

### Step 3.1: Create Project Structure

On **Ubuntu Server**:

```bash
# Navigate to application projects
cd ~/AGENTIC_DEVELOPMENT_PROJECTS/APPLICATION-PROJECTS

# Create a new project folder
mkdir my-first-app
cd my-first-app

# Initialize with git
git init
git branch -m main
```

### Step 3.2: Run Workbench Init

The workbench CLI bootstraps the project scaffold:

```bash
cd ~/AGENTIC_DEVELOPMENT_PROJECTS/APPLICATION-PROJECTS/my-first-app

# Run init with full path to the engine
python ~/AGENTIC_DEVELOPMENT_PROJECTS/agentic-workbench-lab/agentic-workbench-engine/workbench-cli.py init .
```

**What happens during init:**

1. **Directory scaffold created:**
   ```
   my-first-app/
   ├── .workbench/
   │   ├── hooks/          # Git hooks (pre-commit, pre-push)
   │   └── scripts/        # Arbiter Python scripts
   ├── docs/
   │   └── conversations/  # Audit trail
   ├── features/           # Gherkin feature files
   ├── memory-bank/
   │   ├── archive-cold/   # Rotated memory
   │   └── hot-context/    # Active memory
   ├── src/                # Your application code
   ├── tests/
   │   ├── integration/
   │   └── unit/
   ├── _inbox/             # Draft feature ideas
   ├── .clinerules         # System guardrails
   ├── .roomodes           # Custom agent modes
   ├── .roo-settings.json  # Roo Code settings
   ├── .workbench-version  # Version file
   └── state.json          # Master state
   ```

2. **State initialized:**
   ```json
   {
     "state": "INIT",
     "arbiter_capabilities": {
       "test_orchestrator": false,
       "gherkin_validator": false,
       "memory_rotator": false,
       "audit_logger": false,
       "crash_recovery": false,
       "dependency_monitor": false,
       "integration_test_runner": false,
       "git_hooks": false
     }
   }
   ```

3. **Initial commit created:**
   ```
   chore(workbench): initialize Agentic Workbench v2.2
   ```

### Step 3.3: Open in VS Code

```bash
cd ~/AGENTIC_DEVELOPMENT_PROJECTS/APPLICATION-PROJECTS/my-first-app
code .
```

VS Code opens the project. You should see the workbench structure in the Explorer.

### Step 3.4: Configure Roo Code

1. Open the Command Palette (`Ctrl+Shift+P`)
2. Type: `Roo Code: Import Settings`
3. Select `.roo-settings.json` from the project root
4. The settings are now active

### Step 3.5: Key Files to Know

| File | Purpose |
|------|---------|
| `state.json` | Master state. **Read before every session.** |
| `.clinerules` | System guardrails. **Read before every session.** |
| `memory-bank/hot-context/activeContext.md` | Current task, last result, next steps |
| `memory-bank/hot-context/progress.md` | Project checklist |
| `memory-bank/hot-context/decisionLog.md` | Architectural decisions |
| `features/` | Gherkin feature specifications |

### Step 3.6: Start Your First Feature

1. **Open Roo Chat** (green icon in sidebar or `Ctrl+Shift+G`)
2. **Inject your intent:**
   > "I want a simple greeting feature that says 'Hello, [name]!' when given a name"

3. **Architect Agent activates** — Asks clarifying questions (Socratic phase)
4. **Gherkin files created** in `/features/` — Feature specifications written
5. **Human approval (HITL 1)** — You review and approve the `.feature` files
6. **Test Engineer activates** — Writes failing tests for your feature
7. **Developer activates** — Writes code to make tests pass
8. **Review and merge** — Human reviews PR, approves merge

**Tip:** Start with a small, simple feature. Don't try to build a complex system on your first attempt.

---

## Part 4: Configuration Sync Workflow

### How Config Sync Works

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     CONFIG-DOTFILES REPO                          │
│  (GitHub: nghiaphan31/dotfiles)                                  │
├───────────────────────────────────────────────────────────────────────────────────┤
│  .config/VS Code/settings.json  ←──→  ~/.config/Code/User/       │
│  .config/VS Code/keybindings.json ←──→  (symlink)               │
│  .roo-settings.json  ←──→  ~/.roo-settings.json                  │
│  .gitconfig  ←──→  ~/.gitconfig                                  │
│  .ssh/config  ←──→  ~/.ssh/config                                │
│  .bashrc  ←──→  ~/.bashrc                                        │
└─────────────────────────────────────────────────────────────────────────────────┘
           ↑                    ↑                    ↑
      Ubuntu Server        Windows PC          Another PC
```

### Updating Configs on Any Machine

**On Ubuntu Server:**

```bash
cd ~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES

# Make changes to config files
# e.g., edit VS Code settings
nano .config/VS\ Code/settings.json

# Commit and push
git add .
git commit -m "Update VS Code settings"
git push
```

**On Windows PC (via Git Bash):**

```bash
cd ~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES

# Pull latest changes
git pull

# Symlinks already point here, so changes apply automatically
```

### Adding New Config Files

1. Add the config file to `CONFIG-DOTFILES/`
2. Create symlink on each machine
3. Commit and push

Example - adding iTerm2 config (Mac):
```bash
# On Mac
cp ~/Library/Application\ Support/iTerm/com.apple.Terminal.plist ~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES/
cd ~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES
git add .
git commit -m "Add iTerm config"
git push

# On other machines, create the symlink
ln -s ~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES/com.apple.Terminal.plist ~/Library/Application\ Support/iTerm/
```

### Verifying Symlinks

```bash
# Check if symlink is valid
ls -la ~ | grep -E "(roo|git|ssh|bash)"

# If broken (shows red), recreate
unlink ~/.roo-settings.json
ln -s ~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES/.roo-settings.json ~/.roo-settings.json
```

---

## Part 5: Backup & Disaster Recovery

### Scenario A: PC Only, Offline

**When:** No internet, only your Windows PC connected to nothing

**Solution:**
```bash
# Before going offline, ensure all repos are up-to-date
cd ~/AGENTIC_DEVELOPMENT_PROJECTS/agentic-workbench-lab && git pull
git submodule update --recursive
cd ~/AGENTIC_DEVELOPMENT_PROJECTS/APPLICATION-PROJECTS/my-app && git pull
cd ~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES && git pull

# Work normally - all files are local
# When back online:
cd ~/AGENTIC_DEVELOPMENT_PROJECTS/agentic-workbench-lab
git push
git submodule update --recursive
# Submodule changes are pushed with the parent repo
```

### Scenario B: Browser Only (Professional PC)

**When:** Using a work PC that can't have VS Code installed

**Solution: GitHub Codespaces**

```bash
# 1. Go to https://github.com/nghiaphan31/my-app

# 2. Click "Code" → "Create codespace on main"
# This launches a full VS Code in your browser!

# 3. Work normally - it's a full Ubuntu environment
# 4. When done: git push to sync
```

**Limits:**
- 60 hours/month free (varies by plan)
- No GPU access
- Good for quick fixes, not heavy development

### Scenario C: Ubuntu Server Down

**When:** Server is offline, being updated, or experiencing issues

**Option 1: Work Locally on Windows**

```bash
# Install Python and Git on Windows if not present
# Clone repos directly to Windows
git clone https://github.com/nghiaphan31/my-app.git C:\Users\nghia\my-app

# Work locally
cd C:\Users\nghia\my-app
code .

# Later, when server is back: push changes
git push
```

**Option 2: Use GitHub Codespaces**

```bash
# Temporarily use Codespaces as dev environment
# See Scenario B above
```

**Option 3: Wait for Server Recovery**

```bash
# Check if server is reachable
ping <ubuntu-ip>

# If Tailscale is down, check if server is up via other means
# SSH directly using local network IP (if on same network)
ssh nghia@192.168.1.xx

# When server returns:
cd ~/AGENTIC_DEVELOPMENT_PROJECTS/my-app
git pull  # Get any changes you made locally
git push  # Sync back if you worked locally
```

### Recommended Backup Practices

1. **Always `git push` when done** — GitHub is the backup
2. **Commit early and often** — Don't have large uncommitted changes
3. **Keep dotfiles repo in sync** — Your configs are as important as your code
4. **Test restore occasionally** — Verify you can clone and setup on a fresh machine
---

## Part 6: Continuing Development

### Daily Workflow

**Every session, in order:**

1. **SCAN → CHECK → CREATE → READ → ACT**
   - Run: `python .workbench/scripts/arbiter_check.py check-session`
   - Check for `activeContext.md`
   - Read `activeContext.md` and `progress.md`
   - Then start cognitive work

2. **Start work**
   - Open `state.json` — know the current state
   - Open `activeContext.md` — know what's in progress
   - Open `progress.md` — know the project checklist

3. **Do work** with Roo Code agents

4. **End of session**
   - Update `activeContext.md` with status
   - Update `progress.md` with completed items
   - Run audit logger: `python .workbench/scripts/audit_logger.py save --session-id {session_id} --branch {branch}`
   - Write handoff to `handoff-state.md`
   - Commit and push

### Reading State Files

**state.json:**
```bash
cat state.json
```

Key fields:
- `state` — Current pipeline state (INIT, STAGE_1_ACTIVE, GREEN, etc.)
- `active_req_id` — Which feature is currently active
- `feature_registry` — All features and their states

**activeContext.md:**
```bash
cat memory-bank/hot-context/activeContext.md
```

Structure:
```markdown
## Current Task
[What you're working on]

## Last Result
[What happened last session]

## Next Steps
[What to do next]
```

**progress.md:**
```bash
cat memory-bank/hot-context/progress.md
```

Checkboxes for all features:
- [x] REQ-001 - Done
- [ ] REQ-002 - In progress
- [ ] REQ-003 - Pending

### Committing Work

**Good commit practice:**
```bash
# Stage specific files
git add features/REQ-042-login.feature src/auth.py tests/unit/test_auth.spec.ts

# Commit with conventional format
git commit -m "feat(REQ-042): implement login feature

- Add email/password validation
- Create User model
- Add session management

Refs: REQ-042"
```

**Commit types:**
- `feat(REQ-NNN)` — New feature
- `fix(REQ-NNN)` — Bug fix
- `test(REQ-NNN)` — Test changes
- `docs` — Documentation
- `chore` — Maintenance (workbench updates)

### Syncing Across Machines

**Before starting work on any machine:**
```bash
cd ~/AGENTIC_DEVELOPMENT_PROJECTS/agentic-workbench-lab
git pull
git submodule update --recursive
cd ~/AGENTIC_DEVELOPMENT_PROJECTS/APPLICATION-PROJECTS/my-app && git pull
cd ~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES && git pull
```

**After finishing work:**
```bash
cd ~/AGENTIC_DEVELOPMENT_PROJECTS/APPLICATION-PROJECTS/my-app
git add .
git commit -m "feat(REQ-NNN): description"
git push
```

---

## Part 7: Upgrading

### Understanding Upgrade Safety

The workbench can only be upgraded when the project is in a **safe state**:

| State | Upgrade Allowed? |
|-------|------------------|
| `INIT` | ✅ Yes |
| `MERGED` | ✅ Yes |
| `STAGE_1_ACTIVE` | ❌ No — active development |
| `RED` | ❌ No — tests failing |
| `FEATURE_GREEN` | ❌ No — not fully validated |
| `REGRESSION_RED` | ❌ No — regression in progress |

### Step 7.1: Check Current State

```bash
cd ~/AGENTIC_DEVELOPMENT_PROJECTS/APPLICATION-PROJECTS/my-app
cat state.json
```

Look for `"state": "INIT"` or `"state": "MERGED"`.

### Step 7.2: Ensure Safe State

**Wait for active work to complete:**
```bash
# Check for active sessions
cat memory-bank/hot-context/session-checkpoint.md
```

If `status: ACTIVE`, wait for the session to finish.

**Or reset to INIT (destructive):**
```bash
# Edit state.json, set:
# "state": "INIT"
# This abandons all in-progress work!
```

### Step 7.3: Update Local Engine

```bash
cd ~/AGENTIC_DEVELOPMENT_PROJECTS/agentic-workbench-lab
git fetch origin
git log --oneline origin/main -3
cat .workbench-version
```

Note the version (e.g., `2.2`).

### Step 7.4: Run Upgrade

```bash
cd ~/AGENTIC_DEVELOPMENT_PROJECTS/APPLICATION-PROJECTS/my-app

# Run upgrade with target version
python ~/AGENTIC_DEVELOPMENT_PROJECTS/agentic-workbench-lab/agentic-workbench-engine/workbench-cli.py upgrade --version 2.2
```

**What the upgrade does:**
1. **Safety check** — Confirms state is INIT or MERGED
2. **Engine overwrite** — Replaces:
   - `.clinerules`
   - `.roomodes`
   - `.workbench/scripts/` (Arbiter scripts)
   - `.workbench/hooks/` (Git hooks)
   - `.roo-settings.json`
3. **Memory migration** — Creates new memory files if needed; existing memory preserved
4. **Version bump** — Updates `.workbench-version`
5. **Auto-commit** — `chore(workbench): upgrade engine to v2.2`

### Step 7.5: Verify Upgrade

```bash
# Check new version
cat .workbench-version

# View upgrade commit
git log --oneline -n 3

# Review what changed
git diff HEAD~1 --stat
```

### Step 7.6: Review Changes

```bash
# See detailed changes
git diff HEAD~1

# Check new rules
cat .clinerules | head -50

# Check new arbiter capabilities
python .workbench/scripts/arbiter_check.py check-session
```

### Step 7.7: Continue Development

After upgrade, the project is in `INIT` state. You can start new features.

---

## Part 8: Developing the Workbench Itself

### When to Develop the Workbench

You develop the workbench when you want to:
- Fix a bug in the workbench
- Add new functionality to the workbench
- Improve existing arbiter scripts
- Add new agent modes

### Where Development Happens

**`agentic-workbench-lab/`** — This repo

This is where workbench improvements are developed and tested. The engine at `agentic-workbench-engine/` is the canonical template, included as a git submodule.

### Development Workflow

**1. Create a feature for the workbench:**

```bash
cd ~/AGENTIC_DEVELOPMENT_PROJECTS/agentic-workbench-lab

# Use the workbench to develop itself!
code .
```

**2. Use the standard pipeline:**

The workbench uses itself to develop new versions. This is "bootstrapping."

**3. Test changes:**

```bash
cd ~/AGENTIC_DEVELOPMENT_PROJECTS/agentic-workbench-lab

# Run tests
pytest tests/workbench/ -v

# Run specific test file
pytest tests/workbench/test_fac_compliance.py -v
```

**4. Commit changes:**

```bash
git add .
git commit -m "feat(workbench): description

Details about what changed
"

git push
```

**5. Update engine:**

When `agentic-workbench-lab` changes are stable, update the engine:

```bash
cd ~/AGENTIC_DEVELOPMENT_PROJECTS/agentic-workbench-lab/agentic-workbench-engine

# Pull from engine origin
git pull origin main

# The engine is now updated with lab changes
```

### File Locations

| File | Purpose |
|------|---------|
| `workbench-cli.py` | CLI bootstrapper |
| `.workbench/scripts/arbiter_check.py` | Compliance checks |
| `.workbench/scripts/audit_logger.py` | Session logging |
| `.workbench/scripts/crash_recovery.py` | Crash recovery |
| `.workbench/scripts/memory_rotator.py` | Memory management |
| `.workbench/scripts/state_manager.py` | State transitions |
| `.workbench/hooks/pre-commit` | Pre-commit validation |
| `.workbench/hooks/pre-push` | Pre-push validation |
| `.workbench/hooks/post-merge` | Post-merge actions |
| `.workbench/hooks/post-tag` | Post-tagging actions |

### Testing Workbench Changes

```bash
# Run all tests
cd ~/AGENTIC_DEVELOPMENT_PROJECTS/agentic-workbench-lab
pytest tests/ -v --tb=short

# Run with coverage
pytest tests/ --cov=. --cov-report=term-missing

# Run specific test class
pytest tests/workbench/test_state_machine.py::TestStateMachine -v
```

### Committing Workbench Changes

Follow the same commit conventions:

```bash
git commit -m "fix(workbench): correct state transition for REGRESSION_RED

Fixed edge case where transition was blocked incorrectly.
Added test coverage for the scenario.

Refs: REQ-XXX"
```

---

## Appendix A: Troubleshooting

### "command not found: workbench-cli"

The CLI is not in PATH. Either:
1. Use full path: `python ~/AGENTIC_DEVELOPMENT_PROJECTS/agentic-workbench-lab/agentic-workbench-engine/workbench-cli.py`
2. Or add to PATH in `.bashrc`: `export PATH="$PATH:$HOME/AGENTIC_DEVELOPMENT_PROJECTS/agentic-workbench-lab/agentic-workbench-engine"`

### "Error: state is not INIT or MERGED — upgrade blocked"

The project is in an active state. Either:
1. Wait for current work to complete
2. Reset to INIT (destructive): Edit `state.json`, set `"state": "INIT"`

### "Error: Permission denied" during init

The target directory might already exist. Use a different name or remove the existing folder:

```bash
rm -rf my-first-app
python .../workbench-cli.py init my-first-app
```

### "Error: git configuration missing"

Set Git name and email:

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

### Roo Code isn't responding to .clinerules

1. Ensure `.clinerules` is in the **project root** (not a subdirectory)
2. Ensure you've opened the folder in VS Code (File → Open Folder)
3. Ensure Roo Code extension is installed and active
4. Try re-importing settings: `Roo Code: Import Settings` → select `.roo-settings.json`

### SSH connection to Ubuntu fails

1. Verify Tailscale is running on both machines: `tailscale status`
2. Try the Tailscale IP address: `ssh nghia@100.64.1.2`
3. Check SSH service on Ubuntu: `sudo systemctl status ssh`
4. Check Ubuntu firewall: `sudo ufw status`

### Symlink broken

If a symlink shows as broken (red text in `ls -la`):

```bash
# Remove the broken symlink
unlink ~/.roo-settings.json

# Recreate the symlink
ln -s ~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES/.roo-settings.json ~/.roo-settings.json
```

### VS Code Remote SSH disconnects

1. Check if Ubuntu is reachable: `ping <ubuntu-ip>`
2. Check if SSH service is running: `sudo systemctl status ssh`
3. Try reconnecting: `Ctrl+Shift+P` → "Remote-SSH: Connect to Host"

### Git push rejected

Check if there's a pre-push hook blocking:

```bash
# Run the check manually
python .workbench/scripts/arbiter_check.py check-session

# Check for issues
git status
```

The pre-push hook may block if:
- `state.json` is staged by non-Arbiter
- Tests are failing (REGRESSION_RED)
- Feature is not in GREEN state

---

## Appendix B: Key Commands Reference

### Workbench CLI

```bash
# Help
python workbench-cli.py --help

# Version
python workbench-cli.py --cli-version

# Initialize new project
python workbench-cli.py init <project-path>

# Upgrade existing project
python workbench-cli.py upgrade --version <vX.Y>

# Check status
python workbench-cli.py status

# Run compliance scan
python workbench-cli.py check

# Install hooks
python workbench-cli.py install-hooks

# Register arbiter
python workbench-cli.py register-arbiter

# Rotate memory
python workbench-cli.py rotate
```

### Feature Lifecycle Commands

```bash
# Start a new feature
python workbench-cli.py start-feature --req-id REQ-001

# Lock requirements
python workbench-cli.py lock-requirements --req-id REQ-001

# Set RED state
python workbench-cli.py set-red --req-id REQ-001

# Review pending
python workbench-cli.py review-pending --req-id REQ-001

# Merge feature
python workbench-cli.py merge --req-id REQ-001
```

### Git Commands

```bash
# Check status
git status

# Stage files
git add <file1> <file2>

# Commit
git commit -m "feat(REQ-001): description"

# Push
git push

# Pull latest
git pull

# View recent commits
git log --oneline -n 5

# View changes since last commit
git diff HEAD
```

---

## Appendix C: Understanding the State Machine

### State Overview

```
        ┌─────────────────────────────────────────────────────────────────────────────────┐
        │                      INIT (Fresh Start)                       │
        └─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
        ┌─────────────────────────────────────────────────────────────────────────────────┐
        │                   STAGE_1_ACTIVE (Architect)                   │
        │              Writing feature files (.feature)                  │
        └─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
        ┌─────────────────────────────────────────────────────────────────────────────────┐
        │                  REQUIREMENTS_LOCKED                          │
        │              Feature files approved, waiting for tests        │
        └─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
        ┌─────────────────────────────────────────────────────────────────────────────────┐
        │                         RED                                  │
        │              Tests written but failing (expected)            │
        └─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
        ┌─────────────────────────────────────────────────────────────────────────────────┐
        │                     FEATURE_GREEN                             │
        │           Current feature's tests pass (Phase 1)            │
        └─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
        ┌─────────────────────────────────────────────────────────────────────────────────┐
        │               REGRESSION_RED (Something broke)                │
        │              Full test suite reveals regression              │
        └─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ (if fixed)
                                    │
                                    ▼ (if clean)
        ┌─────────────────────────────────────────────────────────────────────────────────┐
        │                         GREEN                                 │
        │      Phase 1 + Phase 2 (full regression) both pass          │
        └─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
        ┌─────────────────────────────────────────────────────────────────────────────────┐
        │                    INTEGRATION_CHECK                          │
        │                 Running integration tests                     │
        └─────────────────────────────────────────────────────────────────────────────────┘
                          ┌─────────────────────────────────┐
                          ▼                                 ▼
        ┌──────────────────────────┐  ┌─────────────────────────────────┐
        │      INTEGRATION_RED      │  │         REVIEW_PENDING          │
        │  Integration tests fail   │  │   Awaiting human review         │
        └──────────────────────────┘  └─────────────────────────────────┘
                          │                                 │
                          ▼                                 ▼
        ┌──────────────────────────┐  ┌─────────────────────────────────┐
        │        GREEN              │  │           MERGED                │
        │ (after fixing)            │  │    Feature complete!            │
        └──────────────────────────┘  └─────────────────────────────────┘
```

### State Definitions

| State | Meaning |
|-------|---------|
| `INIT` | Fresh start, no active feature |
| `STAGE_1_ACTIVE` | Architect is writing feature files |
| `REQUIREMENTS_LOCKED` | Feature files approved, waiting for tests |
| `RED` | Tests are failing (expected initially) |
| `FEATURE_GREEN` | Current feature's unit tests pass (Phase 1 only) |
| `REGRESSION_RED` | A regression was introduced |
| `GREEN` | Phase 1 + Phase 2 (full regression) both pass |
| `INTEGRATION_CHECK` | Running integration tests |
| `INTEGRATION_RED` | Integration tests failing |
| `REVIEW_PENDING` | Awaiting human review |
| `MERGED` | Feature successfully merged |
| `DEPENDENCY_BLOCKED` | Waiting for a dependent feature to merge |
| `PIVOT_IN_PROGRESS` | Mid-feature requirements change |
| `PIVOT_APPROVED` | Pivot approved, re-running tests |
| `UPGRADE_IN_PROGRESS` | Engine upgrade in progress |

### Special States

| State | Trigger | Exit Condition |
|-------|---------|----------------|
| `DEPENDENCY_BLOCKED` | Dependent feature not merged | All dependencies merged |
| `PIVOT_IN_PROGRESS` | Delta prompt during active development | Human approves pivot |
| `PIVOT_APPROVED` | Pivot approved | Tests re-run, returns to RED |
| `UPGRADE_IN_PROGRESS` | Upgrade command run | Upgrade completes |

---

## Getting Help

1. **Read the spec:** `Agentic Workbench v2 - Draft.md` — comprehensive architectural documentation
2. **Check decision log:** `memory-bank/hot-context/decisionLog.md` — architectural decisions
3. **Ask Roo Code:** Use Roo Chat to ask questions about the workbench
4. **Review the engine:** Browse `~/AGENTIC_DEVELOPMENT_PROJECTS/agentic-workbench-lab/agentic-workbench-engine`
5. **Review tests:** Browse `~/AGENTIC_DEVELOPMENT_PROJECTS/agentic-workbench-lab/tests/workbench`

---

*End of Beginner's Guide*

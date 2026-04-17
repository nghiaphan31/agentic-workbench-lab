# Beginners Guide Setup Plan — Calypso Architecture

**Author:** Architect (Roo)
**Date:** 2026-04-17
**Target:** Two-machine setup (calypso headless Ubuntu server + Windows laptop)
**Reference:** [`docs/Beginners_Guide.md`](../docs/Beginners_Guide.md)

---

## Executive Summary

The user has a working two-machine setup with Tailscale VPN and SSH keys configured. This plan addresses the remaining setup steps from the Beginners Guide to achieve full architecture compliance.

---

## Part A: Gap Analysis

### A.1 What EXISTS (Confirmed Working)

| Component | Status | Location |
|-----------|--------|----------|
| Tailscale VPN | ✅ Working | Both machines |
| SSH with keys | ✅ Working | Both machines |
| Folder structure | ✅ Basic | `~/AGENTIC_DEVELOPMENT_PROJECTS/` |
| Git repos | ✅ Cloned | `agentic-workbench-lab/` as repo |
| Engine submodule | ✅ Present | Inside `agentic-workbench-lab/agentic-workbench-engine/` |
| Archive folder | ✅ Exists | `~/AGENTIC_DEVELOPMENT_PROJECTS/archive/` |
| Workbench scripts | ✅ Present | `.workbench/scripts/*.py` |
| Engine state | ✅ INIT | `state.json` shows `state: "INIT"` |

### A.2 What is MISSING or DIFFERENT

| # | Gap | Beginners Guide Says | Current State | Severity |
|---|-----|---------------------|---------------|----------|
| 1 | **Folder Structure Architecture** | Engine cloned as **standalone** repo at `~/AGENTIC_DEVELOPMENT_PROJECTS/agentic-workbench-engine/` | Engine is **git SUBMODULE** inside `agentic-workbench-lab/` → `agentic-workbench-lab/agentic-workbench-engine/` | 🔴 Critical |
| 2 | **CONFIG-DOTFILES Repo** | Must create `~/CONFIG-DOTFILES/` GitHub repo | **Does NOT exist** | 🔴 Critical |
| 3 | **APPLICATION-PROJECTS Folder** | Named `APPLICATION-PROJECTS/` | Named `projects/` (exists but wrong name) | 🟡 Moderate |
| 4 | **VS Code Settings Symlinks** | `~/.config/Code/User/settings.json` → dotfiles | **Not configured** | 🟡 Moderate |
| 5 | **VS Code Keybindings Symlinks** | `~/.config/Code/User/keybindings.json` → dotfiles | **Not configured** | 🟡 Moderate |
| 6 | **Roo Code Settings Symlink** | `~/.roo-settings.json` → dotfiles | **Not configured** | 🟡 Moderate |
| 7 | **Git Config Symlink** | `~/.gitconfig` → dotfiles | **Not configured** | 🟡 Moderate |
| 8 | **SSH Config for calypso** | `~/.ssh/config` with calypso host entry | **Not configured** | 🟡 Moderate |
| 9 | **Bash Profile Symlink** | `~/.bashrc` → dotfiles | **Not configured** | 🟡 Moderate |
| 10 | **VS Code Remote SSH** | Must connect from Windows to Ubuntu | **Not verified** | 🟡 Moderate |
| 11 | **Roo Code Extension** | Must be installed on VS Code Server | **Not verified** | 🟡 Moderate |
| 12 | **workbench-cli.py** | Should respond to `--version` | **Not verified** | 🟡 Moderate |

---

## Part B: Critical Decision Required

### B.1 Folder Structure Architecture — TWO OPTIONS

The **most significant gap** is the folder structure. The Beginners Guide assumes a **standalone clone** of `agentic-workbench-engine/`, but the current setup uses a **git submodule** pattern.

```
BEGINNERS GUIDE (Option A — Standalone Clone):
~/AGENTIC_DEVELOPMENT_PROJECTS/
├── agentic-workbench-engine/    # Standalone clone from GitHub
├── agentic-workbench-lab/       # Standalone clone from GitHub
├── APPLICATION-PROJECTS/
└── archive/

CURRENT SETUP (Option B — Submodule):
~/AGENTIC_DEVELOPMENT_PROJECTS/
├── agentic-workbench-lab/       # Standalone clone from GitHub
│   └── agentic-workbench-engine/ # GIT SUBMODULE inside lab
├── projects/                     # Wrong name (should be APPLICATION-PROJECTS)
└── archive/
```

### Option A: Match Beginners Guide (Standalone)

**Pros:**
- Matches Beginners Guide exactly
- Simpler mental model for beginners
- Engine can be updated independently

**Cons:**
- Requires restructuring existing setup
- Two separate git histories
- More disk space

**Steps:**
1. Clone `agentic-workbench-engine` as standalone repo
2. Remove submodule from inside `agentic-workbench-lab`
3. Update all paths that reference engine location
4. Rename `projects/` → `APPLICATION-PROJECTS/`

### Option B: Keep Current Submodule Pattern

**Pros:**
- Already working
- Engine version locked to lab version
- Simpler for version synchronization

**Cons:**
- Deviates from Beginners Guide documentation
- May confuse future readers
- Path references in docs won't match

**Steps:**
1. Update Beginners Guide to document submodule pattern
2. Update all path references in documentation
3. Create CONFIG-DOTFILES setup
4. Continue with remaining setup items

---

## Part C: Implementation Plan

### Phase 1: Pre-Implementation Verification

> **On calypso (headless Ubuntu server), SSH in and run these checks:**

```bash
# 1. Check home directory structure
ls -la ~/

# 2. Check AGENTIC_DEVELOPMENT_PROJECTS contents
ls -la ~/AGENTIC_DEVELOPMENT_PROJECTS/

# 3. Check if CONFIG-DOTFILES exists
ls -la ~/CONFIG-DOTFILES/ 2>/dev/null || echo "CONFIG-DOTFILES does not exist"

# 4. Check symlinks
ls -la ~/.roo-settings.json ~/.gitconfig ~/.bashrc ~/.ssh/config 2>&1

# 5. Check VS Code config
ls -la ~/.config/Code/User/ 2>&1

# 6. Check if engine is submodule (inside lab) or standalone
cat ~/AGENTIC_DEVELOPMENT_PROJECTS/agentic-workbench-lab/.gitmodules 2>/dev/null || echo "No .gitmodules in lab"

# 7. Test workbench CLI (current path)
cd ~/AGENTIC_DEVELOPMENT_PROJECTS/agentic-workbench-lab
python agentic-workbench-engine/workbench-cli.py --version 2>/dev/null || echo "CLI not found at expected path"
```

### Phase 2: Decision Implementation — OPTION A (STANDALONE)

| Step | Action | Command |
|------|--------|---------|
| 2.1 | Clone engine as standalone repo | `git clone git@github.com:nghiaphan31/agentic-workbench-engine.git ~/AGENTIC_DEVELOPMENT_PROJECTS/agentic-workbench-engine/` |
| 2.2 | Remove submodule from inside lab | Edit `.gitmodules`, remove engine submodule, `git rm -r agentic-workbench-engine/` |
| 2.3 | Rename projects folder | `mv projects APPLICATION-PROJECTS` |
| 2.4 | Verify structure | `ls -la ~/AGENTIC_DEVELOPMENT_PROJECTS/` |

### Phase 3: CONFIG-DOTFILES Setup

| Step | Action | Command |
|------|--------|---------|
| 3.1 | Create GitHub repo | Go to github.com/new, name `dotfiles`, make PRIVATE |
| 3.2 | Clone to calypso | `git clone https://github.com/nghiaphan31/dotfiles.git ~/CONFIG-DOTFILES` |
| 3.3 | Create folder structure | `mkdir -p ~/CONFIG-DOTFILES/.config/VS\ Code ~/CONFIG-DOTFILES/.ssh` |
| 3.4 | Copy existing configs | `cp ~/.config/Code/User/settings.json ~/CONFIG-DOTFILES/.config/VS\ Code/` (if exists) |
| 3.5 | Initial commit | `cd ~/CONFIG-DOTFILES && git add . && git commit -m "Initial config"` |
| 3.6 | Push to GitHub | `git push -u origin main` |

### Phase 4: Create Symlinks on Calypso

```bash
cd ~

# VS Code config
mkdir -p ~/.config/Code/User
ln -sf ~/CONFIG-DOTFILES/.config/VS\ Code/settings.json ~/.config/Code/User/settings.json
ln -sf ~/CONFIG-DOTFILES/.config/VS\ Code/keybindings.json ~/.config/Code/User/keybindings.json

# Roo Code settings
ln -sf ~/CONFIG-DOTFILES/.roo-settings.json ~/.roo-settings.json

# Git config
ln -sf ~/CONFIG-DOTFILES/.gitconfig ~/.gitconfig

# SSH config
ln -sf ~/CONFIG-DOTFILES/.ssh/config ~/.ssh/config

# Bash profile
ln -sf ~/CONFIG-DOTFILES/.bashrc ~/.bashrc
```

### Phase 5: Windows PC Setup

On **Windows laptop** via PowerShell or Git Bash:

```bash
# Clone dotfiles
git clone https://github.com/nghiaphan31/dotfiles.git C:\Users\nghia\CONFIG-DOTFILES

# Create symlinks
cd ~
ln -s /c/Users/nghia/CONFIG-DOTFILES/.roo-settings.json .roo-settings.json
ln -s /c/Users/nghia/CONFIG-DOTFILES/.gitconfig .gitconfig
mkdir -p ~/.config/Code/User
ln -s /c/Users/nghia/CONFIG-DOTFILES/.config/VS\ Code/settings.json ~/.config/Code/User/settings.json
ln -s /c/Users/nghia/CONFIG-DOTFILES/.config/VS\ Code/keybindings.json ~/.config/Code/User/keybindings.json
ln -s /c/Users/nghia/CONFIG-DOTFILES/.bashrc .bashrc
```

### Phase 6: SSH Config for Calypso

Add to `~/CONFIG-DOTFILES/.ssh/config`:

```ssh-config
Host calypso
    HostName <tailscale-ip-of-calypso>
    User nghia
    IdentityFile ~/.ssh/id_ed25519
    StrictHostKeyChecking accept-new
```

### Phase 7: VS Code Remote SSH Verification

1. On Windows: Open VS Code
2. Install **Remote - SSH** extension if not present
3. Press `Ctrl+Shift+P` → "Remote-SSH: Connect to Host"
4. Enter `calypso` (from SSH config)
5. Once connected, install **Roo Code** extension
6. Open folder `~/AGENTIC_DEVELOPMENT_PROJECTS/agentic-workbench-lab`

### Phase 8: Final Verification

```bash
# On calypso via VS Code Terminal:

# 1. Verify workbench CLI
cd ~/AGENTIC_DEVELOPMENT_PROJECTS/agentic-workbench-lab
python agentic-workbench-engine/workbench-cli.py --version

# 2. Verify .clinerules is visible
ls -la .clinerules

# 3. Verify state.json exists
cat agentic-workbench-engine/state.json | grep state

# 4. Verify symlinks are valid
ls -la ~ | grep -E "^l"

# 5. Run arbiter check
python agentic-workbench-engine/.workbench/scripts/arbiter_check.py check-session
```

---

## Part D: Decisions Confirmed

### D.1 Folder Structure Decision: ✅ OPTION A (STANDALONE)

**Decision:** User confirmed **Option A (Standalone)** — 2 separate git repos at same level.

**Final structure on calypso:**
```
~/AGENTIC_DEVELOPMENT_PROJECTS/
├── agentic-workbench-engine/    # Standalone git clone (canonical engine)
├── agentic-workbench-lab/       # Standalone git clone (lab development)
├── APPLICATION-PROJECTS/       # Your application projects
└── archive/                    # Archived projects
```

**Benefits:**
- Matches Beginners Guide exactly
- Independent git repos — simpler mental model
- Can upgrade engine independently
- Clear separation of concerns

### D.2 CONFIG-DOTFILES Repo: PENDING

**Question:** Should I proceed with creating the `dotfiles` repo on GitHub under `nghiaphan31`?

---

## Part E: Todo Checklist

```
Phase 1: Pre-Implementation Verification
[ ] SSH to calypso and verify actual filesystem state
[ ] Document findings of existing symlinks/configs

Phase 2: Architecture Decision
[ ] User confirms Option A or Option B for folder structure
[ ] If Option A: restructure folder layout
[ ] If Option B: update documentation to reflect submodule pattern

Phase 3: CONFIG-DOTFILES Setup
[ ] Create GitHub repo for dotfiles
[ ] Clone to calypso
[ ] Set up folder structure
[ ] Add to GitHub

Phase 4: Calypso Symlinks
[ ] Create symlinks for VS Code, Roo Code, Git, SSH, Bash

Phase 5: Windows Setup
[ ] Clone dotfiles to Windows
[ ] Create symlinks on Windows

Phase 6: SSH Config
[ ] Add calypso host entry to SSH config

Phase 7: VS Code Remote SSH
[ ] Connect from Windows to calypso
[ ] Install Roo Code extension
[ ] Open workbench-lab folder

Phase 8: Final Verification
[ ] Test workbench CLI
[ ] Verify all symlinks
[ ] Run arbiter check
```

---

## Appendix: Reference — Beginners Guide Part 2 Commands

From [`docs/Beginners_Guide.md`](docs/Beginners_Guide.md) lines 210-286:

```bash
# Step 2.7: Clone Workbench Repos
mkdir -p AGENTIC_DEVELOPMENT_PROJECTS
cd AGENTIC_DEVELOPMENT_PROJECTS
git clone https://github.com/nghiaphan31/agentic-workbench-engine.git
git clone https://github.com/nghiaphan31/agentic-workbench-lab.git
mkdir APPLICATION-PROJECTS
mkdir archive

# Step 2.8: Sync dotfiles
cd ~/CONFIG-DOTFILES
cd ~
ln -s ~/CONFIG-DOTFILES/.roo-settings.json .roo-settings.json
ln -s ~/CONFIG-DOTFILES/.gitconfig .gitconfig
ln -s ~/CONFIG-DOTFILES/.bashrc .bashrc
mkdir -p .config/Code/User
ln -s ~/CONFIG-DOTFILES/.config/VS\ Code/settings.json .config/Code/User/settings.json
ln -s ~/CONFIG-DOTFILES/.config/VS\ Code/keybindings.json .config/Code/User/keybindings.json
mkdir -p .ssh
ln -s ~/CONFIG-DOTFILES/.ssh/config .ssh/config

# Step 2.9: Verify Setup
cd AGENTIC_DEVELOPMENT_PROJECTS/agentic-workbench-engine
python workbench-cli.py --version
```

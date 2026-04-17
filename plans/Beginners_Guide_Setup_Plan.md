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

| # | Gap | Expected State | Current State | Severity |
|---|-----|----------------|---------------|----------|
| 1 | **CONFIG-DOTFILES Repo** | Must create `~/CONFIG-DOTFILES/` GitHub repo | **Does NOT exist** | 🔴 Critical |
| 2 | **APPLICATION-PROJECTS Folder** | Named `APPLICATION-PROJECTS/` | Named `projects/` (exists but wrong name) | 🟡 Moderate |
| 3 | **VS Code Settings Symlinks** | `~/.config/Code/User/settings.json` → dotfiles | **Not configured** | 🟡 Moderate |
| 4 | **VS Code Keybindings Symlinks** | `~/.config/Code/User/keybindings.json` → dotfiles | **Not configured** | 🟡 Moderate |
| 5 | **Roo Code Settings Symlink** | `~/.roo-settings.json` → dotfiles | **Not configured** | 🟡 Moderate |
| 6 | **Git Config Symlink** | `~/.gitconfig` → dotfiles | **Not configured** | 🟡 Moderate |
| 7 | **SSH Config for calypso** | `~/.ssh/config` with calypso host entry | **Not configured** | 🟡 Moderate |
| 8 | **Bash Profile Symlink** | `~/.bashrc` → dotfiles | **Not configured** | 🟡 Moderate |
| 9 | **VS Code Remote SSH** | Must connect from Windows to Ubuntu | **Not verified** | 🟡 Moderate |
| 10 | **Roo Code Extension** | Must be installed on VS Code Server | **Not verified** | 🟡 Moderate |
| 11 | **workbench-cli.py** | Should respond to `--version` | **Not verified** | 🟡 Moderate |

---

## Part B: Architecture — SUBMODULE PATTERN CONFIRMED

### B.1 Current Folder Structure

The engine is configured as a **git submodule** inside `agentic-workbench-lab/`. This is the confirmed architecture per ADR-005 and ADR-006.

```
CURRENT SETUP (Submodule Pattern):
~/AGENTIC_DEVELOPMENT_PROJECTS/
├── agentic-workbench-lab/       # Lab repo
│   └── agentic-workbench-engine/ # GIT SUBMODULE (pinned to commit 54b4d0a)
├── agentic-workbench-engine/    # Standalone canonical repo (reference)
├── projects/                     # Should be renamed to APPLICATION-PROJECTS
└── archive/
```

### B.2 Benefits of Submodule Pattern

- Engine version locked to lab version via gitlink
- Single source of truth: the submodule always matches the canonical engine at a specific commit
- Simpler for version synchronization across cloned repos
- ADR-005 compliance: embedded engine is always in sync via submodule pinning

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
ls -la ~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES/ 2>/dev/null || echo "CONFIG-DOTFILES does not exist"

# 4. Check symlinks
ls -la ~/.roo-settings.json ~/.gitconfig ~/.bashrc ~/.ssh/config 2>&1

# 5. Check VS Code config
ls -la ~/.config/Code/User/ 2>&1

# 6. Check submodule is present
cat ~/AGENTIC_DEVELOPMENT_PROJECTS/agentic-workbench-lab/.gitmodules

# 7. Verify submodule content
ls -la ~/AGENTIC_DEVELOPMENT_PROJECTS/agentic-workbench-lab/agentic-workbench-engine/

# 8. Test workbench CLI
cd ~/AGENTIC_DEVELOPMENT_PROJECTS/agentic-workbench-lab
python agentic-workbench-engine/workbench-cli.py --version 2>/dev/null || echo "CLI not found at expected path"
```

### Phase 2: Rename projects Folder

| Step | Action | Command |
|------|--------|---------|
| 2.1 | Rename projects folder | `mv projects APPLICATION-PROJECTS` |
| 2.2 | Verify structure | `ls -la ~/AGENTIC_DEVELOPMENT_PROJECTS/` |

### Phase 3: CONFIG-DOTFILES Setup

| Step | Action | Command |
|------|--------|---------|
| 3.1 | Create GitHub repo | Go to github.com/new, name `dotfiles`, make PRIVATE |
| 3.2 | Clone to calypso | `git clone https://github.com/nghiaphan31/dotfiles.git ~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES` |
| 3.3 | Create folder structure | `mkdir -p ~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES/.config/VS\ Code ~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES/.ssh` |
| 3.4 | Copy existing configs | `cp ~/.config/Code/User/settings.json ~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES/.config/VS\ Code/` (if exists) |
| 3.5 | Initial commit | `cd ~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES && git add . && git commit -m "Initial config"` |
| 3.6 | Push to GitHub | `git push -u origin main` |

### Phase 4: Create Symlinks on Calypso

```bash
cd ~

# VS Code config
mkdir -p ~/.config/Code/User
ln -sf ~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES/.config/VS\ Code/settings.json ~/.config/Code/User/settings.json
ln -sf ~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES/.config/VS\ Code/keybindings.json ~/.config/Code/User/keybindings.json

# Roo Code settings
ln -sf ~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES/.roo-settings.json ~/.roo-settings.json

# Git config
ln -sf ~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES/.gitconfig ~/.gitconfig

# SSH config
ln -sf ~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES/.ssh/config ~/.ssh/config

# Bash profile
ln -sf ~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES/.bashrc ~/.bashrc
```

### Phase 5: Windows PC Setup

On **Windows laptop** via PowerShell or Git Bash:

```bash
# Clone dotfiles
git clone https://github.com/nghiaphan31/dotfiles.git C:\Users\nghia\AGENTIC_DEVELOPMENT_PROJECTS\CONFIG-DOTFILES

# Create symlinks
cd ~
ln -s /c/Users/nghia/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES/.roo-settings.json .roo-settings.json
ln -s /c/Users/nghia/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES/.gitconfig .gitconfig
mkdir -p ~/.config/Code/User
ln -s /c/Users/nghia/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES/.config/VS\ Code/settings.json ~/.config/Code/User/settings.json
ln -s /c/Users/nghia/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES/.config/VS\ Code/keybindings.json ~/.config/Code/User/keybindings.json
ln -s /c/Users/nghia/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES/.bashrc .bashrc
```

### Phase 6: SSH Config for Calypso

Add to `~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES/.ssh/config`:

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

# 6. Verify submodule status
git submodule status
```

---

## Part D: Decisions Confirmed

### D.1 Folder Structure Decision: ✅ SUBMODULE PATTERN

**Decision:** Engine is a git submodule inside `agentic-workbench-lab/` — confirmed via ADR-005 and ADR-006.

**Final structure on calypso:**
```
~/AGENTIC_DEVELOPMENT_PROJECTS/
├── agentic-workbench-lab/           # Lab repo
│   └── agentic-workbench-engine/    # GIT SUBMODULE (pinned to 54b4d0a)
├── agentic-workbench-engine/        # Standalone canonical repo (reference)
├── APPLICATION-PROJECTS/          # Your application projects
└── archive/                         # Archived projects
```

**Benefits:**
- Submodule aligns with ADR-005: embedded engine always in sync via gitlink
- Version pinning: lab repo tests specific engine commit
- Single source of truth in canonical engine repo
- No silent drift risk

### D.2 CONFIG-DOTFILES Repo: PENDING

**Question:** Should I proceed with creating the `dotfiles` repo on GitHub under `nghiaphan31`?

---

## Part E: Todo Checklist

```
Phase 1: Pre-Implementation Verification
[ ] SSH to calypso and verify actual filesystem state
[ ] Document findings of existing symlinks/configs

Phase 2: Folder Structure
[x] Submodule pattern confirmed (ADR-005, ADR-006)
[x] Submodule added to lab repo
[ ] Rename projects/ → APPLICATION-PROJECTS/

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
git clone https://github.com/nghiaphan31/agentic-workbench-lab.git
cd agentic-workbench-lab
git submodule update --init --recursive
mkdir APPLICATION-PROJECTS
mkdir archive

# Step 2.8: Sync dotfiles (after creating CONFIG-DOTFILES)
cd ~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES
cd ~
ln -s ~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES/.roo-settings.json .roo-settings.json
ln -s ~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES/.gitconfig .gitconfig
ln -s ~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES/.bashrc .bashrc
mkdir -p .config/Code/User
ln -s ~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES/.config/VS\ Code/settings.json .config/Code/User/settings.json
ln -s ~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES/.config/VS\ Code/keybindings.json .config/Code/User/keybindings.json
mkdir -p .ssh
ln -s ~/AGENTIC_DEVELOPMENT_PROJECTS/CONFIG-DOTFILES/.ssh/config .ssh/config

# Step 2.9: Verify Setup
cd ~/AGENTIC_DEVELOPMENT_PROJECTS/agentic-workbench-lab
python agentic-workbench-engine/workbench-cli.py --version
git submodule status
```

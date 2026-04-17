# Submodule Restoration Plan

## Objective
Add `agentic-workbench-engine` as a git submodule to `agentic-workbench-lab`.

## Context
- **Date:** 2026-04-17
- **Current State:** Engine directory does NOT exist in lab repo
- **Desired State:** Engine as git submodule at `agentic-workbench-engine/` cloned fresh from GitHub

### Git History Findings (Confirmed by Investigation)

**Original Submodule Configuration:**
- Path: `agentic-workbench-engine`
- URL: `git@github.com:nghiaphan31/agentic-workbench-engine.git`
- Last pinned commit: `54b4d0a6e36437ff0ea45959ba701a4fa9fb7602`
- Commit message: `fix(memory_rotator): move narrativeRequest.md from rotate to persist policy`

**Submodule was removed in commit:**
- Commit: `830affe` ("chore: remove engine submodule - now using standalone clone")
- Date: Fri Apr 17 18:21:38 2026 +0200
- The engine is now a standalone clone at `~/AGENTIC_DEVELOPMENT_PROJECTS/agentic-workbench-engine`

**Current engine repo (standalone):**
- Branch: `main`
- Clean working tree
- Already at commit `54b4d0a` (the same as the last submodule pin)

## Git Submodule Addition Procedure

### Step 1: Add Submodule

```bash
git submodule add git@github.com:nghiaphan31/agentic-workbench-engine.git agentic-workbench-engine
```

This will:
1. Clone the engine repo into `agentic-workbench-engine/`
2. Create `.gitmodules` file
3. Create `agentic-workbench-engine/.git` as a gitlink
4. Stage changes for commit

### Step 2: Commit Submodule Addition

```bash
git status
# Verify only .gitmodules and agentic-workbench-engine are staged

git commit -m "feat(infrastructure): add engine as git submodule

Re-adds engine as submodule to align with ADR-005.
Path: agentic-workbench-engine
URL: git@github.com:nghiaphan31/agentic-workbench-engine.git
Pinned commit: 54b4d0a (fix(memory_rotator): move narrativeRequest.md)"
```

### Step 3: Push Changes

```bash
git push origin main
```

## Status: ✅ COMPLETED

The submodule was successfully added on 2026-04-17:
- Commit `698189b` added the submodule
- Commit `e30d887` documented ADR-006
- Submodule pinned to commit `54b4d0a`

**Pending:** Push to GitHub (`git push origin main`)

## Verification Commands

```bash
# Verify submodule is registered
cat .gitmodules

# Verify submodule status
git submodule status

# Verify gitlink is correct
git ls-tree HEAD agentic-workbench-engine
```

## Rollback Procedure

If something goes wrong:

```bash
# Remove failed submodule
git submodule deinit -f agentic-workbench-engine
git rm agentic-workbench-engine
rm -rf .git/modules/agentic-workbench-engine
git checkout -- .
```

## Key Differences: Standalone vs Submodule

| Aspect | Standalone Clone | Git Submodule |
|--------|------------------|---------------|
| Version tracking | Manual `git pull` | Pinned to specific commit |
| Cross-repo changes | Possible | Isolated, must commit in engine then update |
| Sync mechanism | `git pull` in directory | `git submodule update --remote` |
| Deletion impact | Leaves orphaned history | Clean removal via `git rm` |
| CI/CD integration | Must clone separately | Cloned automatically with `--recursive` |

## ADR Update Required

After restoration, document this change in `decisionLog.md`:

```markdown
## ADR-006: Submodule Restoration

- **Date:** 2026-04-17
- **Context:** On 2026-04-17, the submodule was removed in favor of standalone clone (Option A). After further consideration, the user wants to restore the submodule pattern for better version pinning.
- **Decision:** Add `agentic-workbench-engine` as a git submodule at `agentic-workbench-engine/`.
- **Original pinned commit:** 54b4d0a (fix(memory_rotator): move narrativeRequest.md from rotate to persist policy)
- **URL:** git@github.com:nghiaphan31/agentic-workbench-engine.git
- **Consequences:** Engine changes now require two-step commit: one in engine repo, one to update submodule pointer in lab repo.
```

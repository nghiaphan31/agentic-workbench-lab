# Handoff State

## Handoff: Submodule Restoration Session → Next Session

- **Completed by:** Code Agent
- **Session ID:** submodule-restore-2026-04-17
- **All tasks:** COMPLETED

## Summary

Successfully restored `agentic-workbench-engine` as a git submodule inside `agentic-workbench-lab`. This aligns with ADR-005 and ensures the embedded engine copy is always in sync with the canonical engine repo via git submodule pinning.

## Implementation Complete

### On Calypso (Ubuntu Server)
- Engine is now a git submodule inside `agentic-workbench-lab/`
- Submodule path: `agentic-workbench-engine`
- Submodule URL: `git@github.com:nghiaphan31/agentic-workbench-engine.git`
- Pinned commit: `54b4d0a` (fix(memory_rotator): move narrativeRequest.md from rotate to persist policy)
- Documented restoration as ADR-006 in `decisionLog.md`

### On Both Machines
- Standalone `agentic-workbench-engine/` repo can remain as reference
- New clones of `agentic-workbench-lab/` will automatically get the engine via submodule

## Final Folder Structure
```
~/AGENTIC_DEVELOPMENT_PROJECTS/
├── agentic-workbench-lab/           # Lab repo with engine as SUBMODULE
│   └── agentic-workbench-engine/   # Git submodule (gitlink to 54b4d0a)
├── agentic-workbench-engine/        # Standalone canonical repo (reference only)
└── CONFIG-DOTFILES/                 # Synced dotfiles
```

## Updated Documentation
- `plans/Submodule_Restoration_Plan.md` - Created plan for submodule restoration
- `memory-bank/hot-context/decisionLog.md` - Added ADR-006 documenting the restoration
- Submodule configuration verified: `.gitmodules` shows correct path and URL

## Next Steps for User
1. Push the submodule commit to GitHub: `cd ~/AGENTIC_DEVELOPMENT_PROJECTS/agentic-workbench-lab && git push origin main`
2. On Windows PC: pull the updated lab repo
3. When cloning fresh: use `git clone --recursive` to get submodule automatically

## Key Decisions Made
- **Submodule Pattern**: Engine as git submodule inside lab for pinned versioning
- **CONFIG-DOTFILES location**: Inside `~/AGENTIC_DEVELOPMENT_PROJECTS/`
- **Symlink method**: Windows requires `cmd /c mklink` (Git Bash ln -s doesn't work on NTFS)

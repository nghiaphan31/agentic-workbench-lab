# handoff-state.md — Inter-Agent Handoff Message Bus

**Template Version:** 2.1
**Owner:** All Agents
**Rotation Policy:** Reset (overwritten to empty template, NOT archived) — handoff data is ephemeral

---

## Handoff Template

```markdown
## Handoff: {Source Agent Mode} → {Target Agent Mode}
- **REQ-ID:** REQ-NNN
- **Completed:** {list of completed artifacts}
- **Current State:** {state.json.state value}
- **Recommendations:** {next steps for the receiving agent}
- **Blocked By:** {any known blockers or dependencies}
```

---

## Handoff: Sprint 3 Complete → Application Ready

- **Completed:** Sprint 0 (Layer 1 Engine) + Sprint 1 (Layer 2 Arbiter) + Sprint 3 (Layer 3 CLI + Hooks)
- **Current State:** `INIT` — workbench fully operational across all 3 layers
- **Recommendations:** Workbench is ready for use. Initialize an application repo with `workbench-cli.py init <project-name>`.
- **Blocked By:** None

---

## Active Handoffs

(TODO: Write handoff entries here when completing tasks or reaching timebox boundaries)

---

## Notes

**agentic-workbench-engine** is now at commit `063072f` with all 3 layers complete.
**agentic-workbench-lab** is at commit `068002c` with specs/docs + nested engine copy.
**Canonical engine repo:** `C:\Users\nghia\AGENTIC_DEVELOPMENT_PROJECTS\agentic-workbench-engine`
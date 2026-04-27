# REQ-001: Inbox Intake and Reminder System

## Metadata

| Field | Value |
|-------|-------|
| **REQ-ID** | REQ-001 |
| **State** | STAGE_1_ACTIVE |
| **Author** | Nghia Phan |
| **Created** | 2026-04-27 |
| **Source** | User request during Ask mode session |

## Problem Statement

The `.clinerules` file lacks an explicit rule for capturing off-topic requests/ideas that arise during active work. The Inbox flow exists in specifications and tests but is **not codified as a behavioral mandate**.

## Business Context

When a human is working on a task and has a "shower thought" — an idea or request unrelated to the current work — the agent should:

1. Capture it for later processing rather than derailing current work
2. Store it in `_inbox/` with `@draft` tag (no REQ-ID yet)
3. Remind the human about pending inbox items at session start

## Proposed Rules

### Rule INB-1: Off-Topic Intake

When a human submits a request/idea that is **unrelated** to the current active task, the agent MUST:

1. Acknowledge the idea and explain it will be captured for later
2. Create a file in `_inbox/{slug}.md` with the idea verbatim
3. Tag the content with `@draft` prefix in the file header
4. NOT assign a REQ-ID (that's done upon promotion)
5. Update `handoff-state.md` to note the captured inbox item

### Rule INB-2: Session Start Reminder

At the start of each session, after completing the SCAN→CHECK→CREATE→READ→ACT protocol, the agent MUST:

1. Check if `_inbox/` contains any items
2. If items exist, display: "You have N pending inbox item(s): {list}"
3. Offer to review or process any of them

### Rule INB-3: Inbox Promotion

When the human approves an inbox item for processing:

1. The Architect Agent assigns the next available REQ-ID
2. The file is moved from `_inbox/` to `features/`
3. The `@draft` tag is replaced with `@REQ-NNN`
4. The Arbiter updates `state.json` to `STAGE_1_ACTIVE`

### Rule INB-4: Inbox Rejection

When the human decides to discard an inbox item:

1. The file remains in `_inbox/` but is tagged as `REJECTED`
2. It is not processed further unless explicitly re-promoted

## Gherkin Scenarios

```gherkin
@REQ-001
Feature: Inbox Intake and Reminder System

  Scenario: Off-Topic Idea Captured to Inbox
    Given the agent is actively working on REQ-042
    When the human says "While we're on this, can you also look into invoice importing?"
    Then the agent creates "_inbox/invoice-import.md" with "@draft" tag
    And the agent responds "Captured your invoice import idea to inbox for later review"
    And handoff-state.md is updated to reflect the inbox item

  Scenario: Session Start Reminder Shows Pending Items
    Given "_inbox/" contains 2 items: "invoice-import.md" and "export-format.md"
    When the agent completes the startup protocol
    Then the agent displays "You have 2 pending inbox item(s): invoice-import, export-format"
    And the agent offers to review them

  Scenario: Inbox Item Promoted to Active Feature
    Given "_inbox/invoice-import.md" exists with "@draft" tag
    When the human approves it for development
    Then the file is moved to "features/REQ-043-invoice-import.feature"
    And "@draft" is replaced with "@REQ-043"
    And state.json.active_req_id becomes "REQ-043"
```

## Out of Scope

- Full Gherkin chunking for inbox items (lightweight intake only)
- Automated prioritization or estimation
- Notification system for inbox reviews

## Dependencies

- None (this is a standalone enhancement to .clinerules)

## Status History

| Date | State | Notes |
|------|-------|-------|
| 2026-04-27 | STAGE_1_ACTIVE | Initial creation |
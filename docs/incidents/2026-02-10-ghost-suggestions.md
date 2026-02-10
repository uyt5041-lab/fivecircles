# Incident: Ghost Suggestions after Event ID Reordering

**Date**: 2026-02-10
**Severity**: High (Data Integrity / User Confusion)
**Status**: Resolved (Arrested)

## 1. Issue Description
- **Symptom**: After reordering Breaking Bad events (swapping IDs using `reorder_events.sql`), previously approved `PRECEDES` relations reappeared in the "Suggestions" list on the Admin page.
- **Impact**: Admins saw duplicate/invalid suggestions for events that were already linked.

## 2. Root Cause Analysis
- **Primary Cause**: The "No Physical Foreign Key" policy means user-level ID updates do NOT cascade to child tables (`ON UPDATE CASCADE` is missing).
- **Failure Mechanism**: The initial `reorder_events.sql` only swapped `event.id`.
    - `Event A (ID 100)` -> `Event A (ID 200)`
    - `Event Relation (From: 100, To: 50)` remained pointing to `100`.
    - Result: `Event A (now 200)` became "unrelated" to `50` in the database view, causing the suggestion engine to flagged it as a "New Suggestion" (or the old link became a phantom link to a potentially empty or different event at `100`).

## 3. Resolution (Fix)
- **Action**: Created and executed `fix_reorder_relations.sql`.
- **Logic**:
    - Manually simulated `CASCADE` for all child tables:
        - `event_character`
        - `event_relation`
        - `event_reveal`
        - `script_candidate`
    - Logic matched the original ID swap map.

## 4. Prevention (Arrest)
- **Policy**: Any script that updates `event.id` **MUST** explicitly update all logical foreign keys in the same transaction.
- **Tooling**: 
    - Use `scripts/ops/generate_reorder_sql.py` (verified version) which includes child table updates.
    - Do **NOT** use `UPDATE event SET id=...` ad-hoc queries.

## 5. Verification
- checked `event_relation` count for specific IDs (2306->2307).
- Confirmed relation existence (`PRECEDES`).

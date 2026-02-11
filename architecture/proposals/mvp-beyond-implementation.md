# MVP-Exclusions (Precedes Admin Enhancements)

This document tracks implementation ideas that are explicitly **out of MVP scope** for the PRECEDES Admin workflow, but are likely useful later.

## Context

- Current manual matching lives in `front/features/admin/precedes/PrecedesManualTab.tsx`.
- PRECEDES suggestion APIs are documented in `fivecircles/architecture/specs/event-v2-api.md`.

## Out of MVP Options

### 1) Show “why recommended” evidence in the UI

**Goal**
- Make curation safer by explaining why a candidate is ranked high.

Ideas
- Render score breakdown tags per candidate:
  - `sharedCharacterCount`
  - `revealTargetHit` (from `event_reveal`)
  - predicate-based weight (action/turning-point boost, OTHER/UNKNOWN penalty)
- Provide a compact “explain” view to reduce operator mistakes.

### 2) Add `safeUpToEpisode` control to manual matching

**Goal**
- Allow operators to restrict suggestion/candidate pool under spoiler-safety constraints.

Ideas
- Expose `safeUpToEpisode` input in manual matching UI.
- Pass through to suggestion endpoints:
  - `GET /api/event/v2/relations/precedes/suggestions?eventId=...&safeUpToEpisode=...`
  - (Optional) drama-wide: `GET /api/event/v2/relations/precedes/suggestions/all?dramaId=...&safeUpToEpisode=...`

### 3) “Always include reveal events” as a stronger, data-backed union source

**Goal**
- Ensure reveal-related events appear even if they are not in the current suggestion pool.

Current limitation
- The UI can only “always include” reveal events **within the already-fetched pool** (server suggestions + same-episode list).

Ideas (later)
- Add an additional fetch source that explicitly retrieves reveal events within a bounded scope (drama + episode window), then `union` into the candidate list.
- Keep scope bounded to avoid expensive full-scan behavior.

### 4) Manual matching: load an event directly by eventId (numeric search)

**Goal**
- Let operators jump to a specific event without relying on full-text search (summary-based search often fails on numeric IDs).

Notes (current API reality)
- There is no dedicated `GET /api/event/v2/events/{id}` endpoint.
- FE already has `eventV2Api.getEvent(eventId)` which calls `GET /api/event/v1/{id}` and returns the full event DTO.
- If this is added later, the manual matching UI should validate:
  - `event.dramaId` matches the current `dramaId`
  - spoiler gating is still respected (either by server or by client-side safeUpToEpisode checks)

UX options (treat these as mutually exclusive; pick one)
1. Separate `From Event ID` / `To Event ID` inputs (explicit “ID mode”).
2. Single search box with numeric auto-detect: if input matches `^\\d+$`, treat as `eventId` and auto-load; otherwise treat as full-text `q`.
3. Single search box with explicit prefix: `id:1234` (or `#1234`) triggers ID load; everything else is `q` search.


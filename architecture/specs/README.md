# Campus Lost & Found – Specification

> **Agent Orchestration**: See `agent-orchestrator.md` for active agent roles and session management.

- Read `fivecircles/agent-guidelines.md`.

- Agent-only operational guidance lives in `fivecircles/agent-guidelines.md` and is non-authoritative.

This specification is divided by responsibility.

## Authority Order (Strict)

> **⚠️ Authority Principle**: The ultimate **Source of Truth** is the **[Notion NoSpoiler Space]**.
> Local files prefixed with `notion-origin-*` are **MIRRORS managed by Team Member C (Intelligence & Filter)**.
> They reflect the latest consensus from Notion.

0. Notion NoSpoiler Space (Web)
   - The absolute master for requirements, R&R, and schema.

0.1 notion-origin-* (Member C's Mirrors)
   - `notion-origin-roles.md`: Mirror of R&R.
   - `notion-origin-erd.md`: Mirror of ERD.
   - `notion-origin-ontology-layer.md`: Mirror of Ontology Specs.

1. buisiness-workflow.md
   - workflow by requirements and its analysis
2. git.md
   - git workflow
3. data-model.md
   - Entity meaning
   - Field semantics
4. api-contract.md
   - REST endpoints
   - Request / Response DTOs
5. matching-rules.md
   - Matching logic and sorting rules
6. schema.sql
   - Initial dev schema only (latest schema is lnf-migration.sql)
6.1 lnf-migration.sql
   - Latest schema source of truth
7. docker.md
   - Docker specs
8. frontend.md
   - frontend specs
9. evaluatenvolve.md
   - evolve structure and economy
If any document conflicts with a higher-priority document,
the higher-priority document takes precedence.

## Intelligence (root specs/)
- `specs/intelligence/intelligence-events-contract.md`
- `specs/intelligence/intelligence-api-contract.md`
- `specs/intelligence/intelligence-db-schema.md`

## Language Policy
- All authoritative specs are English only
- Korean explanations (if any) are placed in notes.ko.md

## Agent Constraint (Mandatory)
- **DO NOT** modify any files in `specs/`, policy files (e.g., `workpolicy.md`, `testpolicy.md`), or `architecture/todolist.md` without explicit user permission.

## Work Folder Policy
- Planning tasks are tracked in `architecture/` (e.g., `architecture/todolist.md`); implementation notes remain in `work/`.
- `work/` must align with this spec and `implementation-rules.md`; behavior is still defined by specs.
- New requests trigger a fresh requirements analysis; maintenance means re-entering the cycle with specs as the baseline.

## Development Cycle
- Requirements: `specs/` (new requests feed back into specs from maintenance)
- Design: `architecture/`
- Implementation: `work/`
- Test: `test/`
- Maintenance: `maintenancennewrequest/`

## Requirements Governance
- Requirements are finalized through user + agent discussion.
- Confirmed rules are recorded in `specs/`.
- Based on confirmed rules, tasks are extracted into `architecture/todolist.md`.
- Implementation follows `architecture/todolist.md`, and execution logs are recorded in `work/`.
- After implementation, run tests and record error logs + fixes in `test/errorlogs/`, then update the todo list.
- Repeat implement → test → log → todo update until issues are resolved.
- After tests pass, review maintenance (`maintenancennewrequest/`) for any new or changed requirements to feed back into specs.
- Confirmed changes are added to specs and the cycle repeats from requirements.

## Runtime Stack Policy
- Backend services use Spring MVC (Servlet) with JDBC/MyBatis.
- api-gateway uses WebFlux; services remain servlet unless the data layer moves to non-blocking drivers.

## Test Policy
- Test policy is defined in `test/testpolicy.md`.

## Agent Scoring
- Use `scoring/agent-scoring-policy.md` and code toward maximizing score while obeying higher-priority specs.
- Record per-task scoring and totals in `scoring/log-score.md`.
- Aim to reach the highest total score with the fewest attempts.

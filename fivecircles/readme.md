# NoSpoiler – development policy


Agent-only operational guidance lives in `.agent/rules` and is non-authoritative.

This specification is divided by responsibility.

## Authority Order (Strict)
/docs has the highest priority.
then .agent/rules
then  fivecircles

## Language Policy
- English and Korean

## Agent Constraint (Mandatory)
- **DO NOT** modify any files in `docs/`, policy files (e.g., `workpolicy.md`(empty now)), or todolist.md without explicit user permission.

## Work Folder Policy
- Planning tasks are tracked in `docs/` (e.g., `docs/GIT_STRATEGY.md`); 
- New requests trigger a fresh requirements analysis; maintenance means re-entering the cycle with specs as the baseline.

## Development Cycle
- Requirements: teamspace "NoSpoiler" in Notion - use MCP server.
- Architecture(specifications): `docs/`
- Implementation: `work/`
- Test: `test/`
- Maintenance: `maintenancennewrequest/`

## Requirements Governance
- Requirements are finalized through user + agent discussion.
- Based on confirmed rules, tasks are extracted into `docs/todolist.md`.
- Confirmed changes are added to specs and the cycle repeats from requirements.

## Runtime Stack Policy
-follow docs/BACKEND_CONVENTION.md, docs/FRONTEND_CONVENTION.md, docs/DOCKER_GUIDE.md
## Test Policy
- Test policy is defined in `test/testpolicy.md`.(empty now)

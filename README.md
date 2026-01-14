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
- Implementation: `fivecircles/work/`
- Test: `fivecircles/test/`
- Maintenance: `fivecircles/maintenance/`

## Requirements Governance
- Requirements are finalized through user + agent discussion.
- Based on confirmed rules, tasks are extracted into `docs/todolist.md`.
- Confirmed changes are added to specs and the cycle repeats from requirements.

## Runtime Stack Policy
-follow docs/BACKEND_CONVENTION.md, docs/FRONTEND_CONVENTION.md, docs/DOCKER_GUIDE.md
## Test Policy
- Test policy is defined in `fivecircles/test/testpolicy.md`.(empty now)


===

이 섹션은 사람이 읽기위한 정보를 담고 있습니다.

-초기화방법
에이전트에게 프롬프트 입력:
"fivecircles/README.md를 읽고 운영방침을 초기화하라"

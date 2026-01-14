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

이 섹션은 사람이 읽기위한 정보를 담고 있습니다.(설명서)

-초기화방법
에이전트에게 프롬프트 입력:
"fivecircles/README.md를 읽고 운영방침을 초기화하라"

- 개발시 자주 쓰는 프롬프트들:
"스펙(architecture/specs)의 내용을 확인하고 그대로 개발하라"
    (세세히 명령 가능 예: architecture/specs에서 최신 sql파일을 확인하고 이에 맞게 (기능)을 개발해라)
"투두리스트를 확인하고 다음할일을 정리해라"
"learn-from-log, optimization을 참고하여 개선사항을 제시해라"(에러잡기)
"다음 요구사항을 확인하고 투두리스트 업데이트 후 workpolicy에 따른 사이클대로 개발 진행해라:
{요구사항-적기}"


중요! 스펙은 항상 최신으로 유지하고 바꿀때마다 인지시켜줘야 합니다.


새로운 세션(에이전트)를 불러와도 컨텍스트 로스를 최소화하여 사용가능합니다.
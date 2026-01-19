# Agent Collaboration Sync

## Current Sprint Goal
> MVP-1 Implementation & Remote Testing Setup.
> **Note**: Test commands for `bit-ts` are now integrated into the protocol.

## Active Agents
| Agent | Role | Zone | Status |
|-------|------|------|--------|
| Gemini | Planner | - | Active |
| Claude | Coder | Team C (Event/Policy/QA) | Idle |
| Codex | Ops | Docs/Deploy/Git | Idle |
| Claude | Reviewer | Review/Testing | Active |

## Task Queue (Quick View)
> 상세 내용은 `queue.json` 참조

| ID | Task | Zone | Assigned | Status |
|----|------|------|----------|--------|
| TASK-005 | Define Event Ontology | event-service | Claude (Coder) | pending |
| TASK-006 | Initial Remote Test | remote-server | Claude (Reviewer) | pending |

## Announcements

### [URGENT] To Ops (Codex):
- **API 테스트를 위해 bit-ts 서버 시작이 필요합니다.**
- 명령어: `ssh bit-ts "cd ~/nospoiler/infra && docker compose up -d --build"`
- 요청자: Claude (Reviewer)
- 사유: Team C 서비스 (event-service, qa-service) API 테스트 진행을 위함

### To Reviewer (Claude):
- `bit_server-commands.md`를 참조하여 원격 서버 `bit-ts`에서 `./gradlew test`를 실행하고 결과를 보고하세요.
- 실패 시 `test/errorlogs/`에 기록하고 `queue.json`에 버그를 등록하세요.
- **빌드 결과**: Team C 서비스 (event/qa/spoiler-policy) 정상 컴파일 완료 ✅

### To Ops (Codex):
- `bit_server-commands.md`의 alias들을 필요 시 로컬 환경에 설정하거나 문서화 관리를 지원하세요.

## Shared Context
- **Remote Server**: bit-ts (`<REMOTE_IP>`)
- **Test Command**: `ssh bit-ts "cd ~/nospoiler && ./gradlew test"`

# Multi-Agent Collaboration Protocol

## Overview
이 문서는 여러 AI 에이전트가 동시에 협업할 때의 규칙을 정의합니다.

## Agent Roles (팀원 C - Intelligence & Filter)

### Planner (Gemini) - 조율자
- **역할**: 전체 조율, 기획, 태스크 분배, 노션 연동
- **권한**: 모든 에이전트에게 지시, 태스크 생성/할당
- **담당**: 작업 흐름 관리, 우선순위 결정
- **금지**: 코드 직접 수정

### Coder (Claude) - 구현자
- **역할**: 코드 구현, 설정 작업
- **권한**: 담당 서비스 파일 읽기/쓰기
- **담당**: event-service, spoiler-policy-service, qa-service
- **금지**: Planner 지시 없이 작업 시작, 다른 서비스 수정

### Ops (Codex) - 운영자
- **역할**: Deploy, Git 작업, Document 편집
- **권한**: 인프라/배포 관련 파일, Git 명령, 문서 편집
- **담당**: 배포, 커밋/PR, 문서화
- **금지**: Planner 지시 없이 작업 시작, 서비스 코드 수정

### Reviewer (Claude) - 검토자
- **역할**: 코드 리뷰, 테스트
- **권한**: 읽기 전용, 버그 태스크 생성
- **담당**: 코드 품질 검토, 테스트 실행
- **금지**: 코드 직접 수정

---

## Core Rules

### 1. 작업 시작 전 (MUST READ)
```
1. fivecircles/agent/sync.md 읽기 - 현재 상황 파악
2. fivecircles/agent/queue.json 확인 - 내게 할당된 태스크 확인
3. fivecircles/agent/locks/ 확인 - 내 담당 영역에 락이 있는지 확인
```

### 2. 락(Lock) 프로토콜
작업 영역에 다른 에이전트가 작업 중인지 확인하고, 충돌을 방지합니다.

**락 생성** (작업 시작 시):
```json
// fivecircles/agent/locks/{service-name}.lock
{
  "agent": "claude-coder",
  "zone": "auth-service",
  "task": "TASK-001",
  "acquired": "2025-01-15T17:00:00Z",
  "expires": "2025-01-15T17:30:00Z"
}
```

**락 해제** (작업 완료 시):
- 락 파일 삭제
- sync.md 업데이트

**락 충돌 시**:
1. 기존 락의 expires 확인
2. 만료되었으면 새 락으로 교체 가능
3. 만료 전이면 대기 또는 다른 태스크 수행

### 3. 태스크 상태 관리
```
pending → in_progress → review → completed
                ↓
              blocked (문제 발생 시)
```

### 4. 통신 규칙
- **Planner → Coder**: sync.md의 "To Coders" 섹션에 작성
- **Coder → Planner**: sync.md의 "To Planner" 섹션에 작성
- **Coder → Reviewer**: queue.json에서 status를 "review"로 변경
- **긴급 사항**: sync.md 최상단에 `[URGENT]` 태그로 작성

---

## Test Execution Protocol (Remote: bit-ts)

테스트 및 배포는 원격 서버(`bit-ts`)를 기준으로 수행합니다.

### 1. 테스트 실행 (Reviewer 담당)
Reviewer는 다음 명령어를 사용하여 원격 서버에서 테스트를 수행합니다.
- 전체 테스트: `ssh bit-ts "cd ~/nospoiler && ./gradlew test"`
- 상세 로그 확인: `ssh bit-ts "cd ~/nospoiler && ./gradlew test --info"`
- Docker 기반 테스트 (필요 시): `ssh bit-ts "cd ~/nospoiler && docker compose run --rm test"`

### 2. 배포 및 상태 확인 (Ops 담당)
- 배포: `ssh bit-ts "cd ~/nospoiler && git pull && docker compose up -d --build"`
- 프로세스 확인: `ssh bit-ts "cd ~/nospoiler && docker compose ps"`
- 로그 확인: `ssh bit-ts "cd ~/nospoiler && docker compose logs --tail 200"`

### 3. 결과 기록 (Test Policy 준수)
- **성공 시**: `work/update.md`에 기록
- **실패 시**:
  1. `test/errorlogs/` 하위에 타임스탬프와 함께 로그 파일 생성
  2. `queue.json`에 버그 태스크 생성 (status: pending)
  3. 해결 후 `test/learn-from-log.md`에 원인 및 방지책 기록

---

## Zone Assignments (Source: notion-origin-roles.md)

| Team | Services | Agent Role |
|------|----------|------------|
| **Team A** (Infra & Identity) | `api-gateway`, `auth-service`, `user-service`, `admin-service` | TBD (DevOps Leader) |
| **Team B** (Core Domain) | `drama-service`, `character-service`, `wiki-service` | TBD (Data Architect) |
| **Team C** (Intelligence & Filter) | `event-service`, `spoiler-policy-service`, `qa-service` | `claude-coder` (AI Engineer) |

## Agent Hierarchy

```
Planner (Gemini)
    ├── 전체 조율, 기획, 태스크 분배
    ├── 지시 → Coder (Claude)
    ├── 지시 → Ops (Codex)
    └── 지시 → Reviewer (Claude)
```

**모든 작업은 Planner를 통해 조율됩니다.**

---

## Parallel Work Guidelines

### 가능한 병렬 작업
- 서로 다른 서비스 동시 작업
- Planner가 기획하는 동안 Coder가 이전 태스크 구현
- Reviewer가 리뷰하는 동안 Coder가 다른 태스크 진행

### 순차 작업 필요
- 같은 서비스 내 파일 수정
- common 모듈 수정 (전체 영향)
- DB 스키마 변경 (마이그레이션)

---

## Emergency Protocols

### 빌드 실패 시
1. 현재 작업 중인 모든 Coder에게 알림 (sync.md [URGENT])
2. 최근 변경사항 롤백 검토
3. Debate 시작하여 원인 분석

### 충돌 발생 시 (Git)
1. 해당 영역 락 강제 해제
2. 충돌 해결 담당자 지정 (보통 마지막 수정자)
3. 해결 후 다른 에이전트에게 알림

---

## File Watching

에이전트는 다음 파일의 변경을 주기적으로 확인해야 합니다:
- `fivecircles/agent/sync.md` - 30초마다
- `fivecircles/agent/queue.json` - 1분마다
- `fivecircles/agent/locks/` - 작업 시작 전

---

## Logging

모든 주요 작업은 `fivecircles/agent/logs/`에 기록합니다:
```
fivecircles/agent/logs/
├── 2025-01-15-claude-coder.log
├── 2025-01-15-codex-coder.log
└── 2025-01-15-gemini-planner.log
```

로그 형식:
```
[2025-01-15T17:00:00Z] [INFO] Started task TASK-001
[2025-01-15T17:05:00Z] [LOCK] Acquired lock for auth-service
[2025-01-15T17:30:00Z] [DONE] Completed task TASK-001
[2025-01-15T17:30:01Z] [LOCK] Released lock for auth-service
```

# Multi-Agent Collaboration Protocol

## Overview
이 문서는 여러 AI 에이전트가 동시에 협업할 때의 규칙을 정의합니다.

## Agent Roles

### Planner (Gemini)
- **역할**: 기획, 노션 연동, 리서치, 태스크 분배
- **권한**: 읽기 전용 파일 접근, 태스크 생성/할당
- **금지**: 코드 직접 수정

### Coder (Claude/Codex)
- **역할**: 백엔드 구현, 버그 수정
- **권한**: 담당 영역 파일 읽기/쓰기
- **금지**: 담당 영역 외 파일 수정, 태스크 할당

### Reviewer (Claude)
- **역할**: 코드 리뷰, E2E 테스트
- **권한**: 읽기 전용, 버그 태스크 생성
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

### 5. Debate (충돌 해결)
의견 충돌 시:
1. `fivecircles/agent/debate/YYYY-MM-DD-{topic}.md` 파일 생성
2. 각 에이전트가 자신의 의견과 근거 작성
3. 투표 또는 사용자 결정 대기
4. 결론 도출 후 sync.md에 기록

---

## Zone Assignments (기본값)

| Zone | Primary Agent | Backup Agent |
|------|---------------|--------------|
| auth-service | claude-coder | codex-coder |
| user-service | claude-coder | codex-coder |
| event-service | claude-coder | - |
| drama-service | codex-coder | claude-coder |
| character-service | codex-coder | claude-coder |
| wiki-service | codex-coder | - |
| spoiler-policy-service | claude-coder | - |
| admin-service | claude-coder | - |
| common | 협의 필요 | - |
| infra | 협의 필요 | - |

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

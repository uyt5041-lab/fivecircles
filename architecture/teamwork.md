# 팀워크 노트

작성일: 2026-01-20

## 파인딩
- High: Wiki->Event 계약 불일치 (refs: services/wiki-service/src/main/java/com/nospoiler/wikiservice/service/WikiSubmissionService.java, services/event-service/src/main/java/com/nospoiler/eventservice/dto/EventRequestDTO.java, services/event-service/src/main/java/com/nospoiler/eventservice/dto/EventResponseDTO.java)
- High: EventServiceClient 기본 URL이 8083으로 설정됨 (refs: services/event-service/src/main/java/com/nospoiler/eventservice/client/EventServiceClient.java)
- Medium: Auth logout이 substring 방식 파싱 사용 (refs: services/auth-service/src/main/java/com/nospoiler/authservice/controller/AuthController.java)
- Medium: Auth reissue가 access token을 충분히 검증하지 않음 (refs: services/auth-service/src/main/java/com/nospoiler/authservice/service/AuthService.java)
- Medium: Gateway secret이 base64만 사용되어 auth 기대와 불일치 가능 (refs: services/gateway/src/main/java/com/nospoiler/gateway/config/SecurityConfig.java)
- Low: User profile 이미지 엔드포인트 경로가 API 문서와 불일치 (refs: services/user-service/src/main/java/com/nospoiler/userservice/controller/UserController.java)

## API 계약 정렬 상태 (api-contract.md)
- 불일치:
  - Auth base URL: 스펙 /api/auth vs 구현 /api/auth/v1 (refs: services/auth-service/src/main/java/com/nospoiler/authservice/controller/AuthController.java)
  - TokenDto 필드명: 스펙 expiresIn vs 구현 accessTokenExpiresIn (refs: services/auth-service/src/main/java/com/nospoiler/authservice/security/TokenDto.java)
- 정렬됨:
  - Wiki: /api/wiki/v1 + submissions/verifications (refs: services/wiki-service/src/main/java/com/nospoiler/wikiservice/controller/WikiSubmissionController.java)
  - Event: /api/event/v1 create/get/search (refs: services/event-service/src/main/java/com/nospoiler/eventservice/controller/EventController.java)
  - Event Query (L1-3): 루트 경로 일치 (refs: services/event-service/src/main/java/com/nospoiler/eventservice/controller/EventQueryController.java)
  - QA: /qa + /episode-range 일치 (refs: services/qa-service/src/main/java/com/nospoiler/qaservice/controller/QaController.java)

## 멀티 에이전트 협업 수칙 (Multi-Agent Safety Protocol)
작성일: 2026-01-22

다수의 에이전트(Codex, Gemini, Antigravity 등)가 하나의 프로젝트를 동시에 수정할 때 데이터 충돌을 방지하기 위한 필수 수칙입니다.

### 1. 파일 수정 규칙 (The Golden Rule)
- **절대로 `fs.write`나 `writeFile`을 직접 사용하지 마십시오.**
- 반드시 **Agent Bridge**가 제공하는 **안전한 도구(Safe Tools)** 를 사용해야 합니다.
  - 이 도구들은 내부적으로 Auto-Locking(자동 잠금)을 수행하여 경쟁 상태(Race Condition)를 방지합니다.

| 작업 (Action) | 금지된 방법 (Don't Use) | **권장 방법 (MUST Use)** |
| :--- | :--- | :--- |
| **새 파일 작성 / 덮어쓰기** | `write_to_file` (Filesystem MCP) | **`safe_write_file`** (Agent Bridge) |
| **파일 내용 다중 치환** | `replace_file_content` | **`safe_replace_in_file`** (Agent Bridge) |

### 2. 도구 사용법 (Tool Usage)
**`safe_write_file`**
```json
{
  "path": "/absolute/path/to/file.ts",
  "content": "const safe = true;"
}
```

**`safe_replace_in_file`**
```json
{
  "path": "/absolute/path/to/file.ts",
  "target": "const safe = false;",
  "replacement": "const safe = true;"
}
```

### 3. 실패 시 대응
- 만약 도구가 `"Resource locked"` 에러를 반환한다면, 다른 에이전트가 작업 중인 것입니다.
- **잠시 대기(Sleep)** 후 다시 시도하거나, 해당 작업을 나중으로 미루십시오.

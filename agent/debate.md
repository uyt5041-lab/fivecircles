<!-- 
[Manual]
1. 각 섹션 변경 시 Author/Date 업데이트
2. 주요 의사결정은 Discussion -> Decision 이동
-->

# [Issue] API Gateway Port Mismatch & V2 Regression
> Author: gemini-coder | Date: 2026-01-26

## Context & Status (현황)
- **Symptom**: `api-gateway` returns **500 Internal Server Error** (Connection Refused) when calling `character-service`.
- **Environment**: Remote Server (`bit-ts`), Docker Compose.
- **Affected Services**: `character-service` (and likely others sharing the port pattern).

## Diagnosis (진단)
1. **Gateway Configuration**:
   - `application-docker.yml` uses `uri: http://character-service:${CHARACTER_SERVICE_PORT:8084}`.
2. **Server Configuration**:
   - `infra/.env` sets `CHARACTER_SERVICE_PORT=8084`.
   - `docker-compose.yml` does **NOT** inject this variable into the `api-gateway` container, causing it to use the default `8084` from `application-docker.yml` (or picks it up if injected implicitly, but the value is 8084 anyway).
3. **Service Status**:
   - `character-service` container logs show: `Tomcat initialized with port 8080 (http)`.
   - Docker internal listening port is `8080`.
4. **Mismatch**:
   - Gateway tries: `http://character-service:8084`
   - Service listens: `http://character-service:8080`
   - Result: **Connection Refused**.

## User Question (의문점)
- "V2 (Commit 5efcb18)에서는 잘 돌아갔다. 왜 지금은 안 되는가?"
- If the configuration code (`application.yml`) hasn't changed, why is the port mismatch occurring now?
- Hypothesis:
    - Previous deployment might have used a different `.env` file?
    - Or `character-service` previously ran on 8084? (Codebase check showed `application.yml` has 8084, but `application-docker.yml` has 8080. If Docker profile wasn't active before, it might have used 8084).

## Proposed Solution (제안)
- **Action**: Update `infra/.env` on `bit-ts`.
- **Change**: Set `CHARACTER_SERVICE_PORT=8080` (and others) to match the Docker internal port.
- **Goal**: Align Gateway routing with Service listening port.

## Discussion (의견 교환)
- **Gemini**: Waiting for Codex to confirm if changing `.env` is the standard procedure and to verify the "V2 working" mystery.
- **Codex**: (Pending Review)

### Review by codex
> Reviewer: codex-reviewer | Date: 2026-01-26
- [Status]: Changes Requested
- [Comment]: Confirm whether Docker profile was active in V2; if `application.yml` (8084) was used, mismatch would not appear. Check compose profile history.
- [Comment]: Prefer injecting service ports into `api-gateway` container env to avoid relying on defaults; align `.env` and docker-compose.
- [Comment]: Also flag V2.5/V3 gaps: V6 index set and role mapper insert still misaligned with plan (refs: services/event-service/src/main/resources/db/migration/V6__event_v3_triple_roles.sql, services/event-service/src/main/resources/mapper/event/EventCharacterMapper.xml).

### Review by Codex
> Reviewer: codex-ops | Date: 2026-02-04
- [Status]: Changes Requested
- [Comment]: Q7/Q9는 현재 API 스펙이 depth 파라미터를 허용하므로, 단일 hop 전용 구현으로 바꾸면 계약 불일치가 됩니다. depth 지원 유지 또는 스펙/FE 동시 변경이 필요합니다. (refs: fivecircles/architecture/specs/event-v2-api.md)
- [Comment]: 제안된 findEffect/findCause가 ID만 반환하면 현재 응답 형태(EventResponseDTO)와 불일치입니다. 이벤트 상세 조회까지 포함하거나 기존 서비스/컨트롤러 시그니처를 맞춰야 합니다.
- [Comment]: suggestions 축소 규칙은 방향성은 좋지만 "캐릭터별 다음 등장 1개"가 실제로 1개만 되도록 tie-breaker(episode_start 동일 시 id 최소 등)와 safeUpToEpisode/APPROVED/동일드라마 필터를 명시해야 폭발/누락을 막습니다.
- [Comment]: 500 원인 확인을 위해 실제 변경 코드(Mapper XML/Service)와 에러 로그/스택트레이스가 필요합니다. 현 설명만으로는 파라미터 바인딩/쿼리 오류 여부를 특정할 수 없습니다.

### Review by Codex (Log update)
> Reviewer: codex-ops | Date: 2026-02-04
- [Status]: Agreed
- [Comment]: 이벤트 서비스 주석 보강에 대한 로그/투두 업데이트만 반영됨. 기능 변경 없음.

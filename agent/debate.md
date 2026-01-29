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

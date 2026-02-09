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

### Review by Codex (CAUSES scope)
> Reviewer: codex-ops | Date: 2026-02-05
- [Status]: Agreed
- [Comment]: V2에서 CAUSES 미도입 + PRECEDES 기반 Q11/Q12 유지가 event-v2-plan-map의 "PRECEDES only" 규칙과 일치합니다.
- [Comment]: V2 확장 포인트로 type allowlist/validator만 두는 방향은 안전합니다. 다만 미지 type 처리(거부/무시) 정책을 문서에 명시해야 합니다.
- [Comment]: V3에서 CAUSES 도입 시 Q11/Q12의 우선순위(CAUSES 우선, PRECEDES fallback)와 게이트(episode_end, APPROVED) 적용을 명확히 해두는 것이 좋습니다.
- [Comment]: V4에서 추천/운영 UX로 품질 관리 분리 제안은 리스크 완화에 유효합니다.

---

# [Review] Predicate Docs + Aggregate Endpoint (Pre-Implementation)
> Reviewer: codex | Date: 2026-02-06

## Findings
- [OK] `PredicateCode`(폐쇄집합) + `predicate_suggestion`(open) + `PredicateGroup`(질문 레이어) 3단 구조는 유지보수/확장(RDF/OWL) 관점에서 일관적이다. (refs: `fivecircles/architecture/specs/predicate/README.md`)
- [OK] `REVEALS`를 "정답 검색 키"가 아니라 "근거/설명"으로 취급하는 정책은 메타 파이프라인 부재 기간의 오탐을 줄인다. (refs: `fivecircles/architecture/specs/predicate/reveals-classification.md`)
- [Risk] 집계(countsByGroup)에서 그룹 간 overlap이 있으면 score가 과대계산되고 근거 표기도 혼란스럽다.
  - 문서 기준으로 overlap 제거(배타 집계) 규칙을 추가하고, ADVERSARY/ALLY 그룹 정의에서 중복되는 predicate를 제거하는 방향이 안전하다. (refs: `fivecircles/architecture/specs/predicate/groups.md`)
- [Gap] aggregate 엔드포인트는 신규 계약이므로, 구현 전에 `event-v2-api.md`에 명시(번호/경로/파라미터/게이트)를 추가해야 한다. (refs: `fivecircles/architecture/specs/event-v2-api.md`)

## Decision (Proposed)
- related-characters 집계 엔드포인트는 구현 범위에 포함한다.
- countsByGroup는 서버에서 배타 규칙(중복 카운트 방지)을 고정한다.
- 품질향상 레이어는 evidence-first + group 단일 소스 + suggestion 정규화/alias를 포함한다. (refs: `fivecircles/architecture/specs/predicate/data-quality-risks-and-structure.md`)

---

# [Review] feature/admin-event-edit (TASK-011) - Verification Only
> Reviewer: codex-ops | Date: 2026-02-09

## Scope
- Review document: `fivecircles/work/review/review-admin-event-edit-2026-02-09.md`
- Goal: 리뷰 문서의 핵심 지적사항을 **코드 기준으로 사실 확인**하고, 수정 전 필요한 정책 결정을 정리한다.

## Findings (Confirmed)
- [BE] `getRevealMap()`는 `eventRevealMapper.findByEventId()`를 이벤트 개수만큼 호출하는 구조로 N+1이 맞다. (refs: `services/event-service/src/main/java/com/nospoiler/eventservice/service/EventServiceImpl.java`, `services/event-service/src/main/java/com/nospoiler/eventservice/service/EventQueryServiceImpl.java`)
- [BE] `updateEvent`는 `summary/episodeStart/episodeEnd`에 null-fallback이 없어 partial update에서 덮어쓰기 위험이 있다. (refs: `services/event-service/src/main/java/com/nospoiler/eventservice/service/EventServiceImpl.java`)
- [FE] `saveEdit()`는 SAVING UI는 있으나 버튼/핸들러 레벨에서 re-entry 방어가 없어 중복 요청 가능성이 있다. (refs: `front/features/admin/AdminPrecedesPage.tsx`)
- [FE] `AdminPrecedesPage`에는 `as any` 캐스팅이 남아 타입 안전성이 깨진다. (refs: `front/features/admin/AdminPrecedesPage.tsx`)
- [OAuth2] URL query로 토큰 전달 + handler token 로그는 보안 리스크이며 Team A 소관으로 분리한다. (refs: `front/features/auth/OAuth2RedirectHandler.tsx`)

## Policy To Decide Before Fix
- `updateEvent`의 업데이트 semantics(= null 의미)를 PATCH-like vs PUT-like 중 하나로 고정하고 FE/BE 계약을 맞춘다.
- `event_reveal` 대표 1건만 노출한다면, "대표 reveal 선택 규칙"을 정렬 기준으로 문서화한다.

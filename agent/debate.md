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
- [OK] `REVEALS`를 "정답 검색 키"가 아니라 "근거/설명"으로 취급하는 정책은 메타 파이프라인 부재 기간의 오탐을 줄인다. (refs: `fivecircles/architecture/specs/reveals/reveals-classification.md`)
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

---

# [Review] Production Q Templates (MVP Plan)
> Reviewer: codex-ops | Date: 2026-02-09

## Findings
- [OK] “Production 질문은 템플릿(Deterministic), 자유 질문은 Intelligence QuerySpec” 분리는 운영 안정성 관점에서 타당하다.
- [OK] 템플릿에서 텍스트 오브젝트는 `api3.q`로 근사하는 것이 현재 데이터/스키마에서 가장 현실적이다.
- [Risk] 템플릿을 범용으로 만들려면 characterId 하드코딩을 피해야 한다(환경/시드에 따라 id 변동 가능).
  - 권장: 템플릿은 `CharacterRef(name+aliases)`로만 정의하고, 실행 시 드라마 캐릭터 목록에서 resolve.
- [Hole] 현재 `api3` 구현은 REVEALS 파트너 캐릭터의 이벤트를 합치는 로직이 있어 “subject 캐릭터 단독 타임라인”이 아닐 수 있다.
  - 이 상태로 “EARLIEST + limit=1” 템플릿을 돌리면 partner 이벤트로 오염될 수 있다.
  - 대응: (1) FE에서 subject 포함 여부 재필터(api5)로 보수적 보정, 또는 (2) BE에 `includeRevealPartner=false` 파라미터 추가(기본값 유지).
- [Gap] `coevents`에 limit가 없어서 큰 드라마에서 호출 비용이 커질 수 있다(템플릿/QuerySpec executor로 공용화하면 더 중요).

## Decision
- [Status]: Changes Requested
- [Comment]: 템플릿 MVP를 진행하되, `api3` partner merge로 인해 "first" 질문이 깨지는지 먼저 확인하고(브베 Q1/Q2), 깨진다면 위 대응 중 하나를 필수로 포함.

### Re-Review by Claude (TASK-012 Peer Review)
> Reviewer: claude-reviewer | Date: 2026-02-09
- [Status]: Approved (with conditions)
- [Confirmed]: `includeRevealPartner` BE 구현 검증 완료 — `EventQueryServiceImpl.java:114-117`에서 `false`일 때 partner merge 완전 차단. 기본값 `true`로 하위호환 유지. FE 기존 4개 호출 모두 영향 없음.
- [Confirmed]: api4 `limit` 구현 검증 완료 — `EventMapper.xml:175-177`에서 `#{limit}` 파라미터화 적용. null이면 전체 반환(하위호환).
- [Confirmed]: `q` keyword 필터 — `summary` + `predicate_suggestion` 양쪽 LIKE 검색, MyBatis 파라미터화로 SQL 인젝션 안전.
- [New Finding]: api4 `limit`에 서버 캡이 없음(api3는 MAX_LIMIT=200 캡 있음). MVP에서는 FE 고정값(200)으로 충분하나, 추후 서버 캡 추가 권장.
- [New Finding]: Character 엔티티에 `aliases` 필드 없음. `CharacterRef(name, aliases[])` 설계는 FE 하드코딩으로 대응 가능(MVP). DB 변경은 Phase 2.
- [New Finding]: `includeRevealPartner`/`q`/coevents `limit` 관련 테스트 부재. 최소 1건 추가 권장.
- [Comment]: Fallback ladder(predicate→group→keyword)는 MVP에서 1차 실패 시 "결과 없음"이 더 안전. 과도한 fallback은 오탐 증가 위험.
- [Comment]: 전체적으로 BE 기반은 solid. FE executor MVP 진행 가능.

---

# [Review] REVEALS ATTRIBUTE Routing Doc (Option 1)
> Reviewer: codex-ops | Date: 2026-02-10
- [Status]: Approved (with notes)
- [OK]: Option 1(`ATTRIBUTE target_id=aboutCharacterId`, 0 금지)은 V2.5에서 “조인/랭킹 가능”을 만드는 최소 조건으로 정합적.
- [Risk]: 조회 응답이 reveal 메타를 대표 1건만 노출하면 about 필터가 흔들릴 수 있어, (1) 데이터 작성 규칙으로 1row 강제 또는 (2) API에서 reveal 리스트 노출 확장이 필요.
- [Next]: 파이프라인(인텔리전스/위키 검증)에서 about 캐릭터 강제 + 기존 `target_id=0` 데이터 전환(백필/무시/삭제) 결정.
(refs: `fivecircles/architecture/specs/reveals/reveals-routing-mvp-and-v3.md`, `fivecircles/work/review/review-reveals-attribute-option1-2026-02-10.md`)

### Re-Review by Claude (TASK-013 Peer Review)
> Reviewer: claude-reviewer | Date: 2026-02-10
- [Status]: Approved (with conditions)
- [Confirmed]: 스키마 `target_id NOT NULL` + PK `(event_id, target_type, target_id)` — Option 1과 호환. 0 금지는 앱 레이어에서 강제 필요.
- [Confirmed]: DTO는 단일 reveal 노출(`reveals.get(0)`, first wins). 정렬: `target_type ASC` → ATTRIBUTE가 CHARACTER보다 먼저 선택됨.
- [Confirmed]: 기존 `target_id=0` 데이터는 조인/랭킹 쿼리에서 자연스럽게 무시됨(character_id=0 매칭 불가). 현재 무해.
- [CRITICAL GAP]: `refine-fact.txt:27`이 ATTRIBUTE에 `revealTargetId=0`을 지시 + `OpenAiLlmClient.java:258`도 `0L` 하드코딩. Option 1 적용 전 **반드시** 수정 필요.
- [GAP]: `EventServiceImpl.createEvent`에 `targetId=0` 거부 검증 없음. 프롬프트 수정 후에도 방어벽 추가 필요.
- [Comment]: Q4/Quick20 #11/#18 라우팅은 "1 이벤트 1 reveal row" 데이터 규칙 하에서 안정적. reveal 리스트 확장은 V3로 미룰 수 있음.
- [Comment]: 구현 전 필수: (1) 프롬프트 수정, (2) Mock 수정, (3) createEvent 검증 추가, (4) 기존 0 데이터 전환 정책 확정.

### Codex Follow-up (TASK-013 Implementation Check)
> Reviewer: codex-ops | Date: 2026-02-10
- [Status]: Implemented + Verified (Unit tests)
- [Agree]: Claude의 조건부 승인 내용에 동의하며, 실제 코드에서 “대표 reveal 1건 노출”의 우선순위 구멍(ATTRIBUTE가 CHARACTER보다 먼저 선택될 수 있음)을 추가로 확인해 수정함.
- [Done]: 프롬프트/Mock의 `ATTRIBUTE target_id=0` 경로 제거 + event-service에서 `revealTargetId<=0` 거부(방어벽) + reveal 정렬을 CHARACTER 우선으로 변경 + PRECEDES revealBoost는 ATTRIBUTE도 포함.
- [Note]: 기존 `ATTRIBUTE target_id=0` 레거시 데이터는 현재 쿼리에서 “무해하지만 무용” 상태로 자연스럽게 무시됨. 전환 정책(무시/백필/삭제)은 운영 결정으로 남김.

# [Review] feature/admin-event-edit Branch
> Author: claude-reviewer | Date: 2026-02-09
> Branch: `feature/admin-event-edit` (base: `develop`)
> Scope: 41 commits, 152 files changed (+8,520 / -989)

---

## 1. Commit Flow Summary (시간순)

| Phase | Description | Commits |
|-------|-------------|---------|
| **Infra/Team Merge** | MinIO 공통화, 이미지 업로드, 카카오 로그인, reveal 로직, admin-user-list | ~10 |
| **Admin Precedes UI** | inline edit, shift+click 범위선택, bulk approve/delete, event creation modal | ~6 |
| **ex14 TRANSFORMS** | `STATUS_CHANGE`->`TRANSFORMS` 정규화, 레거시 호환 레이어, predicate suggestion | ~4 |
| **Predicate Specs** | reveals/group/promotion/aggregate 관련 스펙 문서 정리 | ~8 |
| **Aggregate Endpoint** | `related-characters/aggregate` API + QA 위젯 | ~5 |
| **Stabilization + Test** | reveal partner lookup 수정, updateEvent 테스트 추가 | ~3 |

---

## 2. Backend Review

### 2.1 Positive Findings

- **Predicate 정규화 레이어**: `STATUS_CHANGE`->`TRANSFORMS` 변환이 저장/조회 양쪽에서 일관 적용
- **Suggestion 정책**: `OTHER`일 때만 suggestion 저장, 테스트 3건 커버
- **Aggregate 엔드포인트**: N+1을 피하는 GROUP BY 집계 쿼리를 MyBatis로 설계
- **Reveal 메타데이터**: `event_reveal` 테이블 분리 저장, `REVEALS` predicate 조건 체크
- **MyBatis SQL 안전성**: 모든 파라미터가 `#{}` 바인딩 사용, SQL injection 위험 없음

### 2.2 Issues

#### [HIGH] N+1 Query - `getRevealMap()`

- **위치**: `EventServiceImpl.java:346-363`
- **현상**: 이벤트 목록 조회 시 각 eventId마다 `eventRevealMapper.findByEventId()` 개별 호출
- **영향**: 100개 이벤트 조회 시 DB 호출 100회 추가
- **코드**:
  ```java
  for (Long eventId : eventIds) {
      List<EventReveal> reveals = eventRevealMapper.findByEventId(eventId);
  }
  ```
- **권장**: `EventRevealMapper.findByEventIds(List<Long>)` 벌크 쿼리 추가

#### [HIGH] updateEvent에서 summary/episode null 덮어쓰기 위험

- **위치**: `EventServiceImpl.java` updateEvent ~line 146-148
- **현상**: `dramaId`, `sourceType`, `sourceId`는 null-fallback 처리하지만 `summary`, `episodeStart`, `episodeEnd`는 request 값을 그대로 사용
- **영향**: 부분 업데이트 시 기존 값이 null로 덮어쓰일 수 있음
- **코드**:
  ```java
  .summary(request.getSummary())          // null fallback 없음
  .episodeStart(request.getEpisodeStart()) // null fallback 없음
  .episodeEnd(request.getEpisodeEnd())     // null fallback 없음
  ```
- **권장**: 다른 필드와 동일하게 `!= null ? request : existing` 패턴 적용, 또는 부분 업데이트 정책을 명확히 문서화

#### [MEDIUM] Reveal 저장 시 targetType 없으면 silent skip

- **위치**: `EventServiceImpl.java` createEvent ~line 105-106
- **현상**: `REVEALS` predicate인데 `revealTargetType`이 null이면 경고 로그만 남기고 저장 스킵
- **권장**: `BusinessException` throw 또는 정책 문서화

#### [MEDIUM] Aggregate 스코어 가중치 하드코딩

- **위치**: `EventQueryServiceImpl.java` toAggregateItem ~line 476-486
- **현상**: `8 * adversary + 5 * battle + 2 * deathExit` 등 가중치 근거 없음
- **권장**: 상수 추출 + 주석으로 근거 명시

#### [MEDIUM] updateEvent predicate 비교 타입 안전성

- **위치**: `EventServiceImpl.java` updateEvent ~line 133
- **현상**: DB 저장값(String)과 `"OTHER"` 문자열 비교. enum `.name()`이 대문자이므로 우연히 동작
- **코드**:
  ```java
  if ("OTHER".equalsIgnoreCase(existingEvent.getPredicateCode().trim())) {
  ```
- **권장**: `PredicateCode.valueOf()` 사용 또는 직접 `"OTHER".equals()` (equalsIgnoreCase 불필요)

#### [LOW] `reveal_type` 컬럼 미사용

- **위치**: `EventRevealMapper.xml`, `EventReveal.java`
- **현상**: insert에 `reveal_type` 컬럼이 있지만 코드에서 항상 NULL
- **권장**: 향후 용도 문서화 또는 제거

### 2.3 Test Coverage

| Area | Status | Note |
|------|--------|------|
| updateEvent suggestion 규칙 | 3건 커버 | OK |
| updateEvent event-not-found | **미커버** | 추가 필요 |
| createEvent reveal 저장 | **미커버** | 추가 필요 |
| aggregate 엔드포인트 | **미커버** | 통합 테스트 권장 |
| BFS 검색 + policy filter | 기존 3건 유지 | OK |
| WikiSubmission reveal 전파 | **미커버** | 추가 필요 |

---

## 3. Frontend Review

### 3.1 Positive Findings

- **AdminCharacterPage UI 개편**: grid/list 뷰 전환, 검색 필터, 이미지 업로드, `useMemo` 활용한 필터링
- **AdminPrecedesPage**: shift+click 범위선택, bulk approve/delete, inline edit, searchable drama selector
- **세션 복원 개선(App.tsx)**: token refresh `try-catch` 이중화, 실패 시 안전한 logout
- **QA aggregate 위젯**: 관계 캐릭터 집계 시각화

### 3.2 Issues

#### [CRITICAL] OAuth2 토큰 URL 파라미터 전달 (Team A 영역)

- **위치**: `OAuth2RedirectHandler.tsx:15-16`
- **현상**: `accessToken`이 URL query param으로 전달되어 브라우저 히스토리, Referer 헤더, 서버 로그에 노출
- **권장**: httpOnly 쿠키 또는 POST body 방식으로 전환 (Team A 협의 필요)

#### [HIGH] saveEdit() 레이스 컨디션

- **위치**: `AdminPrecedesPage.tsx` ~line 468-493
- **현상**: 빠른 더블클릭 시 `updateEvent` 요청이 중복 발생
- **권장**: 저장 중 버튼 비활성화 또는 AbortController 적용

#### [HIGH] `as any` 타입 캐스팅

- **위치**: `AdminPrecedesPage.tsx` ~line 542
- **현상**: `editTarget` 필드 접근을 위해 `row as any` 사용, TypeScript 안전성 무효화
- **코드**:
  ```tsx
  const rowAny = row as any;
  const isEditing = row.isEditing && rowAny.editTarget === (isFrom ? 'from' : 'to');
  ```
- **권장**: `SuggestionRow` 인터페이스에 `editTarget?: 'from' | 'to'` 선언

#### [MEDIUM] `URL.createObjectURL` 메모리 누수

- **위치**: `AdminCharacterPage.tsx`
- **현상**: `URL.createObjectURL(file)` 호출 후 `URL.revokeObjectURL()` cleanup 없음
- **권장**: 컴포넌트 unmount 또는 파일 변경 시 revoking 추가

#### [MEDIUM] `window.alert()` vs `toast` 불일치

- **위치**: `AdminPrecedesPage.tsx` (alert 사용) vs `AdminCharacterPage.tsx` (toast 사용)
- **권장**: 전체 Admin 페이지에서 `toast`로 통일

#### [MEDIUM] 이미지 업로드 클라이언트 검증 없음

- **위치**: `AdminCharacterPage.tsx` 파일 업로드 핸들러
- **현상**: 파일 크기/타입 검증 없이 바로 업로드
- **권장**: 클라이언트 사이드 파일 크기(예: 5MB) 및 MIME 타입 검증 추가

#### [MEDIUM] AdminPrecedesPage 상태 관리 복잡도

- **현상**: 한 컴포넌트에서 suggestions, events, characters, selectedIds, editingEvent, searchTerm, pagination 등 과다 상태 관리
- **권장**: 커스텀 훅(`usePrecedesSuggestions`, `usePrecedesSelection` 등)으로 분리

#### [LOW] API 파라미터 클라이언트 검증 부재

- **위치**: `precedesApi.ts`, `eventV2Api.ts`
- **현상**: `dramaId`, `limit`, `minScore` 등 범위/타입 검증 없이 바로 전송
- **권장**: 최소한 양수 검증 추가

---

## 4. Documentation Changes

- predicate 관련 스펙이 `fivecircles/architecture/specs/predicate/` 폴더로 체계적 정리
- reveals, group, promotion, aggregate, suggestion-sot-event 등 문서 추가
- ex14 정합성 체크리스트 및 intelligence 매핑 테이블 추가
- Q11/Q12 시맨틱 및 랭킹 문서 명확화

---

## 5. Action Items (우선순위)

| # | Area | Item | Severity | Effort |
|---|------|------|----------|--------|
| 1 | BE | `EventRevealMapper.findByEventIds()` 벌크 쿼리 추가 (N+1 해소) | HIGH | Low |
| 2 | BE | `updateEvent` summary/episode null-fallback 처리 | HIGH | Low |
| 3 | FE | `saveEdit()` 레이스 컨디션 방지 (버튼 비활성화) | HIGH | Low |
| 4 | FE | `as any` 제거, `SuggestionRow` 타입 확장 | HIGH | Low |
| 5 | BE | reveal targetType 필수 검증 또는 정책 문서화 | MEDIUM | Low |
| 6 | FE | `URL.createObjectURL` cleanup 추가 | MEDIUM | Low |
| 7 | FE | `alert()` -> `toast` 통일 | MEDIUM | Low |
| 8 | FE | 이미지 업로드 클라이언트 검증 | MEDIUM | Low |
| 9 | BE | aggregate 스코어 가중치 상수화 + 문서화 | MEDIUM | Low |
| 10 | BE | updateEvent event-not-found 테스트 추가 | MEDIUM | Low |
| 11 | 협의 | OAuth2 토큰 전달 방식 변경 (Team A) | CRITICAL | Medium |

---

## 6. Overall Assessment

| Category | Rating | Note |
|----------|--------|------|
| Feature Completeness | **Good** | Admin CRUD, aggregate, predicate 정규화 모두 구현 |
| Code Quality | **Fair** | N+1 쿼리, 타입 안전성 개선 필요 |
| Test Coverage | **Fair** | 핵심 suggestion 규칙은 커버, edge case 부족 |
| Documentation | **Good** | predicate 스펙 체계적 정리 |
| Security | **Needs Attention** | OAuth2 토큰 노출(Team A), 클라이언트 검증 부재 |
| Architecture | **Good** | 정규화 레이어, reveal 분리 저장 등 설계 양호 |

**Summary**: 기능 구현 품질은 높고, 특히 predicate 정규화 레이어와 suggestion 정책 테스트가 잘 설계됨. N+1 쿼리와 updateEvent 필드 null 처리가 가장 시급한 개선점. 대부분 항목이 난이도 낮으므로 머지 전 또는 다음 스프린트에서 빠르게 처리 가능.

---

## 7. Verification by codex-ops (2026-02-09)

> Note: 이 섹션은 **코드 확인(verification)** 기록이다. 이 문서 업데이트만 수행했으며, 별도 코드 수정/테스트 추가는 하지 않았다.

### Confirmed (Not Fixed Yet)
- [BE-HIGH] `getRevealMap()` N+1: **Confirmed** (event 목록 조회 시 `eventRevealMapper.findByEventId(eventId)` 반복 호출).  
  - 상태: 코드에 TODO로 명시되어 있으며, 현재는 loop 기반으로 1건씩 조회한다.  
  - Refs: `services/event-service/src/main/java/com/nospoiler/eventservice/service/EventServiceImpl.java`, `services/event-service/src/main/java/com/nospoiler/eventservice/service/EventQueryServiceImpl.java`

- [BE-HIGH] `updateEvent` summary/episode null 덮어쓰기 위험: **Confirmed**.  
  - 현상: `dramaId/sourceType/sourceId/predicateSuggestion/sourceStatus` 등 일부는 fallback이 있으나, `summary/episodeStart/episodeEnd`는 request 값을 그대로 사용한다.  
  - 영향: FE에서 `summary`만 보내는 업데이트가 `episodeStart/episodeEnd`를 null로 덮어쓸 수 있다.  
  - Refs: `services/event-service/src/main/java/com/nospoiler/eventservice/service/EventServiceImpl.java`

### Confirmed (Frontend)
- [FE-HIGH] `AdminPrecedesPage saveEdit()` 중복 요청(레이스) 가능: **Confirmed**.  
  - 현상: 저장 시 `status: 'SAVING'`으로 표시(spinner)하나, 저장 버튼이 disable되지 않아 더블클릭/연타 시 중복 호출 가능.  
  - Refs: `front/features/admin/AdminPrecedesPage.tsx`

- [FE-HIGH] `as any` 타입 캐스팅: **Confirmed** (`row as any`, `(row as any).fromSourceType` 등).  
  - Refs: `front/features/admin/AdminPrecedesPage.tsx`

### Confirmed (Team A / Out Of Scope For This Branch)
- [FE-CRITICAL] OAuth2 토큰이 URL query로 전달됨: **Confirmed** (`/oauth2/redirect?accessToken=...`).  
  - 추가 위험: redirect handler가 token을 `console.log`로 출력한다(로그/스크린샷 유출 위험).  
  - 조치: 이 브랜치에서는 구현/수정하지 않음(Team A 소관).  
  - Refs: `front/features/auth/OAuth2RedirectHandler.tsx`

### Policy Decisions Needed (Before Fixing)
- `updateEvent`는 PATCH-like로 볼지(= null은 "변경 없음"), PUT-like로 볼지(= null은 "삭제/초기화") 정책을 문서로 고정 필요.
- `event_reveal`이 1:N인 상황에서 API DTO가 1개만 담는다면, "대표 reveal 1개" 선택 규칙(정렬 기준)을 명시 필요.

### Remaining Test Gaps (Still True)
- updateEvent event-not-found 케이스 테스트 미커버
- createEvent REVEALS 저장 테스트 미커버
- aggregate 엔드포인트 단위/통합 테스트 미커버

---

## 8. Addendum (Re-Review Notes by codex-ops, 2026-02-09)

### Corrections To This Review Doc
- **OAuth2 token in URL params**: issue is real, but **not specific to this branch**. `origin/develop` already has the same pattern in `front/features/auth/OAuth2RedirectHandler.tsx`. Treat as a cross-team security issue (Team A coordination), not a branch-local regression.
- **N+1 scope**: `getRevealMap()` N+1 is present in **both**:
  - `services/event-service/src/main/java/com/nospoiler/eventservice/service/EventServiceImpl.java`
  - `services/event-service/src/main/java/com/nospoiler/eventservice/service/EventQueryServiceImpl.java`

### New / Stronger Findings (Based On Current Code)
- **[BE-CRITICAL] `updateEvent` + FE inline edit = data loss risk is immediate**:
  - FE calls `eventV2Api.updateEvent(eventId, { summary: newValue })` from `front/features/admin/AdminPrecedesPage.tsx`.
  - BE `updateEvent` currently writes `summary/episodeStart/episodeEnd` directly from request without fallback.
  - Result: a summary-only update can null out `episodeStart/episodeEnd` in DB (not theoretical).
- **[BE-HIGH] `EventMapper.findById` filters `source_status = 'APPROVED'`**:
  - `updateEvent` calls `eventMapper.findById(id)`, so non-APPROVED events will be treated as "not found".
  - If admin workflows need editing pending/draft events, this is a contract/mapper problem (either add an admin findById, or remove the status filter for update paths).
  - Policy decision (2026-02-09):
    - approved만 온톨로지 레이어를 타는 데이터로 취급하는 것이 우리 정책이므로 **현 동작은 의도된 정책**
    - pending 데이터까지 다루려면 별도 관리 흐름으로 분리해야 함
    - 지금은 필요 없으므로 정책으로만 표시하고 필요해지면 구현한다 (no code change)
- **[FE-MEDIUM] `URL.createObjectURL` leak exists in more than one admin page**:
  - `front/features/admin/AdminCharacterPage.tsx`
  - `front/features/admin/AdminDramaPage.tsx`
  - Both set preview URLs without `URL.revokeObjectURL()` cleanup.
- **[Docs Gap] `api-contract.md` is missing the update endpoint**:
  - Implementation exposes `PUT /api/event/v1/{id}` (see `services/event-service/src/main/java/com/nospoiler/eventservice/controller/EventController.java`), but `fivecircles/architecture/specs/api-contract.md` does not list it.
- **[Semantics Gap] PUT vs PATCH**:
  - Current usage is PATCH-like (partial payload), but endpoint is PUT and mapper update overwrites all columns.
  - Either enforce full payload from FE or change contract/implementation to PATCH semantics.

### Post-Fix Review Notes (2026-02-09)
- [BE] 대표 reveal 1개 선택은 비결정적(first row)보다 결정적(rule/ORDER BY)인 편이 낫다. 현재는 `findByEventIds` 정렬 + `putIfAbsent`로 고정됨.
- [FE] AdminPrecedesPage의 dead code(`startEdit`) 제거 완료.
- [FE] QA 페이지의 `alert()` 제거: 실패 시 toast 사용으로 통일.
- [FE] Aggregate score 기준 UI는 서버 로직과 drift 위험이 있어, 서버가 score rule(가중치)을 내려주도록 개선하는 편이 안전(추가 작업 예정).

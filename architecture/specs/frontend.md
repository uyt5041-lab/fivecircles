# Frontend Specification

This document defines frontend routing, page responsibilities,
role-based visibility, and API usage rules.

## Event V2 API Endpoints (api1-10)

Base URL: /api/event/v2

- api1: GET /dramas/{dramaId}/events?safeUpToEpisode={K}&predicateCode={CODE}&fromEpisode={A}&toEpisode={B}&limit={N}
- api2: GET /dramas/{dramaId}/characters?safeUpToEpisode={K}&limit={N}&sort={sort}
- api3: GET /characters/{characterId}/events?safeUpToEpisode={K}&predicateCode={CODE}&limit={N}
- api4: GET /characters/{characterId}/coevents?with={bId}&safeUpToEpisode={K}
- api5: GET /events/{eventId}/characters?safeUpToEpisode={K}
- api6: GET /events/{eventId}/related?depth={D}&safeUpToEpisode={K}&types=PRECEDES,RELATED
- api7: GET /events/{eventId}/causes?depth={D}&safeUpToEpisode={K}
- api8: GET /events/{eventId}/effects?depth={D}&safeUpToEpisode={K}
- api9: GET /characters/{characterId}/related-characters?safeUpToEpisode={K}&limit={N}
- api10: GET /characters/path?from={A}&to={B}&maxDepth={D}&safeUpToEpisode={K}

## Event V2 Question Mapping (event-v2-definition.md)

Level 1
- Q1 (Character A timeline) -> api3
- Q2 (Characters A and B co-appearance) -> api4
- Q3 (Character C events by type) -> api3 + predicateCode
- Q4 (Characters in event) -> api5
- Q5 (Events by type) -> api1 + predicateCode

Level 2
- Q6 (Character A affiliation change events) -> api3 + predicateCode=AFFILIATION_CHANGE
- Q7 (Character A death/exit events) -> api3 + predicateCode=DEATH or EXIT
- Q8 (Compare same-type events) -> api1 + predicateCode per type, compare on FE
- Q9 (Events within episode range) -> api1 + fromEpisode/toEpisode
- Q10 (Event category) -> api1 or api3 response predicateCode

Level 3
- Q11 (Prior causes of event) -> api7
- Q12 (Derived effects after event) -> api8
- Q13 (Path A -> event X -> B) -> api10 (verify event X in path)
- Q14 (Characters related to A) -> api9
- Q15 (Events indirectly caused by A) -> api3 then api8 per eventId (or api6 with PRECEDES)

## Page Placement (Current FE Routes)

Routes (HashRouter)
- /#/ : Drama selection
- /#/select-episode : Episode selection
- /#/dashboard : Character list + modal
- /#/timeline : Event timeline
- /#/qa : Q&A
- /#/wiki : Wiki submit
- /#/wiki/reviews : Wiki reviews
- /#/login, /#/signup : Auth

Page -> Questions

**/#/dashboard**
- Q1 (Character A timeline): character modal timeline tab
- Q2 (A and B co-appearance): co-appearance section
- Q3 (Character C events by type): predicateCode filter
- Q6 (Affiliation change events): predicateCode=AFFILIATION_CHANGE
- Q7 (Death/exit events): predicateCode=DEATH/EXIT
- Q13 (Path A -> event X -> B): relation/path tab
- Q14 (Characters related to A): related characters section
- Q15 (Events indirectly caused by A): impact chain section

**/#/timeline**
- Q4 (Characters in event): event detail panel
- Q5 (Events by type): predicate filter
- Q8 (Compare same-type events): compare view per predicate
- Q9 (Events within episode range): from/to filters
- Q10 (Event category): event detail shows predicateCode
- Q11 (Prior causes of event): causes tab
- Q12 (Derived effects after event): effects tab

## QA Drawer Widget Mapping (Experimental)
*Used in /#/qa playground and /#/timeline event detail.*
- Q1_CharacterTrace: api3 (character events) - Character context
- Q2_EventSearch: api1 (drama events search) - Dashboard/Timeline context
- Q3_RelatedCharacters: api9 (related characters) - Character context
- Q5_CoEvents: api4 (co-events) - Character context
- Q7_EventCauses: api7 (event causes) - Timeline context (requires eventId)
- Q9_EventEffects: api8 (event effects) - Timeline context (requires eventId)
- Q11_CharacterPath: api10 (character path) - Character context
- Q13_SpoilerCheck: policy check-text (assumed /api/policy/v1/check-text)
- Q20_NarrativeDistribution: api3 (character events stats) - Character context

Note: QA drawer numbering is currently a UI label for testing and does not match
the spec numbering (e.g., Q3 widget maps to api9/related-characters). Use the
above list as the source of truth for QA drawer tests.

## Widget Test Entry Points (UI)
- /#/qa → V2.5 QA Playground → Global Context: Q2 (search)
- /#/qa → V2.5 QA Playground → Character Context: Q1, Q3, Q5, Q11, Q20
- /#/dashboard → 상단 AI 검색: Q2 (global)
- /#/dashboard → 인물 모달 AI 질문: Q1, Q3, Q5, Q11, Q20 (character)
- /#/timeline → 사건 상세 패널 → AI 분석: Q2, Q7, Q9, Q13 (eventId 제공)

## 페이지 배치 (한글 버전)

현재 라우트 요약 (HashRouter)
- /#/ : 드라마 선택
- /#/select-episode : 에피소드 선택
- /#/dashboard : 인물 목록 + 상세 모달
- /#/timeline : 사건 타임라인
- /#/qa : Q&A
- /#/wiki : 위키 제보
- /#/wiki/reviews : 위키 검수
- /#/login, /#/signup : 로그인/가입

페이지 -> 질문 (사람이 보는 기준)

**/#/dashboard**
- Q1 인물 A 타임라인: 인물 상세 모달의 **타임라인 탭**
- Q2 인물 A·B 공동 등장 사건: 인물 상세 모달의 **공동 등장 섹션**
- Q3 인물 C 사건 유형 필터: **predicateCode 필터**
- Q6 인물 소속 변경 사건: **predicateCode=AFFILIATION_CHANGE**
- Q7 인물 사망/퇴장 사건: **predicateCode=DEATH/EXIT**
- Q13 A -> 사건 X -> B 경로: **관계/경로 탭**
- Q14 인물 A 관련 인물: **연관 인물 섹션**
- Q15 인물 A가 원인인 사건 연쇄: **영향 체인 섹션**

**/#/timeline**
- Q4 사건 등장 인물: **사건 상세 패널**
- Q5 사건 유형별 모아보기: **유형 필터**
- Q8 같은 유형 사건 비교: **유형별 비교 뷰**
- Q9 특정 회차 범위 사건: **from/to 필터**
- Q10 사건 카테고리: **사건 상세의 카테고리 배지**
- Q11 사건 원인(이전 사건): **원인 탭**
- Q12 사건 결과(이후 사건): **결과 탭**

## MVP 최단 구현 플랜 (frontend.md 기준)

목표
- Q1~Q15를 프론트에서 접근 가능하게 만들고, 각 질문은 최소한의 리스트/상세 결과를 노출한다.

원칙
- 새 라우트 추가 없이 **/#/dashboard**와 **/#/timeline** 중심으로 해결한다.
- 그래프/고급 시각화는 제외하고 리스트와 배지로 먼저 구현한다.
- 탭 클릭 시에만 API 호출(지연 로딩)로 초기 속도 확보.

구현 단계
1) API 연결 최소화
   - /api/event/v2 전용 간단 클라이언트 추가.
   - 공통 파라미터 safeUpToEpisode, limit를 기본 처리.

2) **/#/dashboard** (Q1, Q2, Q3, Q6, Q7, Q13, Q14, Q15)
   - 인물 상세 모달에 탭/섹션 추가.
   - 타임라인(Q1): api3.
   - 공동 등장(Q2): api4.
   - 유형 필터(Q3, Q6, Q7): api3 + predicateCode.
   - 연관 인물(Q14): api9.
   - 경로(Q13): api10, 입력은 대상 인물 선택/ID로 단순화.
   - 영향 체인(Q15): api3로 사건 목록 -> api8로 파생 사건 묶기.

3) **/#/timeline** (Q4, Q5, Q8, Q9, Q10, Q11, Q12)
   - 필터 바 추가: predicateCode, from/to episode.
   - 사건 상세 패널: 캐릭터(api5), 카테고리 표시(Q10).
   - 원인/결과 탭: api7/api8.
   - 비교(Q8): predicateCode 2개 선택 -> api1 결과 수/리스트 비교표.

4) QA 대안 (선택)
   - Q2/Q8/Q13을 /#/qa로 이동해 자연어 질의로 처리 가능.
   - 기존 페이지에는 “QA에서 보기” CTA만 남김.

완료 기준
- 각 질문에 대응하는 UI 진입점이 존재하고, 호출 결과가 리스트로 표시된다.
- 빈 상태/에러 상태만 처리하고, 시각적 완성도는 후순위로 둔다.

## QA 기반 대안 배치 (선택)

질문 입력형 경험을 강조하고 싶다면 Q2, Q8, Q13을 /#/qa로 이동해도 자연스럽다.

**/#/qa**
- Q2 인물 A·B 공동 등장 사건: 자연어 질의 -> **공동 등장 사건 리스트**
- Q8 같은 유형 사건 비교: 자연어 질의 -> **비교 요약 + 표**
- Q13 A -> 사건 X -> B 경로: 자연어 질의 -> **경로/그래프 응답**

QA 대안 적용 시 축소/정리 제안

**/#/dashboard**
- Q2 공동 등장 섹션: **요약 카드** + "**QA에서 상세보기**" 링크로 축소
- Q13 관계/경로 탭: 숨김 또는 "**QA에서 탐색**" 버튼만 유지

**/#/timeline**
- Q8 비교 뷰: 탭 제거, 상단에 "**QA 비교**" CTA만 노출

## MVP 재귀 구현 플로우 (에이전트 공유용)

진행 현황
- /#/dashboard: **[완료]** 인물 목록 실제 API 연동 (`characterApi` + `eventV2Api`). V2 탭(타임라인, 공동등장, 경로 등) 기능 구현 완료.
- /#/timeline: **[완료]** 실제 V2 API 기반 타임라인 조회, 필터링, 비교 뷰 구현 완료. 인물 이름 매핑 실제 API 연동 완료.
- /#/wiki: 현재 `mockWikiApi` 사용 중. 실제 백엔드 연동(`wiki-service`) 대기 중.

재귀 실행 규칙
- 페이지 단위 mini-plan -> 구현 -> 서버/Playwright 검증 -> update.md 로그 -> 커밋.
- 오류 발생 시 원인 조사 후 사용자와 논의, 동일 스텝 재실행.

기술 메모 (현 상태 기준)
- Event V2 클라이언트: `front/common/services/eventV2Api.ts` (api1~api10 매핑)
- Character 클라이언트: `front/common/services/characterApi.ts` (인물 메타데이터 조회)
- safeUpToEpisode: `currentEpisode`를 그대로 전달 (dashboard/timeline 모두 동일)
- devAuth 로그인: `/#/login?devAuth=1`에서 1/1, 2/2 버튼 제공 (User ID 확보용)

다음 작업 (우선순위)
1) **Wiki Service Input Part (Priority: High)**
   - 목표: `mockWikiApi` 제거 및 실제 `/api/wiki/v1/submissions` 연동
   - **Step 1: API Client 생성**
     - `front/common/services/wikiApi.ts` 생성
     - 백엔드 DTO(`SubmissionRequest`) 스펙 준수
   - **Step 2: User ID 매핑**
     - 로그인 직후 `GET /api/user/v1/me` 호출하여 numeric `userId` 확보
     - `UserProfile` 타입 내 `id` 필드가 실제 Long ID 문자열인지 확인
   - **Step 3: Page Integration**
     - `WikiPage.tsx`: `submitFact` 호출 시 `authorId`에 실제 user ID 전달. `dramaId`/`characterId`는 `toNumericId`로 변환.
     - `WikiReviewPage.tsx`: `getAllSubmissions` 호출 시 실제 API 사용.
   - **Step 4: 검증**
     - `/login?devAuth=1`로 로그인 -> 위키 제출 -> `/wiki/reviews` 목록 확인 (Round Trip Test)

2) UI Polishing (Low Priority)
   - /#/dashboard: 영향 체인(api8) 결과의 가독성 개선 (현재 raw event list)
   - /#/timeline: 검색 결과 없을 때의 안내 메시지 강화

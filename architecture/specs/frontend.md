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

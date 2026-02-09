# ex16 Production Q1~Q15 구현 현황 (V2.5 기준)

기준 날짜: 2026-02-09  
대상 질문 원문: `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex16-production-Q15s.md`

## 결론(요약)
- **V2.5의 “질의 프리미티브(api1~api10)”는 구현 완료**라서, Q1~Q15를 실행시키기 위한 기반은 갖춰져 있다.
  - 구현: `services/event-service/src/main/java/com/nospoiler/eventservice/controller/EventQueryController.java`
  - 정렬(“최초” 질문 지원): `ORDER BY episode_start ASC` + `LIMIT` (예: `findByCharacterId`)  
    구현: `services/event-service/src/main/resources/mapper/event/EventMapper.xml`
- 하지만 **Q1~Q15를 “프리셋/라우터”로 실행하는 기능(버튼 1개로 실행)은 아직 없다.**
  - 현재 FE는 “탐색 UI(필터/상세/QA Drawer)” 중심이다: `front/features/timeline/EventTimelinePage.tsx`, `front/features/event/components/EventQADrawer.tsx`
- 또한 Q1~Q15 중 다수는 **폐쇄집합 PredicateCode에 직접 대응하는 코드가 부족**해서, “PredicateGroup + OTHER/suggestion 축적”이 필요하다.
  - 폐쇄집합: `common/src/main/java/com/nospoiler/common/PredicateCode.java`
  - 라우팅 초안(스펙): `fivecircles/architecture/specs/predicate/ex16-q1-q15-구현-라우팅-시범용.md`

## 구현 프리미티브(완료)
- api1: 드라마 이벤트 검색/필터 (`/dramas/{dramaId}/events`)
- api3: 캐릭터 이벤트 타임라인 (`/characters/{characterId}/events`)
- api4: 공동 등장(coevents) (`/characters/{characterId}/coevents?with=...`)
- api5: 사건 등장인물 (`/events/{eventId}/characters`)
- api7/api8: PRECEDES 기반 원인/결과 BFS (`/events/{eventId}/causes`, `/events/{eventId}/effects`)
- api9: related-characters(공동 등장 기반) (`/characters/{characterId}/related-characters`)
- (추가) related-characters aggregate 단일 호출 집계(ADVERSARY/ALLY/COEVENTS)
  - `/characters/{characterId}/related-characters/aggregate`

## Q1~Q15 “현재 가능한 수준” 체크

판정 기준
- **READY(Manual)**: 현재 API/정렬/필터만으로 “수동 파라미터 입력”이면 답을 뽑을 수 있음(프리셋 UI/라우터는 없음).
- **PARTIAL**: api3/api4로 근사는 가능하나, PredicateCode 부족 또는 데이터 분류 부족으로 품질이 낮음.
- **NEEDS WORK**: 실행을 위한 최소 라우팅 규칙(그룹/후보추출/프리셋)이 추가로 필요.

| Q | 질문 | 1차 실행(권장) | 상태 | 갭/메모 |
| --- | --- | --- | --- | --- |
| 1 | 월터의 첫 살인? | api3 + `predicateCode=KILLS` + `limit=1` | READY(Manual) | “월터(characterId)”를 프리셋으로 해석/결정하는 레이어가 아직 없음 |
| 2 | 첫 암페타민 제조? | api3 + (해당 PredicateCode가 없으면 `OTHER` 기반) | NEEDS WORK | “제조/암페타민” 구조화 코드 부재. 데이터가 OTHER로 쌓이면 suggestion 기반 승격/그룹화 필요 |
| 3 | 투코를 처음 만나는 시점? | api4(coevents) earliest + `limit=1` | PARTIAL | `MEETS`가 있어도 coevents만으론 “처음 만남”을 항상 보장 못함(근사 규칙 필요) |
| 4 | 스카일러가 월터 범죄를 알아차림? | api3(Skyler) + `predicateCode=DISCOVERS/LEARNS` + earliest | PARTIAL | REVEALS 메타(event_reveal) 파이프라인이 완성되면 “근거”로 강화 가능 |
| 5 | 월터가 처음 ‘범죄’ 결심? | api3(Walter) + 그룹(전환/결심) | NEEDS WORK | 그룹 정의/정규화 필요(폐쇄집합만으로는 부족) |
| 6 | 월터-제시 파트너 계기? | api4(Walter,Jesse) earliest | PARTIAL | `ALLIES_WITH` 등으로 근사 가능하나 “파트너”를 보장하진 않음 |
| 7 | 월터가 처음 거짓말 들킴? | api3(Walter) + 그룹(발각/대면) | NEEDS WORK | 그룹 필요 + 데이터 보강 필요 |
| 8 | ‘명분(가족)’이 흔들리는 지점? | api3(Walter) + 그룹(관계/가치 균열) | NEEDS WORK | 그룹 필요(요약문 기반 라벨링 포함) |
| 9 | 행크가 수사 방향을 바꾸는 계기? | api3(Hank) + 그룹(단서/전환점) | NEEDS WORK | 그룹 필요 |
| 10 | 월터가 본격적 위협을 받는 순간? | api3(Walter) + `ATTACKS` 등 근사 | PARTIAL | “위협” 자체 코드 부재(THREATENED 등 없음). 그룹 필요 |
| 11 | 누가 월터를 의심하기 시작? | api3 후보(의심 이벤트) + api5로 주체 후보 붙이기 | NEEDS WORK | “누가” 추출 규칙이 필요(스펙 약점) |
| 12 | 월터가 처음 통제권을 쥠? | api3(Walter) + 그룹(주도권) | NEEDS WORK | 그룹 필요 |
| 13 | 월터가 돈의 흐름을 만들기 시작? | api3(Walter) + 그룹(거래/수익) | NEEDS WORK | 그룹 필요 |
| 14 | 스카일러-월터 관계 첫 균열? | api4(Walter,Skyler) + `BETRAYS` 등 근사 | PARTIAL | 관계 “균열” 일반형 코드는 없음. 그룹 필요 |
| 15 | 은폐/도주 시작? | api3(Walter) + `ESCAPES` 근사 | PARTIAL | “은폐/증거인멸” 코드 부재. 그룹 필요 |

## 다음 구현(최소) 제안
- **프리셋 실행 레이어 추가**: “Production Q1~Q15”를 `QuerySpec`으로 고정하고, FE/QA 중 한 곳에서 버튼 1개로 api3/api4/api7/api8를 조합 호출.
  - 프리셋에서 반드시 필요한 것:
    - (A) 인물 식별(Walter/Skyler/Hank/Tuco/Jesse)을 **characterId로 해석**하는 규칙(이름 매칭 or 별도 매핑 테이블)
    - (B) PredicateGroup 정의 및 “OTHER + predicate_suggestion” 축적/승격 흐름
- **현실적 1차 범위**: Q1/Q3/Q4만 “READY 품질”로 먼저 프리셋화(폐쇄집합 기반), 나머지는 그룹 정의가 끝난 뒤 단계적 확장.


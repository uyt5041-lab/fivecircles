# Q1 익스펜션 재귀 실행 로그 (Cycle 1)

기준 문서
- `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/specs/questions-anti-halus/09-expension-questions.md`
- `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/specs/questions-anti-halus/06-answers-for-productionQs.md`

실행일
- 2026-02-25

## 재귀 실행 루프 (Q1 후속 6문항 공통)

1. 질문별 웹 근거 확인(정답 맥락 서술의 사실축 고정)
2. DB 앵커 이벤트 후보(`evidence_event_id`) 확정
3. 현재 `event_relation(PRECEDES)` 갭 점검
4. 기존 이벤트 기준 relation만 우선 시딩(없는 것만)
5. Query-only 재실행으로 hop 노출 확인
6. `READY` / `SEED_NEEDED` 판정 후 다음 cycle로 이월

## Cycle 1 실행 결과 (Q1-1 ~ Q1-6)

| 문항 | 앵커/도미노(현재) | 상태 | 비고 |
|---|---|---|---|
| Q1-1 첫 살인 직후 자기정당화 | `2292 -> 2293 -> 2294` | READY | `2292->2293`, `2293->2294` 시딩 반영 |
| Q1-2 폭력 적응의 첫 징후 | `2375 -> 2376 -> 2435 -> 3019` | READY | 기존 선형 체인 유지 |
| Q1-3 전략적 살인 단계로 미는 외부압력 | `2297 -> 2372 -> 2306 -> 2375 -> 2376 -> 2435 -> 3019 -> 2307 -> 2311 -> 3031 -> 3032` | READY | Cycle2에서 S3 strategic-kill 이벤트/연결 반영 |
| Q1-4 살인을 선택지로 계산한 첫 순간 | `2291 -> 2409 -> 2410 -> 2292` | READY | 기존 Q1 체인으로 커버 |
| Q1-5 2차 파장(제시/스카일러/행크) | `2292 -> 2322`, `2292 -> 2345`, `2292 -> 2297` | READY | 3방향 분기 relation 시딩 반영 |
| Q1-6 전환점 3개 트리거 요약 | `2292`, `2435(또는 3019)`, `3031(또는 3032)` | READY | 3번째 트리거(S3) 시드 완료 |

## Cycle 1 실제 시딩

적용 파일
- `/Users/pio/IdeaProjects/nospoiler/scripts/ops/seed_q1_expansion_cycle1_relations.sql`

반영된 relation
- `2292 -> 2293`
- `2293 -> 2294`
- `2372 -> 2306`
- `2292 -> 2322`
- `2292 -> 2345`
- `2292 -> 2297`

검증 쿼리 결과(핵심)
- `2292` 기준 outgoing PRECEDES가 생성되어 후속 hop이 열린 상태
- RDF query-only PoC 재실행 결과 `effectIdsNearestFirst = [2293, 2294, 2295]`

## 웹 근거(요약)

- S1E3 `...And the Bag's in the River`: 월터가 Krazy-8 처리 여부를 계산하고 결국 살해까지 가는 축. [Wikipedia](https://en.wikipedia.org/wiki/...And_the_Bag%27s_in_the_River)
- S1E5 `Gray Matter`: 합법적 출구(치료비 지원) 거절로 범죄 경로를 고정하는 분기. [Wikipedia](https://en.wikipedia.org/wiki/Gray_Matter_(Breaking_Bad))
- S1E6 `Crazy Handful of Nothin'`: 투코 앞 폭발 시연으로 폭력을 협상 도구로 전환. [Wikipedia](https://en.wikipedia.org/wiki/Crazy_Handful_of_Nothin%27)
- S3E12 `Half Measures`: 제시 보호를 위해 월터가 차량 돌진+사살을 수행(전략적 살인 단계). [Wikipedia](https://en.wikipedia.org/wiki/Half_Measures)
- S3E13 `Full Measure`: 생존을 위해 게일 제거 결정을 실행(전략적 제거 고착). [Wikipedia](https://en.wikipedia.org/wiki/Full_Measure)

## Cycle 2 이월 항목

1. S3 구간 신규 이벤트 시드
- 후보 A(absolute 32): 월터가 거리의 두 딜러를 차량으로 치고 사살해 제시를 보호함
- 후보 B(absolute 33): 월터가 자신/제시 생존을 위해 게일 제거를 지시함

2. 신규 이벤트 연결
- `2307 -> [A] -> [B]`로 PRECEDES 연결
- `event_character`에 Walter/Jesse/Gus/Mike(필요 시) 연결

3. 실행 레이어 고정
- Story Reminder용 Q1-1~Q1-6 템플릿 또는 SPARQL 그룹을 분리 정의
- K gate 절대회차 정책으로 `SPOILER_BLOCKED` 동작 재검증

## Cycle 2 실행 결과 (2026-02-25)

적용 파일
- `/Users/pio/IdeaProjects/nospoiler/scripts/ops/seed_q1_expansion_cycle2_s3_events.sql`

신규 이벤트(없는 경우만 생성)
- `3031` (absolute 32): 월터가 두 딜러를 차량으로 치고 사살
- `3032` (absolute 33): 월터가 게일 제거를 지시

신규/보강 relation
- `2294 -> 2297`
- `2295 -> 2297`
- `2311 -> 3031`
- `3031 -> 3032`

검증 결과
- RDF export 성공 (`events=1279`, `precedes=786`)
- Q1 Query-only (`safeUpToEpisode=33`, `maxChainDepth=30`)에서 후속 hop이 `3032`까지 도달
  - `effectIdsNearestFirst = [2293,2294,2295,2297,2372,2306,2375,2376,2435,2307,2311,3031,3032]`

상태 갱신
- Q1-3 전략적 살인 단계: `READY`
- Q1-6 전환점 3개 트리거: `READY` (`2292`, `2435/3019`, `3031/3032`)

## Cycle 3 실행 결과 (2026-02-25, 실행 레이어 고정 + K gate 회귀)

### 1) Story Reminder 템플릿 고정

적용 파일
- `/Users/pio/IdeaProjects/nospoiler/front/common/productionQ/templates.ts`

추가된 템플릿 ID
- `BB_Q1_EXP_01_SELF_JUSTIFICATION`
- `BB_Q1_EXP_02_VIOLENCE_ADAPTATION_SIGN`
- `BB_Q1_EXP_03_EXTERNAL_PRESSURE`
- `BB_Q1_EXP_04_FIRST_CALCULATED_KILL_CHOICE`
- `BB_Q1_EXP_05_SECONDARY_RIPPLES`
- `BB_Q1_EXP_06_THREE_TURNING_TRIGGERS`

실행 정책
- queryKind는 모두 `character_predicate_earliest`로 고정
- strict-first 유지 (`strict 0건이면 probe/게이트 판정`)
- 컨텍스트는 기존 양방향(`causes+effects`) 그대로 사용

### 2) K gate 회귀 검증

검증 스크립트
- `/Users/pio/IdeaProjects/nospoiler/fivecircles/test/validate-q1-expansion-gate.py`
- 방식: DB truth(`strict safe` vs `strict any`)로 tri-state를 계산해 probe 의존 없이 회귀 확인

검증 결과
- `ANSWERED`: Q1E1, Q1E2, Q1E3, Q1E4, Q1E5, Q1E6@K33
- `SPOILER_BLOCKED`: Q1E6@K6
- `NOT_ENOUGH_DATA`: `CONTROL_NO_DATA` (무매치 토큰)

### 3) 빌드 확인

- `front npm run build` 통과

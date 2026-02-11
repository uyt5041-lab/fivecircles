# Production Q1~Q15: Required DB Values (from 06 answers)

관련 문서
- 정답 기준: `fivecircles/architecture/specs/questions-anti-halus/06-answers-for-productionQs.md`
- 실행 필터 기준: `fivecircles/architecture/specs/questions-anti-halus/04-template-strict-must-matrix.md`
- 실행 순서 기준: `fivecircles/architecture/specs/questions-anti-halus/03-implementation-plan.md`

목적
- `evidence_event_id`를 채우기 전에, Q1~Q15가 `ANSWERED`가 되기 위해 DB에 반드시 존재해야 하는 값을 고정한다.
- 본 문서는 “정답 문장(06)”을 “검증 가능한 DB 조건”으로 변환한 최소 체크리스트다.

---

## 공통 필수 조건 (모든 Q에 적용)

- `event.drama_id = 10` (Breaking Bad)
- `event.source_status = 'APPROVED'`
- 질문별 strict 필터를 만족하는 이벤트가 최소 1건 존재
- strict-first 기준에서 earliest 이벤트를 고를 수 있도록 `episode_start`, `episode_end`, `id`가 정상 값
- 관계 질문(Q3,Q6,Q14)은 해당 이벤트에 필요한 `event_character` 조합이 존재
- `evidence_event_id`는 최종적으로 NOT NULL로 채워야 함 (현재는 문서상 TBD 허용)

---

## Q별 필수 DB 존재값

| question_id | question_text | canonical_episode | DB에 반드시 존재해야 하는 strict 조건 |
|---|---|---|---|
| Q01 | 월터의 첫 살인은 언제지 | S1E3 | `subject=Walter` + `predicateCode=KILLS`를 만족하는 earliest 이벤트 |
| Q02 | 월터가 암페타민 제조시작한게 언제지? | S1E1 | `subject=Walter` + `qAnyOf(meth/메스/암페타민/PRODUCTION)`를 만족하는 earliest 이벤트 |
| Q03 | 투코를 처음 만나는 시점은 언제야? | S1E6 | `with=[Walter,Tuco]` + `predicateCode=MEETS` earliest coevent |
| Q04 | 스카일러가 남편의 범죄사실을 알아차린 시점이언제냐? | S3E2 | `subject=Skyler` + `predicateCode in [DISCOVERS,LEARNS]` + `qAnyOf(마약/제조)` |
| Q05 | 월터가 처음 ‘범죄’ 결심한 순간? | S1E1 | `subject=Walter` + `predicateCode in [LEARNS,DISCOVERS]` + 결심/동업/제조시작 의미 키워드 |
| Q06 | 월터와 제시가 처음 파트너가 된 계기? | S1E1 | `with=[Walter,Jesse]` + `predicateCode in [ALLIES_WITH,JOINS,MEETS]` earliest coevent |
| Q07 | 월터가 처음 거짓말을 들키는 순간? | S1E2 | `subject=Walter` + `predicateCode in [DISCOVERS,LEARNS]` + `qAnyOf(거짓말/휴대폰/실종)` |
| Q08 | 월터의 ‘가족 명분’이 처음 흔들리는 지점? | S1E5 | `subject=Walter` + `qAnyOf(가족/치료비/지원 거절/명분)` earliest 이벤트 |
| Q09 | 행크가 수사 방향을 크게 바꾸는 계기? | S1E4 | `subject=Hank` + `predicateCode in [DISCOVERS,LEARNS]` + `qAnyOf(고순도/단서)` |
| Q10 | 월터가 처음 본격적인 조직적 위협을 받는 순간? | S1E6~7 | `subject=Walter` + `predicateCode in [ATTACKS,CAPTURES,BETRAYS,KILLS]` + `exclude=[DISCOVERS,LEARNS]` |
| Q11 | 누가 월터를 의심하기 시작한 최초 시점? | S1E2 | `targetCharacterId=Walter` 의미를 만족하는 earliest 이벤트 |
| Q12 | 월터가 처음 통제권을 쥐는 순간? | S1E6 | `subject=Walter` + `predicateCode in [ATTACKS,DEFEATS]` + `qAnyOf(폭발/협상/통제권)` |
| Q13 | 월터가 처음 돈의 흐름을 만들기 시작한 사건? | S1E7 | `subject=Walter` + 수익/공급/계약 키워드 + `excludePredicateCodeAnyOf=[OTHER]` |
| Q14 | 스카일러-월터 관계가 돌이키기 어려워지는 첫 균열? | S2E13 | `with=[Walter,Skyler]` + `predicateCode in [BETRAYS,LEARNS,DISCOVERS]` |
| Q15 | 월터가 본격적으로 은폐/도주를 시작하는 최초 지점? | S1E2 | `subject=Walter` + `predicateCode in [LEARNS,DISCOVERS]` + `qAnyOf(시신 처리/증거 은폐/알리바이/도주)` |

---

## evidence_event_id 채움 규칙 (실행용)

- 각 Q는 위 strict 조건을 만족하는 earliest 이벤트 1건을 `evidence_event_id`로 기록한다.
- `canonical_episode`와 `evidence_event_id`가 충돌하면, 먼저 데이터(이벤트 라벨/에피소드)를 정정하고 문서를 업데이트한다.
- `evidence_event_id`를 채운 후에는 `04-template-strict-must-matrix.md`의 `TBD`를 실제 ID로 교체한다.

### 2026-02-11 채움 결과 (strict + 06 앵커 검증)

- 채움 완료
  - `Q01` -> `2292` (`KILLS`, S1E3)
  - `Q02` -> `2285` (`암페타민 제조 시작`, S1E1)
  - `Q03` -> `2450` (`폭발 기반 첫 대면 앵커`, S1E6)
  - `Q05` -> `2283` (`범죄 진입 계기`, S1E1)
  - `Q06` -> `2448` (`Walter-Jesse 첫 동업`, S1E1)
  - `Q08` -> `2428` (`치료비 전액 지원 제안`, S1E5)
  - `Q09` -> `2369` (`고순도 메스 추적 전환`, S1E4)
  - `Q10` -> `2306` (`조직적 위협 시작`, S1E6)
  - `Q12` -> `2450` (`폭발로 통제권 전환`, S1E6)
  - `Q15` -> `2289` (`시신 처리/용해 시작`, S1E2)
- 미채움(`TBD` 유지)
  - `Q04,Q07,Q11,Q13,Q14`
  - 사유: strict 0건 또는 의미 신뢰도 부족(질문 의미 대비 이벤트 근거 약함)

### 미채움 Q 상세 진단 (strict 0건/불일치 분해)

| question_id | 상태 | 관찰 | 분류 | 다음 조치 |
|---|---|---|---|---|
| Q03 | 채움 완료 | `MEETS` 부재이지만 Walter-Tuco + `폭발` 앵커로 `2450(S1E6)` 확정 | predicate 미정렬 보정 | 추후 `MEETS` 데이터 보강 시 strict 재상향 |
| Q04 | strict 0건 | `DISCOVERS/LEARNS`는 존재하나 `범죄/마약` 키워드 동시 만족 이벤트 없음 | 토큰 과엄격 + 의미 미매핑 | crime-awareness 동치 토큰셋 보강 또는 `about/target` 신호 추가 |
| Q05 | 채움 완료 | `DEA/단속/도주/제시` 보강 후 `2283(S1E1)` 확정 | 토큰 보강 완료 | 유지 |
| Q07 | strict 0건 | predicate만 완화 시 generic `DISCOVERS`, keyword만 완화 시 `OTHER` 추궁 이벤트 | predicate/keyword 분리 저장 | 거짓말/들킴 전용 predicate 또는 동치 키워드 보강 |
| Q08 | 채움 완료 | `RECOVERS + Elliott/전액지원`으로 `2428(S1E5)` 확정 | canonical 정합 완료 | 유지 |
| Q09 | 채움 완료 | `TRANSFORMS + 고순도`로 `2369(S1E4)` 확정 | canonical 정합 완료 | 유지 |
| Q11 | strict hit(보류) | `2385(S1E2)` hit는 있으나 “마리 경유 불안 전달” 사건으로 질문 의미(최초 의심자=스카일러)와 거리 존재 | 의미 신뢰도 부족 | `target=Walter` + `subject=Skyler` 직접성 신호를 추가해야 evidence 확정 가능 |
| Q12 | 채움 완료 | `target=Tuco + 폭발`로 `2450(S1E6)` 확정 | 의미 분산 해소 | Q10과 동일 evidence 공유 허용 |
| Q13 | strict 0건 | keyword+exclude(OTHER) 모두 0건 | 데이터 공백 | 수익/계약 이벤트의 predicate 정규화 또는 데이터 보강 필요 |
| Q14 | strict 0건 | Walter-Skyler coevent는 있으나 지정 predicate/keyword 불일치 | coevents 의미 미정렬 | 관계 균열 이벤트의 predicate 라벨링 보강 필요 |
| Q15 | 채움 완료 | `산성 용액/용해/시신 처리`로 `2289(S1E2)` 확정 | canonical 정합 완료 | 유지 |

분류 요약
- 미채움 strict 0건/의미불충분: `Q04,Q07,Q11,Q13,Q14`
- 채움 완료(정합): `Q01,Q02,Q03,Q05,Q06,Q08,Q09,Q10,Q12,Q15`

### 다음 실행 순서 (재귀 구현 다음 단계)

1. strict 0건 해소 트랙
- 대상: `Q04,Q07,Q13,Q14`
- 방법: 템플릿 토큰 보강이 아니라 데이터 라벨/관계 보강(`event_character`, predicate 정규화) 중심으로 처리
- 완료 기준: strict 1건 이상 + 06 정답 회차와 충돌 없음

2. 의미 신뢰도 보강 트랙
- 대상: `Q11`
- 방법: `target=Walter`에 더해 “의심 주체가 Skyler”를 강제할 직접성 필터(문장/관계 신호) 추가
- 완료 기준: “Skyler가 Walter를 의심” 의미를 직접 만족하는 evidence 1건 확정

---

## FactGrid 해석 (주석)

```sparql
# 본 문서는 질문별로 “ASK가 true가 되어야 하는 최소 조건”을 고정한다.
# 이후 evidence_event_id는 strict SELECT(earliest) 결과를 저장하는 단계다.
```

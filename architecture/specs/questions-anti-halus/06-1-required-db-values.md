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

### 2026-02-11 1차 채움 결과 (strict 실행 기준)

- 채움 완료
  - `Q01` -> `2292` (`KILLS`, S1E3)
  - `Q02` -> `2285` (`qAnyOf=암페타민/메스...`, S1E1)
  - `Q06` -> `2448` (`with=[Walter,Jesse]`, `MEETS`, S1E1)
  - `Q10` -> `2306` (`ATTACKS`, S1E6)
- 미채움(`TBD` 유지)
  - `Q03,Q04,Q05,Q07,Q08,Q09,Q11,Q12,Q13,Q14,Q15`
  - 사유: strict 조건 0건 또는 canonical_episode와 strict earliest 결과 불일치(질문 의미/토큰/데이터 보강 필요)

---

## FactGrid 해석 (주석)

```sparql
# 본 문서는 질문별로 “ASK가 true가 되어야 하는 최소 조건”을 고정한다.
# 이후 evidence_event_id는 strict SELECT(earliest) 결과를 저장하는 단계다.
```

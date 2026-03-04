# Extension100 3축 분류 + 4축 리마인더 UI 실행안 (2026-02-26)

## 1) 대화 기준 고정안
- 사용자 제안 분류(100문항):
  - B축(REVEALS/ATTRIBUTE): 52
  - C축(predicate_code): 29
  - A축(event list/order): 19
- 합의한 구현 방향:
  - 리마인더는 PRECEDES-only에서 벗어나 **4축(AXIS/SPO/AND/WHY)**을 커버하는 UI로 전환한다.
  - 질문 템플릿이 만든 strict query 조합을 기반으로 결과를 보여준다.
  - PRECEDES는 정답 선정 기준이 아니라, 연결/맥락 보조 레이어로 제한한다.

## 2) 현재 상태 요약
- 구현 완료:
  - ex22.2 `T01~T10` 템플릿 추가
  - 시험용 리마인더 페이지(`/qa-story-reminder-test`) 추가
  - 시험 페이지에서 ex22.2/ex22.3 세트 전환 모드 추가
  - ex22.3 `Q01_EXP_01~06` 템플릿을 `extension-6of100-q1.md` 기준으로 재정렬
  - 상속 정책을 `specs/rdf/policy`로 분리 고정
- 확인된 갭:
  - 일부 확장 질문은 strict `qAnyOf`가 DB 텍스트와 어긋나 `NOT_ENOUGH_DATA`가 발생 가능
  - 현 UI는 selected + PRECEDES 타임라인 중심이라 REVEALS/ATTRIBUTE 축 표현력이 부족
  - 상속은 정의됐지만 `question_id -> required_set` SoT 파일과 closure taxonomy SoT 파일이 없어서 실행 경로가 분리됨

## 3) 실행 규칙 (A/B/C 분류 적용)
- 공통 게이트:
  - `episode_end <= K`
  - `source_status = APPROVED`
- A축(EVENT only):
  - event scope(질문 루트 캐릭터/주제) 기반 이벤트를 에피소드 순으로 노출
- B축(EVENT + REVEAL_ATTRIBUTE):
  - `event_reveal.target_type = ATTRIBUTE` + 질문의 `attribute_set`을 만족한 이벤트 노출
  - `A_*` 상위 키는 closure 이후 실제 `event_reveal.target_id`로 바인딩해야 실행 가능
  - hit 0이면 `NOT_ENOUGH_DATA`
- C축(EVENT + predicate_code):
  - `P_*` 상위 키는 closure 이후 `runtime_bindings -> PredicateCode`로 변환 후 조회
  - `event.predicate_code in predicate_set` 이벤트 노출
  - hit 0이면 `NOT_ENOUGH_DATA`
- BC축(혼합):
  - 기본 `OR`(B ∪ C), 질문별 `combine_mode=AND`면 교집합(B ∩ C) 적용
- PRECEDES:
  - 선정 기준으로 쓰지 않고, 선택 이벤트의 연결선/근거 카드 렌더링에만 사용

## 4) 상속(승계) 적용 원칙
- canonical policy:
  - `fivecircles/architecture/specs/rdf/policy/inheritance-closure-policy.md`
- phase1 taxonomy SoT:
  - `fivecircles/architecture/specs/rdf/policy/inheritance-closure-taxonomy.phase1.json`
- 요약:
  - 상속은 PRECEDES 대체가 아니라 B/C축 매칭 범위 확장(closure) 레이어로만 사용한다.
  - 안전 게이트(`episode_end <= K`, `APPROVED`)는 상속 확장 후에도 동일하게 적용한다.
  - Phase1은 DB 스키마를 바꾸지 않고(`event.predicate_code`, `event_reveal`) closure 파일만 추가해 적용한다.
  - Phase2의 `event_predicate`/`predicate` 정규화는 보류한다.

## 5) 권장 실행순서 (합의안)
1. Q1 확장 6개 strict 토큰 복구(문서 서술형 토큰은 approx로 분리)
2. `question_id -> axis -> required_set(attribute/predicate/scope)` SoT JSON 작성
 - `fivecircles/architecture/specs/extension100/question-map.q01-expansion.phase1.json`
  - `fivecircles/architecture/specs/extension100/question-map.q04-expansion.phase1.json`
  - `fivecircles/architecture/specs/extension100/question-map.q06-expansion.phase1.json`
  - `fivecircles/architecture/specs/extension100/question-map.q07-expansion.phase1.json`
  - `fivecircles/architecture/specs/extension100/question-map.q11-expansion.phase1.json`
  - `fivecircles/architecture/specs/extension100/question-map.q14-expansion.phase1.json`
3. 상속 closure 레이어 추가: taxonomy JSON + `expand(set)` 유틸
   - `fivecircles/architecture/specs/rdf/policy/inheritance-closure-taxonomy.phase1.json`
4. 조회 레이어 추가: `getEventsByRevealAttribute`, `getEventsByPredicate` (expanded set 사용)
   - `A_* -> reveal target_id`, `P_* -> PredicateCode` 바인딩 규칙 고정
5. ProductionQ 결과 모델 확장: `selected + A/B/C lane + precedes lane`
6. 리마인더 UI를 lane 기반으로 전환(REVEALS/ATTRIBUTE 섹션 포함)
7. 게이트 추가: expansion strict hit 회귀 + axis 매핑 drift 검사
8. `/qa-story-reminder-test`에서 ex22.2/ex22.3 + 100문항 샘플 검증

## 6) 산출물/참조
- 공유 온톨로지레이어 플랜 출처(ex20+):
  - `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex20-axis.md`
  - `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex21-SPO-N-Y.md`
  - `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex22-axis-N-Y-scetch.md`
  - `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex22.1-ops.md`
  - `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex22.2-expension-categorized-impl-plan.md`
  - `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex22.3-expension-expension-qs-imple2.md`
  - `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex23-RDF-inheritance.md`

## 6.1) 실행 규칙 연결표 (Spec <- Plan)
| 현재 실행 규칙 | 연결 플랜 문서 | 반영 위치 |
|---|---|---|
| A/B/C 축 기반 조회 분기 | ex20, ex22 | 본 문서 3), question-map |
| strict-first 유지 + WHY 가드 | ex21, ex22.1 | executor + todolist gates |
| Q1 확장 6개를 canonical 질문셋으로 고정 | ex22.2, ex22.3 | `question-map.q01-expansion.phase1.json` |
| reveal-first 질문군(Q4/Q6/Q7/Q11/Q14) draft map 추가 | extension100 tagging, reveal sketch | `question-map.q04-expansion.phase1.json`, `question-map.q06-expansion.phase1.json`, `question-map.q07-expansion.phase1.json`, `question-map.q11-expansion.phase1.json`, `question-map.q14-expansion.phase1.json` |
| RDF 상속은 closure 확장만 사용 | ex23 | `inheritance-closure-policy.md`, taxonomy JSON |
| PRECEDES는 보조 lane | ex22.3, ex23 | 본 문서 3), UI lane 계획 |
| Phase1 DB 무변경 / Phase2 보류 | ex22.1 | 본 문서 4), todolist B2.5 |

- 분류 예시 원문:
  - `fivecircles/architecture/specs/extension100/extension-6of100-q1.md`
- V3+ 축 태깅표:
  - `fivecircles/architecture/specs/extension100/question-axis-tagging-v3-reveal-predicate-precedes.md`
- R 질문군용 reveal 상속계 스케치:
  - `fivecircles/architecture/specs/extension100/reveal-inheritance-sketch-for-r-questions.md`
- question-map draft 인덱스:
  - `fivecircles/architecture/specs/extension100/question-map-drafts-index.md`
- 상속 정책(정식):
  - `fivecircles/architecture/specs/rdf/policy/inheritance-closure-policy.md`
- 상속 taxonomy SoT(Phase1):
  - `fivecircles/architecture/specs/rdf/policy/inheritance-closure-taxonomy.phase1.json`
- Q1 확장 질문 매핑 SoT(Phase1):
  - `fivecircles/architecture/specs/extension100/question-map.q01-expansion.phase1.json`
- 관련 아티팩트:
  - `fivecircles/architecture/specs/predicate/artifacts/answerset-10.json`
  - `fivecircles/architecture/specs/predicate/artifacts/answerset-6-expansion.json`
- 관련 코드:
  - `front/common/productionQ/templates.ts`
  - `front/features/qa/StoryReminderTestPage.tsx`
  - `front/features/qa/components/ProductionQSection/*`

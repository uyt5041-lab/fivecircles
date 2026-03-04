# Answer-First Backward Design (axis/SPO/AND/WHY)

## 목적
- 정책 선고정이 아니라, 질문/답변 데이터로 실제 답 생성 가능성을 먼저 검증한다.
- 작은 실험 세트로 드리프트/과설계를 방지한다.

## 선행 원칙
- 선행 기준: 각 문항에 `answer_event_id` + `because` 근거를 생성할 수 있어야 한다.
- 허용 데이터: `event_character.role`, `event_reveal`, `event_relation(PRECEDES)`
- 금지: 실험 단계에서 신규 relation type/메타 컬럼 추가
- 상태 규칙: strict miss는 `SPOILER_BLOCKED` 또는 `NOT_ENOUGH_DATA`만 허용 (`ANSWERED` 금지)
- 정답 탐색은 strict-first(SQL+코드), RDF/SPARQL은 근거 렌더링 보조로 제한
- 사건(사실)과 해석(라벨)을 분리한다:
  - `event`: 관측 가능한 사실만 저장
  - `event_reveal.reveal_type`: 근거 강도(`HINT|CONFIRM`)만 저장
  - 근거 없는 해석 문구는 reveal로 저장하지 않고 문서/ops 메모로 유지

## Anchor 선정/승격 규칙
- 기준: anchor는 문서 선호가 아니라 **answerset 실행 결과 데이터**로 결정
- 1순위: 기존 `common/PredicateCode`를 strict anchor로 사용
- 2순위: 코드북에 없는 패턴은 `predicateCode=OTHER` + `predicate_suggestion` 후보로 수집
- 승격(신규 enum) 조건:
  - 빈도: 동일 후보가 실험/운영 데이터에서 반복 출현(기본 기준: 3회 이상)
  - 정확도: strict 정답 일치율이 기준 이상(기본 기준: 0.90 이상)
  - 검증: 질문 2종 이상에서 재현되고 오탐이 낮음
- 승격 절차: `PredicateCode` 직접 추가가 아니라 RFC/체크리스트 경유 후 반영

## Phase A-1 (선행 게이트): T01~T10 실험 세트

### 구성
- A(단일 정답/언제) 4문항: `T01~T04`
- B(REVEALS 근거) 3문항: `T05~T07`
- C(WHY/도미노) 3문항: `T08~T10`

### 각 문항 최소 산출물
- `answer_event_id`: strict-first + earliest + approved 단건
- `because`:
  - A/B: `reveal_hint` 1~3개
  - C: `because_chain(PRECEDES)` 2~3 hop

### 스냅샷 포맷(canonical)
- canonical: **BE executor 결과 JSON(정렬 포함)**
- 저장 경로: `fivecircles/architecture/specs/predicate/artifacts/answerset-10.json`
- 권장 키:
  - `question_id` (`T01`..`T10`)
  - `axis`
  - `strict_filters`
  - `anchor_source` (`ENUM` | `OTHER_SUGGESTION_CANDIDATE`)
  - `answer_event_id`
  - `because_chain`
  - `reveal_hint`
  - `status`

## Phase A-2 (확장 검증): 후속 #1~#6
- A-1 완료 후 진행
- 각 문항 산출물:
  - `answer_event_id` 1개
  - `reveal_attribute` 1~3개
  - 필요 시 `because_chain(PRECEDES)` 2 hop
- 저장 경로: `fivecircles/architecture/specs/predicate/artifacts/answerset-6-expansion.json`

## 역설계 산출물 (A-1/A-2 완료 후)
1. 질문 타입별 필수 데이터 체크리스트
2. 템플릿-필터 매트릭스(strictFilters allow-list + 실행 순서)
3. WHY 출력 규격(`answer_event`, `because_chain`, `reveal_hint`)

## 연결 TODO
- `fivecircles/architecture/todolist.md`
  - `axis/SPO/AND/WHY 구현 체크리스트 > A-1`
  - `axis/SPO/AND/WHY 구현 체크리스트 > A-2`

## 참조
- `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex22.2-expansion-categorized-impl-plan.md`
- `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex22.3-expansion-expansion-qs-imple2.md`
- `fivecircles/architecture/specs/reveals/reveals-classification.md` (Rule C: 사실/해석 분리 + HINT/CONFIRM 판정)
- `fivecircles/architecture/specs/reveals/reveal-evidence-label-policy.md` (지속 참고 기준서)

# RDF Inheritance Closure Policy (2026-02-26, v2)

## 1) Purpose
- 상속(승계)은 질문 매칭 범위 확장(closure) 레이어로만 사용한다.
- 대상은 Expension100의 B/C 축 질문(`REVEALS/ATTRIBUTE`, `predicate_code`)이다.
- Event 인스턴스 상속은 하지 않고, `Predicate`/`Attribute` 계층만 상속한다.

## 1.1) Origin References (Shared Ontology Layer, ex20+)
- `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex20-axis.md`
- `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex21-SPO-N-Y.md`
- `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex22-axis-N-Y-scetch.md`
- `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex22.1-ops.md`
- `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex22.2-expension-categorized-impl-plan.md`
- `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex22.3-expension-expension-qs-imple2.md`
- `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex23-RDF-inheritance.md`

## 1.2) Traceability Matrix (Policy <- Plan)
| Policy Rule | Plan Source | Applied Decision |
|---|---|---|
| Axis는 설명 레이어, strict 정답 선정 비영향 | ex20, ex22, ex22.1 | Lane boundary 분리(Executor vs Closure) |
| SPO/AND/WHY contract 유지 | ex21, ex22 | strict-first 유지, BC는 결합모드만 확장 |
| Expension 질문은 Answer-first data 기반 | ex22.2, ex22.3 | `Q01_EXP_01..06` canonical + question_map SoT |
| RDF 상속은 런타임 reasoner 없이 closure 전개 | ex23 | `expand(set)` + JSON SoT 기반 실행 |
| PRECEDES는 선정 기준 아님 | ex15, ex22.3, ex23 | precedes는 설명/연결선 보조 전용 |
| DB 최소 변경 원칙 | ex22.1 | Phase1은 기존 `event`/`event_reveal` 재사용 |

## 2) Hard Rules (MUST)
- PRECEDES는 정답 선정 기준으로 사용하지 않는다(연결선/설명 보조 전용).
- reasoner/SPARQL 런타임 추론은 도입하지 않는다.
- strict-first 정답 규칙은 유지한다(상속은 strict를 대체하지 않음).
- 질문 키는 기존 템플릿 ID(`Q01_EXP_01..06`)를 canonical로 사용한다.

## 3) Lane Boundary
- Executor lane SoT: `StrictQuerySpec`/템플릿(`strict_must`)만 사용.
- RDF/closure lane SoT: 상속 맵만 사용.
- Axis는 설명/탐색 레이어이고 strict 정답 선정에는 영향을 주지 않는다.

## 4) Phase Split (DB 최소 변경)
### Phase1 (현재 적용)
- DB 스키마 변경 없이 진행한다.
- Predicate는 기존 `event.predicate_code`를 그대로 사용한다.
- Attribute는 기존 `event_reveal(target_type=ATTRIBUTE)`를 그대로 사용한다.
- Closure SoT는 파일 기반으로 고정한다.
  - `fivecircles/architecture/specs/rdf/policy/inheritance-closure-taxonomy.phase1.json`

### Phase2 (확장 시)
- 필요 시에만 스키마 확장을 검토한다.
  - `predicate` / `event_predicate` N:M
  - `attribute` 코드 테이블 정규화
- Phase2 전에는 Phase1 규칙을 변경하지 않는다.

## 5) Closure SoT Model
- 단일 SoT 파일에서 도메인을 분리한다.
  - `PREDICATE` 트리: 상위->하위(20+ 노드 시작점)
  - `ATTRIBUTE` 트리: 상위->하위(20+ 노드 시작점)
- 의미:
  - 부모 노드: 질문 매핑용(상위 개념)
  - 자식 노드: 데이터 태깅용(구체 개념)
- 질문 매핑 키:
  - `A_*`: Attribute 축 상위 개념 키
  - `P_*`: Predicate 축 상위 개념 키

## 6) expand(set) Rules
- 입력: 질문이 요구하는 상위 set(`attribute_set`/`predicate_set`).
- 출력: 입력 + 모든 descendant(하위) 집합.
- 부모 방향 확장 금지.
- cycle 방지(`visited`)는 필수.
- depth 기본값은 6으로 제한한다.

## 7) Query Rules
- B축:
  - `event_reveal.target_type = ATTRIBUTE`
  - `event_reveal.target_id IN expanded_attribute_set`
- C축:
  - `event.predicate_code IN expanded_predicate_set`
- BC축:
  - 기본은 `OR`(B ∪ C)
  - 질문별로 `combine_mode=AND`를 지정하면 B ∩ C를 사용
  - 결과 정렬은 `episode asc, id asc`

## 7.1 Binding Rules (MUST)
- B축 바인딩:
  - `A_*` 상위 키는 closure 확장 후, 최종적으로 `event_reveal.target_id` 집합으로 변환되어야 한다.
  - 변환 테이블이 비어 있으면 해당 질문은 `NOT_ENOUGH_DATA`로 처리한다.
- C축 바인딩:
  - `P_*` 상위 키는 closure 확장 후, `runtime_bindings`를 통해 `PredicateCode` 집합으로 변환되어야 한다.
  - `event.predicate_code` 조회에는 `P_*` 키를 직접 사용하지 않는다.

## 8) Safety Gate
- 상속 확장 전/후 모두 아래 게이트를 강제한다.
  - `episode_end <= K`
  - `source_status = APPROVED`
- 축별 hit가 0이면 `NOT_ENOUGH_DATA`.

## 9) Integration
- 리마인더 UI는 lane 기반으로 출력한다.
  - `selected_event`
  - `axis_lane(A/B/C/BC)`
  - `precedes_lane`(옵션)
- 상속은 B/C/BC lane의 후보 확장에만 영향을 준다.

## 10) Canonical Artifacts
- Closure taxonomy SoT:
  - `fivecircles/architecture/specs/rdf/policy/inheritance-closure-taxonomy.phase1.json`
- Q1 확장 질문 매핑 SoT:
  - `fivecircles/architecture/specs/expension100/question-map.q01-expansion.phase1.json`

## 11) Rollout
1. Q1 확장 6개 strict 복구
2. `question_id -> axis -> required_set` SoT 고정
3. closure taxonomy SoT 고정
4. `expand(set)` 유틸 구현(Phase1 JSON 기반)
5. B/C/BC 조회 + UI lane 반영
6. 회귀 게이트(ANSWERED/BLOCKED/NO_DATA) 스냅샷 고정

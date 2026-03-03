# Taxonomy Specs

목적
- taxonomy dashboard와 query axis extension에서 참조하는 SoT/source 문서를 한 곳에서 볼 수 있게 정리한다.
- `query axis`와 `predicate category`를 구분한 상태로 운영 문서를 찾기 쉽게 만든다.

## 1) 핵심 문서

- Dashboard 스펙:
  - `fivecircles/architecture/specs/taxonomy/taxonomy-dashboard.md`
- Dashboard 구현 플랜:
  - `fivecircles/architecture/specs/taxonomy/taxonomy-dashboard-implementation-plan.md`
- Query axis 확장 초안:
  - `fivecircles/architecture/specs/taxonomy/query-axis-reveal-combined-design.md`

## 2) SoT / Source Reference

- `PREDICATE group/filter SoT`
  - `scripts/ops/rdf/taxonomy/predicate_axis_taxonomy.json`
- `PREDICATE tree/visualization SoT (draft)`
  - `scripts/ops/rdf/taxonomy/predicate_inheritance.json`
- `REVEAL semantic SoT`
  - `fivecircles/architecture/specs/reveals/reveal-target-key-codebook.md`
- `REVEAL closure SoT`
  - `fivecircles/architecture/specs/rdf/policy/inheritance-closure-taxonomy.phase1.json`
- `REVEAL read-path blueprint`
  - `fivecircles/architecture/specs/rdf/inheritance-blueprint.md`
- `REVEAL Phase2 cutover`
  - `fivecircles/architecture/specs/rdf/attribute-id-lane-cutover-plan.md`

## 3) 용어 정리

- `query axis`
  - 상단 축: `REVEAL`, `PREDICATE`, `COMBINED`, `PRECEDES`
- `predicate category`
  - `PREDICATE` axis 내부 preview/filter용 group 분류
  - 예: `BATTLE`, `ADVERSARY`, `ALLY`
- `predicate tree`
  - `PREDICATE` axis 내부 시각화용 상속 노드 집합
  - root group + leaf(`PREDICATE_CODE`, `SUGGESTION`)를 함께 포함
- `axisCode`
  - 현재 API 응답에서 남아 있는 legacy 필드명
  - taxonomy 문맥에서는 `category code` 의미로 읽는다.

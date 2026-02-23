# RDF/OWL Extension Notes (Keep Question Layer Stable)

목적
- 추후 RDF/OWL(트리플)로 확장하더라도, 현재 서비스/프론트가 사용하는 "질문 레이어"가 깨지지 않게 한다.
- 본 문서는 구현 노트이며, V3-Advanced 규정은 다음 문서를 따른다:
  - `fivecircles/architecture/specs/event-v3-advanced-rdf-owl.md`

핵심 원칙
- `PredicateCode`는 "뷰/질문 레이어의 타입"으로 유지한다(stable).
- RDF/OWL은 별도 레이어로 확장한다(unstable to stable mapping 가능).
- 초기 도입은 운영 경로(runtime serving path)와 분리한다.

---

## 1) 레이어 분리

Layer A: Question/View layer
- 입력: `PredicateGroup`, `PredicateCode`, `safeUpToEpisode(K)`, `PRECEDES`
- 출력: 이벤트 리스트/집계/근거

Layer B: Ontology/Triple layer (future)
- 입력: `script_line`, `script_triple`, (optional) entity/relationship URI
- 출력: 트리플 질의 결과, 후보 관계, 근거 스팬

연결(bridge)
- `PredicateCode` <-> (ontology predicate URI) 매핑 테이블/문서
- 예: `PredicateCode.REVEALS`는 "reveal" 계열 URI 집합을 대표하는 view-type으로 남는다.

---

## 2) 확장 시나리오(초안)

Scenario 1: 더 세밀한 predicate가 필요해짐
- 먼저: `predicate_suggestion` 축적 -> 승격 프로세스(`fivecircles/architecture/specs/predicate/promotion-process.md`)
- 나중: ontology URI로 세분화해도, view-layer predicate는 안정적으로 유지

Scenario 2: "대상(무엇이 드러났나)" 필터가 필요해짐
- predicate 확장만으로는 부족
- event_reveal / triple object 등 별도 메타(객체/타겟) 레이어가 필요

Scenario 3: 적대자/협력자 같은 파생 질문 최적화
- server aggregate endpoint로 N+1 제거(현재 RDB 집계)
- 추후 triple layer가 도입되면 내부 구현만 교체 가능(질문 레이어는 동일)

---

## 3) Phase 4 Minimal Deliverables (RDF/OWL)

아래 4개를 최소 산출물로 고정한다.

1) `ontology.ttl`
- OWL vocabulary (Event/Character/Relation/Role terms).

2) `shapes.ttl`
- SHACL constraints (domain/range, enum, temporal/rule constraints).

3) `kg.ttl`
- RDB -> RDF export sample/output.

4) `report.json`
- SHACL validation result report.

---

## 4) 초기 실행 방식 (서비스 추가 없이)

- Exporter(batch/command): RDB -> `kg.ttl`
- Validator(SHACL-first): `kg.ttl` -> `report.json`
- 초기 소비자는 사용자 UI가 아니라 ops/review 레이어로 제한한다.

---

## 5) 도입 난이도 단계 (Decision Matrix)

- Export-only (complexity +10)
  - RDB SoT 유지, RDF는 dump/validation/report 용도.

- Query-only (complexity +30)
  - 일부 read-path에서 SPARQL 사용, SoT는 RDB 유지.

- Dual-store (complexity +80)
  - 운영 write/sync/rollback/recovery를 양쪽 스토어 기준으로 관리.

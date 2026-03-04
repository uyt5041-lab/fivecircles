# SPO Index

기준일: 2026-03-04

목적
- 현재 프로젝트에서 SPO(Subject / Predicate / Object) 관련 문서가 흩어져 있는 상태를 정리하고,
  개념 설계 -> 현재 런타임 계약 -> semantic lane/Fuseki 확장 순서로 빠르게 찾을 수 있게 한다.

고정 해석
- 현재 운영 런타임은 완전 일반화 SPO 엔진이 아니라 `SPO-lite`에 가깝다.
- 현재 메인 레인은 RDB strict-first이며, semantic lane(RDF/Fuseki)은 보조 확장 레인으로 본다.
- 현재 실행 필터의 핵심은 아래 4개다.
  - `subjectCharacterId`
  - `withCharacterIds`
  - `targetCharacterId`
  - `aboutCharacterId`

## 1. 핵심 문서(읽기 순서)

- 통합 계획:
  - `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/specs/SPO/generalized-spo-semantic-lane-plan.md`

### 1.1 SPO 개념 / 제안
- `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex21-SPO-N-Y.md`
  - 일반화된 SPO 방향, subject/predicate/object 검색 철학, role 기반 적용안
- `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex22-axis-N-Y-scetch.md`
  - 이벤트를 SPO 컨테이너로 보는 스케치, axis/SPO 결합, SPARQL 선택 적용안
- `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex22.1-ops.md`
  - 기존 `event_character.role(SUBJECT/OBJECT/INVOLVED)` 우선, DB 최소 변경 운영 원칙

### 1.2 현재 런타임 계약(anti-halu / production Q)
- `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/specs/questions-anti-halus/03-implementation-plan.md`
  - `subjectCharacterId`, `withCharacterIds`, `targetCharacterId`, `aboutCharacterId` 실행 계약
- `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/specs/questions-anti-halus/04-template-strict-must-matrix.md`
  - 질문별 strict MUST와 shorthand(`subject=*`, `target=*`, `about=*`) -> 실행 필터 매핑
- `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/specs/predicate/strict-filters-contract.md`
  - strict filter 계약 요약본
- `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/specs/predicate/production-q-templates-and-intelligence-queryspec.md`
  - production Q 템플릿/실행 규칙, strict/probe/answerability 흐름

### 1.3 reveal / object 확장 (semantic lane)
- `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/specs/reveals/reveals-routing-mvp-and-v3.md`
  - ATTRIBUTE reveal의 `aboutCharacterId` 계약, V2.5 -> V3 전환 경계
- `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/specs/reveals/semantic-lane-object-schema-draft.md`
  - semantic 보조 레인 object schema 초안 (`CHARACTER|ATTRIBUTE|RELATION|ALIAS|LOCATION|ORG|ITEM`)
- `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/specs/rdf/semantic-lane-object-schema.draft.ttl`
  - semantic lane object schema TTL 초안
- `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/specs/rdf/semantic-lane-object-schema.sample-queries.md`
  - Fuseki/SPARQL 샘플 쿼리

### 1.4 RDF / reasoner / Fuseki 확장
- `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex25-Reasoner-taxonomy-RDF.md`
  - reasoner / derived facts / semantic lane 확장 논의
- `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/specs/rdf/inheritance-blueprint.md`
  - RDF inheritance, ATTRIBUTE lane, phase1/phase2 경계
- `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/specs/rdf/policy/inheritance-closure-policy.md`
  - 상속 허용 범위와 runtime 바인딩 정책

## 2. 현재 구현 해석

### 2.1 현재 SPO-lite에서 구현된 것
- `subject`
  - runtime: `subjectCharacterId`
- `with`
  - runtime: `withCharacterIds`
- `target`
  - runtime: `targetCharacterId`
- `about`
  - runtime: `aboutCharacterId`

즉 현재는 character/about 중심의 `SPO-lite`가 운영 중이다.

### 2.2 아직 일반화되지 않은 것
- object type 일반화 (`RELATION`, `ALIAS`, `LOCATION`, `ORG`, `ITEM`)
- semantic object resolver
- fully generic SPO query planner

## 3. Fuseki semantic lane으로 갈 때의 해석
- 메인 정답 선택은 계속 RDB strict-first
- Fuseki는 semantic resolver / expansion / alias/sameAs / reveal/predicate inheritance 보조 레인
- `PRECEDES`는 가능하면 계속 RDB

참조:
- `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex25-Reasoner-taxonomy-RDF.md`
- `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/specs/reveals/semantic-lane-object-schema-draft.md`

## 4. 바로 찾기용 키워드
- 일반화된 SPO 설계: `ex21-SPO-N-Y.md`
- 이벤트를 SPO 컨테이너로 보는 문서: `ex22-axis-N-Y-scetch.md`
- 현재 strict 실행 계약: `03-implementation-plan.md`, `04-template-strict-must-matrix.md`
- aboutCharacterId 계약: `reveals-routing-mvp-and-v3.md`
- semantic object schema: `semantic-lane-object-schema-draft.md`
- Fuseki/SPARQL 초안: `semantic-lane-object-schema.draft.ttl`

## 5. 다음 후속 문서 후보
- `generalized-spo-semantic-lane-plan.md`
  - 현재 SPO-lite -> Fuseki semantic lane -> 완성형까지의 통합 계획 문서

# ex19 - RDF 확장 관리성 검토 (predicate/SPO/reveals/relation/role, 그룹/상속)

작성일
- 2026-02-24

목적
- "RDF를 도입했으니 predicate_code, SPO, reveals, relation, role 같은 확장형 데이터를 더 쉽게 관리할 수 있는가?"에 대해 현재 프로젝트 기준으로 사실 점검한다.
- Query-only 운영 목표(V3-Advanced +30)와 충돌 없이, 그룹/상속(ontology) 도입 난이도를 정리한다.

---

## 1) 결론 (현재 코드 기준)

짧은 결론
- 조건부로 맞다.
- 지금 구조에서는 "후보 추출 규칙 변경"은 쉬워졌지만, "정답 결정/게이트/노출 정책"까지 RDF로 쉬워진 상태는 아니다.

왜 이렇게 판단하는가
- `/api/event/v3` 최종 응답은 여전히 RDB hydration + hard gate(`episode_end <= K`, `source_status='APPROVED'`)로 확정된다.
- Query-only는 RDF를 후보 추출 레인으로 쓰고, 최종 결정은 RDB에서 한다.
- 따라서 "RDF만 바꾸면 끝"이 아니라 "RDF 규칙 + RDB 최종 게이트"를 함께 맞춰야 한다.

---

## 2) GPT 답변과의 정합성 리뷰

### 2-1. 맞는 부분

1. "RDF는 후보 패턴 질의 변경에 유리하다"
- 현재도 Q16/Q17/Q18/Q19/Q20 PoC가 RDF/SPARQL 후보 추출로 구현되어 있다.
- 근거:
  - `scripts/ops/rdf/query_v3_advanced_q16_poc.py`
  - `scripts/ops/rdf/query_v3_advanced_q17_poc.py`
  - `scripts/ops/rdf/query_v3_advanced_q18_poc.py`
  - `scripts/ops/rdf/query_v3_advanced_q19_poc.py`
  - `scripts/ops/rdf/query_v3_advanced_q20_poc.py`

2. "RDF에서 그룹/상속을 쓰면 predicate 관리성이 올라간다"
- 방향은 맞다. 다만 현재 repo는 아직 class hierarchy 기반 질의가 핵심이 아니다.

3. "최종 노출 정책은 RDB hard gate가 안전하다"
- 현재 운영 문서/런북과 일치한다.
- 근거:
  - `fivecircles/architecture/specs/event-v3-advanced-query-only-plan.md`
  - `fivecircles/docs/ops/event-v3-q16-q19-query-only-runbook.md`

### 2-2. 보정이 필요한 부분

1. "reveals/relation/role 전체가 RDF에서 확장 관리 가능하다"
- 현재 export는 Event/Character/EventCharacter + PRECEDES만 내보낸다.
- reveals 전용 edge나 relation type 전체는 아직 RDF에 풀로 반영되지 않았다.
- 근거:
  - `scripts/ops/rdf/export_v3_advanced.py`

2. "그룹/상속으로 이미 관리 중"
- 현재 `ontology.ttl`은 최소 클래스/속성 정의 중심이고, predicate 상속 트리는 거의 없다.
- 즉 "가능한 구조"는 있지만 "운영 규칙을 ontology가 주도"하는 단계는 아니다.
- 근거:
  - `fivecircles/architecture/specs/rdf/artifacts/v3-advanced/latest/ontology.ttl`

3. "Q19/Q20 분류가 ontology 중심"
- 현재 PoC는 ontology 추론보다 파이썬 상수 집합(BATTLE/ADVERSARY/ALLY)로 축 분류를 수행한다.
- 규칙 변경 시 코드 수정이 필요한 구조다.
- 근거:
  - `scripts/ops/rdf/query_v3_advanced_q19_poc.py`
  - `scripts/ops/rdf/query_v3_advanced_q20_poc.py`

---

## 3) 우리 구조에서의 정확한 상태 정의

현재 상태
- V3 Core: RDB 중심 운영.
- V3-Advanced: Export-only + Query-only 준비/부분 적용.
- Q16/Q18/Q19/Q20도 source mode(`rdb | rdf-candidate | auto-fallback`) 플래그와 fallback 구조가 이미 마련되어 있다.

실무적 의미
- "툴이 바뀌면 끝"이 아니다.
- Query-only에서 안정성을 유지하려면 아래 3개가 동시에 필요하다.
  1. RDF 후보 규칙
  2. RDB hard gate 재검증
  3. parity 관측(상태/근거/성능)

---

## 4) 그룹/상속(ontology) 도입 난이도와 권장 순서

### Stage A (낮은 리스크, 즉시 가능)
- 목표: 코드 상수에 흩어진 분류 기준을 ontology 파일로 끌어올린다.
- 작업:
  - predicate taxonomy 파일(예: CONFLICT_EVENT 하위군) 추가
  - Q19/Q20 PoC가 taxonomy 파일을 읽어 분류하도록 변경
- 효과:
  - "코드 수정 없이 분류 규칙 변경"의 첫 단계 확보

### Stage B (중간 리스크)
- 목표: relation/reveals를 RDF export에 확장 반영한다.
- 작업:
  - PRECEDES 외 relation type의 RDF 직렬화 범위 명시
  - reveals triple 정의와 SHACL 제약 추가
- 효과:
  - Q17/Q18 계열 후보 패턴의 조합 질의 유연성 증가

### Stage C (높은 리스크)
- 목표: ontology/추론 규칙을 서비스 query 경로의 실질 SSOT로 승격한다.
- 작업:
  - 추론 포함/미포함 정책 고정
  - parity 게이트(상태/근거/Jaccard/성능) 통과 후 rollout
- 효과:
  - 진짜 "그룹/상속 기반 운영" 달성

---

## 5) 지금 당장 사용할 판단 체크리스트 (5문항)

1. ontology에 그룹/상속 정의가 실제로 들어가 있는가?
2. SPARQL/PoC가 그 정의를 실제로 참조하는가? (코드 상수 하드코딩이 아닌가)
3. 그룹 변경이 코드 수정 없이 가능한가?
4. 변경 후에도 RDB hard gate 결과와 parity가 유지되는가?
5. fallback/kill-switch로 즉시 RDB 복귀가 가능한가?

---

## 6) 프로젝트 적용 권고안

권고
- 현재 전략은 유지한다: "V3 Core 안정 + V3-Advanced Query-only 점진 승격".
- 단, "확장 관리성"을 실제로 얻으려면 Q19/Q20 분류 기준을 ontology 외부화(코드 상수 제거)부터 시작한다.

권고 우선순위
1. taxonomy externalization (Q19/Q20 분류 규칙 파일화)
2. export 범위 확장(reveals/relation type 명시 반영)
3. parity 리포트 기준으로 단계 승격

이 문서는 아래 스펙의 보조 제안서로 본다.
- `fivecircles/architecture/specs/event-v3-advanced-rdf-owl.md`
- `fivecircles/architecture/specs/event-v3-advanced-query-only-plan.md`

---

## 7) Reasoner 우선순위 재정의 (추가 합의)

핵심 합의
- 현재 상태(Query-only: RDF 후보 추출 -> RDB hydrate + hard gate 확정)에서, 다음 투자 우선순위는 reasoner 도입이 아니다.
- 1순위는 "그룹/계층 SSOT 고정 + SPARQL 템플릿 반영"이다.

### 7-1. 지금 바로 체감되는 개선 (Reasoner 없이 가능)

1. predicate_code 그룹/상속 SSOT를 단일화
- 옵션 A: RDF 그래프에 그룹 트리플로 고정
- 옵션 B: RDB `predicate_code_group` 매핑 테이블을 SSOT로 두고 export 시 RDF 동기 반영
- 목표: 갈등축/분류 기준 변경 시 코드 수정 없이 반영

2. SPARQL 템플릿이 그룹/계층을 실제 참조하도록 강제
- ontology/매핑을 정의만 해두고 질의에서 쓰지 않으면 운영 체감은 0에 가깝다.
- Query-only에서 실질 엔진은 SPARQL 템플릿이므로, 템플릿 반영이 필수다.

3. SHACL 검증은 계속 유지
- reasoner 유무와 별개로 데이터 정합성 안전핀 역할(role enum, domain/range, shape 위반 탐지)을 담당한다.

### 7-2. Reasoner는 언제 필요한가 (선택 기능)

1. 하위 분류 자동 포함이 반복적으로 필요할 때
- 예: `CONFLICT_EVENT` 질의 시 하위 predicate를 자동 포함하고 싶은 경우
- 이 요구는 SPARQL 확장으로도 가능하며, 운영 복잡도가 낮은 SPARQL 방식이 선행 권장된다.

2. property chain/inverse/transitive 자동 파생이 누적될 때
- 규칙이 복잡해져 SPARQL/코드 유지비가 커지는 지점에서 reasoner 도입을 재평가한다.
- 도입 시에도 초기 프로파일은 제한적으로(예: RDFS/OWL RL 수준) 운영한다.

### 7-3. 실행 순서 (최단 루트)

1. predicate_code 그룹/계층 SSOT 확정
2. Q17/Q19 SPARQL 템플릿에 그룹 규칙 반영
3. parity/성능 추적 후 필요 시 reasoner 도입 검토

한 줄 정리
- "Reasoner first"가 아니라 "SSOT + SPARQL 반영 first"가 현재 단계의 정답이다.

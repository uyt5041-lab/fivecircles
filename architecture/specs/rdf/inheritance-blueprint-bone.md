
아래는 **Predicate 승계 + Attribute 승계** 공통으로 쓸 수 있는 “승계 엔진” 설계도야.

---

## 1) 승계의 의미를 한 문장으로 고정

### 1.1 Attribute 승계 (subclass 느낌)

* `child_attribute`는 `parent_attribute`의 **더 구체적인 버전**이다.
* 따라서 `child`가 드러났다면 `parent`도 드러난 것으로 취급해도 된다(매칭 관점에서).

### 1.2 Predicate 승계 (subproperty 느낌)

* `child_predicate`는 `parent_predicate`의 **더 구체적인 행동/관계**다.
* 따라서 이벤트에 `child`가 붙어 있으면 `parent`로도 매칭된다.

> 즉 둘 다 “추론”이 아니라 **매칭 집합 확장(expand)** 규칙이다.

---

## 2) 데이터 구조: 트리만으로 충분한가? DAG까지 허용할가?

### 결론: **DAG(다중 부모) 허용**

드라마 지식은 “은폐”가 “거짓말”에도 걸리고 “증거인멸”에도 걸리는 식으로, **다중 분류**가 자연스럽게 발생함.

* 허용: `node -> parents[]` 여러 개 가능
* 금지: cycle(순환)

다중 부모를 허용하면 “노드 재사용”이 가능해져서 태그 폭발이 줄어든다.

---

## 3) 승계 구현 방식 2가지 중 하나로 고정

여기부터가 진짜 “구현 설계”.

### 방식 A: Closure Table(권장, 운영 안정 최고)

DB에 “조상-자손 전개 결과(closure)”를 저장해두는 방식.

#### 3.1 테이블 (Predicate, Attribute 공통 형태)

* `predicate_edge(parent_id, child_id)`
* `predicate_closure(ancestor_id, descendant_id, depth)`
* attribute도 동일

```sql
-- direct edges (DAG)
predicate_edge(
  parent_id BIGINT NOT NULL,
  child_id  BIGINT NOT NULL,
  PRIMARY KEY(parent_id, child_id)
);

-- transitive closure (materialized)
predicate_closure(
  ancestor_id   BIGINT NOT NULL,
  descendant_id BIGINT NOT NULL,
  depth         INT NOT NULL,         -- 0이면 자기자신(필수)
  PRIMARY KEY(ancestor_id, descendant_id)
);
```

#### 3.2 closure를 꼭 “자기 자신(depth=0)” 포함

이거 안 하면 expand가 꼬인다.

* `expand({A})`는 최소 `{A}`를 반환해야 함

#### 3.3 장점

* expand를 코드에서 DFS/BFS로 안 돌려도 됨
* “질문이 요구하는 상위 노드”를 그대로 DB에서 **하위까지 즉시 펼침**
* 운영자가 트리를 바꿔도, closure만 재빌드하면 끝

#### 3.4 단점

* edge 바뀔 때 closure 재계산 필요
  하지만 이건 “관리 기능”에서 처리하면 됨(아래에 플로우 포함)

---

### 방식 B: 앱 캐시 + DFS(구현 빠름, 운영은 약간 불편)

* `parent -> children` 맵을 메모리에 로딩하고
* 요청마다 expand를 DFS로 돌린다

단, 지금은 “MVP 이후 확장”이고 운영 UI까지 갈 확률이 크니까
**방식 A(closure)**가 더 장기적으로 싸게 먹힘.

여기서는 **A로 확정**할게.

---

## 4) 승계 엔진의 핵심 규칙(불변 정책)

### R1. “아래로만 확장”

* 입력이 상위면 하위까지 확장
* 입력이 하위면 상위를 자동 포함하지 않음(매칭 관점에서 필요 없음)

  * 단, `depth=0` 자기 자신은 포함

즉 `expand(요구집합)`은 “descendants”만 돌려준다.

### R2. Cycle 금지 (절대)

* edge 추가/수정 시 사이클 생기면 거부
* 구현: `child`가 이미 `parent`의 descendant라면 추가 금지

  * `SELECT 1 FROM closure WHERE ancestor_id = child AND descendant_id = parent`

### R3. Depth limit 운영 정책 (폭발 방지)

* depth가 너무 깊어지면 taxonomy 설계가 나쁜 것
* 운영 정책으로 depth 최대를 8 같은 값으로 제한해도 됨
* closure에는 depth 기록하니까 쉽게 제어 가능

---

## 5) 승계 갱신(운영) 플로우: “edge 변경”은 어떻게 반영하나

Closure table을 쓰면 갱신 전략이 필요해.

### 추천 플로우(가장 단순하고 안전)

* 운영 UI에서 edge 변경이 일어나면
* **해당 taxonomy 전체를 재빌드**한다

  * 규모가 수천 노드여도 재빌드는 충분히 가능(요청 트래픽이랑 분리된 admin 작업)

#### 5.1 재빌드 알고리즘(개념)

1. closure 테이블 truncate
2. 모든 노드에 대해 (ancestor=descendant, depth=0) 삽입
3. edge를 이용해 transitive closure 생성

   * SQL 재귀 CTE 가능하면 DB에서 처리
   * 아니면 서버에서 BFS로 모든 ancestor-descendant를 계산해서 bulk insert

#### 5.2 “부분 갱신”은?

가능하지만 구현 복잡도 올라가고 디버깅 지옥이 생김.
확장 단계에서도 “전체 재빌드 버튼”이 가장 안전.

---

## 6) 실제 매칭 쿼리 구조(승계가 어떻게 쓰이나)

이제 승계가 답변 엔진에서 어떻게 쓰이는지 “딱” 보여줄게.

### 6.1 Attribute 기반(B축): 질문이 요구하는 attribute들의 descendants로 매칭

* 질문 요구: `required_attribute_ids = {A1, A2}`
* expand: `expanded_attr_ids = SELECT descendant FROM attribute_closure WHERE ancestor IN required`

그걸 event_reveal에 적용:

```sql
SELECT DISTINCT e.*
FROM event e
JOIN event_reveal er ON er.event_id = e.id
JOIN attribute_closure ac ON ac.descendant_id = er.target_id
WHERE e.drama_id = :dramaId
  AND e.episode_end <= :K
  AND e.status = 'APPROVED'
  AND er.target_type = 'ATTRIBUTE'
  AND ac.ancestor_id IN (:requiredAttributeIds)
ORDER BY e.episode_start, e.episode_end, e.id;
```

포인트:

* `IN (expanded)`를 앱에서 만들어 넘기지 않아도 됨
* closure join 하나로 끝

### 6.2 Predicate 기반(C축): 질문 요구 predicate의 descendants로 매칭

```sql
SELECT DISTINCT e.*
FROM event e
JOIN event_predicate ep ON ep.event_id = e.id
JOIN predicate_closure pc ON pc.descendant_id = ep.predicate_id
WHERE e.drama_id = :dramaId
  AND e.episode_end <= :K
  AND e.status = 'APPROVED'
  AND pc.ancestor_id IN (:requiredPredicateIds)
ORDER BY e.episode_start, e.episode_end, e.id;
```

### 6.3 BC축(둘 다): union 후 정렬

* 두 쿼리 결과 event_id를 합쳐서 다시 event 로딩하거나,
* SQL로 UNION DISTINCT 가능

---

## 7) 승계 구조의 “모델링 규칙” (노드 설계가 망가지지 않게)

승계 트리가 난장판 되면 expand가 무기 대신 폭탄이 돼. 그래서 규칙을 박아야 해.

### 7.1 Attribute 노드 규칙

* **상태/사실/관계/인지 변화**만 넣는다
* 한 노드는 “명사구”로(행동형 금지)

  * OK: `SUSPICION_HIGH`, `SELF_JUSTIFICATION_ON`
  * 비추: `JUSTIFY_KILLING`(동사형. predicate로 가야 할 가능성 큼)
* “정도/레벨”은 child로 분해

  * `SUSPICION` -> `SUSPICION_RISE` -> `SUSPICION_HIGH`

### 7.2 Predicate 노드 규칙

* **행동/관계 동작**만 넣는다
* 한 이벤트에 여러 predicate가 붙는 걸 전제로 설계
* 너무 상위 노드(예: `ACTION`)는 만들지 말고,
  상위도 “질문 매핑”에 쓸 정도의 의미를 가져야 함

  * 예: `CONCEALMENT`, `VIOLENCE_OR_THREAT`

### 7.3 다중 부모를 허용하되 “원칙”을 둔다

* Attribute의 다중 부모는 최소화(혼란)
* Predicate의 다중 부모는 상대적으로 허용(분류 다중성이 자연스러움)
* 다중 부모가 필요하면 “중간 노드”를 하나 만들고 거기에 모으는 게 더 깔끔한 경우가 많다

---

## 8) 성능/인덱스 설계(closure 쓰면 여기서 승부남)

### 필수 인덱스

* `attribute_closure(ancestor_id, descendant_id)`
* `attribute_closure(descendant_id, ancestor_id)`도 있으면 join 방향 바뀔 때 유리
* `predicate_closure`도 동일
* `event_reveal(target_type, target_id, event_id)`
* `event_predicate(predicate_id, event_id)`
* `event(drama_id, episode_end, status, episode_start)` (정렬/필터용)

closure join이 많아지면 인덱스가 생명줄이다.

---

## 9) 운영 UI/툴에서 승계 구조를 어떻게 다루나

MVP 이후 확장이니까 여기까지 포함해야 현실적이야.

### 9.1 Taxonomy 관리 화면 기능

* 노드 추가/수정/비활성화
* 부모 연결(edge 추가/삭제)
* 사이클 검증(추가 버튼 누르면 즉시 검사)
* “closure 재빌드” 버튼
* “이 노드의 descendants 미리보기” (관리자 디버깅 필수)
* “이 노드를 요구하는 질문 목록 보기” (영향도 파악)

### 9.2 질문 매핑 화면 기능

* 질문이 요구하는 상위 노드 설정
* “현재 데이터로 결과 몇 건 나오나” 테스트(K 입력)
* 결과 0이면 NOT_ENOUGH_DATA 경고

---

## 10) 최종 체크: 이 승계 구조가 해결하는 것/안 하는 것

### 해결 ✅

* 상위 질문 1개로 하위 태그들을 한 번에 커버
* 입력(태깅)은 구체 하위만 찍어도 됨
* 데이터가 늘어도 질문 매핑이 안정적으로 유지됨
* 운영자가 taxonomy를 조정해도 closure 재빌드로 반영 가능

### 안 함 ❌

* “원인-결과” 추론
* “텍스트에서 자동으로 attribute/predicate 판정”
* “이벤트 자체 상속”

---


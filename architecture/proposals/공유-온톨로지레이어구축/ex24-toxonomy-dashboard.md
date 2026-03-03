
> **RDF/OWL에서 정의한 상속 구조 → (전개된 map/closure) → RDB 필터로 변환 → 그 결과를 ‘눈으로 확인’하는 대시보드**

  

이걸 “관리자/운영자용”으로 한 페이지 만들면 끝이야. 👇

  

---

  

## 1) 대시보드 목표를 딱 3개로 고정

  

1. **상속 트리 시각화**

  

* `A_MORAL_FRAME_SHIFT` 같은 상위 축 아래에 어떤 leaf들이 들어가는지

* “전개 결과(closure)”가 실제로 어떤 리스트로 떨어지는지

  

2. **필터 결과 프리뷰**

  

* 선택한 노드(상위 축 or leaf)로 필터했을 때

  

* 매칭되는 이벤트 개수

* 대표 이벤트 20개 (episode_end, predicate_code, summary)

* 캐릭터/에피소드 범위로 추가 필터

  

3. **드리프트/정합성 체크**

  

* “RDF에 있는데 RDB에 없는 코드”

* “RDB에 있는데 RDF 트리에 미분류된 코드”

* “상속 전개 결과가 순환/중복/빈 결과” 같은 이상징후

  

이 3개만 있으면 RDF는 **‘정의’가 아니라 ‘운영 가능한 규칙’**이 돼.

  

---

  

## 2) 화면 구성: 1페이지 3패널(가장 단순, 가장 쓸모)

  

### A. 왼쪽: Taxonomy Tree

  

* 트리 노드 클릭하면 오른쪽 패널들이 갱신

* 노드 옆에 `count badge` 표시(이 노드로 필터했을 때 이벤트 수)

  

### B. 오른쪽 위: Filter Builder

  

* 현재 선택 노드: `axis_code`

* 추가 필터:

  

* character_id (optional)

* episode range (start/end) or K-gate 미리보기

* source_status(기본 APPROVED)

* 버튼 2개만:

  

* **Preview (20개)**

* **Export IDs (CSV)** (운영/디버깅용)

  

### C. 오른쪽 아래: Result Preview Table

  

* columns:

  

* episode_end

* predicate_code

* event_id

* summary (짧게)

* characters (축약)

* row 클릭하면 “Event Detail Drawer”

  

* reveal 축/precede 요약까지 같이 보여주면 디버깅이 빨라짐

  

---

  

## 3) 데이터 파이프라인: “RDF를 직접 쿼리”하지 말고 “taxonomy SoT를 단일 진실로”

대시보드는 RDF 파일(ttl/owl)을 직접 해석해도 되지만, 현재 구현/운영 기준으로는 다음이 가장 안전해:

### 단일 진실(SoT)

* **preview/filter SoT는 `predicate_axis_taxonomy.json`**
* **tree/visualization SoT는 `predicate_inheritance.json`**

* 경로:
  * `scripts/ops/rdf/taxonomy/predicate_axis_taxonomy.json`
  * `scripts/ops/rdf/taxonomy/predicate_inheritance.json`

### Phase 1 동작 방식

* 빌드 산출물 없이 서비스 런타임이 두 JSON을 직접 읽음
* `predicate_axis_taxonomy.json`
  * preview/filter용 closure 계산
* `predicate_inheritance.json`
  * 트리 패널용 root/leaf 구조 제공
* “필터 결과”는 전개된 `predicate_code` 리스트를 SQL에 넣어 preview함

### Phase 2 옵션(추후)

* taxonomy가 복잡해지면 `generated taxonomy map` 또는 `inheritance_map.json` 같은 compile 산출물을 도입할 수 있음

* 하지만 현재 구현/운영 기준은 compile 산출물 없이 taxonomy JSON 직접 로드 방식임

---

  

## 4) 백엔드 API는 3개면 충분

  

1. `GET /admin/taxonomy/tree`

  

* 반환: 트리 + 각 노드의 leaf list(또는 노드 id만, leaf는 별도 호출)

* 옵션: count까지 같이 주면 프론트가 편함

  

2. `POST /admin/taxonomy/preview`

  

* input:

  

* axis_code

* character_id?

* episode_end_max? (K-gate 미리보기용)

* limit (default 20)

* server:

  

* axis_code → leaf list (inheritance_map에서)

* SQL: `... WHERE predicate_code IN (...) AND episode_end <= ? AND source_status='APPROVED' ...`

  

3. `GET /admin/taxonomy/drift`

  

* 반환:

  

* missing_in_rdb: [axis/leaf codes]

* unclassified_in_rdf: [predicate_codes]

* cycles_or_duplicates: diagnostics

* empty_nodes: 상속했는데 결과 0

  

---

  

## 5) 실패 시나리오도 보수적으로 딱 정의

  

* **inheritance_map 로드 실패**

→ 대시보드 상단에 “map missing” 빨간 배너 + preview 버튼 비활성화

  

* **axis_code가 트리에 없음**

→ “unknown axis” 표시 + drift 링크 유도

  

* **leaf list가 너무 길어 SQL IN이 위험**(나중에 커질 때)

→ 미리 방지책:

  

* leaf list가 N 이상이면 “export only” 모드로 제한

* 또는 임시 테이블/CTE로 넣는 방식으로 전환(이건 후속)

  

---

  

## 6) 구현 순서(가장 짧게 끝나는 순)

  

1. `inheritance_map.json`을 “현재 상속구조 기준”으로 확정해서 파일로 박기

2. `/admin/taxonomy/tree` 만들기

3. 프론트: Tree + Preview Table까지만 연결

4. `/admin/taxonomy/drift` 추가해서 운영 안정화

5. Export CSV는 마지막에 30분 컷으로 추가

  

---

   - # 상속보기, 묶어보기

응. **이 설계 그대로면 “축(상위 코드)로 묶어보고, 그 상위 상속 코드로 또 묶어보기”가 된다.**  
핵심은 한 가지야:

> **트리(상속) 노드 = “leaf 코드들의 집합(set)”을 대표한다.**  
> 클릭하면 그 집합으로 SQL 필터가 걸리고, 결과가 나온다.

그래서 “상위로 묶기”는 그냥 **더 큰 집합을 선택**하는 거고, “하위로 내려가기”는 **집합을 좁히는 것**이야.

---

## 1) 이 설계에서 “묶어보기”가 실제로 어떻게 동작하냐

### 트리 노드 클릭(상위 축 코드)

1. UI가 `axis_code = A_MORAL_FRAME_SHIFT`를 선택
    
2. `inheritance_map`에서 leaf 리스트를 뽑음
    
    - 예: `A_MORAL_FRAME_SHIFT -> [A_MORAL_JUSTIFY, A_MORAL_CONTRADICTION, ...]`
        
3. 서버가 SQL을 이렇게 만든다
    

- 이벤트 모드라면:
    
    - `WHERE event.predicate_code IN (leaf...)`
        
- 파생 모드라면:
    
    - `WHERE derived_fact.predicate_code IN (leaf...)`
        

4. 결과 20개 + count + (옵션으로 group-by)을 보여줌
    

즉 **상위 상속 코드로 묶는다 = leaf set이 커진다 = 결과가 넓어진다**.

---

## 2) “상위로 묶어본 다음, 또 상위로 묶는” 것도 되냐?

됨. 방식은 두 개 중 하나로 구현하면 돼(둘 다 가능).

### 방식 A: 트리 자체가 다단계

- `ROOT -> A_MORAL -> A_MORAL_FRAME_SHIFT -> A_MORAL_JUSTIFY -> leaf...`
    
- 클릭하는 노드가 바뀔 때마다 leaf set이 달라짐
    

### 방식 B: 결과 테이블에서 “상위로 재그룹”

- 현재 선택 노드로 결과를 뽑은 뒤
    
- “Group by: parent axis” 같은 드롭다운으로
    
    - leaf들을 다시 상위 축으로 aggregation해서 count를 보여줌
        

**MVP로는 A만 해도 충분**해. 트리 클릭이 곧 그룹핑이니까.

---

## 3) 너가 말한 “축으로 묶어 보고 / 상위상속 코드로 묶어보고”를 UI로 딱 표현하면

- 왼쪽 트리에서
    
    - leaf 클릭 → **좁은 묶음**
        
    - 부모 클릭 → **넓은 묶음**
        
    - 더 위 클릭 → **더 넓은 묶음**
        

그리고 오른쪽에서 옵션 하나만 추가하면 진짜 편해져:

### “Group inside result” (선택 사항, 있으면 쾌감)

- 현재 선택 노드 결과를 가져온 다음
    
- 결과를 leaf 단위로 count 보여주고
    
- 버튼 하나로 “부모 축으로 롤업(roll-up)”해서 다시 묶어 보여줌
    

이건 완전히 이 설계랑 정합이고 충돌 없어.

---

## 4) 딱 한 가지 주의점(부딪힘 포인트 1개)

**“상위 축 코드”가 DB의 predicate_code와 1:1로 일치하지 않으면**  
즉 상위 축은 “분류 노드”일 뿐이고, 실제 이벤트는 leaf 코드만 가진다면:

- 상위 축으로 묶는 건 무조건 **leaf list를 전개해서 IN 필터**로 해야 함.
    

근데 이건 이미 설계의 핵심이라 문제 없음.  
오히려 이 방식이 “상위 코드를 DB에 저장하지 않아도 그룹핑이 된다”는 장점이야.

---

### 결론 한 줄

트리의 상위 노드 = 더 큰 leaf 집합이라서, 클릭만으로 “상속 코드로 묶기”가 성립하고, 필요하면 결과 내부에서 “상위로 롤업”하는 2차 그룹핑도 같은 데이터로 구현 가능하다.

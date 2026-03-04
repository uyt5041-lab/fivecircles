# Reasoner

 **“새로운 사실을 만들어서(추론) 그걸로 다른 질문들을 답하게 하는 페이지”**

## 관련 draft / 참조

- semantic lane object schema 초안:
  - `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/specs/reveals/semantic-lane-object-schema-draft.md`
- triple store용 object schema TTL 초안:
  - `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/specs/rdf/semantic-lane-object-schema.draft.ttl`
- Fuseki/SPARQL 샘플 쿼리:
  - `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/specs/rdf/semantic-lane-object-schema.sample-queries.md`
- reveal semantic 상속 초안:
  - `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/specs/reveals/reveal-semantic-inheritance-draft.md`

이 경우 reasoner는 “토핑” 수준이 아니라, **‘파생 지식 생성기(derived facts generator)’**로 한 단계 역할이 커져.

다만 여기서도 **핫패스(사용자 조회)는 RDB 유지**, reasoner는 **오프라인/준실시간으로 파생 사실을 만들어 RDB에 적재**하는 쪽이 제일 안전하고 구현 리스크가 낮아.

---

## 1) 네 예시 4묶음(A/B/C/D)에서 reasoner가 필요한 지점

### A. 인물 타입/역할 추론

- “월터는 과학교사 vs 화학자?”, “제시는 제조자/유통자?”
    
- 이건 **(인물, role_type) 분류**를 만드는 문제라 reasoner가 딱 맞음.
    
- 핵심은 “둘 다” 같은 **다중 분류 + 시점(에피소드 구간)**.
    

### B. 관계 상속/역관계/전이

- 멘토 ↔ 멘티(역관계), 가족관계 전이(인척), 상하/파트너의 시점별 분기
    
- 이건 전형적인 **규칙(룰) 기반 파생 관계**.
    

### C. 사건 타입 분류(패턴)

- Deal made/broken, power shift
    
- 이건 OWL만으로 하기보다 **룰 기반 + 이벤트 시퀀스/패턴 매칭**이 필요해.
    
- 즉 reasoner라기보다 “룰 엔진/분류기” 성격.
    

### D. K-게이트 기반 노출 가능 여부

- 이건 이미 너희의 강점 영역.
    
- 단, reasoner가 만든 파생 사실도 **episode_end(또는 reveal episode)**를 붙여서 **게이트 대상**이 돼야 함.
    

---

## 2) 제일 단단한 설계: “Reasoner = 파생 사실 생성” + “Runtime = SQL 조회”

### 큰 그림

1. **원천 사실(Facts)**: 지금 RDB 이벤트/관계 테이블(approved only or 전체)
    
2. **규칙(Rules)**: RDF/OWL로 “개념/관계 정의” + 룰 DSL(아주 얇게)
    
3. **전개(Materialize)**: 배치 작업이 룰을 적용해서 **파생 사실(derived triples)** 생성
    
4. **서빙(Serve)**: 사용자 질문은 **파생 사실 테이블 + 원천 이벤트 테이블**을 SQL로 조회
    
5. **게이트(Gate)**: 파생 사실에도 episode 범위가 있어야 하고, 최종 응답에 K-gate 적용
    

이렇게 하면 “추론 질문 100개”가 전부 **SQL로 대답 가능**해져.  
reasoner는 “질문에 직접 응답”이 아니라 “대답할 재료를 미리 굽는 오븐”이 되는 거지. 🍞

---

## 3) 필요한 최소 데이터 모델(추론을 ‘운영 가능’하게 만드는 핵심)

### ✅ derived_fact (또는 event_triple 확장)

파생 사실을 한 테이블로 고정해.

- `subject_type` (CHARACTER / EVENT / ORG 등)
    
- `subject_id`
    
- `predicate_code` (예: IS_A, MENTORS, AFFILIATED_WITH, DEAL_MADE, POWER_SHIFT)
    
- `object_type`
    
- `object_id` (또는 값 string)
    
- `episode_start`
    
- `episode_end` ← **이게 K-게이트 핵심**
    
- `source_status` (APPROVED/GENERATED 등)
    
- `rule_id`
    
- `support_event_ids` (근거 event_id 목록, JSON 가능)
    
- `confidence` (선택)
    

**중요:** “Heisenberg=월터” 같은 민감한 동일인/정체성도 여기 들어가되, **episode_end가 특정 화수 이후**로 잡히면 K-게이트로 자동 차단됨.

---

## 4) 룰을 어떻게 쓰나: “OWL은 분류/스키마”, “룰은 파생 생성”

OWL만으로 네 질문들을 다 처리하려면 너무 무거워져.  
현실적으로는 이렇게 분리하는 게 깔끔해:

- **OWL/RDF**: 클래스/관계의 계층, 라벨, 금지 규칙 같은 “사전”
    
- **Rules (DSL)**: 파생 사실을 만드는 실제 로직
    

### 룰 예시(개념)

#### A) 역할/타입

- `IF character has occupation TEACHER → derived_fact (character IS_A SCIENCE_TEACHER)`
    
- `IF character participates in event with role=SUBJECT and predicate=COOK_METH → IS_A MANUFACTURER (episode range = event range)`
    
- `IF both conditions true at different episodes → 둘 다, 단 episode 범위 분리`
    

#### B) 역관계/전이

- `IF MENTORS(A,B) → MENTORED_BY(B,A)`
    
- `IF SIBLING(A,B) and SPOUSE(B,C) → IN_LAW(A,C)` (필요하면)
    
- `IF PARENT(A,B) and PARENT(B,C) → GRANDPARENT(A,C)` 같은 전이
    

#### C) 사건 타입 분류(패턴)

- `DEAL_MADE(event)` 조건: OFFER + ACCEPT + EXCHANGE가 동일 에피소드/근접 구간 내 존재
    
- `DEAL_BROKEN(event)` 조건: AGREEMENT 이후 VIOLATION 이벤트가 뒤따름
    
- `POWER_SHIFT(event)` 조건: command/control edge가 A→B에서 B→A로 바뀌거나, leader가 변경되는 사실 생성
    

이 파트는 “온톨로지 + 패턴”이라서, 룰 엔진이든 SQL 파이프든 **한쪽으로 고정**해야 해.  
내 추천은: **C는 reasoner보단 SQL 패턴 잡는 파이프**가 더 단순해(디버깅이 쉬움).

---

## 5) 질문 응답 흐름(너희 엔진에 자연스럽게 붙는 형태)

예: “월터는 과학교사와 화학자 중 무엇인가?”

1. 질문 템플릿 매칭 → `QUERY_TYPE: CHARACTER_ROLE_CLASSIFICATION`
    
2. SQL:
    
    - derived_fact에서 `(WALTER, IS_A, SCIENCE_TEACHER)`와 `(WALTER, IS_A, CHEMIST)`를
        
    - `episode_end <= K` 조건으로 조회
        
3. 둘 다 있으면 “둘 다” + “K시점 기준으로는 A만 노출” 같은 응답이 가능
    

예: “멘토면 멘티인가?”

- derived_fact에 역관계가 이미 생성돼 있으니 단순 조회
    

예: “K에서 Heisenberg=월터 노출 가능?”

- derived_fact에 `(HEISENBERG, SAME_AS, WALTER)`가 있고
    
- 그 fact의 `episode_end`가 K보다 크면 자동 차단
    

---

## 6) 여기서 reasoner가 ‘위에 얹는 정도’가 아닌 이유

네가 원하는 건 “필터”가 아니라 **지식 생성**이니까:

- reasoner/룰 엔진이 한 번 돌면서
    
    - **새 predicate들을 만들어내고**
        
    - **시점(episode range)을 부여하고**
        
    - **게이트 가능한 형태로 저장**  
        해야 함.
        

그래서 결론은:

- ✅ **Runtime은 여전히 SQL** (너희 철학/안전성 유지)
    
- ✅ **Reasoner는 오프라인 파생 지식 생성기** (이게 A/B/C/D를 전부 가능하게 함)
    
- ❌ “그냥 위에 얹는” 방식으로 runtime에서 즉석 추론하면
    
    - 성능/결정성/게이트 안정성이 확 떨어짐
        

---

원하면 다음 답변에서, 네가 적어준 A/B/C/D 질문을 기준으로:

1. `derived_fact.predicate_code` 최소 셋(예: IS_A, ROLE_AT_TIME, IN_LAW, MENTORS, PARTNER_AT_TIME, DEAL_MADE, DEAL_BROKEN, POWER_SHIFT, SAME_AS…)을 확정하고
    
2. 각 predicate를 만드는 **룰 1~2줄짜리 “운영용 규칙”**으로 내려서
    
3. “어떤 원천 테이블 컬럼을 봐야 생성되는지”까지 **딱 실행 단위**로 쪼개줄게.

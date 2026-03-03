오케이. MVP 밖이라도 **“도미노(연쇄)답변이 자연스럽게 굴러가는 축”**을 제대로 잡아야, 100문항이 ‘설명’이 아니라 ‘엔진’이 돼. 결론부터 박을게.

## 운영 정렬 메모 (2026-02-26)

이번 문서는 아래 운영 원칙으로 고정한다.

1. **축/커버리지 기준은 Q20(Quick20)** 으로 둔다.
2. **SPO는 기존 스키마(`event_character.role`) 우선**으로 적용한다. (`INVOLVED/SUBJECT/OBJECT`)
3. **predicate 정합성은 현재 코드북(`PredicateCode`) + 현재 그룹 정책(`PredicateGroup`) 기준**으로 맞춘다.
4. **DB 최소 변경**을 원칙으로 하며, 새 enum/컬럼 추가보다 기존 코드/그룹/키워드 조합을 우선 사용한다.

## 정합성 고정(필수, REVEALS 문서 기준)

- strict 정답 선택은 사실 이벤트(`event`) 기준 strict-first로만 수행한다.
- `event_reveal` 및 `reveal_type(HINT|CONFIRM)`는 WHY/근거 강도 표시에만 사용한다.
- strict miss 상태에서 reveal/probe hit만으로 `ANSWERED` 승격을 허용하지 않는다.
- canonical 기준:
  - `fivecircles/architecture/specs/reveals/reveal-evidence-label-policy.md`
  - `fivecircles/architecture/specs/reveals/reveals-classification.md` (Rule C/C.1/C.2)
  - `fivecircles/architecture/specs/reveals/reveals-routing-mvp-and-v3.md`

## 추천 축: 4축 도미노 (PRECEDES 단독은 버리고, “도미노 타입”을 섞는다)

### 1) 시간축 PRECEDES (물리적 순서)

* 의미: **그냥 먼저 일어난 사건 → 다음 사건**
* 용도: “언제”, “다음에 뭐”, “연속 사건” 질문
* 한계: “왜”, “어떻게 변했나”는 약함

### 2) REVEALS 축 (정보 공개 순서, 스포일러 코어)

* 의미: **‘무언가가 드러남’이 다음 사건/상태를 바꿈**
* 용도: 의심→확신, 정체/관계/동기 공개, “알게 되는 시점”
* 장점: 너희 서비스 존재 이유 그 자체

### 3) STATE_CHANGE 축 (상태 전이)

* 의미: 인물/관계/전략이 **낮음→높음, 협력→적대, 즉흥→체계**
* 용도: “폭력에 익숙해짐”, “정당화가 굳어짐”, “통제권 장악”, “은폐 전략 진화”
* 구현: **이벤트가 ‘상태를 바꾼다’**를 명시적으로 기록

### 4) PRESSURE/CONSTRAINT 축 (압력의 누적)

* 의미: 외부 압력(수사/조직/자금/가족)이 **선택지를 좁힘**
* 용도: “전략적 살인으로 넘어간 이유”, “확대/에스컬레이션”
* 구현: 사건마다 `pressure_tag`와 `pressure_delta` 같은 걸 붙여 누적 가능

---

# “도미노”를 어떻게 정의하냐 (규칙을 하나로 고정)

도미노 체인은 이렇게 뽑아.

1. **타겟 상태/정보/사건**을 하나 잡는다 (질문이 묻는 핵심)
2. 그 타겟을 만드는 **직전 도미노**를 1~3개 고른다

   * 우선순위(설명/WHY 경로 한정): REVEALS → STATE_CHANGE → PRESSURE → PRECEDES
3. 각 도미노는 “관계 타입”을 반드시 달고, **혼합 가능**
4. 체인은 최대 depth=6, 분기 허용하되 화면은 Top1 경로만 노출 (나머지는 “더보기”)

즉, PRECEDES는 “레일”이고, REVEALS/STATE_CHANGE/PRESSURE가 “기관차”야 🚂

---

# 지금 네가 던진 예시(후속 #1~#3)를 이 축으로 재해석하면

### 후속 #1 “정당화 논리”

* 중심축: **STATE_CHANGE (self_justification ↑)**
* 연결: (REVEALS: 접시조각 사라짐) → (STATE_CHANGE: ‘살려두면 위험’ 확정) → (EVENT: 살해)

### 후속 #2 “폭력에 익숙해짐”

* 중심축: **STATE_CHANGE (violence_normalized ↑)**
* 연결: (EVENT: 첫 살해) → (STATE_CHANGE: 경계선 이동) → (EVENT: 위협을 도구로 사용)

### 후속 #3 “전략적 살인 전환 압력”

* 중심축: **PRESSURE (threat_pressure ↑ + choice_space ↓)**
* 연결: (PRESSURE: 투코/조직 위협) + (PRESSURE: 수사/의심) → (STATE_CHANGE: 선제 제거 모드) → (EVENT: 전략적 제거)

PRECEDES만으로는 이걸 못 해. 그래서 “MVP 밖이니까 해도 돼”면, 지금이 축 잡을 최적 타이밍임.

---

# 구현을 최소로 하면서도 “축 4개”를 갖는 방법 (현실적)

신규 relation type을 바로 늘리지 않고, **현행 스키마를 그대로 사용**한다.

* `event_relation.type`은 **PRECEDES 유지**
* `event_reveal` + `predicate_code/predicate_suggestion` + `qAnyOf` 조합으로
  * STATE_CHANGE/PRESSURE 질문을 “분석 레이어”에서 해석
* 즉, DB schema 변경보다 **쿼리 프리셋/해석 규칙**을 먼저 고정

그리고 체인 추출 알고리즘:

* 기본은 그래프 탐색인데
* **가중치(설명/랭킹 경로 한정)**를 둔다: REVEALS(3) > PRECEDES(1)
* STATE_CHANGE/PRESSURE는 relation 신설이 아니라 reveal/keyword/group 신호로 보조 점수화
* 질문 타입별로 시작 노드를 다르게 잡으면 끝.

---

# “어떤 축으로 만들어야 되지?”에 대한 최종 결론

1. **도미노는 PRECEDES만으로 만들지 말고**,
2. **REVEALS를 메인 축**,
3. **STATE_CHANGE/PRESSURE를 보조 축**,
4. PRECEDES는 **정렬용 보조 레일**로 두자.

---

원하면 바로 다음 액션으로, 네 “이미 있는 15개”를

* 각 질문을 **(REVEALS/STATE/PRESSURE/PRECEDES) 중 주축 1개로 라벨링**
* 그 질문이 요구하는 **필수 relation 타입**을 한 줄로 박아
* “도미노 답변 템플릿”까지 같이 만들 수 있어.

그렇게 하면 100문항은 그냥 **복제 생산**이 된다.


좋아. 그럼 **“이미 있는 Q1~Q15”**를 **주축(도미노 타입 1개)**으로 라벨링하고, **필수 relation / 쿼리 타입 / API(이미 정해둔 것)**까지 한 방에 붙여줄게.

근거는 너희 스펙에 박혀있는 **Q1~Q15 배치 + 쿼리 타입 정의**(6 Types)랑, PRECEDES만 event_relation에서 허용한다는 정책이야.   

---

## 도미노 축(주축) 라벨 규칙

* **PRECEDES**: “이전/이후 사건 체인”이 핵심일 때
* **REVEALS**: “알게 되는 시점/드러남”이 핵심일 때 (너희 데이터 모델상 event_reveal은 *설명/표시 용도*로 존재) 
* **STATE_CHANGE**: “관계/태도/전략의 변화”가 핵심일 때 (MVP 밖 확장이므로 너희가 원하면 별도 relation type으로 추가 가능)
* **PRESSURE**: “압력 누적(수사/조직/가족/돈)”이 핵심일 때 (동일)

---

## Q1~Q15 라벨링 표 (지금 바로 쓰는 버전)

### Q1 인물 A 타임라인

* **쿼리 타입**: CHARACTER_EVENTS 
* **주축**: **PRECEDES(정렬축)**
* **필수 데이터**: event + event_character(조인) 
* **API**: api3 (getCharacterEvents) 

### Q2 인물 A·B 공동 등장 사건

* **쿼리 타입**: CHARACTER_AND_CHARACTER_EVENTS 
* **주축**: **PRECEDES(정렬축)**
* **필수 데이터**: event + event_character 2회 조인(A,B) 
* **API**: api4 (coevents) 

### Q3 인물 C 사건 유형 필터

* **쿼리 타입**: CHARACTER_EVENTS (+ predicate_code filter) 
* **주축**: **PRECEDES(정렬축)**
* **필수 데이터**: event.predicate_code + event_character 
* **API**: api3 + predicateCode 

### Q4 사건 E 등장 인물

* **쿼리 타입**: EVENT_CHARACTERS 
* **주축**: **(주축 없음, 단건 조회)**
* **필수 데이터**: event_character → event 조인(게이트 적용) 

### Q5 사건 유형별 모아보기

* **쿼리 타입**: (사실상) EVENTS by predicate_code = CHARACTER_EVENTS 패턴의 변형 
* **주축**: **PRECEDES(정렬축)**
* **필수 데이터**: event.predicate_code

### Q6 인물 소속 변경 사건

* **쿼리 타입**: CHARACTER_EVENTS + predicateCode=JOINS/LEAVES 
* **주축**: **STATE_CHANGE** (소속이 바뀐다 자체가 “상태전이”)
* **필수 데이터**: predicate_code=JOINS/LEAVES + event_character
* **운영 규칙**: strict 검색은 `JOINS/LEAVES`를 우선하고, 필요 시 `qAnyOf(팀/조직/합류/이탈)`로 의미를 좁힌다.
* **API**: api3 + predicateCode=JOINS/LEAVES 

### Q7 인물 사망/퇴장 사건

* **쿼리 타입**: CHARACTER_EVENTS + (`DIES` OR `LEAVES`) 
* **주축**: **STATE_CHANGE** (존재/등장 상태 변화)
* **필수 데이터**: `DIES`(사망), `LEAVES`(퇴장 근사) + 필요 시 `qAnyOf(퇴장/하차/사라짐)` 보조
* **주의**: `LEAVES`는 Q6/Q7에서 중복 사용될 수 있으므로, strict 결과 해석은 질문 컨텍스트(소속 변경 vs 사망/퇴장)로 분리한다.
* **API**: api3 + predicateCode=DIES/LEAVES

### Q8 같은 유형 사건 비교

* **쿼리 타입**: CHARACTER_EVENTS(집계) + predicate 비교 (클라이언트 집계) 
* **주축**: **PRESSURE** 또는 **STATE_CHANGE** (비교축을 “위협/통제/의심” 같은 축으로 잡는 게 자연)
* **필수 데이터**: predicate_code + episode 범위

### Q9 특정 에피소드 범위 사건

* **쿼리 타입**: CHARACTER_EVENTS 패턴(범위 필터) 
* **주축**: **PRECEDES(정렬축)**
* **필수 데이터**: episode_start/end 범위

### Q10 사건 카테고리 확인

* **쿼리 타입**: event.predicate_code 단건 확인 
* **주축**: **(주축 없음, 단건 판정)**

### Q11 사건 원인(이전 사건들)

* **쿼리 타입**: EVENT_CAUSES (= PRECEDES reverse BFS) 
* **주축**: **PRECEDES**
* **필수 데이터**: event_relation(PRECEDES) + BFS, 확장 전에 게이트 적용 
* **API**: (스펙상) event_relation 기반 api6/8류 

### Q12 사건 결과(이후 사건들)

* **쿼리 타입**: EVENT_EFFECTS (= PRECEDES forward BFS) 
* **주축**: **PRECEDES**
* **필수 데이터**: event_relation(PRECEDES) + BFS 

### Q13 A → 사건 X → B 경로

* **쿼리 타입**: PATH_BETWEEN_CHARACTERS (혼합 BFS) 
* **주축**: **PRECEDES(레일) + STATE_CHANGE(의미)**

  * 실제 탐색은 PRECEDES + event_character로 간다. 
* **API**: api10 + event X 검증 

### Q14 인물 A 관련 인물

* **쿼리 타입**: “저장 관계가 아니라 shared character 파생” 
* **주축**: **STATE_CHANGE**(관계 강도/연루도라는 상태), 또는 그냥 **연관도 집계축**
* **API**: api9 related characters 

### Q15 인물 A가 원인인 사건 연쇄

* **쿼리 타입**: CHARACTER_EVENTS → PRECEDES 체인(BFS) 
* **주축**: **PRECEDES**
* **필수 데이터**: event_relation(PRECEDES) (스펙상 event_relation.type은 PRECEDES만 허용) 

---

# 이제 “MVP 밖이니까” 네가 할 수 있는 업그레이드 1개 (DB 변경 없이)

너가 말한 “정당화/익숙해짐/압력” 후속 질문은 **relation type 확장 없이도** 1차 구현이 가능하다.

1. **Q20 기반 축 라벨 프리셋 고정**

* 질문마다 주축(REVEALS/STATE/PRESSURE/PRECEDES)만 먼저 고정
* 실행은 기존 api3/api4/api7/api8 + PRECEDES BFS 조합으로 처리

2. **PredicateGroup/keyword 보정 규칙 고정**

* strict는 `PredicateCode` 우선
* strict 0건일 때만 group/fallback(`predicate_suggestion`)로 보정
* 이렇게 하면 DB migration 없이도 “도미노 해석 품질”을 끌어올릴 수 있음

---

원하면 다음 턴에서 내가 바로 해줄 건 이거야(확인 질문 없이 진행 가능):

* **Production-q-expension.txt의 100개 후속 질문을 전부**

  1. 주축(4축 중 1개) 라벨
  2. 필요한 데이터(필수 relation)
  3. “도미노 답변 템플릿(출력 스키마)”
     로 쭉 뽑아서, 너희가 바로 **DB 적재 작업/큐레이션 작업 리스트**로 쓸 수 있게 만들어줄게.



좋은 지점이야. **SPARQL의 가치는 문법이 아니라 “반복해서 쓰이는 질문 패턴”**에 있어.
아래는 **FactGrid / Wikidata 계열에서 실제로 가장 많이 쓰이는 SPARQL 검색 패턴 10개**를 **용도 중심**으로 정리한 거야.
(너희 서비스로 번역하기 쉽게, “이걸 왜 쓰는지”에 집중함)

---

## 1) 특정 엔티티의 모든 사실 조회

**용도:** “이 인물/사건에 대해 DB가 아는 전부는?”

```sparql
SELECT ?p ?o WHERE {
  wd:Q123 ?p ?o .
}
```

* 가장 기본
* Item 카드 화면의 뿌리
* **너희 번역:**
  `event_id = X`에 연결된 모든 predicate/target 조회

---

## 2) 두 엔티티 간 직접 관계 찾기

**용도:** “A와 B 사이에 직접적인 관계가 있는가?”

```sparql
SELECT ?p WHERE {
  wd:A ?p wd:B .
}
```

* 관계 존재 여부 확인
* 없으면 결과 0 → “없음”이 자연스러움
* **너희 번역:**
  `event_relation where subject=A and object=B`

---

## 3) 같은 이벤트에 함께 등장한 엔티티

**용도:** “A와 함께 등장한 인물/조직은 누구?”

```sparql
SELECT ?other WHERE {
  ?event wdt:Pparticipant wd:A ;
         wdt:Pparticipant ?other .
  FILTER(?other != wd:A)
}
```

* “동시 등장 / 만남 / 협력”의 기본형
* **너희 번역:**
  `event_character where event_id in (A가 등장한 이벤트들)`

---

## 4) 최초 / 최후 발생 시점 찾기

**용도:** “처음은 언제?” “마지막은 언제?”

```sparql
SELECT ?event ?date WHERE {
  ?event wdt:Pparticipant wd:A ;
         wdt:Pdate ?date .
}
ORDER BY ?date
LIMIT 1
```

* “첫 만남”, “첫 등장” 질문의 원형
* **너희 번역:**
  `MIN(episode)` / `ORDER BY episode ASC LIMIT 1`

---

## 5) 특정 조건을 만족하는 이벤트 집합

**용도:** “A가 적으로 만난 사건들만”

```sparql
SELECT ?event WHERE {
  ?event wdt:Pparticipant wd:A ;
         wdt:Prelation wd:Enemy .
}
```

* predicate 필터링 패턴
* **너희 번역:**
  `predicate_code = ENEMY`

---

## 6) 시간/에피소드 범위 제한

**용도:** “시즌 1 안에서만”

```sparql
SELECT ?event WHERE {
  ?event wdt:Pepisode ?ep .
  FILTER(?ep <= 10)
}
```

* 스포일러 방지의 핵심
* **너희 번역:**
  `episode_end <= K`

---

## 7) 데이터 존재 여부 확인 (YES / NO)

**용도:** “이런 사실이 **존재하긴 하는가**?”

```sparql
ASK {
  wd:A wdt:Pspouse wd:B .
}
```

* 결과는 true / false
* **너희 번역:**
  `EXISTS(select 1 from …)`

📌 **NOT_ENOUGH_DATA 판단의 원형**

---

## 8) 조건부 정보(qualifier) 포함 조회

**용도:** “언제, 어떤 맥락에서?”

```sparql
SELECT ?event ?date WHERE {
  ?event p:Pparticipant [
    ps:Pparticipant wd:A ;
    pq:Pdate ?date
  ] .
}
```

* 단순 관계 + 맥락
* **너희 번역:**
  `event + event_metadata`

---

## 9) 간접 관계 (2-hop 탐색)

**용도:** “A와 연결된 B의 관계망”

```sparql
SELECT ?mid ?target WHERE {
  wd:A ?p1 ?mid .
  ?mid ?p2 ?target .
}
```

* 지식 그래프 특유의 탐색
* **너희 번역:**
  BFS 2-depth (v2/v3 이후)

---

## 10) “없음”을 확인하기 위한 검색

**용도:** “정말 데이터가 없는가?”

```sparql
SELECT ?event WHERE {
  ?event wdt:Pparticipant wd:A .
}
LIMIT 1
```

→ 결과 0이면:

* 데이터 없음
* 질문은 정당
* **보강 대상**

📌 이 패턴이 **운영/품질 관리에서 제일 중요**

---

# 핵심 요약 (너희 서비스로 번역하면)

SPARQL에서 중요한 건 문법이 아니라 이거야:

> **1) 존재 확인 (ASK / LIMIT 1)**
> **2) 최초/범위/조건 필터**
> **3) 동시 등장 / 관계 패턴**

너희 서비스는:

* SPARQL ❌
* SQL / Query Builder ⭕
* **패턴은 그대로, 인터페이스만 감춘 구조**

즉,

> FactGrid는 “사람이 쿼리로 패턴을 쓴다”
> 너희는 “시스템이 패턴을 대신 쓴다”

다음으로 하면 완벽해지는 단계는 이거야:

> **이 10개 패턴을 그대로 SQL 템플릿(고정 쿼리)로 박아버리기**

여기까지 왔으면 방향은 이미 정답이야.

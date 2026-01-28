좋아. 그럼 **“Predicate(동사)를 어디까지, 어떻게 표준화해야 그래프가 안 망가지는가”**를
**방법론 → 규칙 → 바로 쓰는 목록** 순서로 딱 정리해줄게.
(이건 철학이 아니라 **운영 규칙**이야.)

---

## 0) 결론부터 한 줄

> **Predicate는 ‘사건의 종류(type)’이지, 자연어 문장이 아니다.**
> **MVP에서는 20개 이내의 폐쇄 집합(closed set)** 으로 고정해야 그래프가 산다.

---

## 1) 왜 Predicate 표준화가 필수냐 (망하는 지점)

트리플스토어 방식에서 가장 흔한 실패는 이거야:

* (A) — *kills* — (B)
* (A) — *defeats* — (B)
* (A) — *eliminates* — (B)

사람 눈엔 비슷하지만, **그래프에선 전부 다른 predicate**다.
→ 탐색, 집계, 차단, 설명 **전부 불가능**해짐.

그래서 온톨로지에서는 항상:

* ❌ “자연어 동사”
* ✅ “의미 분류용 동사 코드”

를 쓴다.

---

## 2) Predicate 설계의 4대 원칙 (이거 안 지키면 그래프 망가짐)

### 원칙 1️⃣ Predicate는 **사건의 종류(type)** 다

* 감정 ❌
* 평가 ❌
* 해석 ❌

> Predicate는
> “이 Event를 **어떤 박스에 넣을 것인가**”를 정하는 라벨이다.

---

### 원칙 2️⃣ 하나의 Event = 하나의 핵심 Predicate

* “A가 B를 배신하고 떠난다” ❌
* → 두 개로 쪼갠다:

  * `BETRAYS`
  * `LEAVES`

**복합 동사 금지.**

---

### 원칙 3️⃣ Predicate는 **관계와 역할을 암시해야 한다**

좋은 Predicate는 자동으로 질문을 만들어낸다.

* `JOINS` → 어디에?
* `REVEALS` → 무엇을?
* `DEFEATS` → 누구를?

이 질문들이 바로

* `event_character`
* `event_relation`
* `event_reveal`
  로 이어진다.

---

### 원칙 4️⃣ Predicate 수는 늘리지 말고, Event를 늘려라

표현이 애매해질 때의 올바른 선택:

* ❌ 새로운 predicate 추가
* ✅ Event를 더 쪼갠다

---

## 3) MVP용 Predicate 분류 체계 (권장)

### A. **상태 변화 (State Change)**

| Predicate    | 의미       |
| ------------ | -------- |
| `DIES`       | 사망       |
| `INJURED`    | 부상       |
| `RECOVERS`   | 회복       |
| `TRANSFORMS` | 신분/상태 변화 |

---

### B. **관계 변화 (Relationship)**

| Predicate     | 의미       |
| ------------- | -------- |
| `MEETS`       | 처음 만남    |
| `JOINS`       | 집단/팀에 합류 |
| `LEAVES`      | 집단/팀 이탈  |
| `BETRAYS`     | 배신       |
| `ALLIES_WITH` | 동맹 형성    |

---

### C. **행동/충돌 (Action / Conflict)**

| Predicate  | 의미   |
| ---------- | ---- |
| `ATTACKS`  | 공격   |
| `DEFEATS`  | 패배시킴 |
| `KILLS`    | 살해   |
| `ESCAPES`  | 탈출   |
| `CAPTURES` | 포획   |

---

### D. **정보 드러남 (Reveal / Knowledge)** ⚠️ 핵심

| Predicate   | 의미           |
| ----------- | ------------ |
| `REVEALS`   | 정체/사실이 드러남   |
| `DISCOVERS` | 주체가 사실을 알게 됨 |
| `LEARNS`    | 인지 변화        |

👉 이 계열은 **거의 항상 `event_reveal`과 함께** 간다.
👉 스포일러 정책의 핵심 트리거.

---

### E. **이동/위치 (Optional, MVP 후반)**

| Predicate | 의미 |
| --------- | -- |
| `ARRIVES` | 도착 |
| `DEPARTS` | 출발 |
| `RETURNS` | 귀환 |

---

## 4) “그럼 트리플은 실제로 어떻게 생기냐”

자연어:

> “존이 백색 보행자를 죽인다”

온톨로지화:

* Event:

  * `predicate = KILLS`
* 관계:

  * `(Event) — INVOLVES → Jon`
  * `(Event) — INVOLVES → WhiteWalker`
* 범위:

  * `episode_start = 5`
  * `episode_end = 5`

Event가 **트리플을 담는 컨테이너**인 구조다.

---

## 5) 문서/스펙에 반드시 써야 하는 문장 (중요)

이 한 줄을 스펙에 박아야 팀이 안 흔들린다:

> **Predicate is a controlled vocabulary representing the event type.
> It is not a natural-language verb and must be selected from a fixed list.**

---

## 6) 실무 체크리스트 (이벤트 추가 시)

Event 하나 추가할 때, 이 5개 질문만 통과하면 OK:

1. 한 문장으로 말할 수 있는가?
2. Predicate 하나로 분류되는가?
3. episode_end를 명확히 찍을 수 있는가?
4. INVOLVES 대상이 명확한가?
5. REVEALS라면 “무엇이 드러났는지” 명확한가?

---

## 마지막 요약

* 트리플은 **의미 단위**
* Event는 **시간을 가진 의미 묶음**
* Predicate는 **그래프를 분류하는 태그**
* Predicate를 늘리면 그래프가 죽고
* Event를 늘리면 그래프가 산다

다음으로 가면 자연스러운 단계는 이거야:

> **“Predicate를 코드(enum)로 박을까, DB 테이블로 뺄까?”**

원하면 그 선택지도 **MVP 기준으로 딱 하나** 골라서 정리해줄게.

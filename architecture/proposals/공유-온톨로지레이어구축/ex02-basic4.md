## 온톨로지에서 필수인 기본 4개 항목 



---

## 온톨로지 기본 4개 분류 (가장 표준적인 틀)

온톨로지에서 가장 널리 쓰이는 최소 분해는 이거야:

1. **Entity (개체)**
2. **Event (사건)**
3. **Predicate / Attribute (속성·사건의 성격)**
4. **Relation (관계)**

---

## 지금 nospoiler 모델에 정확히 매핑해보면

### ① Entity

* Character
* Drama
* Episode
  → “시간을 초월해서 존재하는 것”

---

### ② Event

* Event 자체 (id, episode_start/end, summary)
  → “시간에 묶여 발생한 것”

---

### ③ Predicate (사건의 분류 / 성격)

👉 **여기가 `predicate_code`**

* BATTLE
* DEATH
* BETRAYAL
* CONFESSION …

의미:

> “이 사건은 **무슨 종류의 사건인가**?”

온톨로지 4분류 중 **3번**에 정확히 해당.

---

### ④ Relation (사이의 연결)

👉 **여기가 PRECEDES / RELATED / REVEALS / INVOLVES**

* Event ↔ Event : PRECEDES, RELATED, REVEALS
* Event ↔ Character : INVOLVES

의미:

> “이것과 저것은 **어떤 관계로 연결돼 있는가**?”

온톨로지 4분류 중 **4번**.

---

## 그래서 네 질문의 정확한 답

> **“involves, related는 predicate_code의 enum인가?”**
> ❌ 아니고

> **“이거 온톨로지 기본 4개 분류 중 하나인가?”**
> ✅ **그렇다. ‘Relation’이다.**

그리고 `predicate_code`는
👉 **Predicate (사건의 분류)**

---

## 왜 이게 헷갈렸냐 (중요)

자연어에서는

* “A involves B”
* “A is a battle”

둘 다 **동사**처럼 보이거든.

하지만 온톨로지에서는:

* **Predicate** = 사건 *자체*를 분류
* **Relation** = 둘 *사이*를 연결

이 차이를 지금 정확히 짚은 거야.

---

## 한 줄로 정리 (이 문장만 기억하면 끝)

> **predicate_code는 ‘사건이 무엇이냐’,
> relation은 ‘사건들이 어떻게 엮였냐’다.**

이걸 기준으로 보면,
지금 네 설계는 **온톨로지 기본 구조를 아주 정석적으로 밟고 있어.**

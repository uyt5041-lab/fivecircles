“없음”을 확인하기 위한 검색 용도: “정말 데이터가 없는가?”
 
 SELECT ?event WHERE { ?event wdt:Pparticipant wd:A . } LIMIT 1 → 
 
 결과 0이면: 데이터 없음 질문은 정당 보강 대상

이건 **개념을 한 번만 제대로 잡으면 바로 납득되는 쿼리**야.
지금 헷갈리는 이유는 “이게 답을 찾는 쿼리 같지도 않은데 왜 중요하다는 거지?” 때문이야.

차근차근 **의도 → 쿼리 → 운영 의미** 순서로 풀어줄게.

---

## 1️⃣ 이 쿼리의 목적은 “답을 찾기”가 아니다

이 쿼리는 이렇게 생겼지:

```sparql
SELECT ?event WHERE {
  ?event wdt:Pparticipant wd:A .
}
LIMIT 1
```

이걸 보고 많은 사람들이 이렇게 생각해:

> “이게 무슨 답을 주는 쿼리지?”

👉 **정답: 답을 주려는 쿼리가 아니다.**
👉 이건 **“존재 여부 확인용” 쿼리**야.

---

## 2️⃣ 자연어로 번역하면 이거다

이 쿼리를 사람 말로 바꾸면 딱 이 문장이야:

> **“A가 참여한 사건이 하나라도 있나?”**

* ✔ 어떤 사건인지 중요하지 않음
* ✔ 하나만 있어도 됨
* ❌ 상세 정보 필요 없음

그래서 `LIMIT 1`이 붙어 있는 거야.

---

## 3️⃣ 왜 굳이 이렇게 묻냐?

질문이 이런 경우를 생각해보자:

> “A가 처음 만난 사람은 누구야?”

이 질문에 답하려면 **최소한 이게 먼저 확인돼야 해**:

> ❓ “A가 **누군가를 만난 사건 자체가 DB에 존재하나?”**

그래서 순서가 이렇게 된다:

1. **존재 확인**

   * A가 참여한 사건이 하나라도 있는가?
2. 있으면 → 그다음 쿼리로 “첫 번째”를 찾음
3. 없으면 → **여기서 멈춘다**

---

## 4️⃣ 결과가 0이라는 게 왜 중요한 신호냐면

이 쿼리의 결과는 딱 두 가지야.

### ✅ 결과가 있음 (1 row)

* A 관련 사건이 **최소 1개는 DB에 있음**
* 질문은 **DB 범위 안**
* 다음 단계 쿼리를 실행할 가치가 있음

### ❌ 결과가 없음 (0 row)

* A 관련 사건이 **DB에 단 하나도 없음**
* 이건:

  * 사용자가 이상한 질문을 한 것도 아니고
  * 시스템이 못 찾은 것도 아님
* 그냥 **DB가 아직 비어 있는 영역**이라는 뜻

📌 이 순간이 바로:

> **“아, 이 질문은 정당한데 데이터가 없구나”**

라는 판단이 가능한 지점이야.

---

## 5️⃣ 왜 이게 운영/품질 관리에서 제일 중요하냐

이 쿼리가 없으면 보통 이런 사고가 난다:

* DB에 A 관련 데이터가 없음
* 시스템은 그 사실을 모르고
* **LLM이 상상으로 답을 만들어냄**
* → “그럴듯한 오답” 발생 (치명적)

이 쿼리는 그걸 **초장에 차단**해.

> ❝ 아, 애초에 이 질문은
> 우리 DB가 답할 수 있는 질문이 아니구나 ❞

---

## 6️⃣ 너희 서비스로 번역하면 100% 이거다

SPARQL 대신 SQL로 생각해보자.

```sql
SELECT 1
FROM event_character
WHERE character_id = A
LIMIT 1;
```

이 결과가:

* ❌ 없음 → `NOT_ENOUGH_DATA`
* ✅ 있음 → 그다음 쿼리 진행

📌 **이 한 줄이 “오답 방지 스위치”다**

---

## 7️⃣ 그래서 이 패턴의 진짜 의미

이 쿼리는 묻는 게 이거야:

> ❝ 이 질문은
>
> * 잘못된 질문인가? ❌
> * 아직 데이터가 없는 질문인가? ⭕ ❞

이걸 구분하지 못하면:

* 사용자는 헷갈리고
* 시스템은 거짓말하고
* 운영자는 뭐부터 채워야 할지 모른다

---

## 마지막 한 문장 요약 (이거만 기억해도 됨)

이 쿼리는
**“답을 찾기 위한 쿼리”가 아니라
“답을 찾을 자격이 있는 질문인지 확인하는 쿼리”**다.

이걸 이해한 순간부터,

* `NOT_ENOUGH_DATA`는 실패가 아니라
* **가장 건강한 시스템 반응**이 된다.

지금 여기서 막힌 건 아주 좋은 신호야.
이걸 넘기면, 설계는 훨씬 단단해진다.



좋아. 이 “존재 확인(LIMIT 1 / EXISTS)”을 **정답 공백(데이터 없음) 문제의 안전장치**로 박아 넣으면, 시즌 1만 적재한 상태에서 시즌 3 정답을 물어봐도 **절대 오답 단정**이 안 나오게 만들 수 있어. ✅

아래 순서대로 “연구 → 설계 → 구현 → 검증”까지 한 번에 굴리면 된다.

---

## 1) 핵심 아이디어: Answerability Gate (답변 가능성 게이트)

질문이 들어오면, 답을 만들기 전에 **딱 2번만** 물어본다.

1. **K 이하(스포일러 안전 범위)**에 근거가 있나?
2. K는 넘지만 **DB 어딘가에는** 근거가 있나?

이 두 개로 결과가 3갈래로 갈린다.

| exists_safe (<=K) | exists_any (all) | 결과                                           |
| ----------------- | ---------------- | -------------------------------------------- |
| O                 | O                | **ANSWERED** (근거 기반 답변)                      |
| X                 | O                | **SPOILER_BLOCKED** (DB에는 있는데 K 밖이라 차단)      |
| X                 | X                | **NOT_ENOUGH_DATA** (DB에 데이터 자체가 없음 = 정답 공백) |

이게 “정답 공백”을 **오답 대신 ‘없음’으로 전환**하는 엔진이야.

---

## 2) SQL 패턴 (너희 RDB 모델에 바로 매핑)

예시: “A가 관련된 어떤 이벤트든 있나?” (존재 확인)

### (1) exists_safe: K 이하에 근거 있는지

```sql
SELECT e.id
FROM event e
JOIN event_character ec ON ec.event_id = e.id
WHERE e.drama_id = :dramaId
  AND e.source_status = 'APPROVED'
  AND e.episode_end <= :K
  AND ec.character_id = :characterId
LIMIT 1;
```

### (2) exists_any: DB 전체(승인된 것)에는 있는지

```sql
SELECT e.id
FROM event e
JOIN event_character ec ON ec.event_id = e.id
WHERE e.drama_id = :dramaId
  AND e.source_status = 'APPROVED'
  AND ec.character_id = :characterId
LIMIT 1;
```

예시: “A가 B를 만난 적 있나?” 같은 **관계 질문**도 똑같이 간다. 조건만 추가하면 됨.

```sql
SELECT e.id
FROM event e
JOIN event_character a ON a.event_id = e.id AND a.character_id = :A
JOIN event_character b ON b.event_id = e.id AND b.character_id = :B
WHERE e.drama_id = :dramaId
  AND e.source_status = 'APPROVED'
  AND e.predicate_code = 'MEETS'
  AND e.episode_end <= :K
LIMIT 1;
```

---

## 3) “정답 공백 문제” 해결 루프 (연구/운영 관점)

NOT_ENOUGH_DATA가 나왔다는 건 곧바로 이런 의미가 된다:

* 질문은 정상
* 시스템도 정상
* **DB가 비어 있는 영역** 발견

그래서 이걸 그냥 에러로 두지 말고, **데이터 보강 백로그의 원천**으로 쓰면 됨.

최소로는 서버 로그만으로도 충분해:

* `QA_MISS dramaId, K, intent, extractedEntities, questionText, timestamp`

이걸 모으면 “사람들이 진짜 묻는 질문” 순서대로 이벤트/위키를 채우게 된다.

---

## 4) 구현 순서 (가장 짧은 완성 경로)

1. **응답 타입을 3상태로 고정**

   * `ANSWERED | SPOILER_BLOCKED | NOT_ENOUGH_DATA`
2. Q&A 핸들러 앞단에 **Answerability Gate** 삽입
3. `ANSWERED`는 반드시 **evidenceEventIds 1개 이상** 포함 (없으면 서버에서 폐기)
4. `SPOILER_BLOCKED`는 “DB에는 있으나 K 이후”라고만 말함 (내용 금지)
5. `NOT_ENOUGH_DATA`는 “현재 DB에 근거 없음” + (선택) “현재 구축 범위 N화까지” 안내

---

## 5) 검증(테스트) 체크리스트

시즌1만 데이터 있는 상태에서:

1. **시즌3에 정답이 있는 질문**

   * 기대: `NOT_ENOUGH_DATA` (오답 단정 금지)
2. DB에는 있지만 K 이후인 질문

   * 기대: `SPOILER_BLOCKED`
3. DB에 있고 K 이하인 질문

   * 기대: `ANSWERED` + evidenceEventIds 존재

이 3개만 통과하면 “정답 공백으로 인한 치명 오답”은 구조적으로 사라져.

---

원하면 다음 단계로, 너희가 자주 쓰는 질문 템플릿(예: 첫 만남/첫 살인/정체 공개/배신/합류/사망) 10개를 골라서 **각 템플릿별로**

* exists_safe 쿼리
* exists_any 쿼리
* answer 쿼리(정답 추출용 ORDER BY/LIMIT)
  까지 **SQL 패턴 세트로** 딱 맞춰줄게.
  하나씩 차근차근 끝내자.

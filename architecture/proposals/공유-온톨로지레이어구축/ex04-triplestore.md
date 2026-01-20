## 이벤트(노드) 생성 시 트리플로 분해하는 예시

**Event(e)  -> (Subject) (predicates) (object)**

Event e100
- type: KILL
- episode_start = 8
- episode_end = 8
- summary: "John Snow kills a White Walker"

✅ 구조적 트리플 (최소)
(e100) — INVOLVES → (John Snow)
(e100) — INVOLVES → (White Walker)
(e100) — OCCURS_IN → (Episode 8)

(선택) 의미 보강 트리플
(e100) — HAS_PREDICATE → (KILLS)
(e100) — HAS_AGENT → (John Snow)
(e100) — HAS_PATIENT → (White Walker)


**해당 이벤트 조회를 포함하는 자연어 쿼리:**
존스노우가 백귀를 잡은 게 에피소드 몇화였지?(사실)
존스노우의 적은 누구?()


X - 잘못된 예시:

>  e100 -> (John Snow) (Kills) (White Walker)

> triple1 -> (Episode 8) (Involves) (John Snow)
> triple2 -> (John Snow) (fights against) (White Walker)
> triple3 -> (White Walker) (fights against) (John Snow)
> triple4 -> (John Snow and White Walker) (Are against) (Each other)

잘못된예시를 온톨로지 관점에서 분해해보면
원래 의도한 사실

“John Snow가 White Walker를 죽였다 (Episode 8)”

이건 사실 하나다.
그래서 Event는 1개여야 한다.

왜 문제냐
❌ triple1
(Episode 8) (Involves) (John Snow)


Episode는 컨텍스트지, 행위 주체가 아님

이건 “John Snow가 8화에 등장했다”라는 다른 사실

지금 Event(e100)의 핵심과는 분리해야 함

👉 ❌ Event 생성용 트리플로는 부적합

❌ triple2, triple3 (대칭 중복)
(John Snow) (fights against) (White Walker)
(White Walker) (fights against) (John Snow)


“fights against”는 상태/관계이지 사건이 아님

게다가 같은 의미를 두 번 저장

나중에 질의하면 중복 결과가 터진다

👉 이런 건 Event의 predicate로 흡수해야 한다

❌ triple4 (복합 주어)
(John Snow and White Walker) (Are against) (Each other)


이건 온톨로지에서 거의 금기 패턴이다.

주어는 항상 단일 엔티티

“and / each other”는 자연어지 그래프 노드가 아님

질의 불가능, 재사용 불가

👉 ❌ 절대 쓰면 안 되는 형태

5️⃣ 자연어 질의와의 매핑을 보면 더 명확해진다
질의 1

존스노우가 백귀를 잡은 게 에피소드 몇화였지?

정답 흐름

Character(John Snow)
 → INVOLVES
 → Event(type=KILL, object=White Walker)
 → episode_start / end


👉 Event 기반이 정답
👉 triple2~4는 전혀 필요 없음

질의 2

존스노우의 적은 누구?

이건 사실 Event 질의가 아니다.

이건 두 가지 중 하나다:

관계 요약 질의

“John Snow가 적대 행위를 한 대상들”

→ KILL / FIGHT / BETRAY Event들의 object 집합

추상 관계 모델

별도 ENEMY_OF 관계 (MVP 밖)

👉 지금 구조에서는
Event들을 모아서 파생 질의로 답하는 게 정답이다.

6️⃣ 올바른 트리플 분해 규칙 (암기용)
✅ 해야 하는 것

Event = 사실 하나

트리플은 Event를 설명한다

주어는 항상 단일 엔티티

의미 중복은 Event 내부로 흡수

❌ 하지 말 것

자연어 문장을 그대로 트리플로 쪼개기

대칭 관계를 양방향 트리플로 저장

“A and B”, “each other” 같은 복합 노드

Episode를 행위 주체처럼 쓰기



정리:

Event 1개 + 최소 구조 트리플 몇 개가 올바른 구조

=================
>>>>>>>>>>>>>>>>>


## 우리 프로젝트에서 이벤트 생성 시점에 트리플로 분해하는 예시



**“Event는 summary로 저장 + 트리플 분해는 event 생성 시점에 구조 테이블로 저장”**을 전제로, 바로 구현 가능한 형태로 정리할게.

---

## 1) `CreateEventRequest` JSON 스펙 (event-service)

### `POST /events`

```json
{
  "dramaId": 1,
  "episodeStart": 3,
  "episodeEnd": 3,

  "summary": "John Snow kills a White Walker.",
  "predicateCode": "KILLS",

  "source": {
    "sourceType": "WIKI_ENTRY",
    "sourceId": 9000123,
    "reviewStatus": "APPROVED"
  },

  "characters": [
    { "characterId": 101, "role": "SUBJECT" },
    { "characterId": 202, "role": "OBJECT" }
  ],

  "reveals": [
    {
      "revealType": "FACT",
      "targetType": "CHARACTER",
      "targetId": 202,
      "note": "White Walkers can be killed."
    }
  ],

  "relations": [
    { "type": "PRECEDES", "toEventId": 5555 }
  ]
}
```

### 필드 규칙(핵심만)

* `predicateCode` = 사건의 “동사/타입” (트리플의 **P**)
* `characters[]` = 참여자 + 역할 (트리플의 **S/O** 포함)
* `reveals[]` = “알게 됨”이 필요한 경우만 (없어도 됨)
* `relations[]` = 사건↔사건 연결 (없어도 됨)
* `summary`는 **표시용 텍스트**라서 요청에서 받는 게 가장 단순함
  (event-service는 보통 캐릭터 “이름”을 모르니, 여기서 자동 생성하려고 하면 경계가 깨짐)

---

## 2) event-service 저장 순서 (트랜잭션 단위)

> 원칙: **event를 먼저 만들고(event_id 확보), 나머지를 전부 event_id에 붙인다.**

### 트랜잭션 흐름

1. **INSERT event** → `event_id` 획득
2. **INSERT event_character** (N건)
3. (옵션) **INSERT event_reveal** (M건)
4. (옵션) **INSERT event_relation** (R건)
5. COMMIT (중간에 하나라도 실패하면 ROLLBACK)

### SQL 느낌(의사코드)

```sql
BEGIN;

INSERT INTO event (
  drama_id, episode_start, episode_end,
  summary, predicate_code,
  source_type, source_id, review_status
) VALUES (
  :dramaId, :episodeStart, :episodeEnd,
  :summary, :predicateCode,
  :sourceType, :sourceId, :reviewStatus
);

SET @event_id = LAST_INSERT_ID();

-- characters
INSERT INTO event_character (event_id, character_id, role)
VALUES (@event_id, :characterId, :role)  -- 여러 건

-- reveals (optional)
INSERT INTO event_reveal (event_id, reveal_type, target_type, target_id, note)
VALUES (@event_id, :revealType, :targetType, :targetId, :note);

-- relations (optional)
INSERT INTO event_relation (from_event_id, to_event_id, type)
VALUES (@event_id, :toEventId, :type);

COMMIT;
```

---

## 3) 기본값 규칙 (role/predicate가 비었을 때)

### 필수 검증(요청 자체를 400으로 거절)

* `dramaId` 없음 → 거절
* `episodeStart/episodeEnd` 없음 → 거절
* `episodeEnd < episodeStart` → 거절
* `characters`가 아예 없음 → 거절 (사건인데 아무도 없으면 질의 기반이 무너짐)

### 기본값(있으면 좋고 없어도 안 깨지게)

* `predicateCode` 누락 → `"UNKNOWN"`
* `role` 누락 → `"INVOLVED"`
* `reveals` 누락 → 저장 안 함
* `relations` 누락 → 저장 안 함
* `reviewStatus` 누락 → `"APPROVED"` (승인 플로우 기반이면 이게 가장 보수적이고 단순)

---

# 4) 예시: (John Snow) (KILLS) (White Walker) 입력 → 트리플 분해

## A) 사용자 입력(라벨링 UI에서)

* Subject: **John Snow** (characterId=101)
* Predicate: **KILLS** (predicateCode="KILLS")
* Object: **White Walker** (characterId=202)
* episode: 3~3
* summary: "John Snow kills a White Walker."

이걸 “트리플”로 쓰면:

* **S** = Character(101, John Snow)
* **P** = KILLS
* **O** = Character(202, White Walker)

## B) event-service로 보내는 CreateEventRequest

```json
{
  "dramaId": 1,
  "episodeStart": 3,
  "episodeEnd": 3,
  "summary": "John Snow kills a White Walker.",
  "predicateCode": "KILLS",
  "source": { "sourceType": "WIKI_ENTRY", "sourceId": 9000123, "reviewStatus": "APPROVED" },
  "characters": [
    { "characterId": 101, "role": "SUBJECT" },
    { "characterId": 202, "role": "OBJECT" }
  ]
}
```

## C) DB에 저장되는 결과(트리플 “분해”)

### 1) event (노드 1개)

* id = 7001 (예시)
* drama_id = 1
* episode_start = 3
* episode_end = 3
* predicate_code = "KILLS"
* summary = "John Snow kills a White Walker."
* source_type/source_id/review_status = (WIKI_ENTRY, 9000123, APPROVED)

### 2) event_character (S/O 슬롯이 여기로 “쪼개짐”)

* (event_id=7001, character_id=101, role=SUBJECT)
* (event_id=7001, character_id=202, role=OBJECT)

### 3) event_reveal / event_relation

* 이 예시는 “드러남”이나 “선후 사건”을 안 넣었으니 **저장 없음**
* 필요하면 다음처럼 추가됨:

  * reveal: “White Walker can be killed”
  * relation: PRECEDES / RELATED 등

---

원하면 다음으로 바로 이어서,

* `predicateCode` 최소 표준 enum 세트(10~20개)랑
* `role`(SUBJECT/OBJECT/INVOLVED)만으로도 충분히 커버되는 “템플릿 기반 summary 작성 규칙”
  까지 한 번에 고정해줄게.



2) 트리플스토어가 “필요”가 아니라 “유리”해지는 경우

트리플스토어가 빛나는 순간은 이런 상황이야:

관계 종류(Predicate)가 폭발적으로 늘어날 때
RDB에서 컬럼/테이블을 계속 늘리기보다, 새로운 관계를 바로 추가하고 싶을 때

SPARQL 같은 그래프 질의가 핵심 제품 기능일 때
“이런 패턴의 연결을 찾아라”를 질의 언어로 세게 밀어붙일 때

정식 추론(OWL/RDFS)까지 하려는 경우
예: “A가 B의 상위개념이면 A의 속성이 B에도 적용” 같은 계층 추론

외부 지식그래프(위키데이터 등)와 정합성 있게 합치려는 경우
URI 기반으로 표준화된 링크를 대규모로 붙일 때

즉, Level 4 자체가 트리플스토어를 강제하진 않지만,
Level 4를 “그래프 중심 제품”으로 풀겠다면 트리플스토어가 편해질 수 있어.



좋아. 여기서부터가 “온톨로지 맛”이 확 나오는 지점이야. 딱 두 덩어리로 정리할게.

1. **Attribute가 뭔지**
2. **시간 흐름을 어떻게 다룰지**, 특히 “5화에 나온 과거 회상(1화보다 과거 사건)” 같은 케이스
## 시간흐름 넣기는 Optional으로 초반구현 15~20개 를 먼저 구현하고 필요하면 넣기로한다.
---

## 1) Attribute는 뭐야?

**Attribute = ‘무엇(노드/사건/관계)에 붙는 성질(필드)’**이야.
Predicate처럼 “관계/행위의 타입”이 아니라, **설명값**에 가깝다.

### 예시로 감 잡기

#### Event에 붙는 Attribute

* `episode_start`, `episode_end`  (노출 게이트용)
* `summary`
* `importance_score` (있다면)
* `location` (있다면)
* `mood` (있다면)

#### Character에 붙는 Attribute

* `name`
* `house/faction`
* `status(alive/dead)`
* `first_appearance_episode`

#### Relation에 붙는 Attribute

* `type` (PRECEDES/RELATED/REVEALS)
* `confidence` (있다면)
* `note` (있다면)

**한 줄 결론**

* **Predicate**: “이 사건/관계는 어떤 종류냐” (분류/코드)
* **Attribute**: “그 사건/관계/인물의 구체 값들” (필드/속성)

---

## 2) 그럼 4가지로 나눴을 때 “시간 흐름”은 어디서 알지?

여기서 **시간은 2종류**가 있다. 이걸 분리하면 네 예시가 깔끔하게 해결돼.

### A) “방영/서술 시간” (narrative / episode time)

* **몇 화에서 이 이벤트가 *등장*했는가**
* 너희 시스템의 K 게이트는 이 시간을 기준으로 돌아감
  (event.episode_end <= K)

👉 이건 지금 이미 있는 필드로 해결됨:

* `episode_start`, `episode_end`

---

### B) “이야기 세계의 실제 시간” (story / chronological time)

* **극중에서 실제로 언제 일어난 일인가**
* 회상(플래시백) 때문에 “5화에 나오지만 1화보다 과거”가 가능해짐

👉 이건 **별도의 축**이 필요해.

---

## 3) 네 예시(5화에 과거 회상) 처리 방식

### 상황

* 5화에 회상씬으로 “사실은 1화보다 과거에 이런 일이 있었다”가 공개됨

여기서 핵심은:

* **노출 기준(K)은 ‘등장한 화(5화)’ 기준**이어야 안전함
* 하지만 “연대기 정렬”은 ‘극중 시간’ 기준이 필요함

즉, 같은 Event에 **두 시간축을 같이 붙인다.**

---

## 4) 최소 설계(가장 덜 깨지는 답)

### Event에 시간 Attribute를 2개 둔다

1. 이미 있는 것 (서술 시간)

* `episode_start`, `episode_end`

2. 새로 붙일 것 (극중 시간)

* `story_time_start`, `story_time_end` (또는 “Arc/Timeline 포인트”)

그리고 규칙은 단순하게:

* **스포일러 게이트/노출**: episode 기준
* **연대기(Chronological) 보기**: story_time 기준

---

## 5) “근데 극중 시간을 숫자로 어떻게 매겨?” (중요)

여기서 현실적인 최소 해법은 두 가지야.

### ✅ 제일 단순한 해법: “Story Arc Index”

* 극중 시간을 실제 날짜로 만들지 말고
* 드라마 내부에서 정한 **상대적인 타임라인 포인트**로 둠

예:

* `story_arc = "PAST_CHILDHOOD"`
* `story_order = 120` (정렬용 정수)

회상 이벤트는:

* episode_end = 5
* story_order = 10 (훨씬 과거)

이게 제일 구현 쉬워.

---

### ✅ 더 정교한 해법: “TimeRef 엔티티”

* `time_ref` 테이블 만들어서

  * “전쟁 전/후”
  * “왕 즉위 이전”
  * “시즌1 이전”
    같은 기준점을 엔티티로 관리

근데 이건 지금 단계에선 과해질 가능성이 큼.

---

## 6) 너 예시를 Event로 찍어보면

**Event (회상 공개 이벤트)**

* episode_end = 5  ✅ (K=4면 차단)
* story_order = 10 ✅ (연대기에서는 초반에 표시)

즉, 5화에서 공개된 과거 사건은:

* “등장 시점”으로는 5화 정보(스포일러 위험)
* “실제 발생 시점”은 과거

이걸 분리해두면:

* 스포일러 방지와
* 연대기 탐색을
  둘 다 동시에 만족해.

---

## 한 줄로 요약

* **Attribute**는 “값(필드)”이다.
* 시간은 **episode time**과 **story time** 두 축이 필요하고,
* 회상은 “episode=5 / story=과거”로 같이 찍으면 된다.

원하면 다음 턴에, 이걸 최소 변경으로 붙이는 방식으로:

* `event`에 컬럼 2개만 추가하는 버전(가장 싸게)
* 또는 별도 `event_story_time` 테이블로 분리하는 버전(확장성)
  중에서 **더 안전한 하나**로 딱 고정해서 내려줄게.

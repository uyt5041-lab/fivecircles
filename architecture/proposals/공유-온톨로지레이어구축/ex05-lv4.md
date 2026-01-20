레벨 4가려면 트리플스토어가 필요한건가? 
Thought for 20s

필수는 아니야. **Level 4로 가는 데 필요한 건 “트리플스토어”라는 저장소가 아니라, ‘추론/분석에 쓸 신호(라벨·규칙·지표)’**야.

트리플스토어는 도움이 될 수는 있는데, “없으면 못 간다”는 성격이 아니다.

1) Level 4가 어려운 이유는 저장소가 아니라 “의미” 때문

Level 4 질문들은 대체로 이런 걸 요구해:

“중요 인물로 부상” 같은 중요도/전환점 판단

“예고된 사건” 같은 암묵적 예측/전조 해석

“갈등 축” 같은 상위 카테고리(메타 축) 분류

“관점 재구성” 같은 서술 생성 규칙

“서사가 어떤 카테고리에 많이 걸치는지” 같은 통계/분석

이건 (S, P, O)를 어디에 저장하든 자동으로 생기지 않아.
데이터에 ‘그 의미를 계산할 근거’가 있어야 해.




2) 지금 너희 구조(RDB + Event 그래프)로 Level 4 가는 현실적인 방식

현재 설계(Event + event_relation + event_character + reveal + K 게이트)로도 Level 4는 가능해. 대신 필요한 건 저장소 변경이 아니라 아래 같은 추가 신호 레이어야:

분류 신호: event predicate_code/type 정교화, 상위 카테고리(갈등축/테마) 태그

중요도 신호: 사건 중요도 점수(예: 등장 인물 수, 연쇄 파생 사건 수, REVEALS 강도 등)

인과 신호: PRECEDES만으로 부족하면 CAUSES 같은 명시적 관계(또는 derived rule)

품질 신호: source_type 기반 신뢰도, 리뷰 승인 여부, 확신도

이런 신호가 있으면 “부상/전조/갈등축/통계” 같은 Level 4 질문을 규칙+분석으로 계산할 수 있어.

핵심: **Level 4의 병목은 ‘저장 포맷’이 아니라 ‘라벨링과 규칙 정의’**다.


==================
>>>>>>>>>>>>>>>>>>

좋아. **“RDB(Event 그래프) 유지”**를 전제로, Level 4 질문 5개를 **최소 신호(1–2개) 추가**로 어떻게 풀 수 있는지 “참고용 설계”로 정리해볼게.
(공통 전제: **노출 게이트는 항상 `event.episode_end <= K`**. 미래(>K)는 **절대 디테일 노출 금지**)

---

## 0) Level 4로 가는 공통 원칙 2개

1. **“추론” 대신 “명시 라벨 + 약한 통계”**로 간다 (MVP 안전)
2. 그래프/분석 계산은 **결과 반환 직전**이 아니라, 가능한 한 **파생값(derived)로 저장**해 둔다 (성능/결정성)

---

## A) “인물 A가 어떻게 중요 인물로 부상했나”

### 필요한 신호(최소 2개)

1. `event_importance_score` (파생 점수 컬럼 or 별도 테이블 `event_metric`)
2. `event_type/predicate_code` (이미 얘기한 Level2용)

### 계산(보수적, 설명 가능한 방식)

`importance = w1*등장인물수 + w2*관계outdegree + w3*reveal_count`

* 등장인물수: `COUNT(event_character)`
* 관계 outdegree: `COUNT(event_relation where from_event_id=e.id)`
* reveal_count: `COUNT(event_reveal where event_id=e.id)` (있다면)

### 출력(스포일러 안전)

* K 이하 이벤트 중에서 importance 상위 N개를 “부상 포인트”로 보여줌
* 요약은 `safe_summary` (없으면 summary를 짧게)

**SQL 스케치**

```sql
SELECT e.id, e.summary, e.episode_start, e.episode_end, m.importance_score
FROM event e
JOIN event_metric m ON m.event_id = e.id
JOIN event_character ec ON ec.event_id = e.id
WHERE ec.character_id = :characterId
  AND e.episode_end <= :K
ORDER BY m.importance_score DESC, e.episode_start ASC
LIMIT 20;
```

---

## B) “직접 등장하지 않았지만 예고된(foreshadowed) 것들”

여기서 함정: **미래 사건을 ‘내용’으로 보여주면 바로 스포일러**야.

### 필요한 신호(최소 1개)

1. `event_relation.type = FORESHADOWS` (또는 `HINTS`)

   * 사람이(리뷰어) “이건 떡밥이다”라고 명시한 엣지만 인정

### 출력(스포일러 안전한 형태)

* K 이하 이벤트에서 FORESHADOWS로 이어지는 **미래 이벤트는 “존재만”** 보여준다

  * 예: “아직 풀리지 않은 떡밥 3개”
  * 또는 “떡밥 카테고리(갈등축)만” 보여줌 (아래 C의 축이 있으면 가능)
* **미래 이벤트 ID/요약/인물명**은 노출하지 않기

**SQL 스케치(카운트만)**

```sql
SELECT COUNT(DISTINCT r.to_event_id) AS unresolved_count
FROM event_relation r
JOIN event e_from ON e_from.id = r.from_event_id
JOIN event e_to   ON e_to.id   = r.to_event_id
WHERE r.type = 'FORESHADOWS'
  AND e_from.episode_end <= :K
  AND e_to.episode_end > :K;
```

(실패 경로) FORESHADOWS 라벨이 없으면: “예고” 기능은 **0 또는 미지원**이 정상.

---

## C) “서로 다른 에피소드지만 같은 갈등 축(conflict axis)으로 묶어줘”

### 필요한 신호(최소 1개)

1. `event_axis_tag` (테이블 하나면 충분)

* `event_axis_tag(event_id, axis_code)`
* axis_code 예: `POWER`, `FAMILY`, `BETRAYAL`, `SURVIVAL`, `IDENTITY` 같은 상위 축 5~10개

### 입력 방식(최소 구현)

* 리뷰 승인 단계에서 axis_code 1개만 선택(드롭다운)
* 자동 추천은 옵션(없어도 됨)

### 출력

* K 이하 이벤트 중 axis_code로 그룹핑

**SQL 스케치**

```sql
SELECT t.axis_code, e.id, e.summary, e.episode_start, e.episode_end
FROM event_axis_tag t
JOIN event e ON e.id = t.event_id
WHERE e.drama_id = :dramaId
  AND e.episode_end <= :K
  AND t.axis_code = :axis
ORDER BY e.episode_start ASC, e.id ASC;
```

---

## D) “같은 사건을 서로 다른 인물 관점에서 재구성해줘”

이건 생성(서술)처럼 보이지만, MVP에서는 **“관점별 사건 선택 + 요약 템플릿”**로 충분히 흉내낼 수 있어.

### 필요한 신호(최소 1–2개)

1. `event_character.role` (SUBJECT/OBJECT/ALLY/ENEMY 정도)
2. (선택) `safe_summary_template` 같은 짧은 텍스트 규칙

### 출력 방식(안전/간단)

* 관점 캐릭터 X를 기준으로:

  * role=SUBJECT인 이벤트 먼저
  * 그 다음 role=ALLY/ENEMY
* “X의 관점”은 **사건 나열 + 1~2문장 요약**으로만

**SQL 스케치**

```sql
SELECT e.id, e.summary, e.episode_start, e.episode_end, ec.role
FROM event e
JOIN event_character ec ON ec.event_id = e.id
WHERE ec.character_id = :characterId
  AND e.episode_end <= :K
ORDER BY
  CASE ec.role
    WHEN 'SUBJECT' THEN 1
    WHEN 'ALLY' THEN 2
    WHEN 'ENEMY' THEN 3
    ELSE 4
  END,
  e.episode_start ASC, e.id ASC
LIMIT 50;
```

(실패 경로) role이 없으면: 그냥 “캐릭터 참여 사건 타임라인”으로 다운그레이드.

---

## E) “인물의 서사가 어떤 사건 카테고리에 많이 걸쳐 있나(분포/분석)”

이건 사실 Level 2 데이터만 있어도 가능해.

### 필요한 신호(최소 1개)

1. `event.predicate_code` (또는 type)

### 출력

* 캐릭터별 predicate_code 빈도, 상위 N개

**SQL 스케치**

```sql
SELECT e.predicate_code, COUNT(*) AS cnt
FROM event e
JOIN event_character ec ON ec.event_id = e.id
WHERE ec.character_id = :characterId
  AND e.episode_end <= :K
GROUP BY e.predicate_code
ORDER BY cnt DESC, e.predicate_code ASC;
```

---

# “트리플스토어가 꼭 필요하냐?”를 Level 4 기준으로 다시 말하면

* Level 4의 병목은 저장소가 아니라 **라벨(FORESHADOWS/AXIS/ROLE)과 지표(importance)**야.
* 트리플스토어는 “관계가 폭발적으로 늘어날 때” 편해지지만, **지금 Level 4의 최소 구현은 RDB로 충분**해.

---

## 최소 추가물 요약 (정말 최소만)

* `event.predicate_code` (Level2+분석 공통)
* `event_metric.importance_score` (부상)
* `event_relation.type += FORESHADOWS` (예고, 단 결과는 count/axis만)
* `event_axis_tag(event_id, axis_code)` (갈등축)
* `event_character.role` (관점 재구성)

원하면, 이 5개를 **지금 너희 ERD/테이블에 “가장 덜 깨지게” 붙이는 마이그레이션 순서**(1번부터 적용하면 바로 레벨2/3/4가 순차로 열리는 순서)로 딱 정해서 내려줄게.

## **Level 1–3만** 딱 구현 가능한 형태로 “엔드포인트 목록 + (MySQL 기준) 쿼리 설계” 예시


전제는 스펙 그대로: **노출 게이트 = `event.episode_end <= K`** (K=사용자 마지막 시청 화). 【data-model.md: Event / UserState】

---

# 공통 규칙 (모든 조회에 자동 적용)

* **스포일러 게이트(필수)**: `e.drama_id = :dramaId AND e.episode_end <= :K`
* Character 목록도 Event를 통해 “K까지 등장한 캐릭터”만 노출:

  * `event_character` ⨝ `event` (게이트 적용)

---

# Level 1 (단순 연결 조회, MVP 1차)

## L1-1. 안전 캐릭터 카드 리스트

**GET** `/dramas/{dramaId}/characters?safeUpToEpisode={K}&limit={N}`

**의도**: “K까지 등장한 캐릭터”만 보여주기.

**쿼리(핵심)**

* 캐릭터 후보:

  * `character c`
  * `event_character ec`
  * `event e` (게이트)
* 중요도(간단 버전): `COUNT(DISTINCT ec.event_id)` desc

```sql
SELECT c.id, c.display_name,
       COUNT(DISTINCT ec.event_id) AS involvement_count
FROM character c
JOIN event_character ec ON ec.character_id = c.id
JOIN event e ON e.id = ec.event_id
WHERE c.drama_id = :dramaId
  AND e.drama_id = :dramaId
  AND e.episode_end <= :K
GROUP BY c.id
ORDER BY involvement_count DESC, c.id ASC
LIMIT :N;
```

---

## L1-2. 캐릭터 상세(요약은 캐릭터 서비스에서) + 관련 이벤트 타임라인

**GET** `/characters/{characterId}/events?safeUpToEpisode={K}&limit={N}`

```sql
SELECT e.id, e.summary, e.episode_start, e.episode_end
FROM event e
JOIN event_character ec ON ec.event_id = e.id
WHERE ec.character_id = :characterId
  AND e.episode_end <= :K
ORDER BY e.episode_start ASC, e.id ASC
LIMIT :N;
```

---

## L1-3. 이벤트에 등장하는 인물들 전원

**GET** `/events/{eventId}/characters?safeUpToEpisode={K}`
(※ eventId 자체가 K 이하면 OK, 아니면 404/blocked)

```sql
SELECT c.id, c.display_name
FROM event_character ec
JOIN character c ON c.id = ec.character_id
JOIN event e ON e.id = ec.event_id
WHERE ec.event_id = :eventId
  AND e.episode_end <= :K
ORDER BY c.id ASC;
```

---

## L1-4. 두 인물이 함께 나온 사건들

**GET** `/characters/{aId}/coevents?with={bId}&safeUpToEpisode={K}`

```sql
SELECT e.id, e.summary, e.episode_start, e.episode_end
FROM event e
JOIN event_character ec1 ON ec1.event_id = e.id AND ec1.character_id = :aId
JOIN event_character ec2 ON ec2.event_id = e.id AND ec2.character_id = :bId
WHERE e.episode_end <= :K
ORDER BY e.episode_start ASC, e.id ASC;
```

---

## L1-5. 사건 유형(전투/배신 등) 필터

(전제: `event`에 `predicate_code` 또는 `type` 컬럼이 있어야 함. 없으면 `summary` 텍스트로 필터링은 MVP에선 비추천)

**GET** `/dramas/{dramaId}/events?type={TYPE}&safeUpToEpisode={K}&limit={N}`

```sql
SELECT e.id, e.summary, e.episode_start, e.episode_end
FROM event e
WHERE e.drama_id = :dramaId
  AND e.episode_end <= :K
  AND e.type = :TYPE
ORDER BY e.episode_start ASC, e.id ASC
LIMIT :N;
```

---

# Level 2 (범위/유형 필터링, MVP 2차)

## L2-1. 에피소드 구간 안의 사건 모아보기

**GET** `/dramas/{dramaId}/events?fromEpisode={A}&toEpisode={B}&safeUpToEpisode={K}`
(안전상 `B <= K` 강제)

```sql
SELECT e.id, e.summary, e.episode_start, e.episode_end
FROM event e
WHERE e.drama_id = :dramaId
  AND e.episode_end <= :K
  AND e.episode_start >= :A
  AND e.episode_end <= :B
ORDER BY e.episode_start ASC, e.id ASC;
```

---

## L2-2. 캐릭터 사건을 유형으로만 필터

**GET** `/characters/{characterId}/events?type={TYPE}&safeUpToEpisode={K}`

```sql
SELECT e.id, e.summary, e.episode_start, e.episode_end
FROM event e
JOIN event_character ec ON ec.event_id = e.id
WHERE ec.character_id = :characterId
  AND e.episode_end <= :K
  AND e.type = :TYPE
ORDER BY e.episode_start ASC, e.id ASC;
```

---

## L2-3. “등장 빈도/관련도” 기반 Top-N 캐릭터

(캐릭터 카드 리스트의 확장. 이미 L1-1과 동일하니 엔드포인트는 재사용하고 sort 옵션만 추가)

**GET** `/dramas/{dramaId}/characters?safeUpToEpisode={K}&sort=involvement&limit={N}`
쿼리는 L1-1 그대로.

---

# Level 3 (관계 기반 탐색, 온톨로지 체감 구간)

여기부터는 `event_relation`을 탐색하고, **hop(distance)** 를 반환에 포함.

## L3-1. 사건 그래프 확장(멀티홉) 검색

**GET** `/events/{eventId}/related?depth={D}&safeUpToEpisode={K}&types=PRECEDES,INVOLVES`
(기본 types에서 REVEALS는 제외 권장)

**동작**

1. 시작 event가 K 이하인지 확인
2. BFS로 relation 확장 (visited 필수)
3. 최종 결과에서 `episode_end <= K`로 한 번 더 게이트
4. 정렬: `hop ASC, episode_start ASC, id ASC`

**BFS에서 쓰는 배치 쿼리(Frontier IN)**

```sql
SELECT r.from_event_id, r.to_event_id, r.type
FROM event_relation r
WHERE r.from_event_id IN (:frontierIds)
  AND r.type IN (:types);
```

**이웃 이벤트를 한 번에 가져오는 쿼리**

```sql
SELECT e.id, e.summary, e.episode_start, e.episode_end
FROM event e
WHERE e.id IN (:neighborIds)
  AND e.episode_end <= :K;
```

---

## L3-2. “원인이 된 이전 사건들”(PRECEDES 역방향 체인)

**GET** `/events/{eventId}/causes?depth={D}&safeUpToEpisode={K}`
(구현은 L3-1과 동일한 BFS인데, 엣지를 반대로 탐색)

**역방향 relation 배치**

```sql
SELECT r.from_event_id, r.to_event_id, r.type
FROM event_relation r
WHERE r.to_event_id IN (:frontierIds)
  AND r.type = 'PRECEDES';
```

---

## L3-3. “이 사건 이후 파생 사건들”(PRECEDES 정방향 체인)

**GET** `/events/{eventId}/effects?depth={D}&safeUpToEpisode={K}`

정방향은 L3-1의 기본.

---

## L3-4. 캐릭터 A와 “관계있는 인물” 리스트 (그래프 경유)

정의(가장 단순한 MVP):
**A가 포함된 이벤트들(K 이하)을 가져오고 → 그 이벤트들에 같이 등장한 캐릭터들을 distinct로 반환**

**GET** `/characters/{characterId}/related-characters?safeUpToEpisode={K}&limit={N}`

```sql
SELECT c2.id, c2.display_name,
       COUNT(DISTINCT e.id) AS shared_event_count
FROM event e
JOIN event_character ecA ON ecA.event_id = e.id AND ecA.character_id = :characterId
JOIN event_character ec2 ON ec2.event_id = e.id
JOIN character c2 ON c2.id = ec2.character_id
WHERE e.episode_end <= :K
  AND c2.id <> :characterId
GROUP BY c2.id
ORDER BY shared_event_count DESC, c2.id ASC
LIMIT :N;
```

이건 “관계”를 **추론이 아니라 공등장 기반**으로 정의해서 MVP에 맞다.

---

## L3-5. “A → (사건들) → B” 경로 힌트(최단 hop)

MVP에서는 “경로 전체”를 내리기보다, **최단 hop + 중간 event 몇 개**만 내리는 게 안전하고 단순함.

**GET** `/characters/path?from={A}&to={B}&maxDepth={D}&safeUpToEpisode={K}`

구현 아이디어(간단):

* 출발: A가 포함된 이벤트 집합 E(A)
* 각 이벤트에서 공등장 캐릭터 확장하거나, 이벤트 관계로 확장
* 최단거리 도달 시 stop
* 반환: `hop`, `bridge_event_ids[]`

(이건 SQL 한 방보다 서비스 레벨 BFS가 더 현실적)

---

# 인덱스(이거 없으면 바로 느려짐)

* `event`: `(drama_id, episode_end)`, `(episode_start)`, `(type)`
* `event_character`: `(character_id, event_id)`, `(event_id, character_id)`
* `event_relation`: `(from_event_id, type, to_event_id)`, `(to_event_id, type, from_event_id)`
* `user_state`: `(user_id, drama_id)` unique

---

# 구현 팁(딱 3개만, 운영 리스크 줄이기)

1. **Depth 상한**: `D <= 2` 고정(컨트롤러 clamp)
2. **REVEALS 기본 탐색 제외**: 결과 확장에 섞이면 위험도가 급상승
3. **결과 상한 Top-N**: BFS 결과 `maxEvents=200` 같은 컷 필수

---

원하면 다음 단계로, 위 엔드포인트를 **event-service / character-service로 정확히 어디에 둘지**(경계)까지 한 번에 고정해서, 컨트롤러 메서드 이름과 DTO 형태까지 딱 맞춰서 내려줄게.


근데 레벨 2에서 event predicate/type를 찾으려면 트리플구조 데이터셋이 있어야하잖아? 이걸 어디에 넣지?
Thought for 1m 5s

맞아, Level 2(“전투 사건만”, “배신 사건만”) 같은 걸 하려면 “이 Event가 무슨 종류냐”가 DB에 있어야 해.
다만 트리플스토어처럼 (S,P,O) 전체 데이터셋이 꼭 필요한 건 아니고, MVP에선 P(=predicate/type)만 Event에 박아도 Level 2는 충분히 돌아가.

결론: “트리플 구조”는 이렇게 넣는 게 가장 짧고 안전해
1) event 테이블에 predicate_code(또는 type) 컬럼을 추가해서 저장

위치: event-service DB의 event 테이블

이유: 지금 ERD상 event는 summary + episode range + source 를 가지는 “온톨로지 핵심 노드”라서, 분류값(type)을 여기 두는 게 정답이야.

값: enum처럼 쓰는 고정 코드(예: BATTLE, BETRAYAL, REVEAL_IDENTITY, DEATH, JOIN, LEAVE …)

예시 DDL(개념):

ALTER TABLE event
  ADD COLUMN predicate_code VARCHAR(30) NOT NULL;

CREATE INDEX idx_event_drama_pred_ep
  ON event(drama_id, predicate_code, episode_end);

2) “트리플 데이터셋”은 별도 테이블로 안 만들고, 기존 관계 테이블이 이미 담당

트리플스토어 관점으로 보면 지금 구조가 이렇게 대응돼:

S(주어/참여자): event_character (이 이벤트에 누가 관여했는지)

P(동사/분류): event.predicate_code (전투/배신/폭로 같은 사건 유형)

O(대상/드러난 것): 보통은 “전투/배신” 같은 카테고리 질의에는 O가 없어도 되고,
“무엇을 드러냈나”는 이미 event_reveal이 담당

즉, MVP의 “카테고라이제이션”은 (Event 노드 + predicate_code + 참여자 연결) 로 충분히 해결돼.

그럼 이 값은 어디서 채우냐(입력 플로우)

위키 승인 → Event 생성 흐름에 그대로 붙이면 돼.

contributor가 wiki_entry 작성(episode_start/end 필수)

AI가 “추천 predicate_code”를 제안(선택)

reviewer가 승인하면서 predicate_code를 확정

승인 시 event 생성할 때 predicate_code도 같이 저장

이러면 Level 2 엔드포인트의 필터가 단순해져:

“인물 C가 참여한 전투 사건”

event_character로 C가 포함된 event 찾고

event.predicate_code='BATTLE'

그리고 최종 게이트 event.episode_end <= K

왜 “진짜 트리플 테이블(event_triple)”을 지금 안 넣는 게 맞나

지금 니가 원하는 Level 2 기능은 “유형 필터”가 핵심이라서,

트리플 전체 저장(주어/목적어 역할까지 정교화) 은 구현량만 늘고

MVP 질문(전투/배신/폭로 등)에는 실익이 거의 없어.

필요 최소는 딱 이것:

event.predicate_code

event_character

(폭로류만) event_reveal

원하면, 너희가 실제로 쓰려는 predicate_code 후보 15~20개를 “겹치지 않게” 깔끔하게 뽑아서(전투/배신/죽음/동맹/합류/이탈/정체폭로/관계폭로/획득/상실 등) “Level 2 필터가 바로 되는 분류표”로 고정해줄게.
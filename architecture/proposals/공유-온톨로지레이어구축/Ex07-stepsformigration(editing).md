## 레벨 1-4 쿼리구조 설계 (DB미그레이션 포함)


**Level 1–3을 열고, Level 4(참고용) 신호까지**”를 **지금 너희 ERD(서비스별 분리 + Flyway + FK 금지 + MySQL 1DB)** 기준으로 **가장 덜 깨지는 마이그레이션 순서**로 딱 정리해줄게.
(근거: 요구사항의 핵심은 **Event + episode range + rule-based exposure**이고, 그 위에 분류/분석 신호를 최소로 얹는 방식이 안전함.)【/mnt/data/requirements.md】【/mnt/data/data-model.md】【/mnt/data/docker.md】

---

## 0) 전제(안전 규칙)

* **노출 게이트는 항상** `event.episode_end <= K` (K=사용자 last_watched_episode_number)【/mnt/data/data-model.md】
* 서비스별 DB 접근 원칙은 유지:

  * **event-service는 event 도메인 테이블만** (event, event_character, event_relation, event_reveal)【/mnt/data/notion-origin-erd-v2.md】

---

# 1) 마이그레이션 순서 (Flyway, event-service만으로 최대한 끝냄)

## Step 1 (Level 2 오픈): `event.predicate_code` 추가

**목적:** “전투/배신/폭로 같은 타입 필터”를 SQL로 가능하게 만들기

**Flyway**: `V2__event_add_predicate_code.sql` (event-service)

```sql
ALTER TABLE event
  ADD COLUMN predicate_code VARCHAR(30) NOT NULL DEFAULT 'UNKNOWN';

CREATE INDEX idx_event_drama_pred_end
  ON event (drama_id, predicate_code, episode_end, episode_start, id);
```

**운영/실패 안전**

* 기존 데이터는 전부 `UNKNOWN`으로 살아남음 (마이그레이션 깨질 확률 낮음)
* Level2 API에서 `type=BATTLE` 같은 필터는 `UNKNOWN` 이벤트는 자연스럽게 제외됨(보수적)

**코드 변경(최소)**

* Event 생성 시(predicate_code 미지정이면) `UNKNOWN`
* Wiki 승인 → Event 생성 요청 payload에 `predicate_code`를 “옵션”으로 추가 (DB는 event에만 저장)

---

## Step 2 (Level 4-관점의 발판): `event_character.role` 추가

**목적:** “인물 관점 재구성(주체/대상/동참)” 같은 뷰를 아주 얇게 가능하게

**Flyway**: `V3__event_character_add_role.sql`

```sql
ALTER TABLE event_character
  ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'INVOLVED';

CREATE INDEX idx_ec_character_role_event
  ON event_character (character_id, role, event_id);

CREATE INDEX idx_ec_event_role_character
  ON event_character (event_id, role, character_id);
```

**운영/실패 안전**

* role을 안 채워도 전부 INVOLVED로 안전하게 동작
* 나중에 SUBJECT/OBJECT를 일부 이벤트에만 점진 도입 가능

---

## Step 3 (Level 4-갈등축): `event_axis_tag` 신설

**목적:** “같은 갈등 축(conflict axis)으로 묶기”를 추론 없이 가능하게

**Flyway**: `V4__create_event_axis_tag.sql`

```sql
CREATE TABLE event_axis_tag (
  event_id BIGINT NOT NULL,
  axis_code VARCHAR(30) NOT NULL,
  PRIMARY KEY (event_id, axis_code),
  INDEX idx_axis_code_event (axis_code, event_id)
);
```

**운영/실패 안전**

* 데이터가 없으면 “축 기능 없음”으로 그냥 0건 반환 (보수적)
* 축은 5~10개 코드만 운영으로 고정하면 관리가 쉬움

---

## Step 4 (Level 4-부상/중요도): `event_metric` (선택이지만 추천)

**목적:** “중요 사건/전환점”을 **결정적으로**(같은 입력이면 같은 결과) 만들기

**Flyway**: `V5__create_event_metric.sql`

```sql
CREATE TABLE event_metric (
  event_id BIGINT NOT NULL,
  importance_score INT NOT NULL DEFAULT 0,
  character_count INT NOT NULL DEFAULT 0,
  out_degree INT NOT NULL DEFAULT 0,
  reveal_count INT NOT NULL DEFAULT 0,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (event_id),
  INDEX idx_importance (importance_score, event_id)
);
```

**왜 “선택이지만 추천”이냐**

* Level 4는 즉석 집계(매 요청 JOIN+COUNT)가 커지면 성능/일관성이 흔들림
* 이 테이블이 있으면 “검색 결과가 매번 바뀌는 현상”을 줄일 수 있음

**운영/실패 안전**

* metric이 비어 있으면 importance=0으로 간주하고 시간순으로 fallback

---

## Step 5 (스키마 변경 없이 코드만): `event_relation.type`에 FORESHADOWS 추가 (참고용)

**목적:** “예고/떡밥”을 *미래 내용 없이* 카운트/축 수준으로만 제공

* DB 컬럼은 VARCHAR(20)이라 **마이그레이션 불필요**【/mnt/data/notion-origin-erd-v2.md】
* 코드에서 허용 타입 목록에 `FORESHADOWS`만 추가
* 기본 BFS 확장에는 **절대 포함시키지 않기** (위험)

---

# 2) 서비스 흐름(“트리플 데이터”를 어디서 채우나)

너가 물었던 “트리플 구조 데이터셋”은 MVP 기준으로 이렇게 최소화해:

* **P(predicate/type)** → `event.predicate_code` (Step 1)
* **S(참여자 집합)** → `event_character` (이미 있음)
* **O(폭로 대상)** → `event_reveal` (이미 있음, 필요할 때만)

입력은 트리플스토어처럼 간단하게 받되, 저장은 Event 중심:

* Wiki 승인 시(Reviewer UI에서 선택):

  * `predicate_code`(옵션)
  * `axis_code`(옵션)
  * `character roles`(옵션)
* event-service가 Event 생성하면서 event 테이블/보조 테이블에 저장

> 중요한 점: “트리플 전체 저장소”를 새로 만들 필요는 없고, **지금 테이블들이 이미 트리플 역할을 분담**하고 있어.【/mnt/data/data-model.md】

---

# 3) (참고) Level 1–3 쿼리 설계는 “event-service 단독 쿼리”로 이렇게 가져가면 안전

서비스 분리 원칙 때문에, event-service는 **character 이름을 모름**.
따라서 event-service는 **ID 리스트/카운트만 반환**, 프론트(or BFF)가 content-service에서 캐릭터 상세를 batch로 가져오는 구조가 가장 단순해.

### L1: K까지 등장 캐릭터 ID + involvement_count

```sql
SELECT ec.character_id, COUNT(DISTINCT e.id) AS involvement_count
FROM event e
JOIN event_character ec ON ec.event_id = e.id
WHERE e.drama_id = :dramaId
  AND e.episode_end <= :K
GROUP BY ec.character_id
ORDER BY involvement_count DESC, ec.character_id ASC
LIMIT :N;
```

### L2: type 필터(BATTLE 등) 가능해짐 (Step 1 이후)

```sql
SELECT e.id, e.summary, e.episode_start, e.episode_end
FROM event e
WHERE e.drama_id = :dramaId
  AND e.episode_end <= :K
  AND e.predicate_code = :type
ORDER BY e.episode_start ASC, e.id ASC
LIMIT :N;
```

### L3: 멀티홉(BFS)용 배치 relation 조회

```sql
SELECT r.from_event_id, r.to_event_id, r.type
FROM event_relation r
WHERE r.from_event_id IN (:frontierIds)
  AND r.type IN ('PRECEDES','INVOLVES'); -- 기본은 여기까지만
```

---

# 4) “이 순서”가 좋은 이유(짧게)

1. Level2를 여는 데 필요한 건 **predicate 하나**라서 Step1이 최우선
2. role/axis/metric은 **데이터 없어도 시스템이 깨지지 않는 확장 신호**라서 뒤로
3. FORESHADOWS는 스포일러 위험이 크니 **스키마보다 ‘노출 정책’이 먼저**

---

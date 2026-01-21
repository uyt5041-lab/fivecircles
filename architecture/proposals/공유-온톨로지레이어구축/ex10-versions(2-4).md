# V2/V3 마이그레이션 

## V2 - pre-triples
## V3 - triples

* **(DB 스키마 기준) V2 = “트리플 적용 전”**: Event는 `summary + episode range` 중심, 타입/역할 없음
* **V3 = “트리플 적용”**: **P**는 `event.predicate_code`, **S/O**는 `event_character.role`로 들어가서 구조 질의가 가능해짐

아래처럼 **Flyway V2/V3 마이그레이션 + 문서 업데이트 텍스트**까지 한 번에 정리해줄게.

---

## 1) Flyway 마이그레이션 파일

> 경로는 **event-service에서 기존 V1 마이그레이션이 있는 폴더**(보통 `.../src/main/resources/db/migration/`)에 그대로 추가.

### V2__event_add_predicate_code.sql

```sql
ALTER TABLE event
  ADD COLUMN predicate_code VARCHAR(30) NOT NULL DEFAULT 'UNKNOWN';

CREATE INDEX idx_event_drama_pred_end
  ON event (drama_id, predicate_code, episode_end, episode_start, id);
```

### V3__event_character_add_role.sql

```sql
ALTER TABLE event_character
  ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'INVOLVED';

CREATE INDEX idx_ec_event_role_character
  ON event_character (event_id, role, character_id);

CREATE INDEX idx_ec_character_role_event
  ON event_character (character_id, role, event_id);
```

**이 2개는 100% backward-compatible**야.
기존 데이터는 자동으로:

* `predicate_code = UNKNOWN`
* `role = INVOLVED`
  로 살아남음.

---

## 2) “V2 / V3” 의미를 문서에 박아두기 (스펙 업데이트)

### (A) data-model.md에 추가할 확정 문구

```md
## Schema Versioning (Event Domain)

### V2 (pre-triple)
- Event 중심 데이터(episode range + summary)로 스포일러 게이트/기본 질의 지원
- Event type / Character role 없음

### V3 (triple-enabled)
Triple decomposition is stored in existing tables:
- P (Predicate) -> event.predicate_code (default: UNKNOWN)
- S/O participant set -> event_character.role (default: INVOLVED; SUBJECT/OBJECT optional)

Notes:
- summary is display text; triple fields are query structure.
- All exposure rules still use episode_end <= K.
```

### (B) notion-origin-erd-v2.md의 event/event_character 정의에 추가

```md
event
- predicate_code VARCHAR(30) NOT NULL DEFAULT 'UNKNOWN'

event_character
- role VARCHAR(20) NOT NULL DEFAULT 'INVOLVED'
  - SUBJECT | OBJECT | INVOLVED
```

### (C) requirements.md에 “트리플 저장 방식” 고정 문구(짧게)

```md
Triple storage (MVP-friendly):
- Triple is not stored as a new triple-store table.
- It is decomposed into:
  - event.predicate_code (P)
  - event_character(role) participants (S/O)
- This keeps the model queryable while staying relational and service-scoped.
```

---

## 3) 코드 변경 포인트 (최소)

1. **Event 생성/수정 DTO**

* `predicateCode` optional로 받기 (없으면 UNKNOWN)

2. **event_character insert**

* role optional로 받기 (없으면 INVOLVED)
* UI/승인 플로우에서 “S/O 지정”을 안 하면 전부 INVOLVED로 저장

3. **조회 API**

* type 필터가 필요하면 `predicate_code`로 바로 WHERE 가능
* “S/O 기반 질의”는 `event_character.role`로 필터 가능

---

## 4) “트리플 적용”이 실제로 어떻게 저장되는지 (너가 말한 예시)

입력 트리플:

* (John Snow) (KILLS) (White Walker)

DB 저장:

* `event.predicate_code = 'KILLS'`
* `event_character` 두 줄

  * (event_id=E, character_id=JohnSnowId, role=SUBJECT)
  * (event_id=E, character_id=WhiteWalkerId, role=OBJECT)
* `event.summary`는 화면 표시용 텍스트로 그대로

---

# V4 예고(미정)

**contains 포함**

 한 이벤트가 다른 이벤트(들)을 포함하는 경우 

# 데이터 적재/후보/승격 모듈 인덱스
(자동 적재 및 이벤트 승격 파이프라인)

[INDEX]

이 문서는 **Input-data 파이프라인의 핵심 흐름과 규칙**을 한 곳에 고정한다.

- **15-input-data2.md**: Ingest(원천 적재) 기준 요약 + 전체 파이프라인 흐름 고정
- **proposals/공유-온톨로지레이어구축/16-data-input-module.md**: Candidate/Triple 생성 규칙 + 입력 모듈 상세
- **proposals/공유-온톨로지레이어구축/17-export-module.md**: Approved Candidate → Event Export (승격 단계)

---

## Input Data 정리 (v2.1, 고정판)

이 문서는 **event-service 기준**으로 input-data 방향을 단일화한 요약본이다.
원본 논의(14-input-data.md)는 그대로 두고, 결정사항과 실행 흐름만 정리한다.

### 결정사항 (확정)

* **소유 서비스**: event-service DB (script_line / script_candidate / script_triple / mq_job).
* **wiki-service 역할**: 입력/메타/업로드 트리거만 담당, 분해/적재/승격은 event-service.
* **적재 방식**: Python batch + `INSERT IGNORE` 멱등 적재 (hash UNIQUE).
* **FK 정책**: ingest/pipeline 테이블은 **no-FK** 고정.
* **Flyway 정책**: 적용된 버전 파일 수정 금지, 변경은 **항상 새 버전(V8+)**으로 추가.
* **인덱스 정책**: 초기에는 PK/UNIQUE 중심, 조회 성능 인덱스는 필요 시 별도 버전에서 추가.
* **stage/LOAD DATA**: 사용하지 않는다. (원칙: Python batch만 사용)

---

### 1) 원천 대사 저장 (script_line)

```sql
CREATE TABLE script_line (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  drama_id BIGINT NOT NULL,
  season_no INT NOT NULL,
  episode_no INT NOT NULL,
  scene_no INT NOT NULL DEFAULT 0,
  seq_no INT NOT NULL,
  speaker_en VARCHAR(64) NOT NULL,
  speaker_ko VARCHAR(64) NULL,
  text_en TEXT NULL,
  text_ko TEXT NULL,
  source_type VARCHAR(32) NULL,   -- FILE/WIKI/API
  source_ref VARCHAR(128) NULL,   -- 파일명/업로드ID
  source_line_no INT NULL,        -- 파일 내 라인번호(옵션)
  ingest_job_id VARCHAR(128) NULL,
  line_hash BINARY(32) NOT NULL,  -- sha256(canonical_key)
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_script_line_hash (line_hash)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

### 2) 이벤트 후보 (script_candidate)

```sql
CREATE TABLE script_candidate (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  drama_id BIGINT NOT NULL,
  season_no INT NOT NULL,
  episode_start INT NOT NULL,
  episode_end INT NOT NULL,
  scene_no INT NULL,
  line_id_start BIGINT NULL,
  line_id_end BIGINT NULL,
  summary_en VARCHAR(512) NULL,
  summary_ko VARCHAR(512) NULL,
  confidence DECIMAL(4,3) NOT NULL DEFAULT 0.000,
  status VARCHAR(32) NOT NULL DEFAULT 'NEW',       -- NEW/REVIEWED/APPROVED/REJECTED
  pipeline_version VARCHAR(32) NOT NULL DEFAULT 'v1',
  candidate_hash BINARY(32) NOT NULL,
  event_id BIGINT NULL,                           -- export 결과 연결 (멱등성 키)
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_script_candidate_hash (candidate_hash)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

### 3) 트리플 (script_triple)

```sql
CREATE TABLE script_triple (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  candidate_id BIGINT NOT NULL,
  subject_type VARCHAR(16) NOT NULL,   -- CHARACTER / ENTITY / LITERAL
  subject_id BIGINT NULL,
  subject_text VARCHAR(128) NULL,
  predicate_code VARCHAR(64) NOT NULL,
  object_type VARCHAR(16) NOT NULL,
  object_id BIGINT NULL,
  object_text VARCHAR(128) NULL,
  qualifiers_json JSON NULL,           -- (옵션) 시간/장소/근거 등 확장용
  polarity VARCHAR(8) DEFAULT 'POS',   -- POS/NEG
  confidence DECIMAL(4,3) NOT NULL DEFAULT 0.000,
  pipeline_version VARCHAR(32) NOT NULL DEFAULT 'v1',
  triple_hash BINARY(32) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_script_triple_hash (triple_hash)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

### 4) MQ job (멱등/재시도 제어)

```sql
CREATE TABLE mq_job (
  job_id VARCHAR(128) PRIMARY KEY,
  step VARCHAR(32) NOT NULL,       -- INGEST/CANDIDATE/TRIPLE/EXPORT
  status VARCHAR(32) NOT NULL,     -- RECEIVED/RUNNING/DONE/FAILED
  attempt INT NOT NULL DEFAULT 0,
  locked_by VARCHAR(64) NULL,
  locked_until TIMESTAMP NULL,
  last_error TEXT NULL,
  payload_json JSON NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  done_at TIMESTAMP NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---


### 4-1) 입력 포맷(JSONL) 계약

* 각 줄은 JSON 객체 1개.
* 필수: `episode`(S01E01), `seq`(정수), `speaker_en_final` 또는 `speaker_en`.
* 옵션: `scene`, `speaker_ko_final`/`speaker_ko`, `en`/`text_en`, `ko`/`text_ko`.

#### 파싱 규칙

* `episode`는 `S{season}E{episode}`로 분해하여 `season_no`, `episode_no` 생성.
* `scene` 없으면 `scene_no=0`.
* `seq`는 정렬용으로만 사용(0/1 시작 모두 허용).
* `speaker_en`은 공백/빈값 금지(권장). 빈값 라인은 적재 대상에서 제외하는 것을 권장한다.

---

### 4-2) 정규화(Normalization) 규칙

* Unicode: NFC.
* 제어문자 제거(예: `\x0b`), 탭/개행은 공백으로 치환 가능.
* 연속 공백 1개로 압축, 양끝 trim.
* `speaker_en/ko`, `text_en/ko` 모두 동일 규칙 적용.

---

### 4-3) 해시(멱등키) 규칙 상세

* `line_hash` (BINARY(32), sha256):
  `drama_id + season_no + episode_no + scene_no + seq_no + speaker_en + text_ko + text_en + source_ref + source_line_no`
* `candidate_hash` (BINARY(32), sha256):
  `drama_id + season_no + episode_start + episode_end + scene_no + line_id_start + line_id_end + pipeline_version`
* `triple_hash` (BINARY(32), sha256):
  `candidate_id + subject + predicate_code + object + polarity + qualifiers_json + pipeline_version`

---

### 5) 실행 순서 (운영 기준)

1. **script_line** 전량 적재 (Python batch + INSERT IGNORE)
2. scene 기준으로 **script_candidate** 생성
3. 후보마다 **script_triple** 추출
4. 규칙/리뷰 후 **APPROVED만 event로 승격**
5. spoiler-policy-service는 `episode_end <= K` 게이트로 필터

---



### 5-1) 후보 생성 규칙 (MVP 고정)

1. `scene_no > 0`: scene 단위로 묶기.
2. `scene_no = 0`: seq window(기본 8줄, 범위 6~10)로 묶기.
3. 토픽 전환 휴리스틱(옵션): 물음표 증가, speaker 급변, 장면 지시문 패턴 등으로 경계 조정.

---

### 5-2) 로컬 적재 실행 (Python batch, .venv)

* `PyMySQL`은 프로젝트 `.venv`에 설치되어 있다고 가정한다.
* **LOAD DATA/Stage는 사용하지 않는다.**
* 실행 예시:

```
.venv/bin/python ingestion/scripts/ingest_script_line_jsonl.py \
  --jsonl resource/friends-s01/friends_s01_ep01-10_dialogues_labeled.jsonl \
  --drama-id 9 \
  --source-ref friends_s01_ep01-10 \
  --ingest-job-id ingest:9:S1:E01-10:local \
  --db-host 127.0.0.1 --db-port 3307 \
  --db-user nospoiler_user --db-password nospoiler_password \
  --db-name nospoiler_event
```



---

### 5-3) 트리플 추출 규칙 (MVP 고정)

* 우선순위: ASK/ANSWER/DENY/PROMISE/CONFESS/APOLOGIZE 등 발화행위형.
* subject: 기본 CHARACTER(화자 추정) 또는 LITERAL(불명확 시).
* object: 기본 LITERAL(핵심 요약 또는 원문 태그).
* 사실형(predicate 관계/행동)은 추후 확대.

---

### 5-4) 승인 기준 (MVP 권장)

* `confidence >= 0.85` → APPROVED
* `0.60 <= confidence < 0.85` → REVIEWED
* `< 0.60` → NEW 유지 또는 REJECTED
* 상태값은 `NEW/REVIEWED/APPROVED/REJECTED` 고정.

---

### 6) Export 멱등성 규칙 (개념용 요약)

1. **대상**: `script_candidate` 중 `status='APPROVED' AND event_id IS NULL`만 Export 처리한다.
2. **락(권장)**: 한 후보를 한 워커만 집게 `SELECT ... FOR UPDATE` 또는 `mq_job`으로 단계 락을 잡는다.
3. **대표 predicate**: `script_triple`에서 `candidate_id=?` 중 `confidence DESC` 1개를 대표 `predicate_code`로 선택(없으면 `OTHER`).
4. **event 생성(SQL)**: `INSERT INTO event(drama_id, summary, episode_start, episode_end, predicate_code, ...) VALUES(?,?,?,?,?,...);`
5. **event_id 확보**: `SELECT LAST_INSERT_ID();` (또는 반환된 key)
6. **멱등 링크(핵심)**: `UPDATE script_candidate SET event_id=?, updated_at=NOW() WHERE id=? AND event_id IS NULL;`
7. **중복 방지**: 위 UPDATE가 0 rows면 이미 다른 워커가 승격한 것이므로 롤백/종료한다.
8. **인물 연결(옵션)**: 라인 범위/트리플 기반으로 `event_character`를 `INSERT IGNORE`로 채운다.
9. **재시도 안전**: Export 재실행 시 `event_id IS NULL`만 처리되므로 중복 event 생성이 차단된다.

---

### 7) Export 멱등성 규칙 (운영용 고정)

1. **TX 시작** (READ COMMITTED 이상)
2. `SELECT id FROM script_candidate WHERE id=? AND status='APPROVED' AND event_id IS NULL FOR UPDATE;` (없으면 종료)
3. 대표 predicate: `SELECT predicate_code FROM script_triple WHERE candidate_id=? ORDER BY confidence DESC LIMIT 1;` (없으면 `'OTHER'`)
4. `INSERT INTO event(drama_id, summary, episode_start, episode_end, predicate_code, ...) VALUES(?,?,?,?,?,...);`
5. `SET @event_id = LAST_INSERT_ID();`
6. `UPDATE script_candidate SET event_id=@event_id, updated_at=NOW() WHERE id=? AND event_id IS NULL;`
7. **검증**: `ROW_COUNT()=1` 아니면 `SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='export race';` (TX 롤백)
8. (옵션) `event_character`는 `INSERT IGNORE`로 채운다 (동일 TX 안)
9. **TX 커밋**
10. 재시도 안전: `event_id IS NULL`만 처리 + row lock으로 중복 생성/고아 event 방지

---

### 8) 해시 멱등성 요약 (고정)

* `line_hash`:
  `drama_id + season/episode/scene/seq + speaker + ko/en + source_ref + source_line_no`
  기반 canonical key를 **sha256**으로 생성.
* `candidate_hash` / `triple_hash`: 추출 규칙 + `pipeline_version`이 동일하면 같은 해시.
* 해시는 `BINARY(32)`로 저장하고 UNIQUE로 멱등성 보장.

---


### 8-1) mq_job 규약 (권장)

* job_id 예시:
  * ingest: `ingest:{dramaId}:S{season}:E{episode}:{sourceHash12}`
  * candidate/triple/export: `...:v{pipeline_version}`
* 상태 전이: RECEIVED → RUNNING → DONE, 실패는 FAILED로 전이 후 재시도.
* 락 획득(패턴):

```
UPDATE mq_job
SET status='RUNNING',
    attempt=attempt+1,
    locked_by=?,
    locked_until=DATE_ADD(NOW(), INTERVAL 2 MINUTE)
WHERE job_id=?
  AND status IN ('RECEIVED','FAILED')
  AND (locked_until IS NULL OR locked_until < NOW());
```

---

### 8-2) 검증/관측 (필수/권장)

**적재 검증(필수)**:

```
SELECT season_no, episode_no, COUNT(*) AS lines
FROM script_line
WHERE drama_id=?
GROUP BY season_no, episode_no
ORDER BY season_no, episode_no;
```

```
SELECT speaker_en, COUNT(*) c
FROM script_line
WHERE drama_id=? AND season_no=? AND episode_no=?
GROUP BY speaker_en
ORDER BY c DESC
LIMIT 30;
```

**파이프라인 메트릭(권장)**:
ingested_lines, created_candidates, extracted_triples, approved_count, exported_events, export_failures.

---

### 8-3) Do / Don’t / DoD

**Do**
* 모든 단계는 `*_hash UNIQUE + INSERT IGNORE`로 멱등 보장.
* Export는 **TX + FOR UPDATE + event_id 업데이트(ROW_COUNT=1)**로 고정.
* `pipeline_version` 올려 재추출 공존 가능하게 설계.

**Don’t**
* ingest/pipeline 테이블에 FK 추가 금지.
* 적용된 Flyway 파일 수정 금지.
* Export에서 트랜잭션 없이 insert 후 update 금지.
* 상태값 임의 확장 금지.

**DoD**
1. 동일 JSONL을 2회 적재해도 `script_line` row 수 증가 없음.
2. candidate/triple 재실행에도 row 수 증가 없음(동일 pipeline_version).
3. Export 중복 실행해도 event 중복 생성 없음(event_id 기반).
4. 재시도/워커 재기동 후에도 mq_job에 진행상태가 남는다.

---

# V9: 성능 인덱스 추가 (추후 생성)

경로: `services/event-service/src/main/resources/db/migration/`
파일명: `V9__add_script_ingestion_indexes.sql` (추후 생성)

> 원칙: V8에서는 PK/UNIQUE 위주로 두고, V9에서 조회용 인덱스를 추가한다.  
> 현재는 계획만 문서화하고, 실제 파일은 추후 생성한다.

```sql
-- V9__add_script_ingestion_indexes.sql
-- event-service DB

-- script_line: episode/scene/seq 조회 + job 단위 정리/추적
CREATE INDEX idx_script_line_drama_ep_scene_seq
  ON script_line (drama_id, season_no, episode_no, scene_no, seq_no);

CREATE INDEX idx_script_line_drama_ep
  ON script_line (drama_id, season_no, episode_no);

CREATE INDEX idx_script_line_speaker
  ON script_line (speaker_en);

CREATE INDEX idx_script_line_ingest_job
  ON script_line (ingest_job_id);


-- script_candidate: 리뷰 큐 / K 게이팅 / 승인 흐름
CREATE INDEX idx_candidate_drama_ep_status
  ON script_candidate (drama_id, season_no, episode_end, status);

CREATE INDEX idx_candidate_status_conf
  ON script_candidate (status, confidence);

CREATE INDEX idx_candidate_scene
  ON script_candidate (drama_id, season_no, episode_end, scene_no);


-- script_triple: candidate별 조회 + predicate 필터
CREATE INDEX idx_triple_candidate
  ON script_triple (candidate_id);

CREATE INDEX idx_triple_predicate
  ON script_triple (predicate_code);

CREATE INDEX idx_triple_predicate_conf
  ON script_triple (predicate_code, confidence);


-- mq_job: 워커 락/재시도/대기열 조회
CREATE INDEX idx_job_step_status
  ON mq_job (step, status);

CREATE INDEX idx_job_status_lock
  ON mq_job (status, locked_until);
```

---

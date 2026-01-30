좋아. 지금 상태(에피소드/씬/순번 + 화자 + EN/KO 대사)가 **DB에 넣기 딱 좋은 “원천 데이터”**고, 그 위에 **Event/Triple/Predicate는 2차 가공 레이어**로 얹는 게 제일 안정적이야.
한 번에 “완벽한 이벤트 추출”로 가면 거의 100% 흔들려서, **원천 → 후보 → 확정** 3단으로 가자.

---

## 1) 먼저 DB에 “원천 대사”를 그대로 넣자 (ScriptLine 레이어)

### 왜?

* 이벤트 추출 로직이 바뀌어도 **원본은 그대로**라 재추출 가능
* “스포일러 정책 설명(Explain)” 할 때 **근거 라인**을 바로 보여줄 수 있음
* 나중에 Episode K 게이팅에도 **에피소드 경계가 명확**

### 추천 테이블 (event-service 쪽에 두는 걸 추천)

```sql
CREATE TABLE script_line (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  drama_id BIGINT NOT NULL,
  episode INT NOT NULL,          -- 1..n
  scene INT NOT NULL,
  seq INT NOT NULL,              -- scene 내 순서 or 전체 순서
  speaker_raw VARCHAR(64) NOT NULL,
  text_en TEXT,
  text_ko TEXT,
  source VARCHAR(128),           -- 파일명/버전
  line_hash CHAR(40) UNIQUE,     -- 중복 방지(sha1 등)
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

* 너가 만든 CSV/JSONL을 그대로 **bulk insert**하면 끝.
* `line_hash`는 “같은 라인 중복 적재” 방지용 보험.

---

## 2) 다음은 “이벤트 후보”를 만들자 (EventCandidate 레이어)

대사는 촘촘해서 그대로 Event로 만들면 너무 많아져.
그래서 먼저 **후보 테이블**에서 정리하고 승인(혹은 자동 승인 조건)을 태우자.

```sql
CREATE TABLE event_candidate (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  drama_id BIGINT NOT NULL,
  episode_start INT NOT NULL,
  episode_end INT NOT NULL,
  scene INT,
  line_id_start BIGINT,
  line_id_end BIGINT,
  summary_en VARCHAR(512),
  summary_ko VARCHAR(512),
  confidence DECIMAL(4,3) NOT NULL,  -- 0~1
  status VARCHAR(32) NOT NULL,       -- NEW/REVIEWED/APPROVED/REJECTED
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**후보를 만드는 단위(강추):**

* 기본: `scene` 단위로 끊고
* 그 안에서 **“대화 토픽이 바뀌는 지점”** 혹은 **“질문-답변 묶음”** 으로 3~10줄 정도를 한 이벤트 후보로 묶기
  (너무 길면 한 후보에 사실이 여러 개 들어가고, 너무 짧으면 파편화됨)

---

## 3) 트리플을 이벤트에 붙이자 (EventTriple 레이어)

여기서부터 “온톨로지 맛”이 들어간다 🍲
RDF처럼 완전 일반형으로 가도 되고, 우리 서비스에 맞게 “가벼운 트리플 테이블”로 가도 돼.

```sql
CREATE TABLE event_triple (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  event_candidate_id BIGINT NOT NULL,
  subject_type VARCHAR(16) NOT NULL,   -- CHARACTER / ENTITY / LITERAL
  subject_id BIGINT NULL,
  subject_text VARCHAR(128) NULL,

  predicate_code VARCHAR(64) NOT NULL, -- enum 코드
  object_type VARCHAR(16) NOT NULL,
  object_id BIGINT NULL,
  object_text VARCHAR(128) NULL,

  polarity VARCHAR(8) DEFAULT 'POS',   -- POS/NEG (부정문 처리)
  confidence DECIMAL(4,3) NOT NULL,
  FOREIGN KEY (event_candidate_id) REFERENCES event_candidate(id)
);
```

### predicate_code는 어떻게?

처음부터 거대한 taxonomy 만들지 말고, **대사 기반 MVP용 상위 20~40개**만 잡고 시작하면 된다.

예시 (대사에서 자주 나오는 것들):

* `DATE_WITH`, `CRUSH_ON`, `BREAK_UP`, `WORKS_WITH`
* `INTRODUCE_PERSON`, `MENTION_PERSON`
* `DENY`, `CONFESS`, `ASK`, `PROMISE`
* `GO_TO`, `MEET_AT`, `CALL`, `INVITE`

그리고 애매하면 무조건:

* `predicate_code = OTHER` + `object_text`에 원문 정보 남기기
  이게 “진행을 멈추지 않는” 핵심.

---

## 4) 확정 이벤트는 기존 Event 테이블로 “승격”

후보가 승인되면 너희 프로젝트의 `event`에 들어간다.

* `event.summary` = 후보 summary
* `episode_start/end` = 후보 값
* `predicate_code` = 대표 predicate (혹은 “주요 태그”)
* `source_type = SCRIPT`
* `source_id = script_line range` 또는 `event_candidate_id`

그리고 연결:

* `event_character`: 등장인물 (SPEAKER / MENTIONED / TARGET 같은 role로)
* `event_relation`: 이벤트끼리의 관계(원인-결과, 선후, 동일토픽 등)는 나중에

---

## 5) “DB에 어떻게 넣을지” 실행 순서 (가장 현실적인 루트)

1. **script_line** 전량 적재 (EP01~10부터)
2. scene별로 묶어서 **event_candidate** 자동 생성
3. 후보마다 LLM/룰 기반으로 **event_triple** 추출 + confidence 부여
4. confidence 높고 규칙 충족하면 자동 APPROVE, 아니면 REVIEW 큐로
5. APPROVED만 **event로 승격** + event_character 채우기
6. spoiler-policy-service는 기존대로 `episode_end <= K` 게이트로 필터

---

## 6) 네 예시를 이 구조로 보면 이렇게 들어간다

원문:

* Monica: There's nothing to tell!
* Chandler: He's just some guy I work with!
* Joey: C'mon, you're going out with the guy!

가능한 트리플(후보):

* (Chandler) `WORKS_WITH` (UnknownGuy)
* (Chandler) `DATE_WITH` (UnknownGuy) [Joey 발화 기반, confidence 중간]
* (Monica) `DENY` (TELLING_DETAIL) [대사행위형 predicate]

이런 식으로 “사실형 + 발화행위형” 둘 다 담을 수 있음.

---

## 결론: “넣는 방식” 한 줄 요약

* **대사는 script_line으로 100% 보존**
* **이벤트/트리플은 후보 레이어에서 추출해서 승인 후 event로 승격**
* predicate는 처음엔 얇게, `OTHER`로 탈출구 확보

---

원하면, 지금 너한테 맞춰서 **“predicate_code 초안 40개”**를 (대사 기반으로) 바로 뽑고,
`event_character.role`도 **SPEAKER / MENTIONED / TARGET** 같은 최소 세트로 딱 고정해서 V3 마이그레이션 형태(Flyway SQL)까지 같이 써줄게.
=====
>>>>>


좋아. 먼저 결론부터 찍자.

## 이게 Wiki 서비스 역할이냐?

**“원천 텍스트를 받는 입구”는 Wiki 서비스 쪽이 맞는데**,
**대사 → Event/Triple/Predicate로 분해해서 ‘지식 그래프’를 만드는 일은 Wiki의 본업이 아니야.**

Wiki는 “사람이 읽는 문서”를 다루고, Event는 “질의/필터/스포 게이팅”을 다루는 쪽이라서, 역할을 섞으면 금방 지옥문 열려. (변경이 서로 전염됨)

### 권장 책임 분리

* **wiki-service**

  * 원문 저장: 위키 문서, 사용자 작성 요약, 편집 이력
  * 표시/검색: 사람이 읽는 페이지 렌더링
  * “분해 요청” 트리거: MQ로 “이 문서/대사 묶음 분석해줘” 메시지 발행
  * 결과 참조: event ids / candidate ids를 링크로만 보관

* **event-service**

  * 정규화 저장: event, event_character, event_relation, event_reveal(너희 기존)
  * (추가) script_line / event_candidate / event_triple 같은 “그래프 생성용 테이블” 소유
  * K-episode 게이팅을 위한 episode_start/end 책임

* **intelligence/filter 워커(별도 프로세스 가능)**

  * MQ 소비해서 대사 묶고, 후보 만들고, 트리플 추출하고, confidence 계산
  * event-service로 적재(API 또는 DB direct는 비추)

즉, **Wiki는 ‘문서 편집기’**, Event는 **‘지식 그래프 저장소’**, 워커는 **‘증류기’**.

---

## predicate_code 초안 40개

처음부터 거대 분류는 금지. 대사 기반으로 “자주 쓰는 상위”만. (나머지는 `OTHER` 탈출구)

### 관계

1. `DATE_WITH`
2. `CRUSH_ON`
3. `BREAK_UP`
4. `MARRY`
5. `DIVORCE`
6. `FRIENDS_WITH`
7. `FAMILY_OF`
8. `WORKS_WITH`
9. `BOSS_OF`
10. `ROOMMATE_OF`

### 이동/만남/행동

11. `GO_TO`
12. `LEAVE`
13. `MEET_WITH`
14. `FOLLOW`
15. `HIDE_FROM`
16. `HELP`
17. `FIGHT_WITH`
18. `CHASE`

### 커뮤니케이션

19. `CALL`
20. `TELL`
21. `ASK`
22. `ANSWER`
23. `INVITE`
24. `INTRODUCE`
25. `PROMISE`
26. `APOLOGIZE`

### 감정/태도

27. `LIKE`
28. `HATE`
29. `JEALOUS_OF`
30. `WORRIED_ABOUT`
31. `ANGRY_AT`
32. `THANK`

### 상태/사실

33. `IS_PREGNANT`
34. `IS_SICK`
35. `HAS_JOB`
36. `LOSES_JOB`
37. `HAS_ITEM`
38. `LOSES_ITEM`

### 발화행위(스포일러 필터에 꽤 유용)

39. `DENY`
40. `CONFESS`

그리고 항상 예비:

* `OTHER` (텍스트로 보존)
* `UNKNOWN_PERSON` 같은 엔티티도 허용 (object_text로)

---

## event_character.role 최소 세트

너희가 v3에서 `event_character.role` 넣는 흐름이 딱 맞아. 처음은 이 정도면 충분해.

* `SPEAKER` : 그 라인의 화자
* `PARTICIPANT` : 사건에 실제 참여
* `TARGET` : 행위의 대상(고백 대상, 공격 대상 등)
* `MENTIONED` : 언급만 됨
* `RECIPIENT` : 말/선물/전화의 수신자
* `OWNER` : 소유자(아이템 소유 관계에 사용)
* `WITNESS` : 목격자(있으면 좋고 없어도 됨)

---

## DB 적재 스키마 제안 (Flyway용 초안)

“대사 원천”과 “후보/트리플”은 **event-service DB에 두는 게 정석**이야.

### 1) script_line (원천)

```sql
CREATE TABLE script_line (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  drama_id BIGINT NOT NULL,
  season INT NOT NULL,
  episode INT NOT NULL,
  scene INT NOT NULL,
  seq INT NOT NULL,
  speaker_en VARCHAR(64) NOT NULL,
  speaker_ko VARCHAR(64) NULL,
  text_en TEXT NULL,
  text_ko TEXT NULL,
  source VARCHAR(128) NULL,
  line_hash CHAR(40) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_script_line_hash (line_hash),
  KEY idx_script_line_drama_ep (drama_id, season, episode, scene, seq)
);
```

### 2) event_candidate (묶음)

```sql
CREATE TABLE event_candidate (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  drama_id BIGINT NOT NULL,
  season INT NOT NULL,
  episode_start INT NOT NULL,
  episode_end INT NOT NULL,
  scene INT NULL,
  line_id_start BIGINT NULL,
  line_id_end BIGINT NULL,
  summary_en VARCHAR(512) NULL,
  summary_ko VARCHAR(512) NULL,
  confidence DECIMAL(4,3) NOT NULL DEFAULT 0.000,
  status VARCHAR(32) NOT NULL DEFAULT 'NEW',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  KEY idx_candidate_drama_ep (drama_id, season, episode_end, status)
);
```

### 3) event_triple (후보 트리플)

```sql
CREATE TABLE event_triple (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  candidate_id BIGINT NOT NULL,

  subject_type VARCHAR(16) NOT NULL,   -- CHARACTER/ENTITY/LITERAL
  subject_id BIGINT NULL,
  subject_text VARCHAR(128) NULL,

  predicate_code VARCHAR(64) NOT NULL,

  object_type VARCHAR(16) NOT NULL,
  object_id BIGINT NULL,
  object_text VARCHAR(128) NULL,

  polarity VARCHAR(8) NOT NULL DEFAULT 'POS',  -- POS/NEG
  confidence DECIMAL(4,3) NOT NULL DEFAULT 0.000,

  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  KEY idx_triple_candidate (candidate_id),
  KEY idx_triple_predicate (predicate_code),
  CONSTRAINT fk_triple_candidate
    FOREIGN KEY (candidate_id) REFERENCES event_candidate(id)
      ON DELETE CASCADE
);
```

### 4) predicate_code_catalog (코드북)

```sql
CREATE TABLE predicate_code_catalog (
  code VARCHAR(64) PRIMARY KEY,
  category VARCHAR(32) NOT NULL,
  description_ko VARCHAR(255) NULL,
  description_en VARCHAR(255) NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1
);
```

이 코드북은 “정의된 것만 쓰기” 강제에도 좋고, 나중에 UI 필터에도 바로 써먹혀.

---

## 파이프라인 실행 흐름 (Wiki가 “요청만” 하는 구조)

1. wiki-service가 대사/문서 업로드(또는 링크) 받음
2. MQ로 `ANALYZE_SCRIPT(drama_id, season, episode_range, source)` 발행
3. 워커가 script_line 적재, candidate 생성, triple 생성
4. confidence 기준으로 `APPROVED`면 event-service의 **정식 event로 승격**
5. wiki-service는 event id를 참조해서 “이 문서가 어떤 이벤트를 담는지”만 연결

---

정리하면, **“이거 Wiki 역할 아니냐?”**에 대한 답은:

* **입력과 편집 UX는 Wiki**
* **정규화(Event/Triple)와 스포일러 엔진 재료 생산은 Event/Intelligence**

이렇게 나누면 너희 “nospoiler”가 커져도, 각 서비스가 자기 소설을 안 쓰고 자기 역할만 수행해.

다음 액션은 내가 질문 안 하고 제안까지 적을게:
너희 DB에 이미 `event.predicate_code`가 들어가는 흐름이 있으니까, 위 `predicate_code_catalog`부터 넣고, `script_line → candidate → triple` 테이블을 event-service에 추가한 뒤, 워커가 candidate를 만들면서 predicate_code를 채우는 걸 1차 목표로 잡으면 된다.

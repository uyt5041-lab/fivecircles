# Anti-Hallucination Plan: Answerability Gate (exists + limit=1)

목표
- DB에 정답 이벤트가 없는 구간(예: 시즌 미구축)에서 “그럴듯한 오답”이 생성되는 것을 구조적으로 차단한다.
- “결과 0건”을 하나로 퉁치지 않고, 아래 3상태로 분기한다.
  - `ANSWERED`: K 이하에서 근거 기반으로 답변 가능
  - `SPOILER_BLOCKED`: DB에는 있지만 K 밖(또는 사용자 노출 금지 정책에 의해 LOCKED)
  - `NOT_ENOUGH_DATA`: DB에 데이터 자체가 없음

비목표
- object(텍스트 대상) 1급 엔티티화, `target_key` 도입 등 V3 범위 변경은 여기서 하지 않는다.
- 기존 `api3/api4`의 응답 계약을 변경하지 않는다.

---

## 문제 정의

현재 오답은 크게 2종류로 발생한다.

1. **정답 공백(데이터 미구축) 오답**
- 실제로 DB에 “정답 이벤트”가 없는데, 시스템이 근사치/대체값을 골라 정답처럼 보여줌.
- 결과가 0건일 때 “그냥 없음”으로만 처리하면, 스포일러 차단인지/데이터 미구축인지 구분이 안 되고 운영 루프도 끊김.

2. **근사 쿼리(semantic drift) 오답**
- 질문 의미를 충분히 좁히지 못한 근사 조건(예: `DISCOVERS OR LEARNS`)은 0건이 아니라서 exists 게이트를 통과하지만,
  질문 의도(예: “범죄 사실”)와 다른 이벤트(예: “경제/스트레스 인식”)를 정답으로 확정해버릴 수 있음.
- 집계(ALLY/ADVERSARY)도 “점수”만으로 라벨을 확정하면, 신호 없는 관계가 뒤집혀 적이 친구가 되는 오분류가 발생함.

---

## 해결 방향(핵심 전략)

핵심은 “답변 가능성(answerability)”과 “정답성(correctness)”을 분리해 각각을 다른 안전장치로 막는 것이다.

1. **Answerability Gate (exists + limit=1)**
- K 이하 답변 시도를 먼저 하고, 0건일 때만 probe(`existsSafeApproved/existsAnyApproved` boolean only)로 3상태를 판정한다.
- 사용자-facing은 `disclosurePolicy`로 `SPOILER_BLOCKED`를 숨길 수 있어야 한다(민감 질문은 `LOCKED`로 통합).

2. **Strict Answer Query vs Approx Candidate Query**
- “근사 후보”는 만들 수 있지만, `Strict Answer Query`(MUST 강화)로 1건도 안 잡히면 `ANSWERED`를 금지한다.
- 즉, 근사 쿼리는 후보/설명용이며 정답 확정용이 아니다.

3. **Aggregate 라벨 확정 게이트(ALLY/ADVERSARY)**
- 점수는 정렬용으로만 사용하고, 라벨은 “evidence(predicate 존재)”를 최소 1개 이상 만족할 때만 확정한다.
- evidence가 없으면 중립(COEVENT/UNKNOWN)으로만 노출한다.

4. **“First”는 단독이 아니라 `first_<predicate>`로 모델링**
- `first` 단독 질문은 “무엇의 first인지”가 모호해서(첫 등장/첫 만남/첫 살인/첫 배신...) 오답/드리프트를 만들기 쉽다.
- 따라서 “First는 특별”을 1급 기능으로 가져가려면, `first_<predicate>`(예: `first_meets`, `first_kills`)처럼
  **predicate가 포함된 템플릿 패밀리**로 고정하는 것이 안전하다.
- 이 구조는 `Strict Answer Query`(predicate 포함)와 `exists` probe가 자연스럽게 정렬돼서,
  데이터 미구축/근사 후보 문제를 같이 제어할 수 있다.

FactGrid 해석(개념 주석)
- 1) `ASK/EXISTS/LIMIT 1` = “답할 자격이 있는가” 확인
- 2) `SELECT` = “정답 후보를 가져오기”
- 3) 라벨 확정은 `ASK { ... predicate ... }`로 최소 근거를 요구
- 4) `first_<predicate>`는 `ORDER BY ?episode LIMIT 1`의 전형적인 적용처다

FactGrid 해석(주석)
```sparql
# first_meets (Strict Answer Query 예시)
SELECT ?event WHERE {
  ?event wdt:Pparticipant wd:A ;
         wdt:Pparticipant wd:B ;
         wdt:Ppredicate wd:MEETS .
} ORDER BY ?episode LIMIT 1
```

---

## 용어

- `K`: 사용자 스포일러 안전 회차(`safeUpToEpisode`)
- `existsSafeApproved`: 질문 의미(MUST 조건)를 만족하는 근거가 `episode_end <= K` 안에 존재하는지
- `existsAnyApproved`: 질문 의미(MUST 조건)를 만족하는 근거가 DB 전체(승인된 범위) 어디엔가 존재하는지
- `disclosurePolicy`: 사용자-facing에서 `existsAnyApproved`/`SPOILER_BLOCKED`를 노출할지 숨길지 결정하는 플래그
- `probe`: 정답 이벤트를 반환하지 않고, 존재 여부만 boolean으로 판정하는 전용 질의(anti-halu 게이트용)

FactGrid 해석(개념 주석)
- `exists`는 SPARQL로는 `ASK { ... }`에 해당한다.
- `LIMIT 1`은 `SELECT ... LIMIT 1`로 “존재 확인”만 하는 패턴이다.

---

## 핵심 규칙(합의된 실행 흐름)

원칙
- 성공 케이스에서 추가 호출이 생기지 않도록, “답(<=K) 조회”를 먼저 시도한다.
- 0건일 때만 probe로 “왜 0건인지”를 판정한다.
- `exists`는 “답할 수 있는가(answerability)”만 다루고, “정답이 맞는가(correctness)”는 별도의 규칙으로 다룬다.
- fallback은 “의미 동치(equivalent)”인 경우에만 허용한다. 의미 약화 fallback(정답성 훼손)은 금지한다.

실행 순서(고정)
1. `Strict Answer Query(<=K)` 실행
2. Strict가 0건이면 `probe(existsSafeApproved/existsAnyApproved)` 실행
3. (선택) `Approx Candidate Query` 실행 — 내부 참고용, 정답 확정 금지

### Step 1. Strict Answer Query 먼저(<=K)
- 템플릿이 생성한 `Strict Answer Query`를 `safeUpToEpisode=K`로 먼저 실행한다.
- Strict 결과가 1건 이상이면 `ANSWERED`로 종료한다.
- Strict 결과가 0건이면 Step 2(probe)로 이동한다.

FactGrid 해석(주석)
```sparql
# (Answer query; 실제론 결과를 가져오는 SELECT)
SELECT ?event WHERE {
  ?event wdt:Pparticipant wd:Subject .
  # + MUST 조건들 (predicate / keyword / withCharacter 등)
  # + 안전 범위: episode_end <= K
} ORDER BY ?episode LIMIT N
```

### Step 2. 0건이면 probe(existsAnyApproved) 호출
- Step 1이 0건이면, probe 전용 엔드포인트를 호출해 `existsSafeApproved/existsAnyApproved`를 boolean으로 얻는다.
- 여기서 `existsSafeApproved`는 사실상 Step 1에서 이미 0건이므로 대부분 `false`가 되지만,
  - 구현상 “동일한 MUST 조건”이 맞는지 검증할 수 있도록 응답엔 둘 다 포함해도 된다.

FactGrid 해석(주석)
```sparql
# existsSafeApproved (<=K)
ASK {
  ?event wdt:Pparticipant wd:Subject .
  # + MUST 조건들
  # + episode_end <= K
}

# existsAnyApproved (전체)
ASK {
  ?event wdt:Pparticipant wd:Subject .
  # + MUST 조건들
}
```

### Step 3. 3상태 판정 + 마스킹(disclosurePolicy)
- 내부(QA/운영): `ANSWERED / SPOILER_BLOCKED / NOT_ENOUGH_DATA`를 그대로 노출 가능.
- 사용자-facing: `disclosurePolicy=HIDE_EXISTS_BEYOND_K`면 `SPOILER_BLOCKED`를 노출하지 않고 `LOCKED`로 합친다.

판정 표(내부 기준)
| existsSafeApproved | existsAnyApproved | status |
|:---:|:---:|---|
| O | O | `ANSWERED` |
| X | O | `SPOILER_BLOCKED` |
| X | X | `NOT_ENOUGH_DATA` |

---

## 템플릿별 Strict MUST 확정 가이드(초안)

원칙
- 템플릿마다 MUST를 고정하지 않으면, 구현 단계에서 Strict/Approx 경계가 다시 흔들린다.
- 아래 표는 “Phase 1~2에서 우선 고정할 최소 MUST” 예시다.

| Template 예시 | Strict MUST(최소) | Approx(참고용) |
|---|---|---|
| `first_kills` (Q1 류) | `subjectId` + `predicateCode=KILLS` | subject 타임라인 + 액션계열 broad predicate |
| `first_meets` (Q3 류) | `subjectA` + `subjectB` + `predicateCode=MEETS` | coevents earliest (predicate 미지정) |
| `first_production` (Q2 류) | `subjectId` + `qAnyOf`(유의어+정규화 토큰) | subject + broad keyword only |
| `skyler_discovers_crime` (Q4 류) | `subjectId=Skyler` + (`DISCOVERS|LEARNS`) + crime 신호(`qAnyOf` 또는 about/reveal) | `DISCOVERS|LEARNS` only |

주의
- Strict MUST를 만족하지 못하면 Approx 후보가 있어도 `ANSWERED` 금지.
- 템플릿별 MUST는 문서/코드에서 1:1로 동기화한다.

FactGrid 해석(주석)
```sparql
# 템플릿별 MUST는 결국 “ASK/SELECT의 WHERE 절을 고정”하는 작업이다.
```

---

## “근사 쿼리”로 인한 오답 방지: Strict Answer Query vs Approx Candidate Query

문제
- 질문 템플릿이 근사 조건(예: `DISCOVERS OR LEARNS`)만으로 답을 고르면,
  DB에 0건이 아니기 때문에 `exists` 게이트는 통과하지만 의미가 틀린 이벤트가 선택될 수 있다.
- 즉, `exists`는 “데이터가 없다/있다”만 판정하고, “그 데이터가 질문 의미를 충족하는가”는 별도로 막아야 한다.

해결 원칙
- 템플릿(질문)마다 쿼리를 2개로 나눈다.
  - `Strict Answer Query`(정답 확정용, MUST 조건 최대): 이 쿼리가 1건도 없으면 `ANSWERED` 금지.
  - `Approx Candidate Query`(후보/탐색/설명용): 정답이 아니라 “가능한 후보 목록”이다.

실행 규칙(권장)
1. `Strict Answer Query(<=K)`를 먼저 실행한다.
2. Strict가 1건 이상이면 그 안에서 earliest/score로 정답을 고른다. (`ANSWERED`)
3. Strict가 0건이면:
   - 근사 후보(Approx)가 있더라도 정답 확정은 금지
   - 상태는 probe로 `SPOILER_BLOCKED`/`NOT_ENOUGH_DATA`로만 판정
   - (내부용) 후보를 “참고용”으로 보여주는 것은 가능하되, 정답으로 라벨링 금지

FactGrid 해석(주석)
```sparql
# Strict Answer Query (정답 확정): MUST를 최대한 반영한 SELECT
SELECT ?event WHERE {
  ?event wdt:Pparticipant wd:Skyler .
  ?event wdt:Ppredicate wd:DISCOVERS .
  # + MUST: crime keyword OR reveal-about OR co-participant(Walter) 등
  # + episode_end <= K
} ORDER BY ?episode LIMIT N

# Approx Candidate Query (후보): 의미 약화된 SELECT (정답 확정에 쓰면 안 됨)
SELECT ?event WHERE {
  ?event wdt:Pparticipant wd:Skyler .
  FILTER(?predicate IN (wd:DISCOVERS, wd:LEARNS))
  # + episode_end <= K
} ORDER BY ?episode LIMIT N
```

템플릿 작성 가이드(예시: Q4 류)
- Strict MUST를 강화할 수 있는 신호 후보(현 스키마 내)
  - keyword(q)로 “범죄/마약/제조/하이젠베르그/DEA…” 같은 토큰 동시 만족
  - (가능하면) 사건 등장인물에 “about(월터)” 캐릭터가 포함
  - (가능하면) `event_reveal` about/target 조건(존재할 때만)
- 위 신호가 없으면, “Skyler가 뭔가를 발견했다”는 후보는 뽑아도 “범죄 사실” 정답 확정은 금지한다.

---

## Aggregate(ALLY/ADVERSARY) 오분류 방지: 라벨 확정 게이트

문제
- 점수 기반 집계에서 신호가 약한 관계가 점수로만 “적/아군”으로 라벨링되면,
  실제론 중립(coevents)인 관계가 ally/adversary로 오분류될 수 있다.

해결 원칙
- `score`는 정렬에 쓰되, **라벨(ALLY/ADVERSARY) 확정은 최소 evidence 조건을 만족할 때만** 한다.
- evidence 조건을 못 만족하면 “중립(=COEVENT/UNKNOWN)”으로만 노출한다.

권장 라벨 확정 규칙(예시)
- `ALLY` 라벨: ally-signal 그룹 카운트가 1 이상일 때만
  - 예: `ALLIES_WITH`, `JOINS`, `HELPS`, `AFFILIATION_CHANGE`(정의된 그룹) 등
- `ADVERSARY` 라벨: adversary-signal 그룹 카운트가 1 이상일 때만
  - 예: `ATTACKS`, `BETRAYS`, `THREATENS`, `BATTLE`, `KILLS` 등
- 위 evidence가 없으면 score가 높아도 `COEVENTS`로만 처리(라벨 금지)

FactGrid 해석(주석)
```sparql
# 라벨 확정은 “점수”가 아니라 “특정 predicate가 존재하는가(ASK)”로 결정한다.
ASK { ?event wdt:Pparticipant wd:Walter ; wdt:Pparticipant wd:Other ; wdt:Ppredicate wd:BETRAYS . }
```

## 구현 작업(Phase)

### Phase 1. event-service: probe 전용 엔드포인트 추가

목표
- 기존 api3/api4는 손대지 않고, “존재 판정”만 담당하는 endpoint를 별도로 둔다.
- 응답은 boolean only (이벤트 id/회차/요약 반환 금지).

권장 API(초안)
- **단일 endpoint로 통일**
- `POST /api/event/v2/probe`
- Request body(“질문 의미 MUST 조건”을 스냅샷으로 전달)
  - `queryKind` (예: `character_predicate_earliest`, `coevents_earliest`)
  - `safeUpToEpisode` (K)
  - `strictFilters` (subject/with/predicateCodeAnyOf/qAnyOf/about 등)
- Response
  - `{ existsSafeApproved: boolean, existsAnyApproved: boolean }`

설계 메모(단일 endpoint 장점)
- 파라미터 증가(캐릭터, coevents, about/reveal, aggregate 관련 필터)에 대비해 URL을 늘리지 않고 body 스키마로 확장 가능.
- `queryKind + strictFilters` 조합으로 템플릿별 MUST를 명시적으로 재현할 수 있다.

FactGrid 해석(주석)
```sparql
# endpoint가 하는 일은 결국 ASK 2개를 boolean으로 내리는 것.
```

주의
- `existsAnyApproved=true` 자체가 스포일러가 될 수 있으므로, probe는 **항상 boolean만** 반환한다.
- 민감도 정책(disclosurePolicy)은 probe가 아니라 상위 레이어(FE 또는 향후 qa-service)가 담당한다.

### Phase 2. FE: executor에 “0건일 때만 probe” 로직 추가

목표
- 성공 케이스는 기존처럼 1콜로 끝낸다.
- 결과 0건일 때만 probe 호출로 상태를 판정한다.

구현 포인트
- ProductionQTemplate에 `disclosurePolicy` 필드 추가
  - `ALLOW_SPOILER_BLOCKED`
  - `HIDE_EXISTS_BEYOND_K`
- executor는 아래 순서로 동작
  1) Strict answer query(<=K) 실행
  2) 0건이면 probe 호출
  3) internal status(`SPOILER_BLOCKED/NOT_ENOUGH_DATA`)를 구하고,
  4) (선택) Approx candidate query 실행(내부 참고용, 정답 확정 금지)
  5) 사용자-facing이면 `disclosurePolicy`로 `LOCKED` 처리

권장 모델링(`LOCKED` 위치)
- `LOCKED`는 backend status enum이 아니라 **frontend view-state**로 처리한다.
  - backend/domain status: `ANSWERED | SPOILER_BLOCKED | NOT_ENOUGH_DATA` (의미 보존)
  - frontend view-state: `VISIBLE_ANSWER | VISIBLE_BLOCKED | VISIBLE_NO_DATA | LOCKED`
- 이유: domain 의미(관측/로그/운영)를 잃지 않으면서, 사용자 노출 정책만 UI에서 안전하게 바꿀 수 있다.

FactGrid 해석(주석)
```sparql
# 실행기는 “SELECT로 답을 시도 → 실패하면 ASK로 이유를 판정” 패턴이다.
```

### Phase 3. UI: 3상태 메시지 + 운영 보강 액션

내부(QA/운영)
- `SPOILER_BLOCKED`: “DB엔 있으나 K 밖”
- `NOT_ENOUGH_DATA`: “DB에 근거 없음(보강 대상)”

사용자-facing
- `HIDE_EXISTS_BEYOND_K`: “아직 답할 수 없음”(LOCKED)

보강 추천(운영)
- `NOT_ENOUGH_DATA` 발생 시
  - “어떤 MUST 조건으로 miss가 났는지”를 UI/로그에 남긴다.
  - 운영자가 템플릿 `qAnyOf`(유의어 + 정규화 토큰) 보강을 할 수 있게 한다.

FactGrid 해석(주석)
```sparql
# NOT_ENOUGH_DATA는 “질문이 이상하다”가 아니라 “KB가 비어있다”는 신호다.
```

### Phase 4. 관측(로그) 및 백로그 자동화(선택)

목표
- `NOT_ENOUGH_DATA`를 “데이터 보강 백로그”로 전환한다.

로그(초안)
- `QA_MISS`: `{ dramaId, K, templateId, mustFilters, timestamp }`

---

## “토큰 동기화(동치 fallback)” 가이드 (object 텍스트 miss 대응)

문제
- keyword 기반 질문에서 `q=meth`는 summary에 literal이 없으면 0건이 나올 수 있다.
- DB에는 대신 `predicate_suggestion=PRODUCTION` 같은 정규화 토큰이 들어가 있을 수 있다.

해결
- 템플릿의 `qAnyOf[]`는 “유의어 + 정규화 토큰”을 같이 포함한다.
- probe와 answer query는 동일한 `qAnyOf[]` 세트를 MUST 조건으로 사용한다.
- `qAnyOf` 확장 시 “동치 fallback”만 허용한다.
  - 허용: `meth` 확장을 위해 `PRODUCTION`(동일 의미 정규화 토큰) 추가
  - 금지: 의미가 넓은 일반 토큰을 추가해 질문 의도를 약화시키는 확장

MUST 조건 스냅샷 전달 예시
```json
{
  "queryKind": "character_predicate_earliest",
  "subjectId": 19,
  "safeUpToEpisode": 5,
  "strictFilters": {
    "predicateCodeAnyOf": ["DISCOVERS", "LEARNS"],
    "qAnyOf": ["마약", "메스", "범죄", "PRODUCTION"],
    "aboutCharacterId": 17
  }
}
```

probe 요청 예시(개념)
```http
POST /api/event/v2/probe
Content-Type: application/json

{
  "queryKind": "character_predicate_earliest",
  "safeUpToEpisode": 5,
  "strictFilters": {
    "subjectId": 19,
    "predicateCodeAnyOf": ["DISCOVERS", "LEARNS"],
    "qAnyOf": ["마약", "메스", "범죄", "PRODUCTION"],
    "aboutCharacterId": 17
  }
}
```

FactGrid 해석(주석)
```sparql
# object 텍스트는 “라벨 매칭” 문제로 귀결된다.
# MVP에선 label/alias(유의어) + 정규화 토큰으로 recall을 올리고,
# V3에 target_key/object 엔티티로 구조화한다.
```

# ex23 - RDF Inheritance Layer Implementation Plan (B안)

기준일: 2026-02-26

## 운영 고정 결론(요약)
- Runtime(Strict) = `PredicateCode` 중심으로 운영한다.
- Fallback = `PredicateSuggestionCode`를 사용한다 (`predicate_code=OTHER`, strict miss 후, ops/QA 레이어 한정).
- 상속/분류 선언은 RDF(또는 RDF 전개 taxonomy)에서 관리한다.
- 런타임은 reasoner/SPARQL 상속 전개를 수행하지 않는다.
- RDF lane SoT는 단일 파일(`predicate_axis_taxonomy.json`)로 고정한다(Phase1).
- Executor lane SoT는 `StrictQuerySpec(04 매트릭스/템플릿)`로 고정하고 taxonomy를 직접 읽지 않는다.
- SoT 경로/namespace는 현재 운영 기준(`scripts/ops/rdf/taxonomy/...`, `ns:`)을 유지한다.
- FE `strictFilters` 계약 키는 이번 페이즈에서 변경하지 않는다.

## 1) 목적
- B안(상속은 RDF, 런타임은 단일 SoT 기반, compile 산출물은 검증/동기화용)을 실행 가능한 정책/작업으로 고정한다.
- strict-first 계약(Q20/anti-halu)과 충돌 없이 확장 커버리지(WHY/맥락)를 확보한다.

## 1.1) 레이어 경계 정의 (MUST)
- Axis taxonomy = 서사 분류/신호/랭킹 레이어다.
- Query group = 질문 필터/집계 레이어다.
- 같은 groupKey를 사용하더라도 목적이 다르므로 멤버셋 동일성을 요구하지 않는다.
- Query-layer는 group 정의를 사용하고, axis taxonomy를 직접 strict 필터로 사용하지 않는다.

## 2) RDB에서 해야 되는 것 (정답 저장/조회)

### RDB-0 필수: strict-first 최소 요건
1. `event.predicate_code`가 runtime `PredicateCode`와 정합되어야 한다.
- 문서/템플릿/데이터 입력에서 enum 밖 코드 금지.
2. episode gate(K) 필터가 모든 조회에 적용 가능해야 한다.
- 예: `event.episode_end <= K`.
3. `source_status`(APPROVED/LOCKED 등) 필터가 조회에서 동작해야 한다.
- WHY/QA의 근거 신뢰도 유지.

### RDB-1 필수: SPO strict 필터 최소 요건
4. `event_character.role` 저장이 존재해야 한다.
- 현재 기준: `INVOLVED/SUBJECT/OBJECT`.
5. 미입력 role은 조회 레이어에서 `INVOLVED`로 보정해야 한다.
6. 최소 인덱스를 유지해야 한다.
- `event(predicate_code, episode_end)`
- `event_character(character_id, event_id, role)`

### RDB-2 권장: WHY/확장 질문(STATE/PRESSURE) 커버 최소 입력
7. `event_reveal`에 attribute형 reveal 입력이 가능해야 한다.
- 예: `revealsAttribute = threat_pressure_level:2`.
8. WHY 출력용 `event_relation(PRECEDES)` 체인을 최소 입력해야 한다.
- Answer-first 세트(10 + 확장 6) 중심으로 수동 구축.
9. `event_reveal.reveal_type(HINT|CONFIRM)`는 WHY/근거 강도 표시에만 사용한다.
- strict 정답 선택/승격에는 사용하지 않는다.

### RDB-3 옵션: RDF 고급 UI 지원
10. subject/object role 입력 파이프라인(DTO/mapper/backfill) 확장.
11. `event_reveal` 구조화(키/값/레벨 정규화).
- 초기에는 문자열 attribute로 시작 가능.

## 3) RDF 상속 레이어 구축에 필요한 것 (B안 핵심)

> RDF는 이벤트 원문 저장소가 아니라 Predicate taxonomy(상속 트리) 레이어로 사용한다.

### RDF-0 필수: 상속 트리 정의 최소
1. 상위 클래스(그룹) 노드 정의.
- 현재 query-layer 기준 예시: `AFFILIATION_CHANGE`, `DEATH_EXIT`, `BATTLE`, `ADVERSARY`, `ALLY`.
- 운영 groupKey는 query-layer SoT(`fivecircles/architecture/specs/predicate/groups.md`)를 우선 참조한다.
2. 하위 predicate leaf 노드 정의.
- leaf는 runtime/fallback 구분 정보(`kind`)와 코드 식별자(`code`)를 가져야 한다.
3. `rdfs:subClassOf`(또는 동등한 관계)로 트리 연결.

### RDF-1 필수: 전개(compile) 파이프라인
4. 빌드/ops 스크립트 1개.
- 입력: RDF 상속 트리.
- 출력: `predicate_group.generated.json`.
5. 드리프트 방지 규칙.
- RDF 변경 시 generated json diff가 없으면 fail.
- RDF query-only 경로의 loader/classifier는 `predicate_axis_taxonomy.json`만 참조한다.
- executor(템플릿 정답 탐색 경로)는 taxonomy를 직접 읽지 않고 `StrictQuerySpec`만 참조한다.
- generated 결과는 리뷰/검증/문서 동기화 아티팩트로만 사용한다(Phase1).

### RDF-2 권장: 운영 편의
6. leaf에 runtime/suggestion 코드 명시.
- 예: `:code "LEAVES"`, `:kind "RUNTIME"`.
7. user-facing label(ko/en) 포함.
8. groupKey(캐노니컬 키) 고정.

### RDF-3 옵션: SPARQL 근거/맥락 UI 강화
9. RDF export에 `event_reveal` 포함.
10. Event SPO(subject/object/participant) 트리플 export.

## 4) SoT/경로/네임스페이스 통일
- taxonomy SoT: `scripts/ops/rdf/taxonomy/predicate_axis_taxonomy.json`
- taxonomy loader/classifier: `scripts/ops/rdf/predicate_axis_taxonomy.py`
- inheritance TTL: `scripts/ops/rdf/taxonomy/predicate_inheritance.ttl`
- generated output: `scripts/ops/rdf/taxonomy/predicate_group.generated.json` (옵션)
- example TTL: `scripts/ops/rdf/taxonomy/predicate_inheritance.example.ttl`
- example generated JSON: `scripts/ops/rdf/taxonomy/predicate_group.generated.example.json`
- 참고: `PRODUCTION`은 현재 enum에는 존재하지만 query-layer 그룹 매핑은 보류 상태(예시 파일 notes 참조)
- RDF namespace: `ns: <https://nospoiler.dev/ns#>`
- ex23은 taxonomy/group 의미를 신규 정의하지 않고, SoT를 참조해 상속 표현/전개 규격만 다룬다.

### SoT and Lane Boundary (MUST)
- RDF lane SoT(단일): `scripts/ops/rdf/taxonomy/predicate_axis_taxonomy.json`
- RDF query-only 경로의 loader/classifier는 위 파일만 참조한다(Phase1).
- Executor lane SoT: `StrictQuerySpec(04 매트릭스/템플릿)` (taxonomy 직접 참조 금지)
- event-service aggregate(SQL mapper 기반 그룹 집계)는 현행 하드코딩 그룹셋을 유지하며, Phase2에서 taxonomy 연동 범위를 별도 정렬한다.
- `predicate_group.generated.json`은 compile 결과의 검증/리뷰용 산출물이며 런타임은 참조하지 않는다(Phase1).
- Axis는 분류/신호, Group은 필터다. 동일 groupKey라도 멤버셋 동일성을 요구하지 않는다.

## 5) 전개(compile) 규격
### 입력
- `predicate_inheritance.ttl`
- `predicate_axis_taxonomy.json`
- `fivecircles/architecture/specs/predicate/groups.md` (query-layer include/exclude 규칙 참조)

### 출력
- 런타임 참조용 taxonomy(현행 유지)
- 검토/리뷰용 generated json(옵션)

### 검증 규칙
1. `kind=RUNTIME` leaf의 code는 `PredicateCode`에 존재해야 한다.
2. `kind=SUGGESTION` leaf의 code는 `PredicateSuggestionCode`에 존재해야 한다.
3. alias 정규화: `STATUS_CHANGE -> TRANSFORMS`.
4. suggestion 토큰 파싱: `TOKEN|label`, `TOKEN:label` 규칙 강제.
5. suggestion 저장 가드: `predicate_code=OTHER`일 때만 저장한다.
6. suggestion 매칭 가드: `predicate_code=OTHER` 이벤트에서만 fallback 매칭에 사용한다.
7. strict-first(템플릿 정답 탐색 경로 한정): strict(runtime PredicateCode) hit가 있으면 suggestion fallback을 실행하지 않는다.
8. fallback 입력 소스 고정: group fallback 매칭은 `event.predicate_suggestion`의 token(`extractToken`)만 사용한다.

### Deterministic 집계/정렬 규칙 (MUST)
- 다중 소속 leaf는 허용하되, query-layer 집계는 mode별 고정 버킷만 사용한다.
- mode score 수식은 서버 구현과 동일하게 고정한다.
  - `ADVERSARY = 8*ADVERSARY + 5*BATTLE + 2*DEATH_EXIT`
  - `ALLY = 8*ALLY + 5*AFFILIATION_CHANGE`
  - `COEVENTS = COEVENTS`
- aggregate 정렬 tie-breaker:
  - 1차: `score DESC`
  - 2차: `otherCharacterId ASC`
- evidenceEventIds 정렬/제한:
  - 정렬: `episode_end DESC`, `event_id DESC`
  - 제한: 캐릭터당 최대 `MAX_EVIDENCE_PER_OTHER`
- 주의: 본 절은 aggregate/집계 경로 규칙이며, strict-first 템플릿 정답 탐색 규칙과 구분한다.

### 실행 커맨드(초안)
```bash
python3 scripts/ops/rdf/predicate_group_compile.py \
  --ttl scripts/ops/rdf/taxonomy/predicate_inheritance.ttl \
  --taxonomy scripts/ops/rdf/taxonomy/predicate_axis_taxonomy.json \
  --out scripts/ops/rdf/taxonomy/predicate_group.generated.json
```

## 6) 지금 당장 해야 할 것(우선순위)

### 우선순위 1: B안 성립 최소 작업
- [ ] RDB: `PredicateCode` 정합성 고정(문서/템플릿/데이터 enum 밖 코드 금지)
- [ ] RDF: 상속 트리 초안 작성(운영 groupKey 기준)
- [ ] RDF: 전개 스크립트로 `predicate_group.generated.json` 생성
- [ ] 공통: RDF query-only 참조를 axis taxonomy 단일 SoT로 고정하고, executor는 `StrictQuerySpec` 단일 SoT를 유지, generated는 리뷰/검증용으로만 사용

### 우선순위 2: 확장 질문(#1~#6) 데이터-대답 최소 작업
- [ ] RDB: `event_reveal` attribute형 입력 가능 여부 점검/보강
- [ ] RDB: Answer-first(10+6)용 PRECEDES 링크 최소 입력
- [ ] RDF(옵션): export에 `event_reveal` 포함

### 우선순위 3: SPO 정밀화
- [ ] role write-path(DTO/mapper)로 SUBJECT/OBJECT 입력 가능화
- [ ] backfill/편집 UI로 중요 이벤트 role 보강

## 7) 보류 항목 (사용자 결정 반영)
- 보류-1: runtime leaf 1:1 강제 범위
- 보류-2: `strictFilters`에 group 계열 키 추가 여부 (`predicateGroupAnyOf` 등)

## 8) 다음 구체 산출물 옵션
1. RDF 상속 트리(6그룹) 초안 작성
- 운영 enum/SoT를 기준으로 leaf를 실제 코드명으로 배치.
2. `predicate_group.generated.json` 스키마/예시 고정
- 구조를 먼저 고정하고, leaf는 점진적으로 채움.

## 9) 수용 기준 (Acceptance)
- ex23 본문에 RDB/RDF 작업이 분리 명시된다.
- alias가 `STATUS_CHANGE -> TRANSFORMS`로 고정된다.
- SoT 경로/namespace가 현재 운영 기준과 일치한다.
- 레인별 SoT(RDF lane / Executor lane)와 axis/group 경계가 명시된다.
- suggestion 가드(`OTHER` 저장/매칭, strict miss 후 fallback)가 명시된다.
- 우선순위 체크리스트로 바로 실행 가능하다.

## 10) 구현 상태 표기 (2026-02-26 기준)
- `scripts/ops/rdf/predicate_axis_taxonomy.py`: implemented (운영 로더/분류기)
- `scripts/ops/rdf/taxonomy/predicate_axis_taxonomy.json`: implemented (RDF lane SoT)
- `scripts/ops/rdf/taxonomy/predicate_inheritance.example.ttl`: implemented (예시)
- `scripts/ops/rdf/taxonomy/predicate_group.generated.example.json`: implemented (예시)
- `scripts/ops/rdf/predicate_group_compile.py`: planned
- `scripts/ops/rdf/taxonomy/predicate_inheritance.ttl`: planned
- `scripts/ops/rdf/taxonomy/predicate_group.generated.json`: planned

## 11) 참조
- `common/src/main/java/com/nospoiler/common/PredicateCode.java`
- `common/src/main/java/com/nospoiler/common/PredicateSuggestionCode.java`
- `scripts/ops/rdf/taxonomy/predicate_axis_taxonomy.json`
- `scripts/ops/rdf/taxonomy/predicate_inheritance.example.ttl`
- `scripts/ops/rdf/taxonomy/predicate_group.generated.example.json`
- `scripts/ops/rdf/predicate_axis_taxonomy.py`
- `fivecircles/architecture/specs/rdf/artifacts/v3-advanced/latest/ontology.ttl`
- `front/common/productionQ/types.ts`
- `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex23-RDF-inheritance-appendix.md`
- `fivecircles/architecture/specs/reveals/reveal-evidence-label-policy.md`
- `fivecircles/architecture/specs/reveals/reveals-classification.md`
- `fivecircles/architecture/specs/reveals/reveals-routing-mvp-and-v3.md`

## 12) Recursive TODO (Execution)
- [x] T0. 범위 고정 및 기준선 동결
- [x] T0-1. ex23 본문 문구를 이번 합의 기준(SoT/경계/strict scope)으로 고정
- [x] T0-2. 변경 기준선을 `review-ex23-rdf-inheritance-2026-02-26.md` Re-Review와 동기화
- [ ] T1. RDF lane SoT 단일화 적용
- [x] T1-1. `predicate_axis_taxonomy.json`을 RDF lane SoT로 선언/참조 경로 고정
- [x] T1-2. query-only 스크립트에서 taxonomy loader 참조 경로 점검
- [x] T1-3. aggregate(SQL mapper) 경로는 Phase1 유지 범위로 명시
- [ ] T1-3-1. Phase2 연동 후보 지점(aggregate mapper/score rule) 식별
- [x] T1-4. Executor lane SoT(`StrictQuerySpec`) 직접 참조 경로 점검(taxonomy 직접 참조 금지)
- [x] T2. Axis vs Group 경계 운영화
- [x] T2-1. axis(분류/신호)와 group(필터/집계) 역할 문구를 문서/예시에 동일 반영
- [x] T2-2. group 예시를 현재 운영 groupKey 기준으로 통일
- [x] T2-3. 멤버셋 비동일 허용 근거를 appendix 예시와 연결
- [x] T3. Suggestion 가드 정합성 잠금
- [x] T3-1. 저장 가드: `OTHER`일 때만 `predicate_suggestion` 저장 (BE 규칙 확인)
- [x] T3-2. 매칭 가드: `OTHER` 이벤트에서만 fallback 매칭 (SQL/Query 규칙 확인)
- [x] T3-3. strict-first scope를 템플릿 정답 탐색 경로로 한정
- [ ] T4. Deterministic 집계/증거 규칙 잠금
- [x] T4-1. mode별 score 수식 문서와 서버 구현 일치 확인
- [x] T4-2. tie-breaker(`score DESC`, `otherCharacterId ASC`) 일치 확인
- [x] T4-3. evidence 정렬/cap(`episode_end DESC`, `event_id DESC`, cap) 일치 확인
- [ ] T4-4. 다중 소속 leaf 중복 카운트 리스크 점검 및 토큰셋 배타 유지
- [x] T5. Compile 파이프라인 단계화
- [x] T5-1. planned 아티팩트(`predicate_group_compile.py`, 정식 ttl/json) 구현 전제/출력 스키마 고정
- [x] T5-2. drift check 규칙(TTL 변경 대비 generated diff) 정의
- [x] T5-3. implemented/planned 상태표 최신화
- [ ] T6. 검증 및 승인
- [x] T6-1. ex23 자체 리뷰(문서-코드 정합성) 1회 수행
- [ ] T6-2. debate/review 로그 동기화
- [ ] T6-3. Phase1 승인 조건 충족 여부 체크(SoT, 경계, 가드, deterministic)

## 13) 상태 동기화 (2026-02-27)
- 기준 체크리스트: `fivecircles/architecture/todolist.md` 9) BP0~BP8
- 리뷰 문서: `fivecircles/work/review/review-blueprint-bp3-bp8-2026-02-27.md`
- 완료(보류 제외 범위):
  - BP3-4, BP4, BP5, BP6, BP7, BP8-1/2/4/5
- 보류(팀 합의 후 재개):
  - BP3-2(wiki), BP3-3/3-a/3-b(intelligence), BP3-5(wiki 포함 E2E), BP8-3(CI 연결)

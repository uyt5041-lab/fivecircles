# [Review] ex23 RDF Inheritance Plan + Example Artifacts
> Reviewer: codex-ops | Date: 2026-02-26

## Scope
- Proposal: `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex23-RDF-inheritance.md`
- Appendix: `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex23-RDF-inheritance-appendix.md`
- Example artifacts:
  - `scripts/ops/rdf/taxonomy/predicate_group.generated.example.json`
  - `scripts/ops/rdf/taxonomy/predicate_inheritance.example.ttl`
- Baseline SoT:
  - `scripts/ops/rdf/taxonomy/predicate_axis_taxonomy.json`
  - `fivecircles/architecture/specs/predicate/groups.md`
  - `common/src/main/java/com/nospoiler/common/PredicateCode.java`
  - `common/src/main/java/com/nospoiler/common/PredicateSuggestionCode.java`

## Findings (ordered)
1. [P1] SoT 기준이 문서 내에서 단일화되지 않아 drift 위험이 남아있음.
   - 근거: ex23 본문이 `generated 결과(또는 현행 taxonomy SoT)`를 병기하여 런타임 기준이 2개로 읽힘.
   - refs:
     - `ex23-RDF-inheritance.md:64`
     - `ex23-RDF-inheritance.md:116`

2. [P1] 그룹 의미 기준이 `axis SoT`와 `groups.md` 사이에서 충돌 가능.
   - 근거:
     - axis SoT: `ADVERSARY`에 `DIES, LEAVES`, `ALLY`에 `JOINS` 포함.
     - example group: `ADVERSARY`는 `CAPTURES, BETRAYS`만, `ALLY`는 `ALLIES_WITH`만.
   - 현 상태는 의도된 분리일 수 있으나, ex23 본문에 “axis(서사분류) vs group(질문레이어)”의 우선순위 규칙이 명시적으로 고정되어 있지 않음.
   - refs:
     - `scripts/ops/rdf/taxonomy/predicate_axis_taxonomy.json:13`
     - `scripts/ops/rdf/taxonomy/predicate_axis_taxonomy.json:36`
     - `scripts/ops/rdf/taxonomy/predicate_group.generated.example.json:37`
     - `scripts/ops/rdf/taxonomy/predicate_group.generated.example.json:55`
     - `fivecircles/architecture/specs/predicate/groups.md:23`
     - `fivecircles/architecture/specs/predicate/groups.md:24`

3. [P2] 실행 커맨드/산출물 경로는 정의됐지만 실제 파일 존재성이 아직 계획 단계임이 문서에서 충분히 구분되지 않음.
   - 근거:
     - 문서의 compile 스크립트/정식 산출물 경로가 아직 미생성 상태.
   - refs:
     - `ex23-RDF-inheritance.md:79`
     - `ex23-RDF-inheritance.md:80`
     - `ex23-RDF-inheritance.md:104`
     - `scripts/ops/rdf/predicate_group_compile.py` (missing)
     - `scripts/ops/rdf/taxonomy/predicate_inheritance.ttl` (missing)
     - `scripts/ops/rdf/taxonomy/predicate_group.generated.json` (missing)

4. [P2] 다중 소속 leaf(`LEAVES`)에 대한 런타임 집계 dedupe 규칙이 본문에는 약함.
   - 근거:
     - TTL 예시에 `LEAVES`가 `AFFILIATION_CHANGE`, `DEATH_EXIT` 양쪽에 속함.
     - Appendix에는 dedupe 언급이 있으나 본문의 실행 규칙/수용기준에 deterministic 규칙이 없음.
   - refs:
     - `predicate_inheritance.example.ttl:21`
     - `ex23-RDF-inheritance-appendix.md:75`

## Decision
- [Status]: Changes Requested

## Next Actions
1. ex23 본문에 SoT 단일 문구 고정:
   - runtime 참조 1순위(예: generated JSON)와 보조 SoT(예: axis taxonomy)의 역할을 분리 선언.
2. axis vs group 역할을 명문화:
   - axis는 narrative/score 분류,
   - group은 Q-template/query fallback 분류.
3. “planned vs implemented” 상태 표 추가:
   - `predicate_group_compile.py`, `predicate_inheritance.ttl`, `predicate_group.generated.json`.
4. 본문 실행 규칙에 dedupe/tie-breaker 추가:
   - 같은 event가 다중 그룹에 속할 때 mode별 우선순위 1개만 카운트.

---

## Re-Review (criteria update)
> Reviewer: codex-ops | Date: 2026-02-26 (2nd pass)

### Resolved
1. SoT 단일화/경계 문구가 본문에 추가됨.
2. axis vs group 역할 분리가 본문/부록에 반영됨.
3. planned vs implemented 상태 표기가 본문에 추가됨.
4. deterministic score/tie-breaker/evidence cap 규칙이 본문에 추가됨.
5. suggestion guard(`OTHER` 저장/매칭, strict miss fallback)가 본문/부록에 반영됨.

### Remaining findings
1. [P1] Runtime SoT 선언과 현재 서버 구현 범위가 1:1로 맞지 않는 표현이 남아있음.
   - 본문은 "Runtime query/executor는 axis taxonomy만 참조"로 읽히지만, event-service aggregate는 SQL 매퍼 하드코딩 그룹셋을 사용함.
   - refs:
     - `ex23-RDF-inheritance.md:97`
     - `services/event-service/src/main/resources/mapper/event/EventCharacterMapper.xml:147`
     - `services/event-service/src/main/resources/mapper/event/EventCharacterMapper.xml:154`
     - `services/event-service/src/main/resources/mapper/event/EventCharacterMapper.xml:170`
     - `services/event-service/src/main/resources/mapper/event/EventCharacterMapper.xml:215`

2. [P2] RDF-0의 그룹 예시(`SUSPICION/CONCEALMENT/...`)가 현재 query-layer 그룹(`AFFILIATION_CHANGE/DEATH_EXIT/BATTLE/ADVERSARY/ALLY`)과 달라 실행 문서 관점에서 혼동 여지가 있음.
   - ref: `ex23-RDF-inheritance.md:59`

3. [P2] strict-first 문구의 적용 범위가 넓게 읽힐 수 있음.
   - aggregate 집계는 "strict 검색 → fallback 검색" 단계형이 아니라 mode별 합성 카운트 모델이므로, 해당 문구는 "템플릿 정답 탐색 경로"로 스코프를 제한하는 편이 안전함.
   - refs:
     - `ex23-RDF-inheritance.md:118`
     - `services/event-service/src/main/resources/mapper/event/EventCharacterMapper.xml:146`

### Re-Review Decision
- [Status]: Changes Requested (minor wording alignment)

---

## Re-Review (post-fix)
> Reviewer: codex-ops | Date: 2026-02-26 (3rd pass)

### Final check
1. Runtime SoT 범위가 `RDF query-only` 경로로 한정되어 구현과 충돌하지 않음.
2. RDF-0 그룹 예시가 현재 query-layer 그룹키와 정렬됨.
3. strict-first 문구가 템플릿 정답 탐색 스코프로 제한됨.
4. recursive TODO가 실행 순서/하위 체크 단위로 추가되어 즉시 운영 가능.

### Decision
- [Status]: Approved (document criteria aligned)

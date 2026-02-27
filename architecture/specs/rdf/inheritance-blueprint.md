# Inheritance Blueprint (Codebook-First, Phase1-Compatible)

기준일: 2026-02-27

## 0) 목적
- 질문/답변(특히 expansion WHY 질문)에서 "상속 확장"을 쓰되, 현재 운영 계약을 깨지 않고 적용한다.
- 현재 운영처럼 `PredicateCode + StrictQuerySpec` 중심 정답 탐색을 유지한다.
- reveal 확장은 "근거/보조 필터" 품질 개선에 집중한다.

## 1) 고정 원칙 (MUST)
- 레인 경계:
  - RDF lane SoT: `scripts/ops/rdf/taxonomy/predicate_axis_taxonomy.json`
  - Executor lane SoT: `StrictQuerySpec` (questions anti-halu 템플릿/매트릭스)
- strict-first:
  - strict miss이면 reveal/probe hit가 있어도 `ANSWERED` 승격 금지
- reveal 역할:
  - `event_reveal.reveal_type(HINT|CONFIRM)`는 WHY 근거 강도 표시에만 사용
  - 정답 선택(strict)에는 사용하지 않음

참조:
- `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex23-RDF-inheritance.md`
- `fivecircles/architecture/specs/reveals/reveal-evidence-label-policy.md`

## 2) 운영 모델 (지금 기준)

### 2.1 Predicate 축
- Runtime codebook: `common/src/main/java/com/nospoiler/common/PredicateCode.java`
- Group codebook: `fivecircles/architecture/specs/predicate/groups.md`
- Suggestion codebook: `common/src/main/java/com/nospoiler/common/PredicateSuggestionCode.java`

### 2.2 Reveal 축
- 스키마 기본: `event_reveal(event_id, target_type, target_id, reveal_type)`
- 운영 의미:
  - `target_type=CHARACTER` -> `target_id=character_id`
  - `target_type=ATTRIBUTE` -> `target_id=aboutCharacterId` (현행)
- `reveal_type`: `HINT|CONFIRM`만 허용

주의:
- 현행은 ATTRIBUTE 의미를 `target_id`만으로 구분하기 어렵다.
- 따라서 Phase1 확장은 `target_key` 코드북 방식을 사용한다.

## 3) Phase1 확장안 (테이블 추가 최소)

### 3.1 추가 컬럼 (최소 1개)
- `event_reveal.target_key VARCHAR(64) NULL`
  - 예: `A_MORAL_FRAME_SHIFT`, `A_EXTERNAL_PRESSURE`
  - `target_type=ATTRIBUTE`일 때만 사용

### 3.2 코드북 운영
- reveal target key는 코드북(문서 + 코드 상수)로 관리한다.
- 운영 데이터 반영(초기)은 API write 경로보다 `scripts/ops` seed/backfill 스크립트를 우선 사용한다.
- 권장 SoT:
  - 문서: `fivecircles/architecture/specs/reveals/` 하위 코드북 문서
  - 실행 맵: `front/common/productionQ/inheritancePhase1.ts` 또는 동등 JSON
- 네이밍: `A_*` UPPER_SNAKE

### 3.3 상속(확장) 방식
- DB closure 테이블 없이 코드북 확장 맵으로 시작한다.
- 흐름:
  1) 질문이 상위 key 요구 (`A_MORAL_FRAME_SHIFT`)
  2) 코드북에서 descendants 확장
  3) B-lane 쿼리: `target_key IN expanded_keys`
  4) 필요 시 about 캐릭터 필터: `target_id = aboutCharacterId`

## 4) 질문 실행 흐름 (Q01_EXP_01 기준)

1. strict 정답 탐색:
   - `event.predicate_code`, `qAnyOf`, `source_status='APPROVED'`, `episode_end <= K`
2. B-lane 후보:
   - `event_reveal.target_type='ATTRIBUTE'`
   - `event_reveal.target_key IN expanded(A_MORAL_FRAME_SHIFT)`
   - (옵션) `event_reveal.target_id = WalterId`
3. 상태 판정:
   - strict hit면 `ANSWERED`
   - strict miss면 probe 결과로 `NOT_ENOUGH_DATA | SPOILER_BLOCKED`
4. WHY 출력:
   - `answer_event` + `reveal_hint`
   - `because_chain`은 PRECEDES 기반으로 단계적 확장

## 5) API/DTO 규칙
- 하위 호환 유지:
  - 기존 단일 필드(`revealTargetType/revealTargetId/revealType`) 유지
- 운영 원칙:
  - `target_key` 데이터 주입/보정은 Phase1에서 `scripts/ops/seed_*.sql`, `scripts/ops/run_*` 스크립트로 수행
- 확장:
  - `reveals[]` 배열 추가 권장 (event당 다건 reveal 표현)
- 정렬:
  - `CHARACTER` 우선/`ATTRIBUTE` 후순위 고정 또는 명시 규칙 문서화

## 6) 데이터 품질 게이트
- `target_type=ATTRIBUTE`인데 `target_key` 비어 있으면 Phase1 정책 적용:
  - drama10(Q1 expansion) 범위: 차단(검증 fail)
  - 그 외 legacy 범위: 경고 + 백로그 보류
- `target_key`가 코드북 allow-list 밖이면 reject
- `source_status='APPROVED'` 게이트를 모든 질문 실행에 유지
- CI:
  - 템플릿/질문맵의 `A_*` key가 코드북에 없으면 fail

## 7) 단계별 로드맵

### Phase1 (지금)
- `target_key` 추가
- 코드북 상속 맵 확정 (`A_*`, `P_*`)
- Q01 expansion 6개 기준 B/C/BC 실행 안정화

### Phase2 (필요 시)
- `reveals[]` 응답 정식화
- `because_chain` 자동 생성(PRECEDES 2~3 hop)

### Phase3 (규모 커질 때만)
- `attribute`/`attribute_closure` 테이블 승격 검토
- 승격 전제: key 폭발, 운영자 편집/검색 요구, 코드북 유지비 증가

## 8) 비범위 (이번 문서에서 안 하는 것)
- `event_predicate`, `question_requirement` 같은 신규 코어 테이블 즉시 도입
- 런타임 reasoner/SPARQL 상속 전개
- strict 계약 키 추가(`predicateGroupAnyOf` 등)

## 9) 결정 요약
- 지금은 `PredicateCode` 운영 방식과 동일하게 간다.
- reveal도 "코드북 + 최소 컬럼(target_key)"로 확장한다.
- 테이블 증설형 taxonomy는 Phase3 후보로만 둔다.

## 10) 실행 상태 동기화 (2026-02-27)
- 기준 체크리스트: `fivecircles/architecture/todolist.md` (9. Blueprint 섹션)
- 리뷰 근거: `fivecircles/work/review/review-blueprint-bp3-bp8-2026-02-27.md`
- 완료(보류 제외 범위):
  - BP3-4, BP4, BP5, BP6, BP7, BP8-1/2/4/5
- 보류(팀 합의 후 재개):
  - BP3-2(wiki), BP3-3/3-a/3-b(intelligence), BP3-5(wiki 포함 E2E), BP8-3(CI 연결)

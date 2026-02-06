# ex14 정합성 체크리스트 (Definition and Verification Only)

목적
- `ex14-reveal-implementation.md`를 "표준"으로 삼아, 코드/DB/프론트/문서의 정합성을 맞춘다.
- PRECEDES 및 Q1~Q15(질문 위젯/필터/집계)의 정렬 작업을 위한 기반(용어/코드북)을 고정한다.

범위
- Predicate 표준명: `STATUS_CHANGE` → `TRANSFORMS`로 표준을 고정한다.
- Reveal 메타데이터: `event_reveal(target_type, target_id, reveal_type)` 구조와 명세의 정합성을 점검한다.
- "정합성 갭"은 구현하지 않고, 존재 여부만 확인 후 문서/투두에 명시한다.

비범위(금지)
- 캐릭터 해금/타임라인 병합(Identity Reveal 후처리)은 중복 작업이므로 여기서 구현하지 않는다.

관련 문서
- 표준 기준: `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex14-reveal-implementation.md`
- 표준 predicate 설계: `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex13-standard-predicates.md`
- 현재 enum: `common/src/main/java/com/nospoiler/common/PredicateCode.java`
- event_reveal 마이그레이션: `services/event-service/src/main/resources/db/migration/V2__fix_event_reveal_schema.sql`

---

## 0) ex14 기준 정합성 변경 목록(확정)

PredicateCode(표준명/호환성)
- 표준명은 `TRANSFORMS`로 고정한다.
- 기존 `STATUS_CHANGE`는 레거시 호환용으로만 유지하고, 이행 기간 종료 후 제거 후보로 둔다.
- 저장(write)은 `TRANSFORMS`로 표준화한다.
- 조회(read/filter)는 `TRANSFORMS` 요청 시 `STATUS_CHANGE`도 함께 매칭되도록 확장한다(깨짐 방지).

Reveal 메타데이터(event_reveal)
- DB 스키마는 `event_reveal(event_id, target_type, target_id, reveal_type)`를 표준으로 한다.
- wiki/intelligence -> event 파이프라인에서 reveal 메타가 실제 전달/저장되는지는 "정합성 갭 체크"로만 남긴다(구현 금지).

문서/프론트 표기
- 문서/스펙/프론트 집계에서 `STATUS_CHANGE` 표기는 `TRANSFORMS`로 정렬한다.
- 단, Q1~Q15 위젯/필터에서 enum 외 코드(`AFFILIATION_CHANGE`, `DEATH`, `EXIT`, `BATTLE` 등)는 ex14 정합성과 분리한다(별도 티켓).

## 1) 현재 상태(요약)

확인된 정합
- DB 스키마: `event_reveal`은 `target_type`, `target_id`를 사용한다.

정합성 불일치
- 코드 enum: `TRANSFORMS`가 없고 `STATUS_CHANGE`만 존재한다.
- 프론트/문서/스펙: `STATUS_CHANGE` 표기가 남아 있다.

정합성 갭(확인 필요, 구현 금지)
- wiki/intelligence → event 파이프라인에서 `event_reveal` 메타가 실제로 전달/저장되는지 불명확하다.

---

## 1.1) 파일/문서별 불일치(현황)

ex14(표준) 대비, 현재 코드/문서에서 확인된 불일치 목록이다.

PredicateCode 명칭 불일치(STATUS_CHANGE vs TRANSFORMS)
- 코드: `common/src/main/java/com/nospoiler/common/PredicateCode.java`
- 프론트 집계: `front/common/widgets/Q20_NarrativeDistribution.tsx` (STATUS_CHANGE로 키 사용)
- 인텔리전스 스펙/계약: `fivecircles/architecture/specs/intelligence/intelligence-db-schema.md`, `fivecircles/architecture/specs/intelligence/intelligence-events-contract.md` (STATUS_CHANGE 포함)
- 운영/예시 문서: `fivecircles/work/update.md` (predicateCode=STATUS_CHANGE 예시)
- 참고: 표준 predicate 문서(ex13/ex12)에는 TRANSFORMS가 이미 존재한다.

질문/필터에서 enum과 다른 코드 혼재(BATTLE/DEATH/EXIT/AFFILIATION_CHANGE 등)
- 스펙: `fivecircles/architecture/specs/v2.5-unify.md`, `fivecircles/architecture/specs/frontend.md`
- 프론트: `front/features/timeline/EventTimelinePage.tsx`
- 참고: 이 항목은 "ex14 정합성(TRANSFORMS/REVEALS)"과는 별개로, Q1~Q15 구현 정렬을 위해 별도 티켓으로 정리한다.

UNKNOWN vs OTHER 기본값/표기 혼재
- 공통 enum은 `OTHER`를 기본 탈출구로 사용한다(`common/PredicateCode.java`).
- event-service는 이벤트 생성 시 predicate 미지정이면 문자열 "UNKNOWN"을 저장한다(`services/event-service/.../EventServiceImpl.java`).
- 문서/마이그레이션도 `UNKNOWN` 기본값을 언급한다(`fivecircles/architecture/specs/v2.5-unify.md` 등).
- 참고: ex14 자체는 UNKNOWN/OTHER에 대해 명시가 없으므로, 이 항목은 "추가 정합성 작업"으로 분리한다.

인텔리전스 eventType(REVEAL_HINT/REVEAL_CONFIRM/RELATION_CHANGE) vs 저장 predicate
- `fivecircles/architecture/specs/intelligence/intelligence-events-contract.md`는 labelDraft.eventType을 event.predicate_code로 저장한다고 되어 있다.
- 반면 공통 enum에는 REVEAL_HINT/REVEAL_CONFIRM/RELATION_CHANGE가 없다.
- 결론: "내부 라벨"과 "저장 predicate" 레이어 구분이 필요하며, 우선은 문서 정합성으로만 처리한다.

ex04(event_triplestore) 문서의 event_reveal 컬럼 드리프트
- `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex04-triplestore.md`는 `event_reveal(..., note)`를 예시로 든다.
- 현재 DB 스키마(`V2__fix_event_reveal_schema.sql`)에는 `note` 컬럼이 없다.
- 결론: ex04는 ex14 기준으로 보정 또는 "구문 예시(의사코드)"로 재표기 필요.

ex14 주장(Refine JSON에 revealTargetId/type 포함) vs 실제 DTO/코드
- ex14는 refine 응답(JSON)에 `revealTargetId`, `revealTargetType`이 포함된다고 주장한다.
- 현재 `services/intelligence-service/.../dto/RefineResponse.java`에는 reveal 타겟 필드가 없다.
- event-service에도 `EventRevealMapper`/스키마는 있으나, 저장 호출 경로는 검색상 확인되지 않았다.
- 결론: "정합성 갭"으로만 명시하고, 이 문서에서는 구현하지 않는다.

---

## 2) 실행 순서(체크리스트)

### A. 표준 확정(문장)
- [ ] 표준 predicate 명칭은 `TRANSFORMS`로 고정한다.
- [ ] `STATUS_CHANGE`는 이행 기간 동안만 레거시 호환 코드로 취급한다.

### B. 코드 정합(공통 enum)
- [ ] `common/src/main/java/com/nospoiler/common/PredicateCode.java`에 `TRANSFORMS` 추가한다.
- [ ] `STATUS_CHANGE`는 삭제하지 않고 `@Deprecated`로 표시한다.
- [ ] 설명(description) 문구를 `TRANSFORMS` 기준으로 맞춘다.

### C. 저장/조회 정규화(깨짐 방지용)
원칙
- 새로 저장(write)되는 값은 `TRANSFORMS`를 표준으로 한다.
- 조회/필터(read)에서는 이행 기간 동안 `TRANSFORMS` 요청 시 `STATUS_CHANGE`도 함께 매칭한다.

체크
- [ ] 이벤트 생성/정제 파이프라인에서 상태변화 코드는 `TRANSFORMS`로 저장되는지 확인한다.
- [ ] event 조회/필터 파라미터가 `TRANSFORMS`일 때, 과거 데이터(`STATUS_CHANGE`)도 검색되는지 확인한다.

### D. 프론트 집계/표시(Q20 등)
- [ ] 집계에서 `STATUS_CHANGE`를 `TRANSFORMS`로 합산 표시(이행 기간)한다.
- [ ] UI 상의 라벨/필터 값이 enum과 불일치(BATTLE, DEATH, EXIT, AFFILIATION_CHANGE 등)하는 부분은 별도 티켓으로 분리한다.

### E. 문서 정합
- [ ] 문서/스펙에서 `STATUS_CHANGE` 표기를 `TRANSFORMS`로 교체한다.
- [ ] intelligence 문서에서 `REVEAL_HINT/REVEAL_CONFIRM/RELATION_CHANGE`가 "저장 predicate"인지 "내부 라벨"인지 구분 문장을 추가한다.

### F. 정합성 갭 체크(event_reveal 파이프라인)
목표
- 구현은 하지 않는다. 존재 여부만 확인하고, 결과를 문서와 TODO에 남긴다.

체크
- [ ] wiki-service에서 event publish 시 `event_reveal`을 전달/저장하는 로직이 있는지 확인한다.
- [ ] intelligence-service 출력에 reveal 대상(`target_type/target_id`)을 포함하는 계약/DTO가 있는지 확인한다.
- [ ] 결과를 아래 중 하나로 결론낸다.
  - "파이프라인 존재: 파일/클래스 링크"
  - "파이프라인 없음: 정합성 갭(미구현)"

### G. DB 데이터 마이그레이션(서버)
전제
- B~E가 적용된 후에 실행한다(호환 레이어가 준비된 상태에서 안전하게 진행).

체크
- [ ] `nospoiler_event.event.predicate_code='STATUS_CHANGE'`를 `TRANSFORMS`로 일괄 변경한다.
- [ ] `nospoiler_wiki.wiki_submission.predicate_code='STATUS_CHANGE'`를 `TRANSFORMS`로 일괄 변경한다.

---

## 3) 작업 산출물(공유용)

- 비교표: ex14 주장 vs 실제 코드/DB 차이 목록
- 체크리스트: 이 문서
- TODO: `fivecircles/architecture/todolist.md`의 "정합성 갭 체크 (ex14, 협업)" 항목

---

## 4) 변경 계획(코드/DB/프론트/문서)

코드(common)
- `PredicateCode`에 `TRANSFORMS` 추가, `STATUS_CHANGE`는 `@Deprecated`로 유지.

코드(서비스 write 정규화)
- wiki-service: 수동 predicate 입력(String -> Enum) 시 `STATUS_CHANGE`가 들어오면 `TRANSFORMS`로 정규화하는 레이어 추가(이행 기간).
- intelligence-service: refine 결과가 `STATUS_CHANGE`로 들어오는 경우(향후) `TRANSFORMS`로 정규화.
- event-service: EventRequestDTO.predicateCode가 `STATUS_CHANGE`면 저장 문자열을 `TRANSFORMS`로 바꾸고, `TRANSFORMS`가 표준으로 저장되게 고정.

코드(서비스 read 호환)
- event-service: predicateCode 필터가 `TRANSFORMS`면 SQL/mapper에서 `TRANSFORMS` + `STATUS_CHANGE`를 함께 매칭.

프론트
- Q20 분포 집계/라벨: `STATUS_CHANGE` 키를 `TRANSFORMS`로 변경하고, 이행 기간엔 `STATUS_CHANGE` 데이터를 `TRANSFORMS`에 합산.

DB(서버 백필)
- `event.predicate_code='STATUS_CHANGE'`를 `TRANSFORMS`로 UPDATE.
- `wiki_submission.predicate_code='STATUS_CHANGE'`를 `TRANSFORMS`로 UPDATE.
- 백필은 코드 호환 레이어 반영 후 실행(운영 중 깨짐 방지).

문서
- intelligence 문서: `labelDraft.eventType`가 "저장 predicate"인지 "내부 라벨"인지 명확히 분리 표기(현재 문구는 ex14/enum과 충돌).
- v3-details, update.md 등 `STATUS_CHANGE` 언급을 `TRANSFORMS`로 교체.
- ex04-triplestore의 event_reveal 예시(note 컬럼) 보정(또는 의사코드임을 명시).

---

## 5) 우선순위(권장)

P0 (즉시, 위험 낮음)
- 공통 enum에 `TRANSFORMS` 추가 + 레거시 호환(Deprecated) 정책 문장 고정.
- 문서(STATUS_CHANGE -> TRANSFORMS) 치환.
- 프론트(Q20) 집계 키 정렬.

P1 (호환 레이어 적용 후)
- 서비스 write 정규화 + read 확장(IN 조건) 적용.
- 서버 DB 백필 실행.

P2 (갭 체크, 구현 금지)
- event_reveal 파이프라인 존재 여부 확인 결과를 문서/TODO에 반영.

# REVEALS Classification (Draft, Integration-Friendly)

목적
- `PredicateCode.REVEALS`를 "설명용"으로만 두지 않고, 질문/검색/검수에서 재사용 가능한 분류 체계를 만든다.
- 다만 팀원이 진행 중인 작업(캐릭터 해금/타임라인 병합, reveal target 파이프라인)은 중복 구현하지 않고, 통합 포인트로만 남긴다.

범위
- 분류 기준(타입/레벨) 정의
- 저장/조회 레이어에서 필요한 최소 메타데이터 정의
- “지금 가능한 것(메타 없음)”과 “통합되면 가능한 것(메타 있음)”을 분리

비범위(금지)
- Identity Reveal 후처리(캐릭터 해금/타임라인 병합) 구현
- intelligence-service refine 응답에 revealTarget을 추가하는 구현
- wiki/intelligence -> event 파이프라인에서 `event_reveal` 저장을 새로 구현

관련 문서
- 표준 기준(ex14): `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex14-reveal-implementation.md`
- 지속 기준서: `fivecircles/architecture/specs/reveals/reveal-evidence-label-policy.md`
- REVEALS(관계로 취급하는 초기 논의): `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex11-reveals.md`
- REVEALS type 제안(설명력 강화): `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex11.2-reveals2.md`
- semantic inheritance draft: `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/specs/reveals/reveal-semantic-inheritance-draft.md`
- 트리플스토어 예시(note 포함): `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex04-triplestore.md`
- predicate 전략: `fivecircles/architecture/specs/predicate/README.md`
- ex14 정합성 갭: `fivecircles/architecture/specs/ex14-consistency-checklist.md`
- 축/확장 스케치(ex20~ex23): `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex20-axis.md`, `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex22.2-expension-categorized-impl-plan.md`, `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex22.3-expension-expension-qs-imple2.md`, `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex23-RDF-inheritance.md`

---

## 0) 정합성 기준(이 문서가 따르는 표준)

이 문서는 `ex14-reveal-implementation.md`와 현재 실제 DB 스키마(`V2__fix_event_reveal_schema.sql`)를 기준으로 정합성을 잡는다.

정리
- 초기 논의(ex11)는 REVEALS를 `event_relation.type=REVEALS`로 다뤘지만, 현재 표준(ex14)은 **REVEALS를 event의 predicate_code**로 둔다.
- `event_relation.type`는 현재 제품 범위에서 `PRECEDES` 단일값 고정(탐색 안정성)으로 유지한다.
- REVEALS는 스포일러 위험도가 높아서, 탐색/BFS 결과 확장에 기본 포함시키지 않고 설명/근거로만 노출한다.

## 1) 왜 분류가 필요한가

문제
- `REVEALS`는 "드러남"의 형태가 다양해서, predicate 하나만으로는 질문(Q4 같은) 정답 찾기 정확도가 떨어진다.

해결 방향
- `REVEALS`는 그대로 유지하되, "무엇이 드러났는지"를 메타로 분류한다.
- 메타가 아직 없다면, 운영/QA에서는 `REVEALS`를 1급 검색 키로 쓰지 않고(설명/근거용), 인지 변화/대면 행동 등 다른 predicate/group로 정답을 찾는다.

---

## 2) 분류 체계(초안)

### 2.1 RevealTargetType
- `CHARACTER`: 정체/동일인/가면 뒤 인물 공개(Identity Reveal)
- `ATTRIBUTE`: 특정 인물의 속성/상태/사실 공개(Fact Reveal)
- `RELATION` (옵션): 관계/혈연/소속/동맹 등의 "관계 사실" 공개(Relation Reveal)
- 판정 기준(핵심):
  - A=B 동일인 판명은 `CHARACTER`
  - 동일인 판명이 아닌 사실 공개는 `ATTRIBUTE`(about 캐릭터 기준)

### 2.2 RevealType
- `HINT`: 암시/단서
- `CONFIRM`: 확정/공식 확인

주의(용어 충돌)
- `ex11.2-reveals2.md`에서는 `reveal_type`을 IDENTITY/RELATIONSHIP/EVIDENCE 같은 "의미 분류"로 쓰는 안을 제안한다.
- 반면 일부 스펙에서는 HINT/CONFIRM을 `reveal_type`으로 쓰는 형태가 등장한다.
- 현재 DB(`event_reveal.reveal_type` 단일 컬럼)는 두 축(강도 vs 의미 분류)을 동시에 담기 어렵다.
- 그래서 본 문서는 일단 "강도(HINT/CONFIRM)"를 `reveal_type`의 의미로 두고, 의미 분류가 필요해지면 컬럼 추가(예: `reveal_semantic_type`)로 분리하는 것을 통합 포인트로 남긴다(구현 보류).
- 즉 현재 모델은 다음 2축으로 본다.
  - 축1: `target_type` (`CHARACTER|ATTRIBUTE`)
  - 축2: `reveal_type` (`HINT|CONFIRM`)

### 2.3 Trigger(질문 레이어의 사용)
- Q4 같은 "알아차린 시점" 질문:
  - (메타 없음) `DISCOVERS/LEARNS` 계열 또는 group으로 정답 이벤트를 찾고, 같은 이벤트/인접 이벤트의 `REVEALS`를 근거로 보여준다.
  - (메타 있음) `REVEALS + target=(범죄 사실/정체)`로 더 직접적으로 정답 탐색이 가능.

---

## 3) 저장/조회에 필요한 최소 메타(통합 포인트)

DB 메타(권장, ex14 기준)
- `event_reveal(event_id, target_type, target_id, reveal_type)`
- 실제 스키마 참고: `services/event-service/src/main/resources/db/migration/V2__fix_event_reveal_schema.sql`

추가로 필요할 수 있는 필드(옵션, 향후)
- `key` (RELATION/ATTRIBUTE의 세부 키: 예. relationType/attributeKey)
- `note` (설명 텍스트)
  - `ex04-triplestore.md`의 예시에는 있으나, 현재 `event_reveal` 스키마에는 없다.
  - 스키마 확장 전에는 문서/요약(refined_summary 등)에만 남긴다.

통합 포인트(협업)
- intelligence refine 응답에 `revealTargetType`, `revealTargetId`, `revealType(HINT/CONFIRM)`를 포함시키면,
  - wiki 승인 -> event 발행 시 `event_reveal`까지 함께 저장 가능해진다.
- 현재 이 파이프라인은 “정합성 갭 체크” 대상이며, 팀원 작업 완료 후 통합한다.

---

## 4) 운영 규칙(메타 없는 기간)

Rule A: REVEALS는 설명/근거 우선
- 메타가 없으면 `REVEALS`를 1급 검색 키로 사용하지 않는다.
- 대신:
  - 정답 이벤트(인지 변화/대면 행동/사건 전환)를 먼저 찾고,
  - 그 이벤트에 `REVEALS`가 붙어 있으면 "근거"로 출력한다.

Rule A.1: revealType 미입력(null) 허용 (현 운영)
- `event_reveal.reveal_type`는 현재 **미입력(null)을 허용**한다.
- 아직 HINT/CONFIRM을 정책/랭킹/리캡에서 사용하지 않는 기간에는, wiki/intelligence에서 revealType을 강제 생성하지 않는다.
- UI 표기 예: `REVEAL(미분류)` (내용 텍스트 없이 배지/메타 영역에만 표시)

Rule B: labelDraft.eventType과 저장 predicate 분리
- `REVEAL_HINT/REVEAL_CONFIRM` 같은 내부 라벨은 저장 predicate가 아니라, 최종 저장은 `PredicateCode.REVEALS`로 정렬한다.
- HINT/CONFIRM은 메타(`event_reveal.reveal_type`)로 내려간다(통합 시).

Rule C: 사실 이벤트와 해석 라벨을 분리한다 (Answer-first)
- 도미노 답변의 "사건 줄(EP/행동 요약)"은 관측 가능한 사실만 `event`로 저장한다.
- 도미노 답변의 "슬래시 뒤 메모(의미/해석)"는 기본적으로 분석 라벨로 취급한다.
- 분석 라벨은 아래 기준으로만 `event_reveal`에 승격한다.
  - `CONFIRM`: 장면/대사/소품으로 직접 확인 가능한 근거가 있는 경우
  - `HINT`: 행동 연쇄로 합리적 추론은 가능하지만 직접 근거가 약한 경우
  - 근거가 없는 해석 라벨은 `event_reveal`에 넣지 않고 문서/ops 메모로만 유지

Rule C.1: reveal 입력 최소 근거
- `event_reveal.reveal_type`를 채울 때는 최소 1개의 근거 앵커(`evidence event`)를 같이 남긴다.
- 현재 DB 스키마에는 근거 note 컬럼이 없으므로, 근거 문장은 `answerset`/질문맵 문서 필드에서 관리한다.
- 권장 필드(문서 레이어): `evidence_event_id`, `evidence_note`

Rule C.2: 질문 실행과의 경계
- 정답 선택(strict-first)은 사실 이벤트(`event`)만으로 수행한다.
- `reveal_type(HINT/CONFIRM)`는 WHY/근거 카드 강도 표시용으로만 사용한다(정답 승격 금지).

---

## 5) 향후(메타 도입 후) 기대 효과

정확도
- Q4/Q11류 질문에서 "무엇이 드러났나"를 기준으로 필터링 가능.

확장성
- RDF/OWL(트리플) 레이어로 확장할 때도,
  - view-layer predicate(`REVEALS`)는 안정적으로 유지하고,
  - target/object를 별도 레이어로 발전시키기 쉽다.

---

## 6) 예시(대표 케이스, 현재 스키마 기준)

전제
- 현재 스키마는 `event_reveal(target_type, target_id, reveal_type)`까지만 저장한다.
- "어떤 속성이 드러났는지(예: alias=Heisenberg)" 같은 세부는 컬럼이 없으므로, 당장은 이벤트 요약/설명 텍스트에만 남긴다.

예시 A: "하이젠버그의 정체는 월터였다"
- 권장 표현:
  - event.predicate_code = `REVEALS`
  - event_reveal.target_type = `CHARACTER`
  - event_reveal.target_id = (Walter characterId)
  - event_reveal.reveal_type = `CONFIRM`
- 비고:
  - "Heisenberg"라는 별칭 문자열을 구조화하려면 향후 `target_key`/`target_text` 같은 확장이 필요하다.

예시 B: "오일남이 사실은 게임 주최자였다"
- 권장 표현:
  - event.predicate_code = `REVEALS`
  - event_reveal.target_type = `CHARACTER`
  - event_reveal.target_id = (Oh Il-nam characterId)
  - event_reveal.reveal_type = `CONFIRM`

예시 C: "A가 B의 소속(조직)을 알고 있었다/드러났다"
- 현재 스키마만으로는 다음 중 택1이 필요하다.
  - (보수) 소속은 `TRANSFORMS`/`JOINS`/`LEAVES` 같은 predicate로 표현하고, REVEALS는 설명/근거로만 둔다.
  - (확장) `ATTRIBUTE` target_type로 내려 보내되, 무엇(affiliation)이 드러났는지 key가 없어 정확도가 떨어진다.

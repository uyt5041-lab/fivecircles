# Reveal Evidence/Label Policy (Persistent Reference)

기준일: 2026-02-26  
범위: ProductionQ/Expension 질문 구현에서 `event`(사실)과 `event_reveal`(근거 라벨) 경계를 고정한다.

연결 문서(20번대)
- `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex20-axis.md`
- `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex22.2-expansion-categorized-impl-plan.md`
- `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex22.3-expansion-expansion-qs-imple2.md`
- `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex23-RDF-inheritance.md`

## 1) 핵심 원칙
- 사건 줄(EP/행동 요약)은 `event`에 저장한다.  
  - 관측 가능한 사실만 허용한다.
- 슬래시 뒤 메모(의미/해석)는 기본적으로 분석 라벨이다.
- 분석 라벨은 근거가 있을 때만 `event_reveal`로 승격한다.

## 2) reveal_type 판정 기준
- `CONFIRM`
  - 장면/대사/소품 등 직접 관측 근거가 있는 경우
- `HINT`
  - 행동 연쇄로 합리적 추론은 가능하지만 직접 근거가 약한 경우
- `OPS_MEMO`(문서/운영 메모)
  - 근거가 없거나 주관 해석인 경우
  - `event_reveal`에 저장하지 않는다

## 2.1) target_type 판정 기준 (동일인 공개 vs 사실 공개)
- `target_type=CHARACTER`:
  - 동일인 판명(A=B) 형태의 정체 공개
  - 예: "프론트맨의 정체가 황인호임이 밝혀짐"
- `target_type=ATTRIBUTE`:
  - 동일인 판명이 아닌 사실/속성 공개(about 캐릭터 기준)
  - 예: "황준호가 프론트맨의 정체를 확인(인지)함"은 인지 사건 기준으로는 `DISCOVERS` 우선, REVEALS를 쓰면 `ATTRIBUTE`로 처리
- 주의: `reveal_type`은 `HINT|CONFIRM` 강도 축이며, `IDENTITY` 같은 의미 축을 대체하지 않는다.

## 3) 저장 규칙
- `event`
  - 사실 이벤트만 저장
- `event_reveal(event_id, target_type, target_id, reveal_type)`
  - 운영 표준은 `HINT|CONFIRM`
  - 전환기(레거시 입력)에는 `null`을 허용하되, 정답 선택/승격 로직에는 사용하지 않는다
  - 입력 시 최소 1개 근거 앵커를 문서 레이어에 남긴다
- 문서 레이어(`answerset`/`question-map`)
  - 권장 필드: `evidence_event_id`, `evidence_note`

## 4) 실행 규칙(질문/답변)
- strict 정답 선택은 `event` 사실 데이터로만 수행한다.
- `reveal_type(HINT|CONFIRM)`는 WHY/근거 카드 강도 표시에만 사용한다.
- strict miss에서 `reveal_type` 때문에 `ANSWERED`로 승격하면 안 된다.

## 5) 위키 검증소 시나리오 적용
- 위키 제보(`PENDING`) 단계에서는 해석 라벨을 임시로 둘 수 있다.
- 좋아요 검증 기준 충족 후 `APPROVED`로 이벤트 발행할 때:
  - 사실 이벤트만 `event`로 저장
  - 근거가 있는 라벨만 `event_reveal`로 저장
  - 근거 없는 해석 라벨은 운영 메모로만 유지

## 6) 지속 참고 체크리스트
- 질문 문구에 해석이 섞여 있으면 fact/label을 먼저 분리했는가
- `CONFIRM`에 직접 근거가 있는가
- `HINT`가 사실처럼 오해될 문구는 아닌가
- `evidence_event_id`/`evidence_note`를 남겼는가
- 정답 선택 로직이 reveal 강도에 의존하지 않는가

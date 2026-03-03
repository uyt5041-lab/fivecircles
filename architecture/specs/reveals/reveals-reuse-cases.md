# REVEALS Reuse Cases (Policy / Explain / Ranking / Recap)

목적
- `REVEALS` 메타(`event_reveal`)를 검색뿐 아니라 정책/설명/추천/리캡에서 재사용하는 패턴을 정리한다.
- 팀원 작업(파이프라인/후처리)과 충돌하지 않게, **통합 가능성만** 명시하고 구현은 강제하지 않는다.

전제(현재 기준)
- predicate: `PredicateCode.REVEALS`
- 메타(가능하면): `event_reveal(event_id, target_type, target_id, reveal_type)`
- `target_type`은 현재 스키마 기준 `CHARACTER|ATTRIBUTE`
- `reveal_type`은 현재 문서 기준 `HINT|CONFIRM`(강도)
- MVP에서는 비인물 object를 1급 엔티티로 만들지 않는다.
  - 대신 `target_type=ATTRIBUTE`도 조인/랭킹 신호로 쓰려면, `target_id`를 `aboutCharacterId`로 채우는 정책(0 금지)이 필요하다(Option 1).
- `ATTRIBUTE`의 “무슨 사실인지”까지 엄밀히 하려면 `target_key` 같은 확장이 필요할 수 있다(향후, Option 2).
- 사실/해석 분리 원칙: 사건 사실은 `event`, 해석 라벨은 `reveal`로 관리한다.
  - 근거 없는 해석 라벨은 `event_reveal`에 저장하지 않는다.
  - 기준 문서: `reveals-classification.md` Rule C/C.1/C.2

관련 문서
- 분류/정합성: `fivecircles/architecture/specs/reveals/reveals-classification.md`
- 지속 기준서: `fivecircles/architecture/specs/reveals/reveal-evidence-label-policy.md`
- 라우팅(MVP vs V3): `fivecircles/architecture/specs/reveals/reveals-routing-mvp-and-v3.md`
- DB 스키마: `services/event-service/src/main/resources/db/migration/V2__fix_event_reveal_schema.sql`
- 축/확장 연계(ex20~ex23): `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex20-axis.md`, `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex22.2-expension-categorized-impl-plan.md`, `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex22.3-expension-expension-qs-imple2.md`, `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex23-RDF-inheritance.md`

---

## 1) 스포일러 정책 강화(차등 게이트)

아이디어
- REVEALS는 스포일러 위험도가 높으므로, target/strength 기준으로 노출을 더 보수적으로 제어한다.

예시(정책 룰)
- `target_type=CHARACTER` AND `reveal_type=CONFIRM` 인 reveal은 K+1까지는 항상 숨김(설명에도 직접 노출 금지).
- `reveal_type=HINT`는 "존재 여부 배지"만 노출(내용 텍스트는 숨김).

예시(표시)
- 이벤트 카드: `REVEAL(Identity)`, `REVEAL(Hint)` 같은 배지(내용 텍스트 없이)

---

## 2) Q4 류 질문 정확도 보강(정답 찾기 vs 근거 제시 분리)

아이디어
- 메타가 없으면 `REVEALS`를 1급 검색 키로 쓰지 않고, 인지 변화/대면 행동을 먼저 찾는다.
- 메타가 있으면 "무엇이 드러났나"를 기준으로 정답 후보를 좁힐 수 있다.

예시(메타 없는 기간)
1. 정답 찾기: `DISCOVERS/LEARNS` 계열(또는 질문 그룹)로 이벤트 E를 찾는다.
2. 근거 제시: E에 연결된 `event_reveal`이 있다면 "근거" 영역에만 표시한다.
3. `reveal_type(HINT/CONFIRM)`는 근거 강도 표현용이며 정답 판정(ANSWERED) 승격 조건으로 쓰지 않는다.

예시(메타 있는 기간)
- "스카일러가 월터의 범죄를 알아차린 시점" 질문에서:
  - `REVEALS` 이벤트 중 "범죄"에 해당하는 target을 가진 것만 후보로 포함(향후 `target_key`가 필요할 수 있음)

---

## 3) Explain UI(왜 차단됐는지/무슨 공개인지)

아이디어
- REVEALS는 탐색 결과에 섞기보다, "설명/근거"로만 노출하는 것이 안전하다.

예시(UI)
- 섹션 1: 사건 요약(기본)
- 섹션 2: 공개된 정보(있을 때만)
  - `target_type=CHARACTER`: \"정체 공개(캐릭터ID=123)\" (K 밖이면 이 섹션 자체를 숨김)
  - `target_type=ATTRIBUTE`: \"사실 공개\" (향후 key로 구체화)

예시(응답 형태, 개념)
```json
{
  "eventId": 2088,
  "predicateCode": "REVEALS",
  "reveals": [
    { "targetType": "CHARACTER", "targetId": 123, "revealType": "CONFIRM" }
  ]
}
```

---

## 4) PRECEDES suggestion 랭킹 feature(자동 확정 금지, 정렬 신호로만)

아이디어
- REVEALS 메타는 PRECEDES 추천 후보를 "더 그럴듯한 것" 위로 올리는 정렬 신호로 쓸 수 있다.
- 이건 relation을 자동 저장하는 게 아니라 ranking이므로 스펙 철학과 충돌이 적다.
- `reveal_type` 기반 가중치는 "추천 정렬"에만 사용하고, 질문 정답 선택(strict-first)에는 사용하지 않는다.

예시(규칙)
- A 이벤트가 `REVEALS` + `CONFIRM`이고, B 이벤트가 `CAPTURES/ESCAPES/ATTACKS` 계열이면 A->B 후보 점수를 가산

예시(가중치 개념)
- score = sharedCharacterCount + closenessWeight + revealBoost

교차 지점(“만들 때” vs “만든 뒤”)
- 만들 때(서제스천 생성/정렬):
  - REVEALS는 PRECEDES 후보의 정렬 신호(evidence feature)로만 사용한다.
  - 즉, REVEALS가 있다고 해서 PRECEDES를 자동 저장하지 않는다.
- 만든 뒤(승인된 PRECEDES를 표시/설명):
  - causes/effects(PRECEDES 체인)를 UI에 보여줄 때, 체인 중간에 `REVEALS`가 있으면 “전환점 배지/근거”로 강조할 수 있다.
  - 단, 체인 탐색 자체는 PRECEDES만으로 수행하고, REVEALS는 결과 렌더링 단계에서만 소비한다.

---

## 5) 안전 리캡/요약(episode gate 내 reveal만 모으기)

아이디어
- K 이하에서 "공개된 정보"만 모아서 요약하면 스포일러 안전한 리캡을 만들 수 있다.

예시(리캡 생성 규칙)
- `episode_end <= K` AND `predicate_code=REVEALS`인 이벤트를 모으고,
- `reveal_type=CONFIRM`만 리캡 본문에 포함(또는 HINT는 별도 섹션)

예시(출력)
- \"[K화까지 공개된 정체] ...\"
- \"[K화까지 공개된 사실] ...\" (ATTRIBUTE는 key가 생기면 정확도 상승)

---

## 통합 포인트(협업)

아래 항목은 팀원 작업 완료 후 통합 시점에 반영 가능하다.
- intelligence refine 응답에 reveal target 메타가 포함되면, wiki 승인 -> event 발행 시 `event_reveal` 저장이 자동화된다.
- `ATTRIBUTE`를 엄밀히 하려면 `target_key`/`target_text` 같은 확장이 필요할 수 있다.

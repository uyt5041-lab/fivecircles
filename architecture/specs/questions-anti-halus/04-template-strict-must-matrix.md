# Production Q1~Q15: Strict MUST Matrix

목적
- `03-implementation-plan.md`의 실행 원칙(`Strict -> Probe -> Approx`)을 Q1~Q15에 바로 적용할 수 있도록
  템플릿별 `Strict MUST`를 고정한다.
- 본 문서는 “정답 확정 조건(Strict)”과 “후보 탐색 조건(Approx)”을 분리하는 실행 기준표다.

범례
- `Strict MUST`: 이 조건이 없으면 `ANSWERED` 금지
- `Approx`: 내부 참고용 후보 생성(정답 확정 금지)
- `Probe kind`: `/api/event/v2/probe`의 `queryKind` 값
- `Disclosure`: 사용자-facing 노출 정책
  - `ALLOW_SPOILER_BLOCKED`
  - `HIDE_EXISTS_BEYOND_K` (민감 질문, 사용자에게는 `LOCKED`)
- `K/expectedMinEpisode`: 시즌코드(예: 202)가 아니라 누적(절대) 회차를 사용
  - 예: `S1E7=7`, `S2E1=8`, `S2E2=9`, `S2E4=11`

---

## Q1~Q15 실행 입력 기준표

아래 표는 실행기에 그대로 매핑되는 구조화 필드다.

표기 규칙(브베 질문 표현 vs 범용 실행 필터)
- 표의 `strict_must`는 읽기 쉬운 shorthand(`subject=`, `with=` 등)를 허용한다.
- 실제 실행 직전에는 `03-implementation-plan.md`의 범용 `strictFilters` 키로 변환해야 한다.
  - `subject=*` -> `subjectCharacterId`
  - `with=[*,*]` -> `withCharacterIds`
  - `target=*` -> `targetCharacterId` (optional)
  - `about=*` -> `aboutCharacterId` (optional)

| question_id | question_text | queryKind | canonical_episode | strict_must | approx_only | sensitive_policy | evidence_event_id |
|---|---|---|---|---|---|---|---|
| `Q01` | 월터의 첫 직접살인이 언제인가? | `character_predicate_earliest` | `S1E3` | `subject=Walter`, `predicateCodeAnyOf=[KILLS]`, `qAnyOf=[Krazy-8,크레이지-8]` | Walter action broad(정답 확정 금지) | `HIDE_EXISTS_BEYOND_K` | `2292` |
| `Q02` | 월터가 암페타민 제조시작한게 언제지? | `character_keyword_earliest` | `S1E1` | `subject=Walter`, `qAnyOf=[meth,메스,암페타민,PRODUCTION...]` | Walter keyword broad(정답 확정 금지) | `HIDE_EXISTS_BEYOND_K` | `2285` |
| `Q03` | 투코를 처음 만나는 시점은 언제야? | `coevents_earliest` | `S1E6` | `with=[Walter,Tuco]`, `predicateCodeAnyOf=[MEETS]` | `predicateCodeAnyOf=[ALLIES_WITH,ATTACKS]`, `qAnyOf=[폭발,사무실,하이젠베르크]` | `ALLOW_SPOILER_BLOCKED` | `2376` |
| `Q04` | 스카일러가 남편의 범죄사실을 알아차린 시점이언제냐? | `character_predicate_earliest` | `S3E2` | `subject=Skyler`, `predicateCodeAnyOf=[DISCOVERS,LEARNS]`, `qAnyOf=[meth,메스,암페타민,마약,제조]` | `predicateCodeAnyOf=[DISCOVERS,LEARNS]` | `HIDE_EXISTS_BEYOND_K` | `TBD` |
| `Q05` | 월터가 처음 범죄를 결심한 순간은 언제지? | `character_keyword_earliest` | `S1E1` | `subject=Walter`, `predicateCodeAnyOf=[MEETS]`, `qAnyOf=[협박,제안,동업]` | `qAnyOf=[결심,범죄,제시,DEA,단속,암 진단,가족,돈,치료비,직접 제조]` | `HIDE_EXISTS_BEYOND_K` | `2448` |
| `Q06` | 월터와 제시가 처음 파트너가 된 계기? | `coevents_earliest` | `S1E1` | `with=[Walter,Jesse]`, `predicateCodeAnyOf=[ALLIES_WITH,JOINS,MEETS]`, `qAnyOf=[협박,제안,동업]` | `predicateCodeAnyOf=[DISCOVERS,LEARNS,MEETS]`, `qAnyOf=[DEA,도주,RV,거래]` | `ALLOW_SPOILER_BLOCKED` | `2448` |
| `Q07` | 월터가 처음 거짓말을 들키는 순간? | `character_predicate_earliest` | `S2E2` | `subject=Walter`, `qAnyOf=[Which one,어느 폰,두 번째 폰]` | `qAnyOf=[거짓말,부정,변명,두 번째 폰]` | `HIDE_EXISTS_BEYOND_K` | `3001` |
| `Q08` | 월터의 ‘가족 명분’이 처음 흔들리는 지점? | `character_keyword_earliest` | `S1E5` | `subject=Walter`, `predicateCodeAnyOf=[OTHER]`, `qAnyOf=[거절]` | `qAnyOf=[자존심,열등감,갈등,엘리엇,치료비 지원]` | `HIDE_EXISTS_BEYOND_K` | `3005` |
| `Q09` | 행크가 수사 방향을 크게 바꾸는 계기? | `character_predicate_earliest` | `S1E2` | `subject=Hank`, `predicateCodeAnyOf=[DISCOVERS]`, `qAnyOf=[Property of J.P. Wynne High School,J.P. Wynne High School,Wynne High School]` | `qAnyOf=[가스마스크,학교,실험실,인벤토리,휴고]` | `ALLOW_SPOILER_BLOCKED` | `3007` |
| `Q10` | 월터가 처음 본격적인 조직적 위협을 받는 순간? | `character_predicate_earliest` | `S1E6` | `subject=Walter`, `predicateCodeAnyOf=[ATTACKS,CAPTURES,BETRAYS,KILLS]`, `excludePredicateCodeAnyOf=[DISCOVERS,LEARNS]`, `qAnyOf=[투코,구타,폭력,위협]` | `predicateCodeAnyOf=[ATTACKS,CAPTURES]` | `HIDE_EXISTS_BEYOND_K` | `2306` |
| `Q11` | 누가 월터를 의심하기 시작한 최초 시점? | `character_predicate_earliest` | `S1E2` | `subject=Skyler`, `targetCharacterId=Walter`, `qAnyOf=[마리화나,대마,딜러,커버 스토리,추궁]` | `qAnyOf=[의심,제시,행적 공백,거짓말,검증,대면,신뢰]` | `HIDE_EXISTS_BEYOND_K` | `3013` |
| `Q12` | 월터가 처음 통제권을 쥐는 순간? | `character_predicate_earliest` | `S1E6` | `subject=Walter`, `target=Tuco`, `qAnyOf=[선지급,거래 조건,주도권,통제권]` | `qAnyOf=[폭발,투코,쇼다운,협상]` | `HIDE_EXISTS_BEYOND_K` | `3019` |
| `Q13` | 월터가 처음 돈의 흐름을 만들기 시작한 사건? | `character_predicate_earliest` | `S1E7` | `subject=Walter`, `qAnyOf=[대량 공급,계약,정기 수익,주 단위]` | `qAnyOf=[돈,거래,유통]` | `HIDE_EXISTS_BEYOND_K` | `2307` |
| `Q14` | 스카일러-월터 관계가 돌이키기 어려워지는 첫 균열? | `coevents_earliest` | `S2E13` | `with=[Walter,Skyler]`, `predicateCodeAnyOf=[BETRAYS,LEARNS,DISCOVERS]`, `qAnyOf=[별거,신뢰 붕괴,집에서 나가]` | `predicateCodeAnyOf=[MEETS]` | `HIDE_EXISTS_BEYOND_K` | `2923` |
| `Q15` | 월터가 본격적으로 은폐/도주를 시작하는 최초 지점? | `character_predicate_earliest` | `S1E2` | `subject=Walter`, `qAnyOf=[산성 용액,용해,시신 처리]` | `qAnyOf=[위기 대응,회피]` | `HIDE_EXISTS_BEYOND_K` | `2289` |

`evidence_event_id`는 strict query + 06 정답회차 앵커 검증 기준으로 순차 채운다(`Q01,Q02,Q03,Q05,Q06,Q07,Q08,Q09,Q10,Q11,Q12,Q13,Q14,Q15` 반영 완료). 나머지는 `TBD`를 유지한다.
`sensitive_policy`는 런타임의 `disclosurePolicy`에 1:1 매핑한다.

---

## 적용 규칙(강제)

1. Strict 0건이면 `ANSWERED` 금지
- Approx 후보가 1건 이상이어도 정답 확정 불가
- 상태는 probe로만 판정: `SPOILER_BLOCKED` or `NOT_ENOUGH_DATA`

2. Strict/Probe 필터 동기화
- probe 요청의 `strictFilters`는 템플릿 Strict MUST와 1:1로 동일해야 한다.
- Strict와 Probe가 다르면 `existsAnyApproved=true` 오판 위험이 높아진다.

3. 동치 fallback만 허용
- 허용: object 라벨 miss 보완을 위한 정규화 토큰 추가(`meth -> PRODUCTION`)
- 금지: 질문 의미를 넓히는 일반 토큰 추가(semantic dilution)

4. 민감 질문은 `HIDE_EXISTS_BEYOND_K`
- 사용자-facing에서는 `SPOILER_BLOCKED`를 그대로 노출하지 않고 `LOCKED`로 합친다.

5. `prefer*` 계열은 Strict에서 금지
- `strict_must`에는 `preferPredicateCodeAnyOf`를 두지 않는다.
- 선호/가중치/정렬 힌트는 `approx_only`에서만 표현한다.

6. Context Timeline 정렬 순서: `CAUSE → FOCUS → EFFECT`
- 정렬 priority: `CAUSE(1) < FOCUS(2) < EFFECT(3)` — 같은 에피소드 내에서도 시간 순서 보장.
- Dedup priority: `FOCUS`는 항상 최우선 — 동일 이벤트가 CAUSE/EFFECT와 FOCUS에 중복 시 FOCUS로 표시.
- Depth는 BFS hop 수이며, 분기가 있으면 아이템 수는 `2×depth+1`을 초과할 수 있다.

---

## 구현 체크 포인트

- 템플릿에 아래 필드가 있어야 한다.
  - `question_id`
  - `question_text`
  - `queryKind`
  - `canonical_episode`
  - `strict_must` (MUST)
  - `approx_only` (선택)
  - `sensitive_policy` (`disclosurePolicy`와 1:1)
  - `evidence_event_id`

- 실행기는 아래 순서만 허용한다.
  1) Strict query(<=K)
  2) 0건일 때 probe
  3) 필요 시 Approx 후보(내부 참고용)

---

## FactGrid 해석(주석)

```sparql
# Strict는 "정답 확정용 SELECT"
SELECT ?event WHERE {
  ?event wdt:Pparticipant wd:Walter ;
         wdt:Ppredicate wd:KILLS .
  FILTER(?episode <= ?K)
} ORDER BY ?episode LIMIT 1

# Probe는 "존재 확인 ASK"
ASK {
  ?event wdt:Pparticipant wd:Walter ;
         wdt:Ppredicate wd:KILLS .
}
```

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
| `Q01` | 월터의 첫 살인은 언제지 | `character_predicate_earliest` | `S1E3` | `subject=Walter`, `predicateCodeAnyOf=[KILLS]` | Walter action broad(정답 확정 금지) | `HIDE_EXISTS_BEYOND_K` | `2292` |
| `Q02` | 월터가 암페타민 제조시작한게 언제지? | `character_keyword_earliest` | `S1E1` | `subject=Walter`, `qAnyOf=[meth,메스,암페타민,PRODUCTION...]` | Walter keyword broad(정답 확정 금지) | `HIDE_EXISTS_BEYOND_K` | `2285` |
| `Q03` | 투코를 처음 만나는 시점은 언제야? | `coevents_earliest` | `S1E6` | `with=[Walter,Tuco]`, `predicateCodeAnyOf=[MEETS]` | coevents earliest(no predicate) | `ALLOW_SPOILER_BLOCKED` | `TBD` |
| `Q04` | 스카일러가 남편의 범죄사실을 알아차린 시점이언제냐? | `character_predicate_earliest` | `S3E2` | `subject=Skyler`, `predicateCodeAnyOf=[DISCOVERS,LEARNS]`, `qAnyOf=[meth,메스,암페타민,마약,제조]` | `predicateCodeAnyOf=[DISCOVERS,LEARNS]` | `HIDE_EXISTS_BEYOND_K` | `TBD` |
| `Q05` | 월터가 처음 ‘범죄’ 결심한 순간? | `character_predicate_earliest` | `S1E1` | `subject=Walter`, `qAnyOf=[결심,동업,제조 시작,암 진단]`, `predicateCodeAnyOf=[LEARNS,DISCOVERS]` | `qAnyOf=[가족,돈,치료비]` | `HIDE_EXISTS_BEYOND_K` | `TBD` |
| `Q06` | 월터와 제시가 처음 파트너가 된 계기? | `coevents_earliest` | `S1E1` | `with=[Walter,Jesse]`, `predicateCodeAnyOf=[ALLIES_WITH,JOINS,MEETS]` | `predicateCodeAnyOf=[DISCOVERS,LEARNS]` | `ALLOW_SPOILER_BLOCKED` | `2448` |
| `Q07` | 월터가 처음 거짓말을 들키는 순간? | `character_predicate_earliest` | `S1E2` | `subject=Walter`, `predicateCodeAnyOf=[DISCOVERS,LEARNS]`, `qAnyOf=[거짓말,휴대폰,실종,추궁]` | `qAnyOf=[의심,불신]` | `HIDE_EXISTS_BEYOND_K` | `TBD` |
| `Q08` | 월터의 ‘가족 명분’이 처음 흔들리는 지점? | `character_keyword_earliest` | `S1E5` | `subject=Walter`, `qAnyOf=[가족,치료비,지원 거절,명분]` | `qAnyOf=[자존심,열등감,갈등]` | `HIDE_EXISTS_BEYOND_K` | `TBD` |
| `Q09` | 행크가 수사 방향을 크게 바꾸는 계기? | `character_predicate_earliest` | `S1E4` | `subject=Hank`, `predicateCodeAnyOf=[DISCOVERS,LEARNS]`, `qAnyOf=[고순도,수사 방향,단서]` | `qAnyOf=[수사,추적]` | `ALLOW_SPOILER_BLOCKED` | `TBD` |
| `Q10` | 월터가 처음 본격적인 조직적 위협을 받는 순간? | `character_predicate_earliest` | `S1E6~7` | `subject=Walter`, `predicateCodeAnyOf=[ATTACKS,CAPTURES,BETRAYS,KILLS]`, `excludePredicateCodeAnyOf=[DISCOVERS,LEARNS]`, `qAnyOf=[투코,공급 계약,보복]` | `predicateCodeAnyOf=[ATTACKS,CAPTURES]` | `HIDE_EXISTS_BEYOND_K` | `2306` |
| `Q11` | 누가 월터를 의심하기 시작한 최초 시점? | `character_predicate_earliest` | `S1E2` | `targetCharacterId=Walter`, `predicateCodeAnyOf=[DISCOVERS,LEARNS]`, `qAnyOf=[의심,휴대폰,실종]` | `qAnyOf=[행동 이상,불신]` | `HIDE_EXISTS_BEYOND_K` | `TBD` |
| `Q12` | 월터가 처음 통제권을 쥐는 순간? | `character_predicate_earliest` | `S1E6` | `subject=Walter`, `predicateCodeAnyOf=[ATTACKS,DEFEATS]`, `qAnyOf=[폭발,협상,통제권]` | `predicateCodeAnyOf=[MEETS,ALLIES_WITH]` | `HIDE_EXISTS_BEYOND_K` | `TBD` |
| `Q13` | 월터가 처음 돈의 흐름을 만들기 시작한 사건? | `character_predicate_earliest` | `S1E7` | `subject=Walter`, `qAnyOf=[대량 공급,계약,정기 수익,주 단위]`, `excludePredicateCodeAnyOf=[OTHER]` | `qAnyOf=[돈,거래,유통]` | `HIDE_EXISTS_BEYOND_K` | `TBD` |
| `Q14` | 스카일러-월터 관계가 돌이키기 어려워지는 첫 균열? | `coevents_earliest` | `S2E13` | `with=[Walter,Skyler]`, `predicateCodeAnyOf=[BETRAYS,LEARNS,DISCOVERS]`, `qAnyOf=[별거,신뢰 붕괴,집에서 나가]` | `predicateCodeAnyOf=[MEETS]` | `HIDE_EXISTS_BEYOND_K` | `TBD` |
| `Q15` | 월터가 본격적으로 은폐/도주를 시작하는 최초 지점? | `character_predicate_earliest` | `S1E2` | `subject=Walter`, `qAnyOf=[시신 처리,증거 은폐,알리바이,도주]`, `predicateCodeAnyOf=[LEARNS,DISCOVERS]` | `qAnyOf=[위기 대응,회피]` | `HIDE_EXISTS_BEYOND_K` | `TBD` |

`evidence_event_id`는 strict query 기준으로 확정 가능한 Q부터 순차 채운다(`Q01,Q02,Q06,Q10` 반영 완료). 나머지는 `TBD`를 유지한다.
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

# Review: REVEALS ATTRIBUTE (Option 1) Routing Doc
> Reviewer: codex-ops | Date: 2026-02-10

## Scope
- `fivecircles/architecture/specs/reveals/reveals-routing-mvp-and-v3.md`
- `fivecircles/architecture/specs/reveals/reveals-reuse-cases.md`
- Reality check references:
  - DB: `services/event-service/src/main/resources/db/migration/V2__fix_event_reveal_schema.sql`
  - Current prompt behavior (ATTRIBUTE target_id=0): `services/intelligence-service/src/main/resources/prompts/refine-fact.txt`

## Findings (Ordered)

1. [HIGH] Option 1(ATTRIBUTE target_id=aboutCharacterId, 0 금지)은 V2.5에서 “조인/랭킹 가능”을 만드는 최소 조건으로 정합적
- 현재처럼 `ATTRIBUTE target_id=0`이면 REVEALS 메타는 조인/필터/랭킹 신호로 사용할 수 없다(전부 동일 값).
- Option 1을 적용하면 “주체(subject) + about(대상 캐릭터)”까지는 구조화되어, Q4 계열 및 PRECEDES 랭킹 신호에 즉시 재사용 가능.

2. [HIGH] “aboutCharacterId”의 의미를 데이터 작성/검증 규칙으로 고정해야 한다
- about은 “이 사실이 누구에 대한 것인지”이며, **target_type=ATTRIBUTE라도 target_id는 캐릭터 ID**를 의미한다.
- 권장 규칙(문서에 반영됨):
  - about 캐릭터(target_id)는 involvedCharacter로도 포함(`event_character`)되어야 함.
  - about을 특정할 수 없으면 `event_reveal` row를 만들지 않는다(0으로 채우지 않음).

3. [MEDIUM] 현재 조회 응답이 reveal 메타를 “대표 1건”만 내려주는 경우, about 필터가 흔들릴 수 있음
- 다중 reveal row를 저장할 수 있는 스키마인데도, DTO/조회가 1건만 노출하면:
  - Q4 같은 about 필터가 “대표 reveal” 선택 규칙에 종속됨.
- MVP 방안:
  - 데이터 작성 규칙으로 “Q4용 이벤트는 reveal row를 1개만 둔다”를 임시로 강제하거나,
  - API 확장으로 reveal 리스트를 내려서 클라이언트가 about 필터를 정확히 수행하도록 해야 함.

4. [MEDIUM] Q4 “범죄 사실”을 정확히 구분하는 것은 V3(Option 2) 영역이 맞다
- Option 1은 about까지만 보장하고, “범죄/소속/과거/거짓말” 등의 세부 분류는 텍스트로만 남는다.
- 정확도 향상이 필요해지는 시점에 `target_key`(최소 확장) 또는 object 1급 엔티티화(비용 큼)로 확장하는 로드맵이 합리적.

5. [LOW] 문서의 API 표기(드라마 이벤트 조회 등)는 FE의 api3/api4 번호와 혼동될 수 있어, “경로 기준 표기”가 안전하다
- 라우팅 문서에서 `/api/event/v2/...` 경로로 표기하는 방식이 더 명확함(이번 수정으로 정리됨).

## Decision
- **APPROVE WITH NOTES**
  - 문서 자체는 Option 1/2의 경계를 명확히 했고, MVP에서 “object 1급 엔티티화”를 피하면서도 조인 가능성을 확보하는 방향이 일관적이다.

## Next Actions
1. Pipeline 정책 확정: `ATTRIBUTE target_id=0 금지` + about 캐릭터 강제(위키 검증 UI 또는 publish 단계)
2. Transition 계획:
  - 기존 `ATTRIBUTE target_id=0` 데이터 처리(백필/무시/삭제 중 택1)
3. Reveal 노출 정책:
  - 조회 응답에서 reveal 1건만 노출할지, 리스트로 확장할지 결정(대표 선택 규칙도 문서화)


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

---

## Peer Review (TASK-013) by Claude
> Reviewer: claude-reviewer | Date: 2026-02-10

### Code Verification Summary

Option 1 정책을 실제 코드/스키마/프롬프트 기준으로 검증했다.

#### A. 스키마 확인 (CONFIRMED)

| 항목 | 파일 | 상태 | 비고 |
|------|------|------|------|
| `target_id NOT NULL` | `V2__fix_event_reveal_schema.sql:9` | ✓ | null 거부, 0은 허용 |
| PK `(event_id, target_type, target_id)` | `V2__fix_event_reveal_schema.sql:11` | ✓ | 다중 reveal row 허용 |
| DEFAULT 없음 | 같은 파일 | ✓ | 반드시 명시적으로 값 제공 필요 |

- 스키마는 Option 1과 호환. `target_id=0` 금지는 **애플리케이션 레이어에서 강제해야** 함(DB 레벨에서는 0이 합법).

#### B. "대표 1건" 노출 패턴 확인 (CONFIRMED — 리뷰 Finding #3 동의)

- `EventResponseDTO`는 단일 reveal 필드 3개만 존재 (`revealTargetId`, `revealTargetType`, `revealType`).
- `EventServiceImpl:389-391` — `reveals.get(0)` (first reveal wins).
- `EventQueryServiceImpl:279-282` — `map.putIfAbsent()` (first reveal wins, 정렬: target_type ASC, target_id ASC).
- **위험**: 다중 reveal row가 있으면 "대표 1건"이 about 필터 결과를 좌우함. `target_type ASC` 정렬이므로 `ATTRIBUTE < CHARACTER` — ATTRIBUTE가 먼저 선택됨.

#### C. 코드에서 target_id=0 방어 부재 (GAP — 신규 발견)

- `EventServiceImpl:97` — `revealTargetId != null`만 검사, 0은 통과.
- `normalizeRevealTargetType()` — target_type 유효성만 검증, target_id 값은 미검증.
- **테스트**: `EventServiceImplCreateEventRevealTest`에서 `revealTargetId(999L)`로만 테스트, 0 케이스 없음.
- **권장**: `createEvent`에서 `if (REVEALS && ATTRIBUTE && targetId == 0) throw INVALID_INPUT_VALUE` 검증 추가.

#### D. 프롬프트/Mock 코드 불일치 (CRITICAL GAP)

| 소스 | 현재 동작 | Option 1 요구 |
|------|-----------|---------------|
| `refine-fact.txt:27` | `revealTargetId=0` (ATTRIBUTE) | `revealTargetId=aboutCharacterId` |
| `OpenAiLlmClient.java:258` | `revealTargetId = 0L` (mock) | `revealTargetId = involvedIds.get(N)` |

- 프롬프트와 Mock LLM 클라이언트가 **모두** Option 1과 충돌. 이 두 곳을 먼저 수정하지 않으면, 새로 생성되는 모든 ATTRIBUTE reveal이 0으로 들어옴.

#### E. 기존 쿼리에서 target_id=0의 영향 (CONFIRMED SAFE — 현재는)

- `findRevealPartnerId` (EventCharacterMapper.xml:111) — `WHERE er.target_id = #{characterId}`. characterId가 0인 캐릭터는 없으므로 매칭 안 됨.
- PRECEDES suggestion 랭킹 (EventMapper.xml:247,315) — `LEFT JOIN ec_rt ON ec_rt.character_id = er_base.target_id`. target_id=0이면 character_id=0인 row가 없어서 JOIN 실패(NULL). 랭킹 가산 0.
- **결론**: target_id=0 데이터는 **현재 "무해하지만 무용"**. Option 1 적용 후에도 기존 0 데이터는 조인/필터에서 자연스럽게 무시됨.

#### F. Q4 / Quick20 라우팅 안정성 (CONDITIONAL PASS)

- **Q4 "스카일러가 월터의 범죄를 알아차림"**:
  - api3로 Skyler의 REVEALS 이벤트를 가져온 뒤 `revealTargetId == WalterId` 필터.
  - 현재 DTO가 단일 reveal만 노출하므로, **해당 이벤트의 첫 reveal row가 ATTRIBUTE+about=Walter여야** 정상 작동.
  - 다중 reveal row가 있고 CHARACTER row가 먼저 오면(target_type ASC → ATTRIBUTE가 먼저이므로 이 경우는 드묾) 필터가 깨질 수 있음.
  - **MVP 안전 조건**: "REVEALS 이벤트당 reveal row 1개" 데이터 규칙 + about 캐릭터 정확 입력.

- **Quick20 #11 "무엇을 드러냈나"**:
  - 이벤트의 `revealTargetType`/`revealTargetId`를 설명으로 표시만 하면 되므로, 단일 reveal 노출로 충분.
  - V3에서 "종류"까지 구조화하려면 `target_key` 확장 필요(문서 일치).

- **Quick20 #18 "정체 밝혀지는 이벤트 나열"**:
  - `predicateCode=REVEALS` 필터 후 `revealTargetType=CHARACTER` 클라이언트 필터.
  - 단일 reveal 노출이므로 ATTRIBUTE+CHARACTER 혼합 이벤트에서 CHARACTER가 누락될 수 있음.
  - **대응**: MVP에서는 REVEALS 이벤트당 1 row 규칙으로 커버 가능. 리스트 확장은 V3.

### Final Verdict

- **APPROVE** — Option 1 정책 자체는 일관적이고, V2.5/V3 경계가 명확함.
- **구현 전 필수 조건 4건**:

| # | 항목 | 우선순위 | 비고 |
|---|------|----------|------|
| 1 | `refine-fact.txt` 프롬프트 수정: ATTRIBUTE → `revealTargetId=aboutCharacterId` | CRITICAL | 현재 모든 신규 ATTRIBUTE reveal이 0으로 생성됨 |
| 2 | `OpenAiLlmClient.java:258` Mock 수정: 0L → `involvedIds`에서 추론 | HIGH | 개발 환경 데이터도 오염됨 |
| 3 | `EventServiceImpl.createEvent` 검증 추가: ATTRIBUTE + targetId=0 거부 | HIGH | 프롬프트 수정 후에도 방어벽 필요 |
| 4 | 기존 `target_id=0` ATTRIBUTE 데이터 전환 정책 확정 | MEDIUM | 현재는 무해하나, Q4 라우팅 활성화 시 누락 원인 |

- **선택 사항**: DTO reveal 리스트 확장은 MVP에서 불필요. "1 이벤트 1 reveal row" 데이터 규칙으로 충분.

---

## Codex Follow-up (After Claude Review): 정합성 확인 + 결함 수정 반영
> Date: 2026-02-10

클로드 리뷰 내용에 **동의**하며, 실제 코드 기준으로 아래 “정합성 구멍”을 추가 확인했고 즉시 수정했다.

### 추가로 확인된 구멍(대표 reveal 노출 우선순위)
- `EventResponseDTO`가 reveal을 단일 1건만 노출하는 상태에서,
  `EventRevealMapper.xml`의 정렬이 `target_type ASC`라 **ATTRIBUTE가 CHARACTER보다 먼저 선택**될 수 있었다.
- 결과적으로 한 이벤트에 (ATTRIBUTE, CHARACTER) reveal row가 둘 다 있으면 “정체 공개”가 가려질 위험이 있다.

### 반영한 수정(구현 완료 + 테스트 통과)
- Intelligence mock: Option1 변경은 협의 후 적용. 현재는 원래 Mock(`ATTRIBUTE revealTargetId=0`)을 유지하되, Option1 적용 후보 코드를 주석으로 남김.
  - `services/intelligence-service/src/main/java/com/nospoiler/intelligenceservice/service/OpenAiLlmClient.java`
- event-service 방어벽: `REVEALS` + `revealTargetId<=0` 거부(0 금지), ATTRIBUTE about은 characterIds에 포함 강제(있을 때).
  - `services/event-service/src/main/java/com/nospoiler/eventservice/service/EventServiceImpl.java`
- 대표 reveal 안정화: reveal 정렬을 CHARACTER 우선으로 변경(단일 reveal 노출의 안정성).
  - `services/event-service/src/main/resources/mapper/event/EventRevealMapper.xml`
- PRECEDES revealBoost: `event_reveal.target_type`에서 ATTRIBUTE도 포함(aboutCharacterId 가정).
  - `services/event-service/src/main/resources/mapper/event/EventMapper.xml`
- 테스트 보강: `revealTargetId=0` 거부 + ATTRIBUTE about/involved 강제 케이스 추가.
  - `services/event-service/src/test/java/com/nospoiler/eventservice/service/EventServiceImplCreateEventRevealTest.java`

### 남은 리스크(합의 필요)
- OpenAI 호출 실패 시 Intelligence가 Mock refine으로 fallback하면, 여전히 `ATTRIBUTE revealTargetId=0`이 나올 수 있다.
  - 이 경우 event-service가 `revealTargetId<=0`을 거부하므로 publish/create가 실패할 수 있음.
  - 합의 후 처리 옵션: (1) Mock을 Option1로 맞춤, (2) event-service에서 “ATTRIBUTE+0 drop” 정책으로 완화(비추), (3) wiki publish 단계에서 reveal drop/hard-fail 정책 고정.

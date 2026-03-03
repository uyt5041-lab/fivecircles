# REVEALS Routing: MVP(V2.5) vs V3 Expansion

목표
- Production Q(Q1~Q15) + Quick20(Level 질문)에서 `REVEALS`를 **정답 찾기**와 **근거/설명**에 어떻게 쓰는지 라우팅 규칙으로 고정한다.
- MVP(V2.5, 현 스키마/파이프라인 중심)에서는 **비인물 object를 1급 엔티티로 만들지 않는다.**
- 다만 “조인/랭킹 신호”가 필요한 최소 수준의 구조화를 위해, ATTRIBUTE reveal의 `target_id`를 `aboutCharacterId`로 채우는 옵션(Option 1)의 정합성을 정리한다.

정합성 고정(필수)
- 사건 사실(`event`)과 해석 라벨(`reveal`)을 분리한다.
- strict 정답 선택은 사실 이벤트로만 수행하고, `reveal_type(HINT|CONFIRM)`는 WHY/근거 강도 표시로만 사용한다.
- 상세 판정 규칙은 `reveals-classification.md` Rule C/C.1/C.2를 canonical로 따른다.
- 지속 참고 기준서는 `reveal-evidence-label-policy.md`를 canonical로 따른다.
- 축/확장 문서 정합성은 ex20~ex23을 함께 본다.
  - `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex20-axis.md`
  - `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex22.2-expension-categorized-impl-plan.md`
  - `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex22.3-expension-expension-qs-imple2.md`
  - `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex23-RDF-inheritance.md`

전제(현재 구현)
- 이벤트는 `PredicateCode.REVEALS`를 사용하고, 메타는 `event_reveal(event_id, target_type, target_id, reveal_type)`에 저장한다.
- Event V2 응답(EventResponseDTO)은 reveal 메타를 포함할 수 있다. (예: `reveals[]`, 하위호환 `revealTargetType`, `revealTargetId`, `revealType`)
- `event_reveal.target_type`은 스키마상 `CHARACTER|ATTRIBUTE`.
- 현재 Intelligence mock/프롬프트는 `ATTRIBUTE -> target_id=0`을 사용하고 있어(정합성 갭), Option 1 적용 전 수정이 필요하다.
  - 프롬프트: `services/intelligence-service/src/main/resources/prompts/refine-fact.txt`
  - Mock: `services/intelligence-service/src/main/java/com/nospoiler/intelligenceservice/service/OpenAiLlmClient.java`

---

## 1) MVP 정책(Option 1) 요약: ATTRIBUTE도 조인 가능하게 만들기

문제
- 현재 파이프라인에서 `target_type=ATTRIBUTE`는 종종 `target_id=0`으로 내려오는데, 이 값은 **조인/랭킹/필터링에 쓸 수 없다**(전부 동일 값).

Option 1 (MVP 최단거리)
- `target_type=ATTRIBUTE`일 때도 `target_id`는 **0 금지**.
- 대신 `target_id`에 “이 사실이 누구에 대한 것인지”를 나타내는 **aboutCharacterId**를 저장한다.
  - 예: "스카일러가 월터의 범죄 사실을 알아차림" => `target_type=ATTRIBUTE`, `target_id=WalterId`

이 옵션으로 얻는 것(V2.5에서 바로 유효)
- “주체가 X이고, about이 Y인 reveal”을 **정확히 필터**할 수 있다.
- PRECEDES 추천 랭킹에서 “reveal target hit” 같은 신호를 **동일 방식으로 계산**할 수 있다.

이 옵션이 해결하지 못하는 것(= V3로 미룸)
- about이 같아도 "범죄/소속/과거/질병/거짓말" 등 **속성 종류별로 구분**할 수는 없다.
  - MVP에서는 상세 내용은 `summary/refined_summary` 텍스트로만 설명한다.

운영 안전 규칙(권장)
- aboutCharacter를 특정할 수 없는 ATTRIBUTE reveal은 `event_reveal` row를 만들지 않는다(요약 텍스트만 남김).
  - 스키마상 target_id NOT NULL이므로 “0으로 채우기”는 금지.
  - 현실적으로는 Wiki 검증 UI에서 about 캐릭터 선택을 강제하는 방식이 가장 깔끔하다.

---

## 2) V2.5 라우팅 규칙(정답 찾기 / 근거 제시 분리)

### Rule R1: REVEALS는 “정답 찾기”에 직접 쓰지 말고, 가능한 경우 “about 필터”로만 좁혀라
- `REVEALS` 자체는 포괄적이어서 오탐이 날 수 있다.
- MVP에서 “정답 찾기”는 다음 우선순위를 권장:
  1) `DISCOVERS/LEARNS` 같은 인지 변화 predicate
  2) (가능하면) `REVEALS + aboutCharacterId` 필터
  3) (최후) `q` 키워드 검색(요약 텍스트 기반)

### Rule R2: 답변에는 REVEALS를 “근거/설명” 영역으로 붙여라
- 정답 이벤트 E를 찾은 뒤, E의 reveal 메타가 있으면:
  - Identity: `target_type=CHARACTER`이면 “정체 공개(캐릭터)”로 표시
  - Fact: `target_type=ATTRIBUTE`이면 “사실 공개(about=캐릭터)”로 표시
- MVP에서는 ATTRIBUTE의 “무슨 사실인지”는 요약 텍스트로만 표현한다.
- `reveal_type`는 근거 강도(`HINT|CONFIRM`) 표시에만 사용하며, strict 정답 승격/강등 조건으로 사용하지 않는다.

---

## 3) Production Q 라우팅 예시(Option 1 기준)

### Q4. “스카일러가 월터의 범죄 사실을 알아차린 시점?”

입력
- subject = Skyler
- about = Walter
- safeUpToEpisode = K

라우팅(결정론, V2.5로 가능)
1) 후보 생성(정답 이벤트 후보, 우선순위):
   - 1차(인지 변화): `DISCOVERS`, `LEARNS`를 사용해 후보를 넓힌다.
     - api3: `GET /api/event/v2/characters/{SkylerId}/events?safeUpToEpisode=K&predicateCode=DISCOVERS&includeRevealPartner=false`
     - api3: `GET /api/event/v2/characters/{SkylerId}/events?safeUpToEpisode=K&predicateCode=LEARNS&includeRevealPartner=false`
   - 2차(REVEALS): reveal 메타가 있는 후보를 원하면 `predicateCode=REVEALS`도 함께 조회한다(근거/설명용).
2) about 필터(가능한 경우에만 강하게 적용):
   - `revealTargetType in (CHARACTER, ATTRIBUTE)` AND `revealTargetId == WalterId`
3) earliest 1개 선택:
   - `episodeStart ASC, id ASC`로 1개 선택
4) 결과 렌더링:
   - 선택 이벤트 summary + (reveal 메타가 있으면) “about=월터” 배지
5) fallback(데이터가 아직 부족하면):
   - 텍스트(`q`) 기반은 오탐이 커질 수 있으므로 MVP에서는 “결과 없음”을 허용하는 편이 안전

---

## 4) Quick20(Level 질문)에서 Option 1이 커버하는 범위

### #11 “이 사건이 무엇을 드러낸(reveal) 사건인지 설명해줘”
- V2.5:
  - 이벤트가 `predicateCode=REVEALS`이면, EventResponseDTO의 reveal 메타를 그대로 설명 영역에 표시한다.
  - `target_type=ATTRIBUTE`인 경우에도 about 캐릭터가 있으면 “(about=캐릭터) 사실 공개”까지만 구조화하고,
    상세는 summary/refined_summary 텍스트를 그대로 보여준다.
- V3 필요(옵션2):
  - “무엇(범죄/소속/관계/과거…)”까지 분류된 답이 필요해지면 `target_key/target_text`가 필요.

### #18 “‘정체가 밝혀지는’ 유형의 사건들만 모아서 나열해줘”
- V2.5에서 충분:
  - api4: `GET /api/event/v2/dramas/{dramaId}/events?predicateCode=REVEALS&safeUpToEpisode=K&limit=N`
  - 결과 중 `revealTargetType=CHARACTER`인 것만 필터링해서 나열
- V3는 선택:
  - `reveal_type=HINT/CONFIRM`으로 강도 기준 정렬/필터를 하려면, 파이프라인에서 revealType을 채워야 한다.

---

## 5) V3에서 Option 2가 “필요해지는” 질문들(구체)

Option 2 = `target_key`(또는 object 1급 엔티티화)

### 필요해지는 대표 케이스
- Production Q4 같은 질문에서 “범죄 사실”만 골라내고 싶을 때
  - about=월터 reveal은 많을 수 있으므로, `target_key=CRIME_FACT` 같은 분리가 필요
- Production Q2 “첫 암페타민 제조?”처럼 “물질/아이템/오브젝트”가 정답 정의에 들어갈 때
  - MVP는 `q`로 근사하지만, 정확도를 올리려면 object를 구조화할 필요가 커진다
- Quick20 #11 “무엇을 드러냈나”를 “구조화된 타입”으로 대답해야 할 때
  - ATTRIBUTE의 종류/관계/조직/아이템 등을 텍스트 설명이 아니라 필터 가능한 데이터로 만들려면 key/엔티티가 필요

### V3 최소 확장안(권장)
- `event_reveal`에 `target_key`(코드) 추가:
  - 예: `CRIME_FACT`, `AFFILIATION`, `SECRET_PAST`, `RELATIONSHIP`, `ALIAS_IDENTITY` 등
- 필요 시 `target_text`(짧은 문자열) 추가:
  - 예: `"Heisenberg"`, `"DEA"` 같은 표면 텍스트

### V3 정석 확장안(비용 큼)
- `object/attribute`를 1급 엔티티로 만들고, `event_object` 같은 조인 테이블을 도입
- 장점: Q2/Q4/Quick20#11 같은 질문에서 “정답 정의가 object에 걸리는 경우” 정확도가 크게 상승
- 단점: 위키 작성 규칙/인텔리전스 프롬프트/검증 UI/백필/마이그레이션이 연쇄 변경된다

---

## 6) 결론(로드맵)

- V2.5(MVP)에서 해야 하는 것:
  - **Option 1**: `ATTRIBUTE target_id = aboutCharacterId` (0 금지) 정책 확정 + 파이프라인 반영
  - Q4/Quick20#11에서 REVEALS는 “about 필터 + 설명” 중심으로 사용
- V3에서 할 것:
  - “무슨 사실인지”가 정답/필터에 직접 필요해지는 질문들(Q2, Q4, Quick20#11 등)을 위해
    `target_key` 또는 object 1급 엔티티화를 도입

---

## 6.1) Production Q15 / Quick20과 Option1/2 정합성 체크(요약)

원칙
- V2.5(=지금 스키마/파이프라인 유지)에서 **정답 찾기**는 `PredicateCode`/그룹/키워드(q) 중심.
- `REVEALS`/`event_reveal`은 (메타가 있을 때) **근거/설명 + about 필터**로만 보조한다.

매핑(핵심만)
- Production Q4(“누가 누구의 범죄 사실을 알아차림”): Option1이 있으면 about 필터로 후보를 좁힐 수 있어 유효.
- Production Q2(“첫 암페타민 제조”): Option2(object/target_key)는 **정확도 개선용**. MVP는 `q`로 근사.
- Quick20 #11(“무엇을 드러냈나”): Option1로 “about=캐릭터”는 구조화 가능. “무슨 사실인지”는 Option2가 있어야 타입별 답이 가능.
- Quick20 #18(“정체 reveal 이벤트만 나열”): Option1과 무관(CHARACTER reveal). 단, 현재 DTO가 대표 1건만 노출하므로 “대표 reveal 우선순위(CHARACTER 우선)”이 필요.

---

## 7) 실행 계획(Option 1, V2.5)

목표
- `target_type=ATTRIBUTE`도 “about 캐릭터” 단위로 조인/랭킹/필터가 가능하도록 만든다.
- MVP 범위에서는 속성(object) 1급 엔티티화는 하지 않는다.

### 7.1 정책 확정(문서/규칙)
1) 0 금지
- `target_type=ATTRIBUTE`일 때 `target_id=0`을 금지한다.
- 의미: `target_id`는 “이 사실이 누구에 대한 것인지(aboutCharacterId)”를 뜻한다.

2) about 캐릭터는 involved에도 포함
- `event_reveal.target_id`(about) 캐릭터는 해당 이벤트의 `event_character`에도 포함하는 것을 원칙으로 한다.
- 이유: V2.5에서 조인/랭킹 신호는 `event_character`를 기반으로 계산하는 것이 비용/일관성 측면에서 가장 단순하다.

3) 다중 reveal row 정책(최종, BP7)
- 스키마는 `(event_id, target_type, target_id)` 복수 row를 허용한다.
- 조회/필터/근거 계산은 `reveals[]` 리스트를 우선 사용한다.
- 단건 레거시 필드는 하위호환 읽기용으로만 유지한다.
- 렌더링 규칙:
  - WHY 영역은 `reveals[]`를 최대 5건 노출(`event_id | reveal_type | target_type | target_key | target_id`)
  - 카드 요약에는 대표 1건(CHARACTER 우선)만 보조 배지로 노출 가능

정합성 메모(현재 코드 기준)
- `first wins` 단건 의존은 회귀로 간주한다.

### 7.2 파이프라인 반영(구현)
0) (BLOCKER) 프롬프트/Mock 정합성 수정
- `services/intelligence-service/src/main/resources/prompts/refine-fact.txt`
  - 기존: ATTRIBUTE는 `revealTargetId=0`
  - 변경: ATTRIBUTE는 `revealTargetId=aboutCharacterId` (0 금지)
- `services/intelligence-service/src/main/java/com/nospoiler/intelligenceservice/service/OpenAiLlmClient.java`
  - 기존: ATTRIBUTE는 `revealTargetId = 0L` 하드코딩
  - 변경: about 캐릭터를 추정해 캐릭터 ID를 내려주거나, 최소한 null로 두고 Wiki 검증 UI에서 강제 입력하도록 한다.

1) (BLOCKER) event-service 방어벽 추가
- `services/event-service/src/main/java/com/nospoiler/eventservice/service/EventServiceImpl.java`
  - createEvent에서 `predicateCode=REVEALS`이고 `revealTargetType=ATTRIBUTE`인 경우 `revealTargetId==0`을 거부(예외)한다.
  - 이유: DB 레벨에서 0은 합법이라 앱 레벨에서 강제하지 않으면 계속 데이터가 오염된다.

2) Intelligence 단계(추천값)
- refine 결과에서 `target_type=ATTRIBUTE`일 때도 “about 캐릭터” 후보를 제안할 수는 있다.
- 단, LLM 추정은 오탐 가능성이 있으므로 최종 결정은 Wiki 검증 UI가 가져간다(강제 입력).

2) Wiki 검증 UI(강제 지점, 권장)
- `predicateCode=REVEALS`일 때:
  - `target_type` 선택(CHARACTER/ATTRIBUTE)
  - `target_id(about/identity)` 선택 강제(0 불가)
  - (선택) `reveal_type(HINT/CONFIRM)` 입력은 당장은 null 허용
  - `reveal_type`를 입력하는 경우 최소 1개 근거 앵커(`evidence_event`)를 문서 레이어(answerset/question-map)에 함께 남긴다.
- `target_type=ATTRIBUTE`의 `target_id`는 “about 캐릭터”로 라벨링해 혼동을 줄인다.

3) Wiki publish -> event-service
- publish 시 `event_reveal` 저장이 end-to-end로 반영되도록:
  - `ATTRIBUTE`도 `target_id`가 캐릭터 ID로 내려가야 한다.
- 기존 “0으로 내려오는 케이스”는 publish 단계에서 hard-fail(권장) 또는 reveal drop(차선) 중 택1 필요.

### 7.3 기존 데이터 전환(선택)
현실적으로 `target_id=0` 데이터가 이미 존재할 수 있으므로 전환 정책을 고정해야 한다.
- A안(보수, 추천): `target_id=0`인 ATTRIBUTE reveal은 랭킹/필터에 사용하지 않고, 텍스트 설명으로만 남긴다.
- B안(백필): 운영자가 about 캐릭터를 지정해 backfill한다(오탐 방지를 위해 자동 백필은 비추).
- C안(정리): `target_id=0` row는 제거하고, 필요하면 이벤트 summary에만 남긴다.

### 7.4 검증(AC)
- Q4 라우팅에서:
  - `subject`(인지자) 이벤트 타임라인에서 REVEALS 후보를 찾고,
  - reveal about 필터(`target_id == aboutCharacterId`)가 안정적으로 동작해야 한다.
- PRECEDES suggestion 랭킹에서:
  - reveal target hit 신호가 계산 가능해야 한다(about 캐릭터가 involved에 포함되어 있다는 전제).

---

## 8) 재귀적 실행 플랜(Option1 데이터 보강 루프)

목표
- “0 금지 + about 캐릭터 강제 + 대표 reveal 선택 규칙”을 먼저 안정화하고,
- 소수 드라마(예: dramaId=10)에서 데이터 보강을 반복하면서 규칙/가이드를 튜닝한다.

Loop(반복)
1) Guardrail 반영(코드/프롬프트)
   - (필수) `ATTRIBUTE target_id=0` 생성 경로를 제거(프롬프트/Mock)
   - (필수) `event-service createEvent`에서 `revealTargetId<=0` 거부 + (가능하면) about은 involved에 포함 강제
   - (필수) “대표 reveal” 노출은 CHARACTER 우선으로 정렬(단일 reveal DTO의 안정성)
2) Data 보강(운영/QA)
   - REVEALS 이벤트는 “1 event = 1 reveal row”를 임시 규칙으로 적용(대표 reveal 흔들림 방지)
   - ATTRIBUTE는 about 캐릭터가 확정될 때만 저장(모르면 omit)
3) 검증(질문 라우팅)
   - Production Q4 / Quick20 #11/#18 템플릿으로 smoke test
   - PRECEDES suggestion에서 revealBoost가 “연관 후보를 위로 올리는지” 확인
4) Gap 수집 -> 규칙 수정
   - about 누락 케이스: 위키 검증 UI에서 강제할지 / publish hard-fail할지 결정
   - “무슨 사실인지”가 필요해지는 질문이 늘면 Option2(V3)로 승격
5) 다시 1)로 회귀

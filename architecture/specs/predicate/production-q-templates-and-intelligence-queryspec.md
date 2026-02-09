# Production Q Templates + Intelligence QuerySpec (Plan)

기준 날짜: 2026-02-09

목표
- Production 질문(Q1~Q15)을 “프리셋 템플릿”으로 빠르게 실행한다.
- 동시에 자유 질문(자연어)은 intelligence-service가 **존재하는 API로만 실행 가능한 QuerySpec**을 생성하게 한다.
- `PredicateCode` 폐쇄집합은 유지하고, 텍스트 대상(object)이 필요한 경우는 `q`(keyword) 필터로 근사한다.

전제(현재 구현 상태)
- `api3`(character events)에 `q` 키워드 필터가 추가되어 `summary`/`predicate_suggestion` 검색이 가능하다.
  - `GET /api/event/v2/characters/{characterId}/events?safeUpToEpisode=K&q=...&predicateCode=...&limit=N`
- Production Q1~Q15 프리셋 실행 레이어는 아직 없다(문서/플랜만 존재).

관련 문서
- Production 질문 원문: `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex16-production-Q15s.md`
- Q1~Q15 라우팅(시범용): `fivecircles/architecture/specs/predicate/ex16-q1-q15-구현-라우팅-시범용.md`
- 구현 현황: `fivecircles/architecture/specs/predicate/ex16-production-q1-q15-implementation-status.md`
- Event V2 API: `fivecircles/architecture/specs/event-v2-api.md`

---

## A. 프리셋 템플릿(Deterministic)

의도
- Production 질문은 “정답 형태”가 비교적 고정이라, LLM 라우팅을 끼우면 오히려 흔들린다.
- 그래서 Q1~Q15는 템플릿(프리셋)으로 고정하고, 필요한 경우에만 `q`로 텍스트 매칭을 사용한다.

템플릿 최소 스키마(초안)
```ts
type QueryOp =
  | { kind: "CHARACTER_EVENTS"; subjectCharacterId: number; safeUpToEpisode: number; predicateCode?: string; q?: string; limit?: number }
  | { kind: "COEVENTS"; aCharacterId: number; bCharacterId: number; safeUpToEpisode: number; limit?: number }
  | { kind: "CAUSES"; eventIdFromPrev: true; safeUpToEpisode: number; depth?: number }
  | { kind: "EFFECTS"; eventIdFromPrev: true; safeUpToEpisode: number; depth?: number };

type ProductionQuestionTemplate = {
  id: "Q1" | "Q2" | "Q3" | string;
  title: string;
  // “first/earliest”는 별도 predicate가 아니라 실행 전략(earliest + limit=1)
  pick: "EARLIEST" | "LATEST";
  ops: QueryOp[];
};
```

실행 규칙(초안)
- `ops[0]` 실행 결과가 “이벤트 리스트”면 `pick` 기준으로 1개를 선택한다(earliest/largest).
- `CAUSES/EFFECTS`는 직전 선택 이벤트의 `eventId`를 입력으로 사용한다.
- 결과는 `primaryEvent + (optional) explanationEvents[]` 형태로 렌더링한다.

예시(초안)
- Q1 “월터의 첫 살인”
  - `CHARACTER_EVENTS(subject=Walter, predicateCode=KILLS, limit=50)` -> pick EARLIEST -> (옵션) `CAUSES(depth=1)`
- Q2 “첫 암페타민 제조”
  - `CHARACTER_EVENTS(subject=Walter, q="암페타민", limit=200)` -> pick EARLIEST
  - 주의: “암페타민”이 summary에 안 들어가면 실패. 이 경우 `q` 키워드 세트(동의어) 또는 데이터 보강이 필요.
- Q3 “투코를 처음 만남”
  - `COEVENTS(a=Walter, b=Tuco, limit=200)` -> pick EARLIEST
  - 강화: 결과 이벤트 중 `predicateCode=MEETS`가 있으면 그걸 우선 선택(없으면 earliest coevent 근사).

FE 배치(추천)
- `/qa` 또는 별도 “Production Q” 섹션에 템플릿 목록을 노출.
- “드라마 10(브베)”부터 시작하고, 점진적으로 다른 드라마로 확장.

---

## B. Intelligence QuerySpec(LLM-assisted, Guardrailed)

의도
- 자유 질문은 object가 텍스트(“암페타민”, “돈의 흐름”)인 경우가 많아서 `q`가 필요하다.
- LLM은 “질문에서 필요한 subject/object 키워드 추출 + 어떤 API 조합이 필요한지”는 잘하지만,
  - 임의 predicate 생성/환각 위험이 있으므로, 반드시 **허용된 API/필드만** 만들게 해야 한다.

권장 책임 분리
- intelligence-service: 자연어 → QuerySpec(JSON) **생성만** (실제 API 호출/실행은 하지 않음)
- executor(FE 또는 qa-service): QuerySpec 검증 후 event-service API 호출

계약(초안)
- `POST /api/intelligence/v1/queryspec`
  - Request: `{ dramaId, safeUpToEpisode, queryText }`
  - Response: `{ specVersion, confidence, querySpec }`

QuerySpec 최소 스키마(초안)
```json
{
  "intent": "FIND_EVENT",
  "subject": { "characterName": "Walter White" },
  "object": { "characterName": "Tuco" },
  "predicateCodes": ["MEETS"],
  "q": null,
  "pick": "EARLIEST",
  "explain": { "causesDepth": 1 }
}
```

가드레일(필수)
- predicate는 `common/PredicateCode` 값만 허용(unknown이면 reject).
- QuerySpec이 요구하는 실행 연산은 allow-list(api3/api4/api7/api8 등)로 제한.
- `q`는 길이 제한 + 금칙어/제어문자 제거(로그/SQL 안전).
- 실패 시 fallback:
  - (1) 템플릿에 매칭되면 템플릿 실행
  - (2) 아니면 api1(드라마 events) `q` 검색으로만 보수적으로 실행

---

## Implementation Plan (Phased)

1) Template MVP (브베 dramaId=10)
- FE에 `ProductionQuestionTemplate[]` 추가 + 실행기 구현
- 최소 Q1/Q2/Q3만 먼저 제공(폐쇄집합 + q 검색)
- 실행 결과 화면에 “사용한 파라미터(ops)”를 같이 표시(디버그/운영용)

2) QuerySpec executor 공용화
- FE 내부에서 ops 실행 로직을 모듈로 분리(템플릿/LLM 공용)
- QuerySpec 검증(allow-list + predicate enum) 로직 추가

3) Intelligence QuerySpec endpoint (opt-in)
- intelligence-service에 `/queryspec` 추가(생성-only)
- api-contract 문서에 계약 반영: `fivecircles/architecture/specs/api-contract.md`

4) 운영/품질(후순위)
- 템플릿 Q2 같은 “키워드 기반”은 동의어 세트/정규화 규칙이 필요(데이터 보강 포함).
- QuerySpec 로깅/샘플링으로 “자주 실패하는 질문”을 수집해 템플릿/그룹 후보로 승격.

---

## FE MVP Implementation Plan (Concrete)

목표
- dramaId=10(브베)에서 Q1/Q2/Q3를 “프리셋 버튼”으로 실행 가능하게 한다.
- 백엔드 추가 변경 없이 진행하되, 정확도를 깨는 **Known Risk**가 확인되면 (아래) BE 옵션을 켠다.

대상 파일(예시)
- `front/features/qa/QaPage.tsx`: Production Q 섹션 UI 추가(드롭다운 + 실행 버튼 + 결과 패널)
- `front/common/productionQ/templates.ts`: `ProductionQuestionTemplate` 타입 + 템플릿 레지스트리
- `front/common/productionQ/executor.ts`: ops 실행기(api3/api4/api7/api8 호출 + pick 로직)
- `front/common/productionQ/characterResolver.ts`: `CharacterRef(name/aliases)` -> id 해석(드라마 캐릭터 리스트 기반)

설계 원칙
- 템플릿은 **ID를 하드코딩하지 않고** `CharacterRef{name, aliases[]}`로 정의한다.
  - 이유: 동일 드라마라도 환경(DB seed)에 따라 characterId가 달라질 수 있음.
- 텍스트 오브젝트는 `qAnyOf: string[]`로 정의하고, executor가 여러 번 호출해 합쳐서 earliest를 고른다.
  - 이유: 서버는 `q` 1개만 지원(단일 LIKE). 동의어는 executor가 OR로 처리.
- 결과는 최소 형태로:
  - `primaryEvent` 1개(earliest)
  - `explanations[]` (옵션: causes depth=1)
  - `debug.executedOps[]` (운영/디버그)

템플릿 초안(브베)
- Q1: subject=월터, predicate=KILLS, pick=EARLIEST, explain=causes depth=1 (옵션)
- Q2: subject=월터, qAnyOf=["암페타민","메스","meth","cook"], pick=EARLIEST
- Q3: coevents(월터, 투코), pick=EARLIEST (강화: predicate=MEETS가 있으면 우선)

수동 QA(최소)
1. 로컬에서 FE `/qa` 진입, 드라마=브베 선택 후 Production Q 실행.
2. 네트워크 탭에서 호출 확인:
   - Q1: `/characters/{id}/events?...predicateCode=KILLS`
   - Q2: `/characters/{id}/events?...q=암페타민` (여러 키워드면 여러 호출)
   - Q3: `/characters/{a}/coevents?with={b}`
3. 결과 카드에 `eventId/episodeStart~End/summary` 표시 확인.

Known Risk (Hole)
- 현재 `api3`(getEventsByCharacter)는 REVEALS 파트너 캐릭터의 이벤트를 합치는 로직이 있어,
  "subject=월터" 조회 결과가 **월터 단독 타임라인이 아닐 수 있음**.
  - 영향: "첫 살인" 같은 “first” 템플릿이 partner 이벤트로 오염될 수 있음.
  - 대응(우선순위 순):
    1) (FE-only) `strictSubject=true` 옵션을 두고, candidate 상위 N개 이벤트에 대해 `api5(event characters)`로 subject 포함 여부를 필터(호출 비용 증가).
    2) (BE) `includeRevealPartner=false` 같은 파라미터를 api3에 추가해 partner merge를 끄는 모드 제공(기본값은 기존 동작 유지).


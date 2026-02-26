# Production Q Templates + Intelligence QuerySpec (Guidelines)

기준 날짜: 2026-02-13

목표
- Production 질문(Q1~Q15)을 “프리셋 템플릿”으로 빠르게 실행한다.
- 동시에 자유 질문(자연어)은 intelligence-service가 **존재하는 API로만 실행 가능한 QuerySpec**을 생성하게 한다.
- `PredicateCode` 폐쇄집합은 유지하고, 텍스트 대상(object)이 필요한 경우는 `q`(keyword) 필터로 근사한다.

전제(현재 구현 상태)
- `api3`(character events)에 `q` 키워드 필터가 추가되어 `summary`/`predicate_suggestion` 검색이 가능하다.
  - `GET /api/event/v2/characters/{characterId}/events?safeUpToEpisode=K&q=...&predicateCode=...&limit=N`
- `api3`는 `includeRevealPartner` 파라미터로 “subject 단독 타임라인”을 강제할 수 있다(템플릿은 false 권장).
  - `.../events?...&includeRevealPartner=false`
- `api4`(coevents)는 `limit` optional 파라미터를 지원한다.
  - `GET /api/event/v2/characters/{aId}/coevents?with={bId}&safeUpToEpisode=K&limit=N`
- `api7/api8` 성격(원인/결과 맥락)은 PRECEDES 기반으로 제공된다.
  - `GET /api/event/v2/events/{eventId}/causes?depth=D&safeUpToEpisode=K`
  - `GET /api/event/v2/events/{eventId}/effects?depth=D&safeUpToEpisode=K`
- 프리셋 템플릿 실행 레이어(MVP)는 FE에 존재한다.
  - `front/common/productionQ/templates.ts`
  - `front/common/productionQ/executor.ts`
  - `front/features/qa/components/ProductionQSection.tsx`
- Anti-halu의 “0건 판정”을 위해 probe endpoint가 존재한다.
  - `POST /api/event/v2/probe`
  - 관련 원칙: `fivecircles/architecture/specs/questions-anti-halus/03-implementation-plan.md`

관련 문서
- Production 질문 원문: `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex16-production-Q15s.md`
- Q1~Q15 라우팅(시범용): `fivecircles/architecture/specs/predicate/ex16-q1-q15-구현-라우팅-시범용.md`
- 구현 현황: `fivecircles/architecture/specs/predicate/ex16-production-q1-q15-implementation-status.md`
- Event V2 API: `fivecircles/architecture/specs/event-v2-api.md`
- Strict/Probe 기준표: `fivecircles/architecture/specs/questions-anti-halus/04-template-strict-must-matrix.md`

---

## A. 프리셋 템플릿(Deterministic)

의도
- Production 질문은 “정답 형태”가 비교적 고정이라, LLM 라우팅을 끼우면 오히려 흔들린다.
- 그래서 Q1~Q15는 템플릿(프리셋)으로 고정하고, 필요한 경우에만 `q`로 텍스트 매칭을 사용한다.

템플릿 최소 스키마(초안)
```ts
type CharacterRef = { name: string; aliases?: string[] };

type ProbeStrictFilters = {
  dramaId?: number;
  subjectCharacterId?: number;
  withCharacterIds?: number[];
  aboutCharacterId?: number;
  targetCharacterId?: number;
  predicateCodeAnyOf?: string[];
  excludePredicateCodeAnyOf?: string[];
  qAnyOf?: string[];
};

type QueryOp =
  // Answer ops (Strict)
  | { kind: "CHARACTER_PREDICATE_EARLIEST"; subjectCharacterRef: CharacterRef; predicateCodeAnyOf?: string[]; qAnyOf?: string[]; excludePredicateCodeAnyOf?: string[] }
  | { kind: "CHARACTER_KEYWORD_EARLIEST"; subjectCharacterRef: CharacterRef; qAnyOf: string[]; predicateCodeAnyOf?: string[]; excludePredicateCodeAnyOf?: string[] }
  | { kind: "COEVENTS_EARLIEST"; aCharacterRef: CharacterRef; bCharacterRef: CharacterRef; predicateCodeAnyOf?: string[]; qAnyOf?: string[]; preferPredicateCodeAnyOf?: string[] }
  // Answerability gate (Probe)
  | { kind: "PROBE"; queryKind: "character_predicate_earliest" | "character_keyword_earliest" | "coevents_earliest"; strictFilters: ProbeStrictFilters }
  // Context ops (Explanation only)
  | { kind: "CAUSES"; eventIdFromPrev: true; depth: number }
  | { kind: "EFFECTS"; eventIdFromPrev: true; depth: number }
  // Ordering helper (Explanation only)
  | { kind: "PRECEDES_EDGES_BETWEEN"; eventIdsFromContext: true };

type ProductionQuestionTemplate = {
  // Template registry id (stable; not the same as question_id)
  id: string;
  // Q1~Q15 question id (for docs alignment)
  question_id: string;
  title: string;
  question_text: string;
  dramaId: number;
  expectedMinEpisode?: number;

  // “first/earliest”는 별도 predicate가 아니라 실행 전략(earliest + limit=1).
  // Deterministic: episodeStart ASC, then id ASC.
  pick: "EARLIEST" | "LATEST";

  // Strict answer query spec (MUST) + optional approx candidates (NOT for answering)
  strict: QueryOp;
  approxCandidates?: QueryOp[];

  // Answerability/0-result gate
  probe: QueryOp;

  // Context timeline (optional, explanation)
  context?: {
    causesDepth?: number;
    effectsDepth?: number;
  };
};
```

실행 규칙(가이드라인)
- 캐릭터 ref는 `CharacterRef(name, aliases[])`로 정의하고, 런타임에 “드라마 캐릭터 목록”에서 resolve한다.
  - resolve가 모호하면 실행을 중단하고(운영 UI라면) 후보를 노출해 수동 선택을 받는다.
- Strict Answer Query는 반드시 템플릿의 `strict`만 사용한다(정답 확정용).
  - Strict가 0건이면 `ANSWERED` 금지(Approx 후보가 있어도 정답 라벨링 금지).
  - 0건일 때만 `probe`를 호출해 `SPOILER_BLOCKED / NOT_ENOUGH_DATA`를 판정한다.
- “earliest” 결정 규칙(Deterministic)
  - 정렬: `episodeStart ASC`, tie-break: `id ASC`
  - “latest”는 `episodeEnd DESC`, tie-break: `id DESC`를 권장(필요 시)
- coevents에서 `MEETS` 우선 규칙
  - `preferPredicateCodeAnyOf`가 존재하면, strict 후보 중 해당 predicate를 우선 pick한다.
  - 없으면 strict 후보 전체에서 earliest를 pick한다.
- 이벤트 `summary` 문장 규칙
  - 사용자 노출용 문장은 캐릭터 시점의 자연어로 작성한다.
  - 내부 태그/개발용 토큰(`SUSPICION_SIGNAL_*`, `*_TRIGGER` 등)은 `summary`에 넣지 않는다.
  - 검색 안정성은 `predicate_suggestion`에 별칭/토큰을 보강해 분리 보장한다.
- causes/effects 체이닝(설명용)
  - selected event가 있으면, **causes/effects를 둘 다** depth로 조회한다(양방향 기본).
  - 단방향 조회는 예외 케이스(명시적 UX 요구, 비용 제약)에서만 허용한다.
  - **주의: causes/effects의 결과는 “집합”에 가까워 shortcut edge가 있으면 렌더 순서가 흔들릴 수 있다.**
    - 예: `a->b`, `b->c`, `a->c`가 함께 있을 때 단순 episode 정렬은 `a,c,b` 같은 순서를 만들 수 있다.
  - 순차 타임라인(= `a,b,c,d`)을 보장하려면 “관계(edge)”를 함께 가져와 위상 정렬해야 한다.
    - FE는 context에 포함된 eventIds로 `PRECEDES edge between`을 조회한 뒤(아래 API),
      Kahn topological sort + tie-break(episode/id)로 안정적으로 정렬한다.
    - edge 정보가 부족하면(= DB에 `b->c` 같은 연결이 없으면) 위상정렬도 순서를 강제할 수 없다.

예시(초안)
- Q1 “월터의 첫 살인”
  - strict: `{ kind:"CHARACTER_PREDICATE_EARLIEST", subjectCharacterRef: Walter, predicateCodeAnyOf:["KILLS"] }`
  - pick: `EARLIEST`
  - context: causesDepth=1 (옵션)
- Q2 “첫 암페타민 제조”
  - strict: `{ kind:"CHARACTER_KEYWORD_EARLIEST", subjectCharacterRef: Walter, qAnyOf:["암페타민","메스","meth",...] }`
  - pick: `EARLIEST`
  - 주의: 키워드가 summary/suggestion에 실제로 존재해야 한다. 없으면 데이터 보강 또는 동의어 세트 확장이 필요.
- Q3 “투코를 처음 만남”
  - strict: `{ kind:"COEVENTS_EARLIEST", aCharacterRef: Walter, bCharacterRef: Tuco, predicateCodeAnyOf:["MEETS"], preferPredicateCodeAnyOf:["MEETS"] }`
  - pick: `EARLIEST`
  - (Approx 후보는 별도 op로만 둔다: 정답 확정 금지)

FE 배치(추천)
- `/qa` 또는 별도 “Production Q” 섹션에 템플릿 목록을 노출.
- “드라마 10(브베)”부터 시작하고, 점진적으로 다른 드라마로 확장.

템플릿/정답 운영 워크플로우(중요)
- 1) 정답을 먼저 고정한다.
  - `fivecircles/architecture/specs/questions-anti-halus/06-answers-for-productionQs.md`에 “정답 앵커”를 확정.
- 2) 정답 조회용 템플릿을 만든다(Strict MUST).
  - `fivecircles/architecture/specs/questions-anti-halus/04-template-strict-must-matrix.md` 기준으로 strict 필터를 고정.
  - `evidence_event_id`를 채운다(Strict + earliest + 정답 앵커 검증).
- 3) 답변의 “맥락 체인”을 PRECEDES로 연결한다(event_relation).
  - 정답 문서에서 설명한 선후관계(= 원인/결과)를 `event_relation(type=PRECEDES)`로 주입한다.
  - 이벤트가 없으면 먼저 생성해서 넣는다(event + event_character + status=APPROVED).
  - 이후 PRECEDES를 주입한다.
- 4) 검증한다.
  - Strict 결과 event id가 `evidence_event_id`와 동일해야 한다.
  - Context timeline(causes/effects)에서 chain이 의도대로 따라오는지 확인한다.

확장 질문 작성 파이프라인(운영 표준)
- 1) 질문 정의
  - 질문 의도(무엇을 earliest/latest로 찾는지)와 노출 정책을 먼저 고정한다.
- 2) 정답/맥락 도미노 작성
  - 웹 검증(공식/신뢰 가능한 출처) 포함으로 사건 도미노를 작성하고, 출처 링크를 남긴다.
- 3) 앵커 이벤트 확정
  - `evidence_event_id`를 strict + earliest 기준으로 확정한다.
- 4) 실행 설계 결정
  - 템플릿 기반 실행인지, RDF/SPARQL 보조 실행인지(또는 병행) 결정한다.
- 5) 데이터 반영
  - `event`, `event_character`, `event_relation(PRECEDES)`를 idempotent하게 반영한다.
  - `event.summary`는 사용자 문장으로 작성한다(캐릭터 시점, 개발용 토큰 금지).
- 6) 질문/답변 구현
  - UI/응답에서 컨텍스트는 기본적으로 양방향(`causes+effects`)으로 붙인다.
- 7) 검증
  - Strict 결과=앵커, Probe 분기, K gate, 체인 순서를 점검한다.
- 8) 문서 동기화
  - anti-halu 문서, 템플릿 가이드, 운영 스크립트/검증 SQL을 함께 갱신한다.

핵심 고정 원칙(반드시 유지)
- `strict-first`: strict 0건일 때만 probe로 상태 판정한다.
- `K gate`: `safeUpToEpisode`는 절대회차 기준으로 강제한다.
- `bidirectional context`: 컨텍스트는 기본 양방향(원인+결과)으로 조회한다.

PRECEDES edge 조회(정렬 메타)
- causes/effects 결과를 “순차 타임라인”으로 표시하려면 edge가 필요하다.
- 이를 위해 eventIds 집합 내의 PRECEDES만 반환하는 endpoint를 사용한다.
  - `POST /api/event/v2/relations/precedes/between`
  - Request: `{ eventIds: number[], safeUpToEpisode?: number }`
  - Response: `{ fromEventId, toEventId, type }[]` (type=PRECEDES)

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

현황(2026-02-13)
- FE 템플릿 실행기/템플릿 레지스트리/QA UI는 구현되어 있다.
  - `front/common/productionQ/templates.ts`
  - `front/common/productionQ/executor.ts`
  - `front/features/qa/components/ProductionQSection.tsx`
- Strict 0건 판정은 probe로 분기한다.
  - `POST /api/event/v2/probe`
- Context timeline의 “순차 타임라인” 표시를 위해 PRECEDES edge 조회 + 위상정렬을 사용한다.
  - `POST /api/event/v2/relations/precedes/between`
  - (edge가 없으면 순차 보장은 불가능하므로, 운영으로 PRECEDES를 채워야 한다)

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

## FE Implementation Notes (Concrete)

목표
- Production Q 템플릿은 “정답 조회(Strict)”를 deterministic하게 실행하고, 0건일 때는 probe로 상태만 판정한다.
- Context timeline은 PRECEDES 기반으로 제공하되, shortcut edge가 있어도 순차 타임라인이 깨지지 않게 edge 기반 위상정렬로 정렬한다.

대상 파일(예시)
- `front/features/qa/components/ProductionQSection.tsx`: 템플릿 목록 + 실행 버튼 + 결과/맥락 패널
- `front/common/productionQ/templates.ts`: 템플릿 레지스트리(드라마별 Q1~Q15 등)
- `front/common/productionQ/executor.ts`: ops 실행기(api3/api4/api7/api8 호출 + pick 로직)
- `front/common/productionQ/characterResolver.ts`: `CharacterRef(name/aliases)` -> id 해석(드라마 캐릭터 리스트 기반)
- `front/common/services/eventV2Api.ts`: event-service API 클라이언트(`/probe`, `/relations/precedes/between` 포함)

설계 원칙
- 템플릿은 **ID를 하드코딩하지 않고** `CharacterRef{name, aliases[]}`로 정의한다.
  - 이유: 동일 드라마라도 환경(DB seed)에 따라 characterId가 달라질 수 있음.
  - 주의: 현재 character-service 스키마에는 `aliases` 필드가 없으므로, aliases는 "템플릿 데이터(하드코딩)"로만 유지한다(MVP).
- 텍스트 오브젝트는 `qAnyOf: string[]`로 정의하고, executor가 여러 번 호출해 합쳐서 earliest를 고른다.
  - 이유: 서버는 `q` 1개만 지원(단일 LIKE). 동의어는 executor가 OR로 처리.
- 결과는 최소 형태로:
  - `primaryEvent` 1개(earliest)
  - `explanations[]` (옵션: causes depth=1)
  - `debug.executedOps[]` (운영/디버그)

Context timeline 정렬(중요)
- causes/effects endpoint가 주는 결과는 “집합”이라 shortcut PRECEDES가 있으면 순서가 흔들릴 수 있다.
- 따라서 UI는 context eventIds를 모아 `/relations/precedes/between`으로 edge를 받은 뒤,
  edge 기반 위상정렬(Kahn) + tie-break(episode/id)로 표시 순서를 고정한다.

Context 기본 정책(운영 가이드)
- 템플릿 실행에서 selected event가 존재하면 기본적으로 아래 두 API를 모두 호출한다.
  - `GET /api/event/v2/events/{eventId}/causes?depth=D&safeUpToEpisode=K`
  - `GET /api/event/v2/events/{eventId}/effects?depth=D&safeUpToEpisode=K`
- 기본 depth 권장값:
  - 일반 템플릿: `2`
  - 직접 전후관계만 필요한 템플릿: `1`
  - 긴 도미노 체인(Q12 계열): `5`까지 허용
- 화면 라벨이 "원인 질문" 또는 "결과 질문"이어도, 맥락 보강 목적이면 양방향 컨텍스트를 유지한다.

템플릿 초안(브베)
- Q1: subject=월터, predicate=KILLS, pick=EARLIEST, explain=causes depth=1 (옵션)
- Q2: subject=월터, qAnyOf=["암페타민","메스","meth","cook"], pick=EARLIEST
- Q3: coevents(월터, 투코), pick=EARLIEST (강화: predicate=MEETS가 있으면 우선)

템플릿 fallback(권장)
목표
- 0건/애매함을 “한 번에 해결”하려고 하면 오답이 생긴다.
- 그래서 템플릿은 **정답 확정(Strict)** 과 **후보 탐색(Approx)** 를 분리한다.

Fallback Ladder (템플릿 가이드라인)
- 1차: predicateCode 기반(Strict MUST)
  - 질문 의미가 predicate로 고정되는 유형(Q1 kills, Q4 discovers 등)은 `predicateCodeAnyOf`를 우선으로 둔다.
- 2차: group/fallback(Strict MUST의 “구체화된 union”)
  - “단일 predicate로는 부족하지만 의미가 고정되는” 질문은 group을 정의해서 `predicateCodeAnyOf`로 확장한다.
  - group은 런타임이 아니라 **템플릿 데이터(운영)** 로 관리한다(LLM이 임의로 생성 금지).
- 3차: q 키워드(Approx candidates only)
  - 텍스트 기반은 drift 위험이 커서, strict 0건이면 probe로 상태만 판정하고,
    q 기반 결과는 “후보”로만 제시한다(정답 라벨링 금지).

coevents에서 MEETS 우선(강화 규칙)
- strict가 coevents 전체라면 “첫 만남” 류 질문에서 오답이 생길 수 있다.
- 따라서 `preferPredicateCodeAnyOf=[MEETS]`를 두고, 있으면 그 안에서 earliest를 pick한다.

수동 QA(최소)
1. 로컬에서 FE `/qa` 진입, 드라마=브베 선택 후 Production Q 실행.
2. 네트워크 탭에서 호출 확인:
   - Q1: `/characters/{id}/events?...predicateCode=KILLS&includeRevealPartner=false`
   - Q2: `/characters/{id}/events?...q=암페타민&includeRevealPartner=false` (여러 키워드면 여러 호출)
   - Q3: `/characters/{a}/coevents?with={b}&limit=200`
3. 결과 카드에 `eventId/episodeStart~End/summary` 표시 확인.

Known Risk (Hole)
- 텍스트 오브젝트 기반 템플릿(Q2 등)은 결국 데이터(summary/suggestion)에 키워드가 존재해야 한다.
  - 대응: `qAnyOf[]` 동의어 세트 + 데이터 보강(운영)으로 해결.

Applied Fix (Quality Guard)
- `api3`는 `includeRevealPartner` 파라미터로 “subject 단독 타임라인”을 강제할 수 있다.
  - 템플릿/프리셋은 기본적으로 `includeRevealPartner=false`로 호출한다.
  - 기존 위젯/호환을 위해 기본값은 `true` 유지.

범용 템플릿(다른 드라마 적용) 체크포인트
- 템플릿은 **드라마-불변 엔진 + 드라마별 템플릿 데이터**로 분리한다.
  - 엔진: ops 실행/조합/픽(earliest/latest), 결과 렌더링, 디버그 출력
  - 데이터: `CharacterRef(name+aliases)` + `qAnyOf[]` 키워드 세트
- 캐릭터 resolve가 실패/모호한 경우 처리:
  - 기본: `aliases[]`를 충분히 제공해 충돌을 줄인다.
  - 그래도 모호하면: 후보를 UI에서 보여주고 사용자가 선택(템플릿 실행 전에 1회만)하도록 한다.

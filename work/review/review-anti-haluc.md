by claude

⏺ 현재 QA 서비스의 실제 구현 상태와 비교해서 분석하겠습니다.                      
                                                                                  
⏺ Explore(Analyze QA service implementation)                                      
  ⎿  Done (33 tool uses · 103.1k tokens · 1m 15s)                                 
                                                                                  
⏺ 두 문서를 읽었고, 현재 구현과 대조 분석을 완료했습니다.                         
                                                                                  
  ---                                                                             
  분석 결과                                                                       
                                                                                  
  문서의 핵심 제안: "Answerability Gate" (답변 가능성 게이트)                     
                                                                                  
  질문 처리 전에 EXISTS ... LIMIT 1로 데이터 존재 여부를 먼저 확인하고, 응답을    
  3상태로 분기:
  ┌───────────────────┬───────────────────┬──────────────────────────────────────┐
  │ exists_safe (<=K) │ exists_any (전체) │                 결과                 │
  ├───────────────────┼───────────────────┼──────────────────────────────────────┤
  │         O         │         O         │ ANSWERED — 근거 있는 답변            │
  ├───────────────────┼───────────────────┼──────────────────────────────────────┤
  │         X         │         O         │ SPOILER_BLOCKED — DB에는 있지만 K 밖 │
  ├───────────────────┼───────────────────┼──────────────────────────────────────┤
  │         X         │         X         │ NOT_ENOUGH_DATA — 데이터 자체가 없음 │
  └───────────────────┴───────────────────┴──────────────────────────────────────┘
  ---
  현재 우리 구현과의 갭

  현재 상태: Production Q 템플릿(프론트엔드)이 api3/api4를 직접 호출하고, 결과가
  비어있으면 그냥 "결과 없음"으로 표시합니다. 레거시 QaService도 confidence=0.0
  하나로 퉁치고 있습니다.
  ┌───────────────────────┬───────────────────────────┬──────────────────────────┐
  │       문서 제안       │         현재 구현         │            갭            │
  ├───────────────────────┼───────────────────────────┼──────────────────────────┤
  │                       │                           │ SPOILER_BLOCKED vs       │
  │ 3상태 분기            │ 있음/없음 2상태           │ NOT_ENOUGH_DATA 구분     │
  │                       │                           │ 못함                     │
  ├───────────────────────┼───────────────────────────┼──────────────────────────┤
  │ exists_safe +         │ api3 호출 1번             │ K 없이 전체 범위 조회가  │
  │ exists_any 2단 체크   │ (safeUpToEpisode 포함)    │ 없음                     │
  ├───────────────────────┼───────────────────────────┼──────────────────────────┤
  │ evidenceEventIds 필수 │ event 목록은 반환하지만   │ 약한 갭                  │
  │                       │ "근거"로 명시 안 됨       │                          │
  ├───────────────────────┼───────────────────────────┼──────────────────────────┤
  │ QA_MISS 로그 수집     │ 없음                      │ 운영 관점 갭             │
  └───────────────────────┴───────────────────────────┴──────────────────────────┘
  ---
  이 제안이 맞는가?

  방향은 정확합니다. 다만 현재 아키텍처에 맞게 적용 지점을 조정해야 합니다.

  맞는 부분

  1. "답을 찾기 전에 답할 자격을 확인한다" — 이건 anti-hallucination의 본질이고,
  LLM 없이 DB 기반 답변을 하는 우리 시스템에서 특히 중요합니다. 현재 "결과 0건 =
  화면에 아무것도 안 뜸"인데, 사용자는 이게 데이터가 없어서인지 vs 스포일러
  차단인지 구분할 수 없습니다.
  2. SPOILER_BLOCKED 분리 — 이것이 가장 가치 있는 포인트입니다. 사용자가 "월터의
  첫 살인은?"이라고 물었을 때, K=1이면 데이터는 ep3에 있지만 차단됩니다. 현재는
  그냥 빈 결과인데, "아직 볼 수 없는 정보입니다"라고 알려주는 게 UX상 훨씬
  낫습니다.
  3. EXISTS LIMIT 1 패턴 — 정답 쿼리 전에 가벼운 존재 확인을 하는 건 성능상으로도
  맞습니다. 무거운 ORDER BY + JOIN 전에 데이터가 있는지 먼저 보는 건 표준적인
  패턴입니다.

  주의할 부분

  1. 적용 지점이 프론트엔드가 아니라 백엔드여야 합니다. 현재 Production Q는
  프론트에서 api3/api4를 직접 치는데, exists_safe/exists_any를 프론트에서 2번
  호출하면 API 콜이 2배가 됩니다. 백엔드(event-service)에서 게이트를 내장하고 응답
   DTO에 상태를 포함시키는 게 맞습니다.
  2. exists_any 쿼리의 보안 문제. K 없이 전체 범위를 조회하면, 응답에 "DB에 있긴
  하다"라는 사실 자체가 스포일러가 될 수 있습니다. 예를 들어 "월터가 죽나요?"에
  SPOILER_BLOCKED가 뜨면, 사용자는 "아 죽긴 하는구나"를 추론합니다. 이건
  predicate별로 위험도가 다릅니다:
    - KILLS, DIES, BETRAYS → SPOILER_BLOCKED 자체가 스포일러
    - MEETS, DISCOVERS → 비교적 안전
  3. 10개 SPARQL 패턴 전부를 SQL 템플릿으로 만들 필요는 없습니다. 현재 Production
  Q가 이미 패턴 3개(character_predicate_earliest, character_keyword_earliest,
  coevents_earliest)로 커버하고 있고, 이것만으로도 Q1~Q15 대부분을 처리합니다.
  나머지 패턴(2-hop, qualifier 등)은 이미 api7/api8에 구현되어 있습니다.

  ---
  실질적 제안: 어떻게 적용하면 좋을지

  [현재]
  FE → api3(safeUpToEpisode=K) → 결과 0건이면 끝

  [제안]
  FE → api3(safeUpToEpisode=K) → 결과 있으면 ANSWERED
                                → 결과 없으면:
                                  → api3(safeUpToEpisode=전체) → 결과 있으면
  SPOILER_BLOCKED
                                                              → 결과 없으면
  NOT_ENOUGH_DATA

  이걸 백엔드 1회 호출로 합치면 가장 깔끔합니다:

  GET /api/event/v2/characters/{id}/events
      ?safeUpToEpisode=3
      &predicateCode=KILLS
      &answerabilityCheck=true   ← 새 파라미터

  Response:
  {
    "status": "SPOILER_BLOCKED",   // or "ANSWERED" or "NOT_ENOUGH_DATA"
    "events": [],                   // K 이내 결과만
    "existsBeyondK": true           // K 밖에 데이터 존재 여부 (boolean만, 내용은
  안 줌)
  }

  이러면 API 호출 1회로 3상태 판정이 가능하고, existsBeyondK는 boolean만
  반환하므로 구체적 스포일러 노출 없이 UX 분기가 됩니다.

  ---
  결론
  Column 1: 방향
  판정: 맞다 — 존재 확인 → 3상태 분기는 정확한 접근
  ────────────────────────────────────────
  Column 1: 즉시 가치
  판정: 높다 — SPOILER_BLOCKED vs NOT_ENOUGH_DATA 구분만으로 UX가 크게 개선됨
  ────────────────────────────────────────
  Column 1: 주의점
  판정: SPOILER_BLOCKED 자체가 스포일러가 되는 predicate(DIES, KILLS 등)에 대한
    정책 결정 필요
  ────────────────────────────────────────
  Column 1: 구현 우선순위
  판정: api3 응답에 existsBeyondK: boolean 추가가 최소 비용 최대 효과




==============


# by Codex

그럼 이런식으로 우리 로직들을 재정리하려면 무슨 작업을해야되니?


• 지금 questions-anti-halus/ 방식으로 “로직을 재정리(=질문 패턴 중심으로 재구성)”하려면, 해야 할 작업은 크게 6덩어리예요.

  1. 질문 패턴 카탈로그화 (SoT 만들기)

  - Production Q / Quick20 / QA 위젯 질문들을 “패턴(01query-examples의 10개)”에 매핑
  - 각 질문을 패턴 + 입력(엔티티) + MUST/SHOULD 조건 + 결과 타입(earliest/aggregate/path)로 정리

  2. QuerySpec(질문 실행 스펙) 표준화

  - 질문을 실행 코드가 아니라 “스펙 객체”로 표현
  - 각 QuerySpec에 아래를 반드시 포함
      - exists_safe probe (K 이하, limit=1)
      - exists_any probe (전체, boolean only)
      - answer query (후보 확장 + 선택 규칙)
      - evidence 요구조건 (없으면 ANSWERED 금지)

  3. Answerability Gate를 ‘백엔드’로 내리기

  - exists_any는 스포일러 표면적이 있어서 FE에서 전체 데이터를 가져오지 말고, 서버가 boolean만 반환하게
  - 응답 상태를 문서대로 3상태로 고정
      - ANSWERED | SPOILER_BLOCKED | NOT_ENOUGH_DATA

  4. 선택(정답) 로직을 “게이트 통과 후”로 강제

  - 지금 오답의 대부분은 “게이트 없이 earliest를 뽑는 것”에서 나오니까,
  - 모든 템플릿 실행기(Production Q, QA 라우터)에 공통으로:
      - probe 실패 시 절대 느슨한 fallback으로 답을 만들지 않기
      - 동치 fallback만 허용(예: Q2에서 meth 실패 → PRODUCTION 토큰으로 probe/answer)

  5. 관측/운영 루프(데이터 보강 백로그 자동 생성)

  - NOT_ENOUGH_DATA가 나올 때마다 (드라마, K, QuerySpec id, 추출 엔티티, 조건) 로그/집계를 남겨서
  - “사람들이 실제로 묻는데 DB가 비어있는 구간”을 자동으로 뽑게 만들기

  6. 테스트 시나리오 고정

  - “시즌1만 있는 DB” 같은 조건에서 3상태가 기대대로 나오는지 스모크 테스트를 고정
      - 시즌3 정답 질문 → NOT_ENOUGH_DATA
      - DB엔 있는데 K 밖 → SPOILER_BLOCKED
      - K 이하에 근거 있음 + evidence 있음 → ANSWERED

  원하면, 우리가 다음 턴에 바로 할 수 있는 실무형 산출물은 2개예요.

  1. Production Q1~Q15를 QuerySpec 표로 “MUST/SHOULD + exists_safe/any + answer”까지 확정한 문서 1장
  2. 서버에 필요한 최소 엔드포인트(=exists_any boolean)와 응답 스키마(3상태)만 정의한 계약서 1장


› 이거하면 엔드포인트 전면수정해야되는거아니냐?


• I’m looking at how to integrate minimal changes while considering various options. One idea is to implement an existing gate using
  current endpoints, or maybe create a new endpoint for checking existence. The user seems to want an explanation without drastic
  revisions. I could add a small endpoint like GET /api/event/v2/exists, which wouldn’t break anything. There’s also the possibility of
  incorporating a check that returns counts only, allowing for flexibility. Let’s focus on what feels most feasible!

  Considering endpoint changes

  I can keep the current endpoints while adding an optional parameter like probe=true that returns only the ID, or I could create a new
  endpoint like /api/event/v2/probes/character-events/exists that returns a boolean. That's not a full overhaul, so it should be fine. For
  frontend gating, we’d use existing endpoints with limit=1 and safeUpToEpisode, but for production, it’s better to implement a server
  boolean. I want to provide clear, concise options without unnecessary edits!

  Evaluating gating approaches

  For internal QA, I can use existing endpoints with limit=1 and safeUpToEpisode, but they don’t clearly distinguish between blocked
  spoilers and just a lack of data. I could add a small probe endpoint in the event service, such as GET /api/event/v2/probe/character-
  events, returning booleans for whether data exists. Alternatively, I could create a new POST /qa/answerability endpoint that integrates
  the event service. If we want to avoid endpoint changes, we could use a metadata approach. I’ll craft a clear response!

• 전면수정까지는 아니에요. 이 “exists gate”는 기존 조회 엔드포인트를 갈아엎는 게 아니라, 질문 실행 레이어에 ‘사전검사’를 하나 얹는 작업이라
  서 변경 폭을 작게 가져갈 수 있어요.

  가능한 선택지는 3개예요(위험/변경량 순):

  1. 엔드포인트 변경 0 (QA 내부 한정)

  - exists_safe는 지금 있는 api3/api4에 safeUpToEpisode + limit=1로 바로 할 수 있음
  - 다만 exists_any(DB 전체에 있긴 한지)는 FE에서 기존 엔드포인트로 치면 “미래 이벤트 내용을 받을 위험(스포일러 표면적)”이 생겨서, 이 옵션
    은 QA/운영 화면처럼 내부용에서만 추천

  2. 엔드포인트 “추가” 1개(권장, breaking 없음)

  - 예: GET /api/event/v2/probe/... 같은 형태로 boolean만 내려주는 probe 엔드포인트를 새로 추가
  - 그러면 기존 조회 API는 그대로 두고,
      - exists_safe는 기존 api3(limit=1, K)
      - exists_any는 probe(boolean only)
        로 3상태(ANSWERED/SPOILER_BLOCKED/NOT_ENOUGH_DATA)를 안전하게 만들 수 있어요

  3. QA-service에만 추가(외부 계약 최소화)

  - FE는 POST /qa/answerability 같은 걸 호출하고
  - QA-service가 내부적으로 event-service에 물어봐서 boolean만 조합
  - 외부에 노출되는 변화는 QA 쪽 1개로 제한 가능

  즉, “전면수정”이 아니라 (A) 질문 실행기 규칙 강화 + (B) probe boolean API 추가(또는 QA에서 흡수) 정도가 현실적인 스코프예요.

==================

# by Claude



⏺ 코덱스 리뷰를 봤습니다. 내 분석과 코덱스 분석을 비교하면:

  ---
  코덱스 리뷰 평가

  잘 짚은 부분

  6단계 작업 분해가 실용적입니다. 특히:

  - 1단계(패턴 카탈로그화) — Production Q를 10개 패턴에 매핑하자는 건 정리로서 가치 있음. 현재 코드에 흩어진 질문 로직을
  한 눈에 볼 수 있게 됨.
  - 4단계(게이트 통과 후에만 정답) — 핵심 포인트. "게이트 없이 earliest를 뽑는 것"이 오답의 원인이라는 진단이 정확함.
  - 6단계(테스트 시나리오 고정) — 시즌1 DB에서 시즌3 질문을 던져 3상태가 나오는지 검증하자는 건, 이 기능의 신뢰성을
  보장하는 유일한 방법.

  3가지 구현 옵션도 현실적입니다:
  옵션: 1. 엔드포인트 변경 0
  코덱스 제안: api3 limit=1로 exists_safe만
  내 의견: 맞지만 exists_any가 빠져서 2상태밖에 안 됨. 내부용으로만 의미.
  ────────────────────────────────────────
  옵션: 2. probe 엔드포인트 1개 추가
  코덱스 제안: 권장
  내 의견: 동의. 내가 제안한 existsBeyondK: boolean과 본질적으로 같은 접근.
  ────────────────────────────────────────
  옵션: 3. QA-service에서 흡수
  코덱스 제안: 외부 계약 최소화
  내 의견: 깔끔하지만, 현재 Production Q가 QA-service를 우회하고 api3/api4를 직접 치고 있어서 QA-service에 넣으면 호출
    경로가 이원화됨.
  ---
  아쉬운 부분

  1. "SPOILER_BLOCKED 자체가 스포일러" 문제를 다루지 않았음.

  이게 이 설계에서 가장 까다로운 부분입니다. 코덱스는 exists_any boolean의 "스포일러 표면적"을 언급하긴 했는데(옵션
  1에서), 정작 어떤 predicate에서 이 문제가 심각한지 분류를 안 했습니다.

  예: "월터가 죽나요?" → SPOILER_BLOCKED → 사용자: "아, 죽긴 하는구나"

  이건 DIES/KILLS/BETRAYS 같은 결정적 predicate에서 boolean 자체가 정답을 유출합니다. 이에 대한 정책이 없으면 기능을
  넣고도 못 쓰는 predicate가 생깁니다.

  내 제안: 위험 predicate는 SPOILER_BLOCKED 대신 NOT_ENOUGH_DATA와 동일하게 처리하거나, "이 질문에는 아직 답할 수
  없습니다"로 통합 처리.

  2. QuerySpec 표준화(2단계)가 과도할 수 있음.

  현재 Production Q 템플릿이 이미 { kind, subject, predicateCode, ... } 형태로 구조화되어 있습니다. 여기에
  exists_safe/exists_any probe 필드만 추가하면 되는데, 별도의 "QuerySpec 객체" 표준을 새로 만들면 기존 템플릿과 이중
  관리가 됩니다. 기존 ProductionQTemplate 타입을 확장하는 게 더 낫습니다.

  3. 구현 우선순위가 불명확함.

  6덩어리를 나열했지만 "뭘 먼저 하느냐"가 빠져 있습니다. 현실적으로는:

  Phase 1 (최소 가치): probe 엔드포인트 1개 + api3 응답에 상태 추가
  Phase 2 (UX 반영):   FE 템플릿에서 3상태 분기 UI
  Phase 3 (운영):      QA_MISS 로그 + 데이터 보강 백로그

  이 순서가 되어야 Phase 1만 하고도 즉시 가치를 얻을 수 있습니다.

  ---
  종합
  ┌───────────┬───────────────────────────────────────────────────────────────────────────────────────────────┐
  │   항목    │                                             평가                                              │
  ├───────────┼───────────────────────────────────────────────────────────────────────────────────────────────┤
  │ 방향성    │ 내 분석과 일치. 둘 다 "probe → 3상태 → 백엔드"로 수렴                                         │
  ├───────────┼───────────────────────────────────────────────────────────────────────────────────────────────┤
  │ 작업 분해 │ 실용적이지만 우선순위가 빠짐                                                                  │
  ├───────────┼───────────────────────────────────────────────────────────────────────────────────────────────┤
  │ 구현 옵션 │ 옵션 2(probe 엔드포인트 추가)가 가장 현실적 — 양쪽 동의                                       │
  ├───────────┼───────────────────────────────────────────────────────────────────────────────────────────────┤
  │ 빠진 것   │ SPOILER_BLOCKED 역설(스포일러 유출) 정책, 기존 템플릿 확장 vs 새 스펙 판단, 페이즈별 우선순위 │
  └───────────┴───────────────────────────────────────────────────────────────────────────────────────────────┘
  코덱스 리뷰는 "어떤 작업이 필요한가"를 잘 정리했고, 내 분석은 "어디가 위험한가"에 더 무게를 두었습니다. 둘을 합치면 구현
   계획이 완성됩니다.





========


by Codex

 클로드 리뷰, 전체적으로 방향 좋고 “우리 시스템에서 실제로 어디가 위험한지”를 꽤 정확히 짚었어요. 핵심 포인트별로 의견만 정리할게요.

  ## 좋은 지적(동의)

  - 3상태 분기(ANSWERED / SPOILER_BLOCKED / NOT_ENOUGH_DATA): “0건이면 그냥 없음”이 아니라 왜 없는지를 분리해야 오답을 구조적으로 막을 수
    있음.
  - exists-safe + exists-any 2단 체크: 시즌 데이터가 비어있는 구간에서 “그럴듯한 오답”을 차단하는 가장 값싼 안전장치.
  - 적용 지점은 FE보다 BE: FE에서 2번 호출로 만들면 호출 수가 늘고, 무엇보다 exists-any가 스포일러 표면적을 키움. 서버에서 boolean으로 흡수
    하는 게 맞음.

  ## 꼭 보완해야 할 구멍(클로드도 언급했지만, 더 강하게)

  - SPOILER_BLOCKED 자체가 스포일러가 되는 질문이 있다는 건 진짜 핵심 리스크예요.
      - 예: “월터가 죽나요?” 같은 질문에서 existsBeyondK=true는 사실상 “죽는다”를 암시.
      - 그래서 exists-any의 결과는 “무조건 사용자에게 노출”이 아니라 질문/프레디켓 민감도에 따라 마스킹 정책이 필요해요.
      - 실무적으로는 2단계가 현실적:
          1. 내부 QA/운영: 3상태 그대로 노출 가능
          2. 사용자-facing: 민감한 intent/predicate는 LOCKED 같은 단일 상태로 합치고(=spoiler-proof), “존재 여부”는 숨김

  ## 제안한 구현 형태에 대한 내 의견

  - 클로드가 제시한 answerabilityCheck=true 같은 기존 api3 응답에 status/existsBeyondK를 섞는 방식은 “변경량이 적다”는 장점이 있지만,
      - 한 엔드포인트가 “데이터 조회 + 정책판정”을 같이 하게 돼서 계약이 애매해지고,
      - 클라이언트/캐시/로그가 섞이기 쉬워요.
  - 대신 나는 probe 전용 endpoint(또는 QA-service에서 probe 흡수) 쪽이 더 깔끔하다고 봐요.
      - probe는 boolean만 반환 (절대 이벤트 내용/ID/에피소드 리턴 금지)
      - user-facing일수록 “existsBeyondK”도 숨길 수 있게

  ## “지금 구현 상태”에 대한 리뷰의 정확성

  - “현재는 2상태(있음/없음)로 퉁친다”는 지적은 대체로 맞아요. (우리가 FE에 expectedMinEpisode로 잠금은 넣었지만, 그건 템플릿별 UX 힌트고
    DB가 실제로 있는지/없는지를 구조적으로 판정하진 못함)
  - 즉, exists-gate를 하면 “오답 방지”가 한 단계 더 올라가는 건 맞습니다.

  정리하면: 클로드 리뷰는 방향 90% 정답이고, 우리가 추가로 결정해야 하는 건 딱 하나예요.
  exists_any 결과를 “사용자에게 보여줄 수 있는가?”를 질문 민감도 정책으로 분리하자. 이거 없으면 anti-halu가 anti-spoiler를 깨뜨릴 수 있어
  요.
============

# Claude


  ---                                                                                                                     
  코덱스 추가 의견 평가                            
                                                                                                                          
  강하게 동의하는 부분                                                                                                    
                                                                                                                          
  1. "exists_any 결과를 사용자에게 보여줄 수 있는가?"를 질문 민감도 정책으로 분리하자                                     

  이건 내가 제기한 "SPOILER_BLOCKED 역설" 문제에 대한 실질적인 해법을 제시한 것입니다. 내가 문제만 지적했다면, 코덱스는
  2단계 마스킹 정책으로 구체화했습니다:
  ┌───────────────┬────────────────────────────────────────────────────────┐
  │     대상      │                          정책                          │
  ├───────────────┼────────────────────────────────────────────────────────┤
  │ 내부(QA/운영) │ 3상태 그대로 노출                                      │
  ├───────────────┼────────────────────────────────────────────────────────┤
  │ 사용자-facing │ 민감 predicate는 LOCKED로 합쳐서 존재 여부 자체를 숨김 │
  └───────────────┴────────────────────────────────────────────────────────┘
  이게 맞습니다. DIES/KILLS/BETRAYS 질문에서는 SPOILER_BLOCKED를 보여주면 안 되니까, 프론트에서 predicate별로 표시 정책을
  다르게 적용하면 됩니다.

  2. answerabilityCheck=true 파라미터 방식에 대한 비판

  내가 제안한 "기존 api3에 파라미터 추가" 방식에 대해 코덱스가 정확히 약점을 짚었습니다:

  "한 엔드포인트가 데이터 조회 + 정책판정을 같이 하게 돼서 계약이 애매해지고, 클라이언트/캐시/로그가 섞이기 쉬움"

  이건 맞는 지적입니다. probe를 별도 엔드포인트로 분리하면:
  - api3은 순수 데이터 조회 → 캐시 가능
  - probe는 정책 판정 → 로그/집계 가능
  - 관심사 분리가 깨끗함

  내 제안을 수정합니다: answerabilityCheck 파라미터 방식보다 probe 전용 엔드포인트가 더 낫습니다.

  ---
  살짝 보완이 필요한 부분

  코덱스가 "결정해야 할 건 딱 하나"라고 했는데, 실제로는 두 가지입니다:

  1. 질문 민감도 정책 (코덱스가 언급) — 어떤 predicate가 민감한가?
  2. probe 엔드포인트 위치 — event-service에 넣을 것인가, qa-service에서 흡수할 것인가?

  현재 Production Q가 qa-service를 우회하고 api3/api4를 직접 치고 있으므로, probe도 event-service에 두는 게 호출 경로가
  일관됩니다. qa-service에 넣으면 "Production Q는 event-service 직접 호출 + probe만 qa-service 경유"라는 비대칭이
  생깁니다.

  ---
  3자 합의 요약

  세 리뷰(원본 문서 + 코덱스 + 나)가 수렴한 결론:
  ┌────────────────────────────────────────────────────┬──────────────────────────────┐
  │                     합의 사항                      │             상태             │
  ├────────────────────────────────────────────────────┼──────────────────────────────┤
  │ 3상태 분기 필요                                    │ 전원 동의                    │
  ├────────────────────────────────────────────────────┼──────────────────────────────┤
  │ probe는 백엔드에서 boolean only                    │ 전원 동의                    │
  ├────────────────────────────────────────────────────┼──────────────────────────────┤
  │ 기존 엔드포인트 전면수정 불필요                    │ 전원 동의                    │
  ├────────────────────────────────────────────────────┼──────────────────────────────┤
  │ probe 전용 엔드포인트 분리 (기존 api3에 섞지 않기) │ 코덱스 제안 → 나도 수정 동의 │
  ├────────────────────────────────────────────────────┼──────────────────────────────┤
  │ 민감 predicate는 LOCKED로 마스킹                   │ 코덱스 제안 → 동의           │
  ├────────────────────────────────────────────────────┼──────────────────────────────┤
  │ 미결정: probe 위치 (event-service vs qa-service)   │ 결정 필요                    │
  ├────────────────────────────────────────────────────┼──────────────────────────────┤
  │ 미결정: 민감 predicate 목록 확정                   │ 결정 필요                    │
  └────────────────────────────────────────────────────┴──────────────────────────────┘


====================

# by Claude

 코덱스 의견 봤습니다.                                                                                                   
                                                                                                                          
  ---                                                                                                                     
  두 가지 결정에 대한 내 의견                                                                                             
                                                                                                                          
  1. probe 위치: event-service → 동의, 확정                                                                               
                                                                                                                          
  세 차례 리뷰를 거치면서 전원 같은 결론입니다. 더 논의할 게 없습니다.                                                    

  2. 민감도를 템플릿 단위로 → 이게 더 낫습니다

  코덱스가 predicate 단위가 아니라 템플릿(질문) 단위로 민감도를 관리하자고 한 건, 내가 처음 제안한 "predicate별 위험도
  분류"보다 정확합니다.

  코덱스가 든 예시가 핵심:
  같은 DISCOVERS라도 "경제적 어려움 인식" vs "범죄 사실 인식"은 민감도가 다름

  맞습니다. predicate는 너무 거친 단위입니다. 같은 KILLS도 "첫 살인은?" (치명적 스포일러) vs "이 전투에서 누가 죽었나?"
  (맥락에 따라 다름)는 다릅니다. 템플릿에 플래그 하나 붙이는 게 가장 실용적입니다:

  // 기존 ProductionQTemplate에 1줄 추가
  {
    id: 'BB_Q1_WALTER_FIRST_KILL',
    kind: 'character_predicate_earliest',
    predicateCode: 'KILLS',
    disclosurePolicy: 'HIDE_EXISTS_BEYOND_K',  // ← 이것만 추가
    ...
  }

  - ALLOW_SPOILER_BLOCKED → 사용자에게 "아직 볼 수 없는 정보입니다" 표시 OK
  - HIDE_EXISTS_BEYOND_K → existsBeyondK 여부 자체를 숨기고 "답할 수 없습니다"로 통합

  ---
  추가 코멘트에 대해

  "Q2에서 q=meth로 0건 뜨는 케이스는 DB 토큰과 템플릿 qAnyOf가 안 맞아서"

  이건 exists-gate와는 별개의 문제이고, gate가 있으면 이 문제가 더 명확하게 드러납니다. gate 없이는 "0건 = 뭔지
  모름"이지만, gate가 있으면 "NOT_ENOUGH_DATA인데 이 드라마에 데이터가 분명 있는데?" → 토큰 불일치를 즉시 발견할 수
  있습니다. gate가 디버깅 도구로도 작동하는 셈입니다.

  ---
  3자 합의 최종 정리
  ┌────────────────┬────────────────────────────────────────────────────┬──────┐
  │      결정      │                        결론                        │ 상태 │
  ├────────────────┼────────────────────────────────────────────────────┼──────┤
  │ probe 위치     │ event-service                                      │ 확정 │
  ├────────────────┼────────────────────────────────────────────────────┼──────┤
  │ 민감도 관리    │ 템플릿 단위 disclosurePolicy                       │ 확정 │
  ├────────────────┼────────────────────────────────────────────────────┼──────┤
  │ probe 응답     │ { existsSafe: bool, existsAny: bool } boolean only │ 확정 │
  ├────────────────┼────────────────────────────────────────────────────┼──────┤
  │ 기존 api3/api4 │ 변경 없음                                          │ 확정 │
  └────────────────┴────────────────────────────────────────────────────┴──────┘



======================
### user Q & Clause A


❯ 근데 qa 서비스의 질문엔드포인트가 event에있는건 괜찮나? 디비를 거기서 긁어오니까그게낫나?                               
                                                                                                                       
⏺ 좋은 질문입니다. 현재 구조를 정리하면:                                                                                  
                                                                                                                        
  [현재 호출 경로]                                                                                                        
                                                   
  Production Q (FE) ──직접──→ event-service (api3/api4)                                                                   
                                ↓ DB: nospoiler_event                                                                     
                                (event, event_character, event_relation)                                                  
                                                                                                                          
  qa-service ← 거의 안 씀 (레거시)

  "질문" 로직이 event-service에 있는 게 맞느냐? 에 대해서:

  ---
  현실적으로는 맞습니다

  이유 1: 데이터가 거기 있음.
  EXISTS 쿼리든 earliest 쿼리든, 결국 event + event_character 테이블을 직접 읽어야 합니다. qa-service에 probe를 넣으면
  qa-service → event-service로 내부 HTTP 호출이 한 번 더 생깁니다. EXISTS LIMIT 1처럼 가벼운 쿼리를 위해 네트워크 홉을
  추가하는 건 비효율적입니다.

  이유 2: 이미 event-service가 "질문에 답하는 쿼리"를 갖고 있음.
  api3(캐릭터 이벤트), api4(공동 출연), api7(관계 탐색), api8(인과 관계) — 이것들이 실질적인 "질문 응답 엔진"입니다.
  probe도 이 쿼리들의 EXISTS 버전일 뿐이니, 같은 서비스에 두는 게 자연스럽습니다.

  이유 3: qa-service의 현재 역할이 사실상 없음.
  Production Q가 qa-service를 완전히 우회하고 있어서, qa-service에 probe를 넣으면 "probe만 qa-service 경유, 나머지는
  event-service 직접" 이라는 비대칭이 생깁니다.

  ---
  다만 장기적으로는 경계를 정리할 필요가 있음
  ┌─────────────┬────────────────────────────────────────────────┬─────────────────────────────────────┐
  │    관점     │              event-service에 두기              │          qa-service에 두기          │
  ├─────────────┼────────────────────────────────────────────────┼─────────────────────────────────────┤
  │ DB 접근     │ 직접 (빠름)                                    │ event-service 경유 (네트워크 홉 +1) │
  ├─────────────┼────────────────────────────────────────────────┼─────────────────────────────────────┤
  │ 관심사 분리 │ "데이터 조회"와 "답변 가능성 판정"이 섞임      │ 깔끔하게 분리                       │
  ├─────────────┼────────────────────────────────────────────────┼─────────────────────────────────────┤
  │ 현실        │ Production Q가 이미 직접 호출 중               │ 호출 경로 이원화                    │
  ├─────────────┼────────────────────────────────────────────────┼─────────────────────────────────────┤
  │ 민감도 정책 │ event-service가 predicate 민감도까지 알아야 함 │ qa-service가 정책 판단 담당         │
  └─────────────┴────────────────────────────────────────────────┴─────────────────────────────────────┘
  민감도 마스킹(LOCKED 처리) 같은 정책 로직까지 event-service에 넣으면 event-service의 책임이 과해집니다. 그래서 현실적
  타협은:

  [제안 구조]

  event-service:
    - probe 엔드포인트 추가 (순수 boolean, 정책 판단 없음)
    - GET /api/event/v2/probe/character-events
      → { existsSafe: true/false, existsAny: true/false }

  FE (Production Q executor):
    - probe 호출 → 3상태 판정 + 민감도 마스킹은 FE에서
    - ANSWERED이면 → 기존 api3/api4로 데이터 조회

  이러면:
  - event-service는 데이터 존재 확인만 (자기 책임 범위)
  - 정책 판단(민감 predicate 마스킹)은 FE 또는 향후 qa-service에서
  - qa-service를 지금 당장 건드릴 필요 없음
  - 나중에 qa-service를 "질문 오케스트레이터"로 키우고 싶으면, probe를 qa-service가 감싸면 됨

  결론: probe는 event-service에 넣되, boolean만 반환하는 순수 데이터 쿼리로 한정하면 경계가 깨지지 않습니다. "이 데이터가
  존재하느냐"는 데이터 주인이 답하는 게 맞습니다.

✻ Worked for 40s

❯ 후에 그래프ql이나 SPARQL, owl 등을 쓰기 시작하고 v3로 넘어가면 분리가 필요해지나/.                                      
                                                                                                                       
⏺ 핵심을 찌르는 질문입니다.                                                                                               
                                                                                                                       
  ---                                                                                                                     
  짧은 답: 네, 그때는 분리가 필수가 됩니다.        
                                                                                                                          
  이유는 단순합니다 — 데이터 저장소가 바뀌면 쿼리 레이어가 갈라지기 때문입니다.                                           
                                                                                                                          
  ---                                                                                                                     
  현재 (V2): 분리 불필요

  event-service (MySQL)
    └─ event, event_character, event_relation
    └─ api3/api4/api7/api8 = SQL 쿼리
    └─ probe = SQL EXISTS

  하나의 서비스가 하나의 DB를 가지고 조회 + 존재확인을 다 합니다. 깔끔합니다.

  ---
  V3 (그래프 도입 시): 분리 필수

  그래프 DB(Neo4j, RDF store 등)를 도입하면 이런 구조가 됩니다:

  event-service (MySQL)          graph-service (Neo4j / RDF store)
    └─ 이벤트 CRUD, 원본 저장       └─ 트리플 저장, 관계 탐색
    └─ 쓰기(write)의 주인            └─ 읽기(read) 특화

           ↑ 동기화(CDC/이벤트)  ↑

                qa-service (질문 오케스트레이터)
                  └─ probe: "어디에 물어봐야 하지?"
                  └─ 라우팅: SQL 쿼리 vs SPARQL 쿼리
                  └─ 결과 합성 + 3상태 판정 + 민감도 마스킹

  분리가 필요한 이유 3가지:

  1. 쿼리 언어가 달라짐
  ┌───────────────────────────────────────────┬──────────────────────────────────────────────────┐
  │                 현재 (V2)                 │                        V3                        │
  ├───────────────────────────────────────────┼──────────────────────────────────────────────────┤
  │ SELECT ... FROM event_character WHERE ... │ SELECT ?e WHERE { ?e :participant :WalterWhite } │
  ├───────────────────────────────────────────┼──────────────────────────────────────────────────┤
  │ SQL 한 종류                               │ SQL + SPARQL (또는 Cypher) 혼재                  │
  └───────────────────────────────────────────┴──────────────────────────────────────────────────┘
  probe 하나를 치더라도 "MySQL에 물어볼 것인가, 그래프 DB에 물어볼 것인가"를 결정하는 레이어가 필요합니다. 이 결정을
  event-service 안에 넣으면 event-service가 두 DB를 다 알아야 하고, 책임이 폭발합니다.

  2. 탐색 깊이가 달라짐

  현재 2-hop BFS(api7)를 SQL JOIN으로 억지로 하고 있는데, 그래프 DB에서는 N-hop 탐색이 네이티브입니다. "A와 B의 관계
  경로를 찾아라" 같은 질문은 그래프 DB에 위임하는 게 맞고, event-service가 이걸 직접 하면 안 됩니다.

  3. OWL/온톨로지 추론이 들어오면 "추론된 사실"이 생김

  OWL 추론기를 붙이면 DB에 명시적으로 없는 관계도 도출됩니다:
  - DB에 저장된 사실: "월터 KILLS 크레이지-8"
  - 추론된 사실: "월터 IS_A 살인자" (OWL 클래스 추론)

  이 경우 probe의 existsAny가 저장된 사실 기준인지, 추론 포함인지도 결정해야 합니다. 이건 데이터 저장
  서비스(event-service)의 책임이 아니라 질문 해석 서비스의 책임입니다.

  ---
  그래서 로드맵으로 보면

  V2 (지금)
    event-service에 probe 추가 (SQL EXISTS, boolean only)
    FE에서 3상태 판정 + 마스킹
    → 빠르고 간단, 충분함

  V2.5 → V3 전환기
    qa-service를 "질문 오케스트레이터"로 승격
    qa-service가 probe를 감싸서 호출 (FE는 qa-service만 호출)
    event-service의 probe는 내부 API로 전환
    → 이때 분리하면 됨, 지금 할 필요 없음

  V3 (그래프 도입)
    qa-service가 쿼리 라우팅 담당
      ├─ 단순 존재확인 → event-service (SQL)
      ├─ 관계 탐색/경로 → graph-service (SPARQL/Cypher)
      └─ 추론 질문 → OWL reasoner
    event-service는 CRUD + 동기화만

  결론: 지금은 event-service에 probe를 넣는 게 맞고, 그래프 DB를 도입하는 시점에 qa-service로 올리면 됩니다. 중요한 건
  지금 probe를 boolean only로 깨끗하게 만들어두면, 나중에 qa-service가 감싸기만 하면 되니까 이전 비용이 거의 0입니다.


=============================

# 최종 요약 (2026-02-11, Claude + Codex + 사용자 합의)

## 1. Answerability Gate (3상태 분기) — 확정

질문 실행 전에 데이터 존재 여부를 확인하고, 응답을 3상태로 분기한다.

| exists_safe (<=K) | exists_any (전체) | 결과 |
|:---:|:---:|---|
| O | O | **ANSWERED** — 근거 기반 답변 |
| X | O | **SPOILER_BLOCKED** — DB에는 있지만 K 밖 |
| X | X | **NOT_ENOUGH_DATA** — 데이터 자체가 없음 |

## 2. 구현 결정사항 — 확정

| 항목 | 결정 |
|---|---|
| probe 위치 | **event-service** (DB 직접 접근, 호출 경로 일관성) |
| probe 응답 | `{ existsSafe: bool, existsAny: bool }` **boolean only** |
| probe 형태 | **전용 엔드포인트 분리** (기존 api3에 섞지 않음) |
| 기존 api3/api4 | **변경 없음** |
| 민감도 관리 | **템플릿(질문) 단위** `disclosurePolicy` 플래그 |
| 민감도 값 | `ALLOW_SPOILER_BLOCKED` / `HIDE_EXISTS_BEYOND_K` |
| 정책 판단 위치 | **FE** (또는 향후 qa-service) — event-service는 boolean만 반환 |

## 3. V3(그래프 도입) 시 분리 계획 — 합의

| 단계 | probe 위치 | qa-service 역할 |
|---|---|---|
| V2 (현재) | event-service | 거의 안 씀 |
| V2.5→V3 전환기 | event-service (내부 API) | 질문 오케스트레이터로 승격, probe를 감싸서 호출 |
| V3 (그래프 도입) | event-service + graph-service | 쿼리 라우팅 (SQL vs SPARQL/Cypher) + 결과 합성 |

## 4. Object(텍스트 대상) 문제 — 합의

"월터의 첫 마약 제조?" 같은 질문에서 object(마약/메스암페타민)가 구조화 안 됨 → `q="meth"` LIKE 검색 miss 발생.

| 단계 | object 처리 |
|---|---|
| **V2.5 (현재)** | `qAnyOf[]` 유의어 + 사용자가 수동 보강 |
| **V3** | `target_key` 코드화 또는 object 1급 엔티티화 |

- V2.5에서는 **사용자(운영자)가 수동으로** 템플릿 `qAnyOf[]`에 유의어를 추가하여 검색 miss를 줄인다.
- object의 코드화(구조화)는 **V3 단계에서** `target_key` 또는 `event_object` 테이블로 구현한다.
- 관련 스펙 경로: `fivecircles/architecture/specs/object구현계획-경로.md`

## 5. 구현 우선순위 (Phase)

1. **Phase 1**: event-service에 probe 엔드포인트 추가 + ProductionQTemplate에 `disclosurePolicy` 추가
2. **Phase 2**: FE executor에서 probe → 3상태 분기 UI 반영
3. **Phase 3**: QA_MISS 로그 수집 + 데이터 보강 백로그 자동 생성
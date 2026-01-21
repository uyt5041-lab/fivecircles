## reveals는 대체 어떤종류의 연결이냐?

좋은 질문이야.
**REVEALS는 온톨로지 4분류 중에서도 가장 헷갈리기 쉬운 “특수한 Relation”**이거든.

결론부터 말하면:

REVEALS는 “사건 ↔ 사건” 관계 중에서
‘정보 공개(knowledge change)’를 표현하는 인과적·인지적 연결이다.

아래에서 딱 필요한 만큼만 정리할게.

1️⃣ REVEALS는 어떤 종류의 연결이냐
분류부터 정확히

❌ Predicate (사건의 종류) 아님

❌ 단순 시간 관계 아님

✅ Relation (사건 ↔ 사건)

✅ 그중에서도 인지 상태를 바꾸는 관계

즉, “현실에서 무슨 일이 일어났는가”가 아니라
“알게 되었는가 / 드러났는가”를 연결하는 관계야.

2️⃣ 문장으로 보면 바로 이해됨
PRECEDES

Event A happened before Event B

→ 시간

RELATED

Event A is contextually related to Event B

→ 맥락

REVEALS

Event A reveals information about Event B

→ 지식의 변화

이게 핵심 차이야.

3️⃣ 구체 예시 (드라마/스토리 기준)
예시 1: 정체 공개

Event A: “주인공이 마스크를 벗는다”

Event B: “주인공의 정체가 사실 X였다”

Event A -- REVEALS --> Event B


👉 Event B(정체 사실)는
Event A가 일어나야만 ‘알 수 있게 되는’ 사건

예시 2: 배신의 진실

Event A: “녹음 파일이 재생됨”

Event B: “A가 배신자라는 사실”

녹음 재생 -- REVEALS --> 배신 사실


배신은 과거에 이미 있었을 수 있지만,
‘알게 되는 사건’은 지금 발생한 거야.

4️⃣ 그래서 REVEALS는 왜 위험하냐 (스포일러 관점)

REVEALS는 본질적으로 이런 성질을 가져:

아직 보지 않은 사람이 ‘알면 안 되는 정보’를 직접 가리킨다

그래서:

BFS 탐색에 넣는 순간 ❌

K(시청 화수) 필터 전에 노출되면 ❌

설명 텍스트에 직접 쓰여도 ❌

즉, REVEALS는:

그래프에는 있어야 하지만

탐색과 노출에서는 특별 취급해야 하는 관계

5️⃣ 온톨로지적으로 보면 REVEALS의 정체

한 단계 더 추상화하면 이렇게 볼 수 있어:

PRECEDES → Temporal relation

RELATED → Contextual relation

REVEALS → Epistemic / Informational relation

(“세계가 바뀌었나?”가 아니라
“사람이 알게 되었나?”)

6️⃣ 그래서 네 설계에서의 올바른 위치

지금 네 구조 기준으로:

event_relation.type = REVEALS
→ 그래프 저장용

❌ BFS 확장 금지

❌ “관련 사건” 자동 추천 금지

❌ 캐릭터 요약 자동 노출 금지

대신:

“왜 이 정보가 차단됐는지 설명”할 때만 사용

관리자/검수자 뷰에서만 직접 활용

이게 요구사항에도 맞고, 스포일러 안전성도 지킴.

7️⃣ 한 문장 요약 (가장 중요)

REVEALS는 ‘사건이 다른 사건을 일으킨다’가 아니라,
‘사건이 다른 사건을 알게 만든다’를 표현하는 관계다.

그래서:

강력하고

유용하지만

자동 탐색에는 절대 넣으면 안 되는 관계

지금 네가 REVEALS를 “특별 취급”하려고 한 직감은
완전히 맞았어.
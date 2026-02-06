맞아. 지금 너희가 잘 되는 건 **“극중 진행순서(시간 축)”**이고, 그걸 그대로 **causes/effects(인과 축)**로 쓰면 “맞기도 하고 틀리기도”가 정상이다.
그래서 로직을 이렇게 **2축으로 분리**해야 causes/effects가 “잘 찾아진다”.

---

## 0) 핵심 결론: causes/effects는 “시간”이 아니라 “인과 엣지”가 필요함

* **timeline(극중 진행축)**: 화면에 나온 순서가 아니라, 극중에서의 앞/뒤(회상씬이 있어도 “극중에서 먼저/나중”)
* **causes/effects(원인/결과)**: “A 때문에 B가 일어났다”라는 인과

즉, causes/effects가 제대로 되려면 **인과 후보를 뽑고, 그중 일부를 ‘인과 엣지’로 확정 저장**해야 한다.
(자동 확정은 위험하니, MVP에선 *제안 → 승인 → 저장*이 정답)

---

## 1) 데이터 구조는 그대로 가도 됨 (스펙 안 깨고)

* `event_relation`은 계속 **PRECEDES만 저장**
* 단, **Q11/Q12에서는 PRECEDES를 “인과적으로 검수된 precedes”로만 쓰는 정책**으로 운영한다
* 반대로 “단순 진행순서”는 DB 엣지로 저장하지 말고, 필요하면 **정렬(episode/id)**로만 제공

즉:

* Q11/Q12(원인/결과) = **검수된 PRECEDES 엣지**
* “극중 진행축” = **정렬/리스트(derived), 또는 별도 endpoint**

이렇게 하면 “우린 지금 순서만 된다” 문제를 정면으로 해결한다.

---

## 1.1) Q11/Q12 조회 규칙 (입력순서/ID와 무관)

핵심: Q11/Q12는 “정렬로 추론”하지 말고, `event_relation(PRECEDES)`에 **인과로 승인된 엣지**만 넣어서 푼다.
(= Level3 요구사항 “자동 추론 없음”을 지키면서도, 원인/결과를 안정화)

* **Q12 effects(결과)**: outgoing PRECEDES
  * `from_event_id = E` -> `to_event_id`
  * 정렬: `to.episode_start ASC, to.id ASC` (id는 tie-breaker)
* **Q11 causes(원인)**: incoming PRECEDES
  * `to_event_id = E` -> `from_event_id`
  * 정렬: `from.episode_end DESC, from.id DESC` (id는 tie-breaker)

---

## 2) causes/effects를 잘 찾게 만드는 로직 = “후보 생성 + 랭킹” (저장 X)

너희가 이미 suggestions가 폭발하는 걸 봤지?
그래서 후보를 **폭발하지 않게** 만들면서, 인과에 가까운 것을 **위로 올리는 점수**가 필요해.

### A) 후보 생성 (Candidate Generation) — 넓게 잡되 폭발 금지

기준 이벤트 A에서 효과 후보 B를 만들 때:

1. 같은 drama_id
2. 시간 제약: `A.episode_end < B.episode_start` (겹치면 제외)
3. “캐릭터별 next 1개” 방식으로 후보 수를 **캐릭터 수 수준으로 제한**

   * 이미 너희가 정리한 그 방식 그대로

이 단계는 “시간상 다음일 수 있는 것”만 모아오는 단계.

### B) 인과 점수화 (Ranking) — 여기서 ‘원인/결과스러움’을 올린다

후보 (A→B)에 대해 아래 피처를 계산해서 스코어로 정렬해.

**MVP 우선순위(구현 리스크 낮은 순서)**

1. **공유 캐릭터 수**: shared_character_count
2. **가까움**: `B.episode_start - A.episode_end`가 작을수록 가산
3) **REVEALS 연계(있으면 강력)**: A가 reveal을 만들고, B가 같은 reveal target(캐릭터/속성)에 걸리면 가산
   * 구현 힌트: `shared_reveal_count` (A와 B의 reveal target 교집합 크기)

**(후속) 추가 피처**
* 변화 이벤트 우선: B가 “상태 변화/결과형” predicate면 가산 (예: 죽음/체포/공개/폭로/결별/승진/퇴장/발견/파괴)
* 역할 기반: A에서 특정 role이 트리거이고 B에서 그 role의 결과가 나타나면 가산 (예: “협박” -> “배신”, “공격” -> “부상”)

> 이건 “자동 확정”이 아니라 **정렬 로직**이라 스펙 철학을 안 깨면서도 체감 정확도가 확 올라간다.

---

## 3) 운영 플로우: “제안 → 승인 → Q11/Q12에서 사용”

이제 causes/effects가 “잘 나오는” 실제 동작 흐름은 이렇게 고정하면 돼.

1. **causal-suggestions**: 위 점수로 상위 N개 추천 (저장 X)
2. 운영자가 **인과로 맞는 것만 승인**
3. 승인된 것만 `event_relation(PRECEDES)`로 저장
4. Q11/Q12:

   * Q11 causes: `to_event_id = E` incoming PRECEDES
   * Q12 effects: `from_event_id = E` outgoing PRECEDES
   * “가까운 우선” 정렬은 그대로 적용

이렇게 하면 Q11/Q12는 더 이상 “진행순서”가 아니라 **검수된 인과 그래프**가 된다.

---

## 4) 왜 이게 “꼬임”을 푸는 정답인가

* 지금은 PRECEDES가 사실상 “다음에 일어난 일”로 들어가니까 인과가 흔들림
* 앞으로는 PRECEDES를 **인과로 승인된 연결만** 저장하게 되니까

  * Q11/Q12는 인과로 안정
  * “진행순서”는 정렬 기반으로 따로 제공하면 됨

요약하면:

* **인과는 엣지(승인된 relation)**
* **시간은 정렬(derived)**

---

## 4.1) 같은 에피소드에서 “입력순서=진행순서” 착시 제거 규칙

결론: 같은 에피소드 내부에서 **정렬로 진행순서를 만들지 않는다.**
입력순서 기반 정렬은 “중간 사건”이 나중에 추가되는 순간 100% 깨진다.

* 같은 에피소드 내부 진행순서는 기본적으로 “정의되지 않음”
* 같은 에피소드에서 순서를 보여주고 싶으면 **오직 PRECEDES 엣지로만** 순서를 만든다
* PRECEDES 엣지가 없는 이벤트들은 **의미 없는 안정 정렬(예: id)**로만 보여준다 (결정성만 담당)

### (옵션) 같은 에피소드에서 “추론 없이” 진행순서를 보여주는 최소 구현

1. 해당 에피소드 이벤트 전체를 가져온다
2. 그중 “같은 에피소드 내부” PRECEDES 엣지만 가져온다
3. 그 엣지들로 topological sort(부분 순서) 수행
4. 정렬 안 되는(엣지 없는) 이벤트는 뒤에 id로 붙인다
5. 사이클(운영 실수) 발생 시 전체를 id 정렬로 fallback

---

## 5) 바로 적용되는 MVP 규칙(한 줄로 못박기)

* **Q11/Q12(causes/effects)는 ‘인과로 승인된 PRECEDES’만 사용한다.**
* **단순 timeline은 저장하지 않고 episode 정렬로 제공한다.**
* **인과 후보는 자동 저장하지 않고 점수화 추천만 한다.**

---

추가로, 운영자가 “왜 이게 원인/결과 후보인지” 한눈에 판단하게 하려면 suggestions 응답에 아래 3개만 추가해도 된다.

* `shared_character_count`
* `episode_gap` (= `B.episode_start - A.episode_end`)
* `shared_reveal_count`

# V2~V2.5 Adoption Review (Anti-Hallucination)

목적
- `questions-anti-halus` 설계를 V2~V2.5 기준으로 채택/보강/주의 관점에서 빠르게 점검한다.
- 구현 직전 체크포인트를 명확히 남긴다.

---

## 1) 잘 만든 점 (V2~V2.5에서 그대로 채택)

1. 0건을 3상태로 분해
- `ANSWERED / SPOILER_BLOCKED / NOT_ENOUGH_DATA` 분기는 운영 루프를 살린다.
- “왜 0건인지” 설명 가능해져 온톨로지 레이어 목적과 정합적이다.

2. Strict(정답 확정) vs Approx(후보 탐색) 분리
- `exists`는 answerability, correctness는 별도 처리라는 구조가 핵심.
- semantic drift가 exists를 통과하는 문제를 구조적으로 차단한다.

3. 성공 케이스 1콜 유지(0건일 때만 probe)
- 성능/NFR 관점과 UX 관점 모두에서 합리적이다.

4. `first_<predicate>` 패밀리로 고정
- `first` 단독 모호성을 제거해, 데이터가 작을 때 오답 폭발을 방지한다.

---

## 2) 즉시 보강 필요(안 하면 오판/누수 가능)

### A. probe의 existsAny는 반드시 APPROVED 기준

문제
- `PENDING`이 existsAny 판정에 섞이면 사용자/운영 해석이 꼬인다.

보강 규칙
- `/probe`는 기본적으로 아래 2개만 반환한다.
  - `existsSafeApproved` (`<=K + source_status=APPROVED`)
  - `existsAnyApproved` (`전체 + source_status=APPROVED`)

정책
- `PENDING` 존재 여부는 wiki/admin 도메인에서 별도로 다룬다.

### B. Strict/Probe 필터 동기화는 “코드 구조”로 강제

문제
- 문서 약속만으로는 필터 불일치가 발생한다.
  - 예: Strict엔 `qAnyOf` 포함, probe엔 누락 → `existsAny=true` 오판

보강 규칙
- `StrictQuerySpec` 단일 객체를 만들고, 같은 빌더에서 아래 2개를 생성한다.
  - answer SELECT
  - probe SELECT 1 LIMIT 1 (safe/any)

---

## 3) V2.5 스펙 매핑 체크 (확장성)

현재 `queryKind`는 V2.5의 “질문 유형 + 정렬/limit 프로파일”로 해석 가능하다.

- `character_predicate_earliest`
  - `CHARACTER_EVENTS + predicateCode + ORDER BY + LIMIT 1`
- `coevents_earliest`
  - `CHARACTER_AND_CHARACTER_EVENTS + (optional predicate) + earliest`
- `character_keyword_earliest`
  - `CHARACTER_EVENTS + keyword token set(qAnyOf)`

결론
- V2.5의 6타입 철학 위에 earliest 프로파일을 얹은 구조라 확장성은 충분하다.

---

## 4) V2.5에서 수동으로 남기는 포인트

1. 템플릿별 Strict MUST 사전 합의
- 질문 추가는 “Strict MUST 추가”로만 받는다.

2. `qAnyOf`(동치 토큰) 유지보수
- V2.5의 라벨 매칭은 운영 루프가 핵심이다.
- `QA_MISS` 로그를 백로그로 연결한다.

3. 동일 에피소드 PRECEDES 수동 큐레이션 유지
- V2.5 원칙(동일 에피소드 PRECEDES는 운영자 수동)과 충돌 없음.

---

## 5) RDF/OWL 일반 패턴 관점에서 커버 범위

현재 V2.5는 ASK + SELECT 패턴을 SQL로 재현한다.

- ASK 역할: `SELECT 1 ... LIMIT 1`
- SELECT 역할: `SELECT ... ORDER BY ... LIMIT N`

결론
- 운영 안정성 패턴은 충분히 커버한다.
- OWL 추론(Reasoning)은 의도적으로 범위 밖이며, V2.5 보수적 해석과 일치한다.

---

## 6) 최종 체크리스트 (구현/검증 통과 기준)

1. probe는 boolean only + APPROVED 기준
2. `StrictQuerySpec` 단일화로 answer/probe 동기화
3. Strict 0건이면 `ANSWERED` 절대 금지(Approx 있어도)
4. `disclosurePolicy`로 사용자 노출에서 `SPOILER_BLOCKED -> LOCKED` 마스킹 가능
5. `NOT_ENOUGH_DATA`를 `mustFilters` 스냅샷 로그로 백로그화

위 5개가 지켜지면, “시즌1만 적재된 환경에서 시즌3 정답이 섞여 나오는 오류”를 구조적으로 차단할 수 있다.


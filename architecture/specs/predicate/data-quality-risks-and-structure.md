# Data Quality: Structural Risks and Quality-Boosting Design

목적
- Q1~Q15 및 파생 질문 구현 시 “오탐/누락”을 유발하는 구조적 결함을 사전에 명시한다.
- 코드가 커지기 전에, 품질을 올리는 설계 원칙을 문서로 고정해 팀 합의 비용을 줄인다.

관련 문서
- Predicate 전략/레이어: `fivecircles/architecture/specs/predicate/README.md`
- 그룹 정의: `fivecircles/architecture/specs/predicate/groups.md`
- Related characters 집계: `fivecircles/architecture/specs/predicate/related-characters-aggregate.md`
- REVEALS 분류/통합 포인트: `fivecircles/architecture/specs/predicate/reveals-classification.md`

---

## 1) 구조적 결함(품질 훼손 요인)

### R1. Free-text drift (predicate_suggestion)
문제
- `predicate_suggestion`은 텍스트라서 표기 흔들림(대소문자/띄어쓰기/오타/다국어)이 누적된다.
- 그룹 fallback이 텍스트에 직접 의존하면 시간이 갈수록 정확도가 떨어진다.

권장 방어
- raw 텍스트를 그대로 group by 하지 말고, 집계/그룹 용으로는 “정규화된 키”를 별도로 유지한다.
  - 권장: 후보 레지스트리 테이블에 `(drama_id, suggestion_key)` 단위로 `hit_count`를 누적(upsert).
  - `suggestion_key` 예시
    - `TOKEN|한국어` 형태면 `TOKEN` + `label`로 분리 저장하고, group fallback은 토큰만 사용.
    - NEW/free-text면 upper+trim(+ alias map) 같은 정규화 키를 사용.
- 그룹 fallback은 “정규화된 값(토큰/키)”만 사용한다.

### R2. Direction 부족(누가 가해자인가)
문제
- coevent 기반 “적대/협력”은 같은 사건이라도 주체/대상이 분리되지 않으면 오탐이 늘어난다.

권장 방어
- 그룹에 “방향성이 강한 predicate(ATTACKS/DEFEATS/KILLS/BETRAYS)”를 우선 포함한다.
- 집계 응답에 evidenceEventIds를 포함해 운영자가 검증 가능하게 한다.

### R3. 진행축(에피소드 노출)과 인과/관계축 혼용
문제
- 회상/교차편집에서 episode 정렬은 극중 시간과 어긋난다.
- 이를 `PRECEDES`(설명/탐색 엣지) 의미와 섞으면 인과 질문이 흔들린다.

권장 방어
- 진행축: episode 기반 정렬/필터(derived)
- 인과축: 승인된 PRECEDES(설명/탐색 엣지)
- 문서/코드/테스트에서 의미를 고정한다.

### R4. OTHER/UNKNOWN의 1급 필터화
문제
- OTHER/UNKNOWN은 “미분류 저장용”인데, user-facing 필터로 노출되면 결과 품질/신뢰가 급격히 떨어진다.

권장 방어
- user-facing 필터에서 OTHER/UNKNOWN은 “필터 미적용(null)”으로 처리한다.
- 그룹 조회에서만 제한적으로 fallback 허용.

---

## 2) 품질을 올리는 구조(설계 원칙)

### S1. Evidence-first 응답(근거 중심)
원칙
- 점수/라벨만 주지 말고, 항상 “근거 이벤트(IDs)”를 같이 준다.
- QA/운영 화면은 근거를 먼저 보여준다.

효과
- 자동 추론이 아니라 “검증 가능한 추천”이 되어서, 운영 비용이 감소한다.

### S2. 그룹 매핑 단일 소스(서버 고정)
원칙
- 그룹 정의는 한 곳(`groups.md` + 서버 구현)에서만 유지한다.
- FE는 group 이름만 쓰고, 실제 predicate 합집합/가중치는 서버가 책임진다.
- 특히 집계 응답(countsByGroup)은 "중복 카운트"가 나지 않도록, 그룹 간 precedence/배타 규칙을 서버에서 고정한다.

효과
- FE/BE 불일치로 인한 장기 drift를 막는다.

### S3. Gate를 모든 집계/추천에 강제
원칙
- `safeUpToEpisode=K`를 required로 하고 서버에서 강제한다.

효과
- 스포일러 리스크를 구조적으로 낮춘다.

### S4. 승격 프로세스(폐쇄집합 유지)
원칙
- 많이 쓰이거나 품질 개선에 결정적인 의미만 enum으로 승격한다.
- 승격 전에는 그룹 fallback/설명 패널에서만 보정한다.

효과
- enum 폭발을 막으면서도, 실제 사용 패턴 기반으로 품질을 끌어올린다.

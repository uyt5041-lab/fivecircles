# 5서클 필수 EGM 설계·계약 검토

정책 버전: `fivecircles-egm-v3-risk-scoped` · 2026-11-03

설계·계약·구조 설계와 릴레이의 Doc/Contract 단계에서 EGM 사용은 필수다.
변경 위험도로 필요한 범위를 정한다. 계약·권한·데이터 변경은 전체 검토,
서식 같은 작은 수정은 관련 단계만 검토한다. 유효한 기존 결과는 재사용한다.
이 정책은 작은 변경도 항상 전체 5단계를 실행하던 v2를 대체한다.

## 1. 위험도와 필수 범위 결정

먼저 실제 diff와 영향을 받는 호출자·설정·의존성을 확인한다. 변경 제목, 파일 확장자,
줄 수만으로 분류하지 않는다. 섞인 변경은 가장 높은 위험도를 적용한다.
독립 범위로 분리하려면 공유 계약·의존 영향이 없다는 근거가 필요하다.

| 위험도 | 실제 변화 | 필수 범위 |
|---|---|---|
| HIGH | 계약의 입력/출력·기본값·오류·호환성, 권한·인증·신뢰 경계, 데이터 스키마·의미·조회 필터·변환·저장·삭제·보존·캐시 격리/수명 변경 | FULL: 공식 5단계 |
| MEDIUM | 위 경계를 유지하는 내부 구조·알고리즘·의존성·계측·UI 동작 변경 | TARGETED: 영향받는 단계·검토자. 의미/경계 변화가 드러나면 HIGH로 승격 |
| LOW | 동작·계약·권한·데이터 의미가 동일한 서식·주석·비규범 문서 오타 등 | TARGETED: 해당 변경을 확인할 최소 단계·검토자 |
| UNKNOWN | diff/호출자/의미 영향의 근거가 부족함 | FULL로 보수 분류. 좁은 추가 확인으로 영향이 밝혀지면 근거와 함께 재분류 |

계약 문서도 표 배치만 바꾸면 LOW일 수 있지만, 오타라는 이름으로 기본값·의무·예시 의미를
바꾸면 HIGH다. Python/YAML 들여쓰기, SQL/정규식/프롬프트 문구, UI 클릭 영역 등은
서식처럼 보여도 동작이 달라질 수 있다. 동작 동일성을 확인하기 전에는 LOW로 두지 않는다.
새 기능도 같은 기준으로 판단한다. 필수 계약이나 영향 범위가 불명확하면 FULL이다.

분류 근거에는 변경 위치, 불변/변경된 계약, 영향받는 호출자와 확인 방법을 짧게 남긴다.
리소스·단계별 보안·중복·구조·호환성 5차원은 항상 영향 여부를 확인한다.
영향 없는 차원은 불변 근거를 공유해 `NOT_APPLICABLE(변경 영향 없음)`으로 짧게 남길 수 있다.
서식 수정 때문에 변경되지 않은 운영 보안 전체를 새로 감사하지 않는다.

## 2. 실행 상태와 재사용

검토 범위와 실행 상태를 구분한다.

- `required_scope`: `FULL / TARGETED` 및 필요한 단계·검토자 목록.
- `execution`: `FRESH / REUSED / MIXED / BLOCKED`.
  FRESH는 필요한 검토를 새로 실행, REUSED는 필요한 범위를 모두 기존 결과로 충족,
  MIXED는 유효한 일부 결과 재사용 + 변경된 부분의 새 검토다.
- `BLOCKED`: 필요한 bundle·독립 검토 수단·자료 또는 선택한 필수 검토 결과가 없다.
  독립 준비는 계속할 수 있지만 해당 설계/계약 완료와 종속 구현 인계를 선언하지 않는다.

재사용은 실제 완료 receipt가 있을 때만 한다. 다음을 모두 확인한다.

1. 대상·검토 범위·단계·검토자·실제 완료 응답·결론·남은 finding이 추적 가능하다.
2. 해당 범위의 소스/문서/계약/호출자·설정·의존성·보안 단계와 검토 기준의 fingerprint가
   일치하거나, 변경된 부분과 영향 없는 부분을 명확히 분리해 불변을 확인했다.
   파일명이나 branch/head 이름만 같다는 이유로 재사용하지 않는다.
3. 기존 결과가 **현재 필요한 범위**를 충족한다. TARGETED 결과를 FULL로 격상하지 않는다.
   HIGH 변경의 영향을 받는 과거 결과는 무효다. 새 변경에 대한 전체 5단계를 실행한다.
4. 기준 버전이 다르면 호환성을 확인한다. v2의 실제 FULL 결과는 같은 개발 기준과
   불변 입력에 대해 v3 FULL/TARGETED를 충족할 수 있다. 버전만 보고 자동 승인하지 않는다.
5. 미해결 필수 finding, 실패·미실행·UNKNOWN을 PASS로 세탁하지 않는다. 남은 상태를 승계한다.

변경된 부분은 기존 결과로 덮지 않고 필요한 새 검토를 받는다. 예를 들어 기존 FULL 이후
순수 서식만 바뀌면 영향 없는 결과를 재사용하고 해당 코드/문체 단계만 새로 확인한다(MIXED).
관련 입력이 전부 동일한 설계→계약→릴레이 인계는 receipt 하나를 재사용한다(REUSED).
관련 없는 파일의 변경으로 head SHA가 달라졌다는 이유만으로 전부 다시 실행하지 않는다.
그 변경이 검토 범위·호출자·의존성에 영향을 주지 않는지는 diff로 확인한다.

## 3. FULL과 TARGETED 실행

현재 설치 메타데이터에서 EGM bundle을 찾고 `<root>/skills/egm-review/SKILL.md`,
`<root>/docs/codex.md`와 같은 bundle의 persona/standard를 사용한다.
Codex에서는 `codex plugin list --marketplace egm --json`으로 설치 상태를 확인할 수 있다.
개인 cache 경로·버전을 고정하지 않고 원래 bundle과 라이선스를 유지한다.

FULL은 공식 `Step: uninterrupted`의 다음 5단계를 순서대로 실행한다.

1. Initial zoom out: `zoom_out`, 전체 목표·복잡도·개발 단계.
2. Comprehension: `comprehension`, 대상 문서만 전달. 소스·이전 리뷰는 주지 않는다.
3. Critic: `design_critic / structural / style` 각각 독립 검토.
4. Intermediate zoom out: `zoom_out`, 앞선 결과와 변경 방향 종합.
5. Implementation readiness: `implementation_readiness / codebase_details / style` 각각 독립 검토.

FULL 문서는 `## Detailed Implementation Plan` 경계로 기능/구현 범위를 나눈다.
공식 zoom-out/feature-spec/implementation-readiness 표준과
[개발 필수 기준](engineering-review-standard.md)을 해당 단계에 적용한다.

TARGETED는 다음 기준으로 필요한 단계와 persona만 선택한다. 선택하지 않은 단계는
`NOT_SELECTED`와 불필요한 이유를 기록하며 PASS나 FULL 완료로 표시하지 않는다.

| 영향 | 필요한 EGM 검토 예시 |
|---|---|
| 비규범 문서 오타·표 배치 | 3의 style. 의미가 모호하면 2 comprehension 추가 |
| 동작 불변 코드 서식·주석 | 5의 codebase_details로 동작 불변 확인. 가독성 이슈가 있으면 style 추가 |
| 경계 불변의 내부 구조·중복 정리 | 3 structural + 5 codebase_details. 다른 단계는 실제 영향이 있을 때 추가 |
| 내부 계측·UI 변경 | 5 codebase_details 및 필요한 readiness 검토. 외부 계약·보안·데이터 변화 발견 시 FULL |

이 표는 최소 선택 예시다. 실제 영향이 넓으면 관련 검토를 추가하거나 FULL로 승격한다.
작은 수정에는 새 장문 명세를 만들 필요가 없다. diff·불변 근거·짧은 변경 설명으로 충분하다.
변경된 입력을 검토할 때는 최소 1명의 실제 fresh-context EGM 검토자가 필요하다.
정확히 불변인 범위를 유효한 receipt로 전부 충족하는 REUSED는 새 검토자를 띄우지 않는다.

`fork_turns="none"` 또는 호스트의 `fork_context=false`, `Mode: REVIEW`와 공식 persona,
대상 범위·허용 근거만 전달한다. 읽기 전용이며 지정 밖 탐색·메모리/히스토리·재위임·외부 호출은 금지한다.
호스트 공통 지침까지 완전 격리했다고 주장하지 않는다. 같은 단계의 독립 검토는 병렬 가능하다.
요구된 검토의 완료 응답을 실제로 받고 원문 결과를 보존한다. 자기 검토로 대체하지 않는다.
누락·실패·timeout은 지적 0개가 아니다. 관련 검토 1회 + 필요한 수리 확인 1회를 기본 한도로 한다.
남은 필수 문제는 `NEEDS_DECISION / REQUEST_CHANGES`로 남기고 자동 위험 수용하지 않는다.

## 4. 근거와 완료 판정

Graft를 먼저 사용하되 그래프와 실제 검토 snapshot의 일치를 확인한다. 미색인이면 좁은 원본 확인으로
전환한다. PR의 base/head, 관련 파일/문서·persona·기준의 경로와 hash를 기록하고 기존 WIP와 섞지 않는다.
기존 문서 위치와 한국어 출력을 유지한다. 과거 PR의 명세를 재구성하면 그 사실과 불명확한 의도를 표시한다.
비밀값은 근거 payload에 넣지 않는다.

기존 설계/리뷰/릴레이 양식에 아래를 남긴다. 작은 작업은 한 줄 요약·기존 receipt 참조로 충분하다.

- 정책/bundle 버전, risk와 diff 근거, required_scope, 선택한 단계·persona 및 선택하지 않은 이유.
- execution, 재사용 receipt와 유효성 확인, 무효화/재검토 범위, 단계별 실제 agent·결과·근거 fingerprint.
- 5차원의 영향·판정, 보안 현재/후기 조치의 이유·트리거·책임 역할·완료 기준.
- finding의 위치·영향·최소 조치·OPEN/FIXED/CONTESTED/DEFERRED/명시적 위험 수용 상태.
- 검증 명령·결과·미실행 범위, document_state와 결정. 실제 사용량 미제공 시 token/cost는 null.

현재 선택된 필수 검토가 실제 결과 또는 유효한 재사용으로 충족되어야 완료다.
FULL 요구인데 일부 단계만 했거나, 현재 필수 계약/보안 finding이 미결이면 완료로 처리하지 않는다.
TARGETED 완료는 해당 범위의 완료이며 FULL·배포·사용자 인수가 아니다.
사용자의 명시적 면제/solo/중지는 그대로 존중하고 실제 미실행 사실을 기록한다.
이미 허용된 작업에 단계별 재승인을 만들지 않으며, 리뷰가 제품 수정·발송·push·배포 권한을 추가하지 않는다.

공식 출처: https://github.com/google/elephant-goldfish-model
위험도별 필수 범위·재사용 규칙은 사용자 요청에 따른 Fivecircles 정책이며 공식 EGM 자체 기능과 구분한다.

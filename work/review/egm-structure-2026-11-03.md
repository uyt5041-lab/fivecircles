# EGM 위험도 정책과 structure-architect 적용

작업 ID: `FC-EGM-RISK-20261103` · 작성일: 2026-11-03

## 결과와 범위

EGM 필수 사용을 유지하면서 검토 범위와 실행 여부를 분리했다. 계약·권한·데이터 의미가
바뀌면 FULL, 경계가 유지되는 작은 변경은 관련 단계만 TARGETED로 검토한다.
유효한 이전 결과는 재사용하되 미실행·미선택 단계를 PASS로 표시하지 않는다.

이번 작업은 스킬 유지보수와 합성 사례 적용 확인이다. 아래 사례에 실제 제품 수정이나
공식 FULL 5단계 실행을 했다는 의미가 아니다. 운영 성능·토큰 절감 효과는 측정하지 않았다.

- 정책: `fivecircles-egm-v3-risk-scoped`
- 개발 기준: `fivecircles-engineering-v1`
- 유지보수 검증 범위: TARGETED. 이전 정책의 독립 검토와 8개 사례 결과를 재사용하고,
  변경된 구조 스킬의 적용 결과 및 공개 패키지는 새로 확인했다.
- 실제 EGM 실행에는 별도 공식 bundle과 fresh-context 검토 도구가 필요하다.
- 검토자는 읽기 전용으로 참여했다. 유지보수 검증은 제품의 FULL 검토나 배포 인수를 대신하지 않는다.

## 구조 스킬에 반영한 수정

| 확인한 문제 | 반영한 내용 |
|---|---|
| 작은 변경에도 뒤의 전체 절차가 적용될 수 있음 | `Scope before structure`가 뒤의 단계·양식 범위를 결정하도록 명시 |
| 작은 CLI에도 많은 계층을 권할 수 있음 | 단순 CLI는 평평한 구조 예시 제공, 계층 추가는 실제 책임이 있을 때만 적용 |
| MSA·분리 후보가 항상 필요해 보임 | 실제 규모·변경·운영 필요가 없으면 NOT_APPLICABLE과 재검토 조건만 기록 |
| 높은 구조 점수를 승인으로 오해할 수 있음 | 점수는 진단용. 미해결 계약·보안·데이터 문제를 해소하지 못함 |
| 계약 양식에 권한·전환 설명이 부족함 | 영향이 있을 때 신뢰 경계, 호환·이관·롤백, 현재·후기 보안 항목 작성 |
| 동일한 성장 단계 트리가 중복됨 | 기존 Step 5 예시를 참조하여 중복 제거 |

5개 개발 차원은 유지한다: 리소스 효율, 보안 적용 시점, 중복, 파일·메서드 책임 구조,
호환·확장성. 비해당 항목은 근거와 NOT_APPLICABLE로 남기고 점수를 임의로 채우지 않는다.

## 구조 스킬 재적용 사례

| 사례와 제공 근거 | 기대·확인 결과 | 산출 범위 |
|---|---|---|
| A: 작은 CLI의 서식·주석 변경. AST·호출·계약·데이터 불변 근거와 유효한 이전 FULL receipt 제공 | LOW / TARGETED / MIXED. 변경 부분 codebase_details 확인, 불변 결과 재사용 | diff·불변 근거·검증 결과만. 새 구조 트리·MSA·점수표·19절 문서 불필요 |
| B: catalog의 삭제 책임을 orders로 이동하며 API 권한과 DB 소유 경계 변경 | HIGH / FULL. 영향받은 이전 결과 재사용 불가 | 책임·API·인가·이관·삭제·롤백 계약 필요. 배포 노출 불명은 UNKNOWN 유지. MSA 도입은 별도 근거 필요 |

초기 검토자 `structure_skill_application`의 6개 지적을 반영한 뒤, 별도 검토자
`structure_skill_reapplication`이 수정본으로 위 2개 사례를 적용했다. 두 사례 모두 기대한
분류와 산출 범위가 나왔다. 후속 지적 1건(표에 NOT_APPLICABLE 누락)도 반영했다.
이는 사례 기반 지시 해석 확인이며 자동 테스트 2개 또는 실제 FULL 실행 2회를 뜻하지 않는다.

## 기존 위험도 정책 결과 재사용

기존 독립 구조 검토와 8개 합성 사례 결과를 정책 본문의 동일 fingerprint에 한해 재사용했다.
정책 본문 SHA-256: `1b1630331882ed256e082099c6840d488d5c2da165b8b35814639d948295b65d`.

| 사례 | 확인된 분류·처리 |
|---|---|
| 계약 표의 배치만 변경, 의미 불변 | LOW / TARGETED, 불변 검토 재사용 + style 새 검토 |
| 모바일 버튼 간격 변경, 클릭 범위 영향 가능 | MEDIUM 잠정, codebase_details·필요 readiness. 경계 영향 시 승격 |
| API 기본값 null을 빈 문자열로 변경 | HIGH / FULL |
| 권한 역할 변경 | HIGH / FULL |
| YAML 들여쓰기로 개인정보 로깅 설정 의미 변경 | HIGH / FULL |
| 과거 PASS만 있고 범위·fingerprint 증거 없음 | UNKNOWN / FULL / BLOCKED, 재사용 불가 |
| 입력과 기준이 모두 같은 설계→릴레이 인계 | 실제 receipt 범위 확인 후 REUSED, 불필요한 재실행 없음 |
| 문서 서식과 삭제 권한 변경이 섞임 | HIGH / FULL, 낮은 위험 검토로 전체 승인 불가 |

## 공개 패키지 점검

공개 정본은 `agent/skills/structure-architect/SKILL.md`이다. 예전
`agent/structure-architect/SKILL.md`는 정본으로 안내하는 호환 진입점으로 유지했다.
특정 제품의 flow 경로를 공통 전제로 삼던 문구를 제거하고 실제 프로젝트에서 확인한
문서 경로를 쓰도록 했다. 공개 relay 식별자는 `relay-shot`, 한국어 호출 키워드는 유지한다.

공개 검토자 `fivecircles_publish_audit`가 지적한 고정 경로와 필수 문서 경로를 수정했다.
마지막 좁은 재확인에서 발견한 남은 경로 3줄도 같은 원칙으로 수정했다.

공개 변경물만 검사했으며 기존 저장소의 전체 역사나 제품별 런타임을 감사했다고 주장하지 않는다.

| 실행 검증 | 결과 |
|---|---|
| skill-creator의 quick_validate.py (공개 SKILL 6개) | 6/6 통과 |
| 새 패키지·보고서·README 추가분의 상대 링크 | 누락 0건 |
| 변경 패키지의 개인 절대 경로·제품 식별·키 패턴 검사 | 발견 0건. 비밀값 부재의 완전 증명은 아님 |
| git diff --check | exit 0 |
| 구조 스킬 합성 사례 독립 재적용 | 2/2 기대 분류. 실제 제품 FULL 실행은 미실시 |

검증 대상 SKILL은 doc-contract-writer, structure-architect, fivecircles, relay-shot,
one-shot-delivery-orchestrator 및 이전 structure-architect 경로의 호환 진입점이다.
공식 EGM bundle 실행·호스트별 전체 릴레이 통합 테스트는 이번 게시 검증 범위에 포함하지 않았다.

## 근거 문서

- [공통 EGM 정책](../../agent/skills/doc-contract-writer/references/egm-design-review.md)
- [개발 기준과 Ponytail 출처](../../agent/skills/doc-contract-writer/references/engineering-review-standard.md)
- [구조 스킬](../../agent/skills/structure-architect/SKILL.md)
- [작업 범위와 롤백](../worklog.md)
- [푸시·머지 기록](../integrate-log.md)

## 공개 스킬 fingerprint

검증한 정책·스킬 입력의 SHA-256이다. 이후 관련 입력이 바뀌면 해당 검토를 다시 확인한다.

| 파일 | SHA-256 |
|---|---|
| `agent/skills/doc-contract-writer/SKILL.md` | `0b5fd9e145840a6cfd18f4ea4019570805c93fae3c5ed85a76d25d546ee3f5b4` |
| `agent/skills/structure-architect/SKILL.md` | `f42a67568047dc36526e1808a8be6c0b3ce766e15bb79907ee3e62febfeb0a37` |
| `agent/skills/fivecircles/SKILL.md` | `71d40903a4b1c7eeefd5c1aae5471141e8bf6570ad57b5afcd564c4e53944526` |
| `agent/skills/relay-shot/SKILL.md` | `db9ad88af61f7ad76e8f26cd30f247dfe14863795c2d4e49e9bf0701c52407aa` |
| `agent/skills/one-shot-delivery-orchestrator/SKILL.md` | `001123571bf7aee777d6bb2aa3762159f02284605652431030cd3799d2ce0073` |
| `agent/structure-architect/SKILL.md` | `6aee7efda0a4687523333baa07a78501c767226594c24cfba0b891a0ed08b98d` |
| `agent/skills/doc-contract-writer/references/engineering-review-standard.md` | `d6c3046cba7511fba675d3276225488ae238e414c642b6bc2317ac0ccab947c4` |
| `agent/skills/doc-contract-writer/references/egm-design-review.md` | `1b1630331882ed256e082099c6840d488d5c2da165b8b35814639d948295b65d` |
| `agent/skills/protocol_one_shot_delivery.md` | `bac64b2b27a5ae5c9313875a2cd601ef20c4716daa797f186a04eb23d37759ea` |

추가 확인: 새 파일까지 staging한 첫 `git diff --cached --check`에서 개발 기준 파일 끝의
빈 줄 1개를 발견했다. 의미 변경 없이 제거한 뒤 다시 실행해 exit 0을 확인했다.

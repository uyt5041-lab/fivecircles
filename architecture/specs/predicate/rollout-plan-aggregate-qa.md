# Rollout Plan: Related Characters Aggregate (QA exposure)

목적
- `related-characters/aggregate`를 QA 질문 위젯에서 사용 가능하게 한다.
- 프론트 구현은 Antigravity가 담당하고, 본 문서는 팀 합의 및 배포/검증 체크리스트를 고정한다.

범위
- Event service: 엔드포인트 제공
- Specs: V2/V2.5/api-contract 반영
- QA 노출: /qa 페이지에서만 노출(현 단계 고정)

비범위
- 프론트 실제 구현(담당: Antigravity)
- 품질향상 레이어(정규화/alias 등)의 추가 구현은 별도 todo로만 관리

관련 문서
- 엔드포인트 스펙: `fivecircles/architecture/specs/predicate/related-characters-aggregate.md`
- 품질 리스크/방어: `fivecircles/architecture/specs/predicate/data-quality-risks-and-structure.md`
- API 계약: `fivecircles/architecture/specs/api-contract.md`

---

## 1) 현 상태(백엔드)

- 구현 완료:
  - `GET /api/event/v2/characters/{characterId}/related-characters/aggregate`
  - mode: `ADVERSARY|ALLY|COEVENTS`
  - 옵션: `includeEvidenceEventIds=true` 시 evidenceEventIds 포함(상위 후보만, 추가 1회 쿼리)

---

## 2) 프론트 연동(담당: Antigravity)

- /qa 페이지에 위젯 추가(고정)
- 캐릭터 컨텍스트(characterId, safeUpToEpisode=K)에서 호출
- 표시(최소)
  - otherCharacterId
  - score
  - countsByGroup
- 표시(옵션)
  - evidenceEventIds: 토글로 on/off 또는 최초 on (성능 고려)

---

## 3) 테스트(성공 기준 고정)

주의
- “테스트 성공”은 로컬 unit test가 아니라, **서버 배포 후 엔드포인트 스모크 검사 성공**으로 정의한다.

스모크 체크(예시, curl)
- ADVERSARY
  - `GET /api/event/v2/characters/{id}/related-characters/aggregate?safeUpToEpisode=K&mode=ADVERSARY&limit=30`
- ALLY
  - `GET /api/event/v2/characters/{id}/related-characters/aggregate?safeUpToEpisode=K&mode=ALLY&limit=30`
- evidence 포함
  - `GET /api/event/v2/characters/{id}/related-characters/aggregate?safeUpToEpisode=K&mode=ADVERSARY&includeEvidenceEventIds=true`

검증 항목
- 200 응답
- K 게이트 적용(게이트 밖 데이터가 노출되지 않음)
- mode validation(잘못된 mode는 400 성격 오류)
- includeEvidenceEventIds=true일 때 evidenceEventIds가 포함되고, false일 때 null/미포함

---

## 4) 후속(투두로만)

- 품질향상 레이어 구현
  - suggestion 정규화/alias
  - 그룹 배타 집계 규칙을 코드/문서 단일 소스로 고정
  - evidence-first UI 패턴 고정


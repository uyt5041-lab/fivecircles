# Review: Production Q Templates (MVP) + Defect Fixes
> Reviewer: codex-ops | Date: 2026-02-09

## Scope
- Plan doc: `fivecircles/architecture/specs/predicate/production-q-templates-and-intelligence-queryspec.md`
- Target: Template MVP for dramaId=10 (Q1/Q2/Q3)
- Constraint: Use existing APIs (api3/api4/api7/api8) + `q` keyword filter; no Intelligence wiring in this task.

## Findings (Ordered)

### 1) api3 subject contamination risk (HIGH)
- 현재 `api3` 구현(`getEventsByCharacter`)은 REVEALS 파트너 캐릭터 이벤트를 합칠 수 있다.
- 템플릿이 `EARLIEST + limit=1`을 사용하면 “first” 질문이 파트너 이벤트로 오염될 수 있음.

**Fix (Applied in plan + implementation direction)**:
- 템플릿/프리셋 실행기는 `includeRevealPartner=false`로 api3를 호출해 “subject 단독 타임라인”을 강제한다.
- 기존 동작 호환을 위해 기본값은 `true`로 유지한다(기존 위젯 영향 최소화).

### 2) coevents 무제한 결과 비용 (MEDIUM)
- `api4` coevents는 limit 파라미터가 없어 큰 드라마에서 비용/응답이 커질 수 있다.

**Fix (Applied)**:
- `api4`에 `limit` optional 파라미터를 추가하고, 템플릿은 기본 limit(예: 200)로 호출한다.

### 3) 범용 템플릿을 위한 캐릭터 식별 (MEDIUM)
- 캐릭터 ID는 환경/시드에 따라 달라질 수 있어서 템플릿에서 id 하드코딩은 금지해야 범용화된다.

**Recommendation**:
- 템플릿은 `CharacterRef(name + aliases[])`로만 정의하고, 실행 시 드라마 캐릭터 목록에서 resolve한다.

### 4) 텍스트 오브젝트(q) 정확도 (MEDIUM)
- Q2 같은 텍스트 오브젝트는 결국 `summary/predicate_suggestion` 텍스트에 의존.

**Mitigation**:
- `qAnyOf[]`로 동의어를 여러 번 호출해 OR를 흉내내고, 결과를 합쳐 earliest 1개 선택.
- 실패 케이스는 “데이터 보강” 또는 “템플릿 키워드 세트 확장”로 해결(운영 레벨).

---

## Follow-up Review (After Defect Fixes)
- api3 `includeRevealPartner` / api4 `limit`은 구현 반영 완료(템플릿에서 사용 가능).
- 아래는 템플릿 실행기(프론트 구현)에서 남아있는 설계 구멍이다.

### 5) `qAnyOf[]` OR 다중 호출의 중복 제거 미정의 (MEDIUM)
- 같은 이벤트가 여러 키워드에 매칭될 수 있음.
- executor union 시 `Set<eventId>`로 중복 제거 후 `episodeStart ASC, id ASC`로 earliest를 고르는 규칙을 고정해야 함.

### 6) characterResolver 모호성 처리 (MEDIUM)
- MVP 목표가 “프리셋 버튼 1개로 실행”이면, 모호성 UI는 Phase 2로 미루는 게 일관적.
- MVP 권장: exact match only(name 또는 aliases의 정확 일치)로 제한하고, 모호하면 실패 메시지 + 템플릿 실행 중단.

### 7) Q3 "처음 만남" 정확도 한계 (LOW-MEDIUM)
- `MEETS` 데이터가 없으면 earliest coevent는 “첫 만남”을 보장하지 않음.
- Known risk로 문서화하고, 데이터 보강/승격은 후순위.

### 8) Intelligence QuerySpec 스키마 확정 시점 (LOW)
- Phase 1(템플릿 MVP) 결과를 보고 Phase 3(QuerySpec) 스키마를 확정하는 게 안전함.

### 9) Claude review 요청 상태
- `fivecircles/agent/queue.json`에 `TASK-012`로 review 요청을 등록함(대기).

## Decision
- **APPROVE WITH NOTES** (BE 결함 수정 반영 완료. FE executor 구현 시 MEDIUM(5,6) 체크 필수)

## Next Actions (Implementation)
| # | Action | Owner | Priority |
|---|--------|-------|----------|
| 1 | FE: `productionQ/executor.ts` 구현 (qAnyOf 중복 제거 + Promise.all 병렬) | antigravity | HIGH |
| 2 | FE: `productionQ/characterResolver.ts` (exact match only, MVP) | antigravity | HIGH |
| 3 | FE: `productionQ/templates.ts` (Q1/Q2/Q3 브베 템플릿 데이터) | antigravity | HIGH |
| 4 | FE: QaPage에 Production Q 섹션 UI 추가 | antigravity | HIGH |

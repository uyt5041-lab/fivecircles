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

## Decision
- REQUEST_CHANGES (플랜 자체는 타당, 단 HIGH 결함(api3 contamination) 대응이 반드시 포함돼야 함)

## Next Actions (Implementation)
1. BE: api3에 `includeRevealPartner` 파라미터 추가(기본 true) + false면 partner merge 비활성
2. BE: api4(coevents)에 `limit` 추가(기본 null)
3. Docs: event-v2-api/frontend.md 계약 반영
4. FE: Production Q 템플릿 MVP 실행기 구현(Q1/Q2/Q3) 시 위 파라미터 사용


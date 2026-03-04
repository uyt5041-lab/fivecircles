# [구현 보고] ex14. 표준 Predicate 및 Reveal 메타데이터 구축 결과

## 1. 개요
온톨로지 v3 제안서(`ex11`, `ex13`)에 따라 프로젝트 전반의 사건 분류 시스템을 표준화하고, 스포일러 방지의 핵심인 '정보 공개(Reveal)' 로직을 시스템화하여 구현을 완료함.

## 2. 주요 변경 사항

### 2.1 Predicate 표준화 (PredicateCode.java)
- **`STATUS_CHANGE` → `TRANSFORMS`**: 상태/신분 변화 코드를 온톨로지 표준 명칭으로 변경.
- **`FACT_REVEAL` 제거**: 별개의 코드로 존재하던 '사실 공개'를 `REVEALS`로 통합하고 메타데이터로 구분하도록 단순화.
- **의미**: Predicate는 자연어 동사가 아닌 '사건의 타입(Closed Set)'으로 관리됨을 확정.

### 2.2 Reveal 메타데이터 시스템 (`event_reveal` 테이블)
기존의 텍스트 기반 관리를 벗어나, 공개된 정보의 실체를 추적할 수 있는 구조화된 레이어를 도입함.

| 컬럼 | 타입 | 설명 |
| :--- | :--- | :--- |
| `event_id` | BIGINT | 해당 Reveal 발생 이벤트 ID |
| `target_type` | VARCHAR | `CHARACTER` (정체 공개) 또는 `ATTRIBUTE` (사실 공개) |
| `target_id` | BIGINT | `CHARACTER`일 경우, 새롭게 밝혀진 인물의 고유 ID |

## 3. 핵심 비즈니스 로직: Identity vs Fact

### Type A: Identity Reveal (정체/동일인 공개)
- **트리거**: `predicate = REVEALS` AND `target_type = 'CHARACTER'`
- **시스템 동작**:
    1. **캐릭터 해금**: `target_id`에 해당하는 캐릭터의 `isHidden` 상태를 해제 (이미지 투명도 제거).
    2. **타임라인 통합**: `findRevealPartnerId` 쿼리를 통해 노출용 캐릭터와 실제 정체 캐릭터의 이벤트를 공유/병합.
- **예시**: "프론트맨의 정체가 황인호임이 밝혀짐" -> 프론트맨과 황인호의 타임라인을 하나로 인지.

### Type B: Fact Reveal (단순 사실 공개)
- **트리거**: `predicate = REVEALS` AND `target_type = 'ATTRIBUTE'`
- **시스템 동작**: 
    - 특수 트리거 없이 해당 인물의 새로운 정보로만 기록.
    - `Event` 테이블의 `refined_summary`를 통해 사용자에게 정보 제공.
- **예시**: "성기훈이 빚이 4억 있다는 사실이 드러남" -> 기훈의 정보성 이벤트로 노출.

## 4. AI 서비스 연동 (intelligence-service)
- **Refine Prompt 업데이트**: AI가 `REVEALS` 사건을 감지할 때, 문맥에 따라 자동으로 `revealTargetId`와 `revealTargetType`을 JSON 응답에 포함하도록 페르소나 강화.
- **Mock Logic 반영**: 개발 환경의 Mock LLM에서도 새로운 표준 코드를 따르도록 수정함.

## 4. 해결 완료 및 개선 사항 (2026-02-06 업데이트)

### 4.1. AI Reveal 분류 정밀도 향상 (Intelligence Service)
*   **문제**: AI가 "정체를 확인했다"는 문장을 보고 단순히 주인공을 `targetId`로 매핑하거나, 단순 사실 공개를 `CHARACTER` 타입으로 오분류하는 문제 발생.
*   **해결**: `refine-fact.txt` 프롬프트를 수정하여 **'Identity Reveal(동일인 판명)'**과 **'Fact Reveal(사실/속성 공개)'**을 엄격히 구분.
    *   **Identity Reveal**: A=B가 밝혀지는 경우에만 `CHARACTER` 타입 사용.
    *   **Fact Reveal**: 정체가 아닌 비밀이나 사실을 알게 된 경우 `ATTRIBUTE` 타입 사용.

### 4.2. 데이터 정합성 로직 강화 (Event Service)
*   **수정**: `EventServiceImpl.java`에서 `targetType`이 없을 때 기본값인 "CHARACTER"를 강제로 넣던 로직 제거.
*   **로직**: 오직 `predicateCode`가 **`REVEALS`인 경우에만** `event_reveal` 데이터 생성 시도.

### 4.3. 데이터셋 품질 전략 (Ontology)
*   **전략**: 위키 원본 문장을 그대로 쓰지 않고, **[행위]**와 **[정체 공개]**로 문장을 분리하여 입력.
    *   예: "황준호가 프론트맨에게 발각되어 정체를 확인함" -> "황준호가 발각됨(행위)" + "프론트맨의 정체가 황인호임이 밝혀짐(정체 공개)"

---

## 5. 결론 및 향후 계획

이번 구현을 통해 **"누가 누구인지"에 대한 그래프 관계**를 RDB 레벨에서 추적할 수 있는 기반을 마련했다. 이는 향후 복잡한 인물 관계도(Relation Graph)를 동적으로 생성하는 핵심 엔진이 된다.

또한 금일 업데이트를 통해 **'Reveal' 데이터의 분류 정확도**와 **시스템 적재 로직의 정합성**을 강화했다. (Identity vs Fact 구분, event-service 저장 가드)

### 향후 계획
1.  **전체 데이터셋 적재**: 나머지 에피소드 데이터셋에 대해 Bulk Insert 수행 및 데이터 검증.
2.  **프론트엔드 통합 (Next Week)**:
    *   8화 이후 시점에서 `EventReveal` 데이터를 기반으로 **프론트맨과 황인호의 타임라인을 하나로 합쳐서 보여주는 UI 로직** 구현.
    *   스포일러 필터링이 요약(Summary) 텍스트에 제대로 적용되는지 확인.
3.  **코드 리팩토링 (ex15 논의 사항)**:
    *   `EventQueryServiceImpl`의 비대해진 조회 로직을 `EventAssembler` 도입 등을 통해 다이어트.
    *   `EventRevealMapper`에 Bulk 조회 쿼리 추가로 N+1 문제 해결.

### 관련 후속 문서
- semantic 보조 레인 object schema 초안:
  - `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/specs/reveals/semantic-lane-object-schema-draft.md`
- reveal semantic 상속 초안:
  - `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/specs/reveals/reveal-semantic-inheritance-draft.md`

---
**작성일**: 2026-02-06 (초안: 2026-02-05)
**작성자**: Antigravity (AI Assistant)

# [기술 제안] EventQueryServiceImpl 리팩토링 및 구조 개선 제안

## 1. 개요
현재 `EventQueryServiceImpl`은 사건(Event) 조회 로직뿐만 아니라 복잡한 그래프 탐색 알고리즘과 데이터 가공(DTO Enrichment) 로직이 집중되어 있어 가독성과 유지보수성이 저하된 상태임. 이에 대한 구체적인 이슈 분석과 개선 방향을 제안함.

## 2. 현재 코드의 주요 문제점 (Code Smell)

### 2.1 낮은 응집도와 비대한 클래스 (God Class)
- **책임 과중**: DB 조회(MyBatis Mapper 호출), 그래프 탐색(BFS/DFS), DTO 변환 및 데이터 보충(Reveal 정보 매핑)이 단일 클래스에서 모두 수행됨.
- **코드 길이**: 클래스가 400라인을 넘어가며, 주요 메서드들이 80~100라인에 육박함.

### 2.2 중복된 조립(Assembling) 로직
- `getEventsByDrama`, `getEventsByCharacter`, `getCoEvents`, `traverseEvents` 등 이벤트를 목록으로 반환하는 모든 메서드에서 다음 패턴이 반복됨:
  ```java
  // 중복 패턴
  Map<Long, EventReveal> revealMap = getRevealMap(events);
  return events.stream()
          .map(e -> toDTO(e, revealMap.get(e.getId())))
          .collect(Collectors.toList());
  ```
- 새로운 메타데이터(예: 첨부 이미지, 태그 등)가 추가될 때마다 모든 메서드의 조립 로직을 일일이 수정해야 하는 번거로움이 있음.

### 2.3 알고리즘과 도메인 로직의 혼재
- `traverseEvents`와 `getCharacterPath` 메서드는 인접 리스트 탐색 로직(Visited 관리, Frontier 갱신 등)과 DB 필터링 로직이 뒤섞여 있어 가독성이 매우 낮음.
- 정체 공개 시 타임라인을 병합하는 로직(`getEventsByCharacter` 내의 PartnerId 처리)이 서비스 레이어 깊숙이 박혀 있어 정책 변경에 취약함.

---

## 3. 리팩토링 제안 방향

### 3.1 레이어드 아키텍처 기반 책임 분리
1. **EventAssembler (또는 Mapper/Converter)**:
   - `Event` 엔티티를 `EventResponseDTO`로 변환하는 전용 컴포넌트 도입.
   - **Enrichment 전담**: 변환 시 필요한 `EventReveal`(폭로 정보) 등 추가 데이터를 Batch로 가져와 매핑하는 책임을 이 레이어로 이동.
   - 서비스는 "무슨 데이터를 가져올지"만 결정하고, "어떻게 조립할지"는 Assembler에게 위임.

2. **GraphExplorer (알고리즘 분리)**:
   - BFS 알고리즘 및 노드 간 거리 계산 등을 처리하는 순수 로직 컴포넌트.
   - 서비스 레이어에서는 복잡한 `while`이나 `for` 루프 없이 탐색 결과 리스트만 받도록 추상화.

### 3.2 기대 결과 1: 파일 구조의 명확화
`EventAssembler` 도입 시 다음과 같이 책임에 따른 파일 분리가 이루어짐:
- `com.nospoiler.eventservice.service.assembler.EventAssembler`: [신규] 엔티티 조립 및 DTO 변환 전담.
- `com.nospoiler.eventservice.dto.EventResponseDTO`: 데이터 모델 유지.
- `com.nospoiler.eventservice.service.EventQueryServiceImpl`: 비즈니스 흐름 제어에 집중.

### 3.3 기대 결과 2: 코드 다이어트 및 가독성 향상
- **서비스 코드 슬림화**: 내부에 비대하게 존재하던 `toDTO()`, `getRevealMap()` 등의 유틸리티성 메서드가 제거됨에 따라 클래스 크기가 약 30~40% 줄어듦.
- **선언적 로직**: 서비스 메서드가 "어떻게 조립하는가"가 아닌 "무엇을 조회하는가"에 집중하게 되어, 코드가 한눈에 읽히는 '선언적(Declarative)' 코드로 변모함.

### 3.4 기대 결과 3: 구조적 이점 (Clear Roles)
파일이 추가됨에도 불구하고 전체 시스템의 유지보수성은 오히려 향상됨:
1. **Mapper (Persistence)**: SQL과 DB 인터렉션에만 집중.
2. **Service (Business)**: 도메인 로직, 트랜잭션, 검색 조건 판별에만 집중.
3. **Assembler (Enrichment)**: 여러 출처(Event, Reveal, Character 등)의 데이터를 합쳐서 UI용 응답 객체로 포장하는 일에만 집중.

## 4. 리팩토링 로직 예시 (After 시뮬레이션)
```java
// 서비스 코드가 비즈니스 핵심만 남고 매우 간결해짐
@Override
public List<EventResponseDTO> getEventsByDrama(Long dramaId, ...) {
    // 1. 데이터 조회 (Service의 본질적 역할)
    List<Event> events = eventMapper.findByDramaFiltered(...);
    
    // 2. 조립 및 가공 위임 (Assembler에게 맡김)
    return eventAssembler.toResponseList(events, safeUpToEpisode); 
}
```

## 4. 해결 완료 및 개선 사항 (2025-02-06 업데이트)

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

## 5. 결론 및 향후 계획 (Next Steps)

금일 작업을 통해 **'Reveal' 데이터의 분류 정확도와 시스템 적재 로직의 정합성**을 확보했습니다. 이제 데이터베이스에는 스포일러 방지 로직을 수행할 수 있는 고품질의 메타데이터가 적재됩니다.

### 향후 계획
1.  **전체 데이터셋 적재**: 나머지 에피소드 데이터셋에 대해 Bulk Insert 수행 및 데이터 검증.
2.  **프론트엔드 통합 (Next Week)**:
    *   8화 이후 시점에서 `EventReveal` 데이터를 기반으로 **프론트맨과 황인호의 타임라인을 하나로 합쳐서 보여주는 UI 로직** 구현.
    *   스포일러 필터링이 요약(Summary) 텍스트에 제대로 적용되는지 확인.
3.  **코드 리팩토링 (ex15 논의 사항)**:
    *   `EventQueryServiceImpl`의 비대해진 조회 로직을 `EventAssembler` 도입 등을 통해 다이어트.
    *   `EventRevealMapper`에 Bulk 조회 쿼리 추가로 N+1 문제 해결.

---
**작성일**: 2026-02-06
**작성자**: Antigravity (AI Assistant)

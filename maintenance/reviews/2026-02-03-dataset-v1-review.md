# 1차 데이터셋 작업 및 결과물 리뷰 (2026-02-03)
> Author: Team Member B | Recorded by: Team Member C

## 1. Frontend
- **정체 공개 (Identity Reveal)**
  - 인물이 언급될 때 이미지가 표시되어야 함.
  - 단, **정체가 공개된 시점(Flag)** 이후에만 이미지가 공개되어야 함 (스포일러 방지).
- **위키 검증소 (Wiki Verification)**
  - 인물별, 에피소드별 필터링/뷰 기능 필요.
- **위키 기여 프로세스 고도화 (Wiki Contribution)**
  - 사용자 기여도 향상을 위한 다중 선택 및 상세 제어 기능.
  - **Proposed Workflow**:
    1. 기여자가 문장(문단) 작성.
    2. AI에게 분석 요청 (비동기 대기).
    3. AI가 [이벤트별 인물, PredicateCode, RefinedSummary]로 자동 분류하여 제안.
    4. 기여자가 결과 확인 및 수정 (인물 추가/삭제, PredicateCode 변경, 요약문 수정).
    5. 수정된 내용을 바탕으로 AI 재요청 또는 최종 제출.

## 2. Backend
- **중복 데이터 처리 (Deduplication)**
  - 백엔드 필터링(Matching Logic)을 통한 자동 반려.
  - 검증소에서 사용자(Crowd)가 직접 판별.
- **문장 분해 및 저장 (Sentence Decomposition)**
  - LLM을 활용한 문장 분해 처리 (현재는 Mockup 고려).
  - 다중 이벤트의 분리(Atomic Event extraction): 한 문장에 여러 이벤트가 포함된 경우 이를 개별 이벤트 단위(예: 2문장)로 분해하는 과정.
  - 문단 단위의 문장화(Sentencization): 문단 단위로 주어졌을 때 이를 유의미한 문장 단위로 분해하는 처리를 포함함.
- **관점별 재서술 (Rashomon Effect)**
  - 같은 사건이라도 인물에 따라 서술이 달라져야 함.
  - 한 문장이 작성되면 상대방의 입장에서 재서술된 문장이 자동으로 생성될 수 있음.
  - 예시 (SUICIDE_AFTER_REQUEST):
    - Actor 관점: "{actor}는 {target}에게 마지막 부탁을 남기고 자결했다."
    - Recipient 관점: "{recipient}는 {actor}의 마지막 부탁을 듣고 그의 죽음을 목격했다."
  - 저장 및 캐싱 전략:
    - 재서술된 문장들을 효율적으로 관리하기 위해 [In-Memory Cache (Redis) / DB 저장 / 캐시+DB 하이브리드] 형태 고려.
- **Predicate 확장**
  - `predicate_suggestion` 로그를 분석하여 유의미한 코드 추가.
- **비선형적 시간 순서 (Non-linear Timeline)**
  - 같은 에피소드 내에서도 사건 발생 순서가 뒤섞일 수 있음.
  - 해결책: 프롬프트 고도화 또는 순서 정렬 로직 개선 필요.
- **RAG / External API**
  - MS API 등 외부 RAG 솔루션 도입 고려.
- **Event Reveal 처리**
  - `event_reveal` 테이블이 비어있는 상태에 대한 처리 방안 수립 필요.

## 3. Database
- **진화 방향 (Evolution)**
  - V4, V5 단계에서 RDF(Resource Description Framework), OWL(Web Ontology Language) 도입 가능성 예상.
  - 본격적인 Knowledge Graph 구조로의 전환 대비.

## 4. Agent Suggestion (Image Spoiler Protection)
- **문제 인식**: 인물의 단순 "언급(Involved)"과 "정체/얼굴 공개(Reveal)"는 다름. 가면 쓴 인물이나 반전 캐릭터의 이미지가 미리 노출되면 치명적임.
- **해결 제안 (V3 Ontology)**:
  - **초기 상태(Default State)**: 캐릭터별 `isHidden` (default: false) 속성 정의. 반전 캐릭터는 true로 시작.
  - **해금 트리거(Unlock Trigger)**: `PredicateCode`에 `IDENTITY_REVEAL` 또는 `FACE_REVEAL` 추가.
  - **로직**: 사용자의 `safeUpToEpisode` 시점 이전에 `REVEAL` 이벤트가 존재해야만 이미지/실명(True Name)을 반환.
  - **UI/UX**: 해금 전까지는 [실루엣 이미지 + 가명/???] 처리.
  - **구현 전략(Implementation Strategy)**:
    - `REVEALS` 코드는 이미 존재함.
    - **핵심**: "누가 반전 캐릭터인가?"를 정의하는 시점.
      - **옵션 A (Admin Pre-set)**: 관리자가 캐릭터 생성 시 `is_hidden=true`로 설정 (확실하지만 번거로움).
      - **옵션 B (Crowd Contribution)**:
        - 관리자가 모든 드라마의 반전 요소를 알 수 없음.
        - 위키 기여자가 작성 시 **"이 캐릭터는 나중에 정체가 밝혀지는 반전 인물입니다"** 체크박스(`is_spoiler_identity`)를 선택하도록 유도.
        - AI/검증소 승인 시 `is_hidden=true` 반영.
    - **결론(Decision)**: 기술적 메커니즘은 `is_hidden=true`를 확정 사용. 데이터 구축은 확장성을 위해 **기여자(Crowd) 주도 방식(옵션 B)**을 주력으로 채택함.

  - **사례 연구: 오징어 게임 (황인호 vs 프론트맨)**:
    - **딜레마 (Image Paradox)**:
      - 9화에 처음 공개되는 황인호의 얼굴(이병헌) 자체가 거대한 스포일러.
      - 4화 실종 언급 시점에 황인호 ID에 이 사진을 쓰면 바로 스포일러가 됨.
    - **최적의 접근법 (Separate IDs + Virtual Merge)**:
      - **ID 분리**: '황인호(ID A)'와 '프론트맨(ID B)'를 별도로 관리.
      - **이미지 전략**:
        - **ID A (황인호)**: 1~8화 구간에는 **[실루엣/이미지 없음]**으로 처리 (혹은 작중 등장하는 증명사진이 있다면 사용). **절대 9화의 정체 공개 사진을 미리 쓰지 않음.**
        - **ID B (프론트맨)**: **[가면 쓴 사진]** 사용.
      - **9화 Reveal 이벤트 발생 시**:
        - 시스템이 A와 B를 `REVEALS`로 연결.
        - **병합 & 해금**: ID B(프론트맨) 클릭 시 ID A(황인호)의 정보가 합쳐짐. 이때 비로소 A의 프로필 이미지를 **[9화의 정체 공개 사진]**으로 업데이트(교체)하거나 해금함.
      - **결론**: 분리된 ID를 써야 "황인호는 실루엣, 프론트맨은 가면"이라는 안전한 초기 상태를 유지할 수 있음.

  - **Frontend 검증 (CharacterCard.tsx)**:
    - **현황**: 현재는 `currentEpisode < firstAppearanceEpisode` 조건으로만 실루엣(Lock) 처리 중.
    - **개선점**: 단순히 등장했다고 해서 얼굴을 까면 안 됨.
    - **Mod**: `isLocked` 조건에 `|| character.isHidden`을 추가하여, 언급이 되더라도(`Event`가 생성되더라도) `is_hidden` 상태라면 실루엣을 유지하도록 변경 필요. (클릭 가능 여부는 기획에 따라 결정)

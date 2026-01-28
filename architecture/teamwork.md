# 팀워크 노트

작성일: 2026-01-20

## 파인딩
- High: Wiki->Event 계약 불일치 (refs: services/wiki-service/src/main/java/com/nospoiler/wikiservice/service/WikiSubmissionService.java, services/event-service/src/main/java/com/nospoiler/eventservice/dto/EventRequestDTO.java, services/event-service/src/main/java/com/nospoiler/eventservice/dto/EventResponseDTO.java)
- High: EventServiceClient 기본 URL이 8083으로 설정됨 (refs: services/event-service/src/main/java/com/nospoiler/eventservice/client/EventServiceClient.java)
- Medium: Auth logout이 substring 방식 파싱 사용 (refs: services/auth-service/src/main/java/com/nospoiler/authservice/controller/AuthController.java)
- Medium: Auth reissue가 access token을 충분히 검증하지 않음 (refs: services/auth-service/src/main/java/com/nospoiler/authservice/service/AuthService.java)
- Medium: Gateway secret이 base64만 사용되어 auth 기대와 불일치 가능 (refs: services/gateway/src/main/java/com/nospoiler/gateway/config/SecurityConfig.java)
- Low: User profile 이미지 엔드포인트 경로가 API 문서와 불일치 (refs: services/user-service/src/main/java/com/nospoiler/userservice/controller/UserController.java)

## API 계약 정렬 상태 (api-contract.md)
- 불일치:
  - Auth base URL: 스펙 /api/auth vs 구현 /api/auth/v1 (refs: services/auth-service/src/main/java/com/nospoiler/authservice/controller/AuthController.java)
  - TokenDto 필드명: 스펙 expiresIn vs 구현 accessTokenExpiresIn (refs: services/auth-service/src/main/java/com/nospoiler/authservice/security/TokenDto.java)
- 정렬됨:
  - Wiki: /api/wiki/v1 + submissions/verifications (refs: services/wiki-service/src/main/java/com/nospoiler/wikiservice/controller/WikiSubmissionController.java)
  - Event: /api/event/v1 create/get/search (refs: services/event-service/src/main/java/com/nospoiler/eventservice/controller/EventController.java)
  - Event Query (L1-3): 루트 경로 일치 (refs: services/event-service/src/main/java/com/nospoiler/eventservice/controller/EventQueryController.java)
  - QA: /qa + /episode-range 일치 (refs: services/qa-service/src/main/java/com/nospoiler/qaservice/controller/QaController.java)

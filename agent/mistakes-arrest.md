# Mistakes Arrest

Purpose
- 경로 실수(컨트롤러/스펙/게이트웨이 불일치) 재발 방지.

Trigger
- 404/경로 불일치 발생
- v1/v2 prefix 혼선
- "api-contract랑 경로 안맞음" 피드백

Alignment Flow (Keyword Check)
1) 키워드 스캔
- controllers: `@RequestMapping`, `@GetMapping`, `@PostMapping`
- docs: `Base URL`, `GET /`, `POST /`
- gateway: `/api/*` routes

2) 기준 문서 확인
- `fivecircles/architecture/specs/api-contract.md`
- `fivecircles/architecture/specs/event-v2-api.md`
- `services/api-gateway/src/main/resources/application-docker.yml`

3) 불일치 분류
- [경로설정] base URL 불일치
- [api분류] v1/v2 prefix 혼선
- [게이트웨이] 라우트 누락/리라이트 문제

4) 수정 순서
- 컨트롤러 경로 → 스펙 문서 → 게이트웨이 라우트
- 내 영역 외 파일은 `origin/develop`로 되돌림

5) 테스트
- 서버 curl로 v1/v2 대표 엔드포인트 확인

6) 기록
- `fivecircles/work/update.md`
- 필요 시 `fivecircles/scoring/optimization.md`

Response Output Arrest
- Trigger: "diff 보여줘", "출력 보여줘" 요청인데 요약만 전달한 경우.
- Rule: 요청받은 출력(디프/로그)을 먼저 제공하고, 요약은 확인 요청 후 제공.

Commit Timing Guardrail
1) 커밋 전 체크
- "새 브랜치 + 투두 완료 후 커밋" 지시 여부 확인
- 지시가 있으면 커밋 금지
2) 실수 시 조치
- 즉시 스테이징/커밋 중단
- `fivecircles/agent/mistakes-repeating.md`에 기록

Server Sync Guardrail
1) 테스트 전 체크
- `fivecircles/architecture/specs/test-server-policy-4C.md`의 Latest Sync Check 실행
2) 불일치 시 조치
- 서버에서 develop 최신화 후 테스트 재개

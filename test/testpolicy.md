# Test Policy

## Required
- 새 행동(새 기능/새 규칙)에는 unit test가 있어야 한다.
- integration test가 필요한 경우(해당 시):
  - external I/O 추가/변경
  - persistence boundary 변경
  - API contract 변경

## Evidence
- command output snippet OR
- CI link OR
- 저장된 로그 파일

## Error Logs
실패 시 `test/errorlogs/`에 새 파일 생성:
- `YYYY-MM-DD__short-title.md`
포함:
- failing test name
- error message
- fix summary
- pass evidence

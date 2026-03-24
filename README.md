# fivecircles

이 폴더는 프로젝트에 “개발 5사이클(+Integrate)” 운영체제를 이식하기 위한 템플릿입니다.

## 어디에 뭐가 있나
- **agent/**: 에이전트 행동 지침(총지휘소). 에이전트는 여기부터 읽고 움직입니다.
- **requirements/**: 프로젝트 요구사항. 사용자와 합의/논쟁(debate)하고 확정하는 공간입니다.
- **spec/**: 요구사항/결정에 기반해 “분석된 기술적 내용”만 기록합니다. (설계·API·DB·성능·보안 등)
- **architecture/**: 작업 배치/태스크 분해(플랜)
- **work/**: 실행 로그(결정, 근거, 결과)
- **test/**: 테스트 정책 및 실패 로그
- **maintenance/**: 유지보수/새 요구사항 환류
- **scoring/**: (옵션) 에이전트 점수 규칙/기록

## 시작 순서 (사람/에이전트 공통)
1) agent/README.md
2) requirements/README.md
3) architecture/todolist.md 작성 후 사이클 시작

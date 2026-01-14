# fivecircles

이 폴더는 프로젝트에 “개발 5사이클(+Integrate)” 운영체제를 이식하기 위한 템플릿입니다.

## License
This project’s design and governance documents are licensed under **CC BY 4.0**.

## 시작하기
- architecture/specs/README.md를 읽고 워크플로우를 초기화합니다.

## 어디에 뭐가 있나
- architecture/specs/README.md 전체 워크플로우를 정의합니다.
- **requirements/**: 프로젝트 요구사항. 사용자와 합의/논쟁(debate)하고 확정하는 공간입니다.
- **architecture/spec/**: architecture/specs/README.md에 명시된 절차에 따라, 요구사항/결정에 기반해 “분석된 기술적 내용”만 기록합니다. (설계·API·DB·성능·보안 등)
- **architecture/todo/**: 작업 배치/태스크 분해(플랜)
- **work/**: 실행 로그(결정, 근거, 결과), 업데이트 기록
- **test/**: 테스트 정책 및 실패 로그, 개선사항 기록/제안
- **maintenance/**: 유지보수/새 요구사항 환류
- **scoring/**: 에이전트 점수 규칙/기록, 더 나은 코딩 절차 제안

## 시작 순서 (사람/에이전트 공통)
1) architecture/specs/README.md
2) agent/agent-guidelines.md
3) requirements/README.md
4) architecture/todolist.md 작성 후 사이클 시작

===

이 섹션은 사람이 읽기위한 정보를 담고 있습니다.(설명서)

-초기화방법
에이전트에게 프롬프트 입력:
"fivecircles/README.md를 읽고 운영방침을 초기화하라"

- 개발시 자주 쓰는 프롬프트들:
"스펙(architecture/specs)의 내용을 확인하고 그대로 개발하라"
    (세세히 명령 가능 예: architecture/specs에서 최신 sql파일을 확인하고 이에 맞게 (기능)을 개발해라)
"투두리스트를 확인하고 다음할일을 정리해라"
"learn-from-log, optimization을 참고하여 개선사항을 제시해라"(에러잡기)
"다음 요구사항을 확인하고 투두리스트 업데이트 후 workpolicy에 따른 사이클대로 개발 진행해라:
{요구사항-적기}"


중요! 스펙은 항상 최신으로 유지하고 바꿀때마다 인지시켜줘야 합니다.


새로운 세션(에이전트)를 불러와도 컨텍스트 로스를 최소화하여 사용가능합니다.
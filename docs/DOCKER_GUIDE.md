# Docker 운영 가이드 (Docker Strategy)

MSA 서비스 구축 시 일관성 있는 컨테이너 환경을 제공하기 위한 가이드입니다.

## 1. 파일 구조 전략

모든 마이크로서비스는 다음과 같은 구조를 따르는 것을 권장합니다.

```text
service-name/
├── Dockerfile                  # docs/docker-template/Dockerfile 참조
└── src/
    └── main/
        └── resources/
            ├── application.yml         # 로컬 개발용 (Local DB 등)
            └── application-docker.yml  # 배포/컨테이너용 (환경변수 기반)
```

## 2. Dockerfile 규칙 (Multi-stage Build)

우리는 **Multi-stage Build**를 사용하여 이미지 크기를 최소화하고 보안을 강화합니다.
템플릿 파일: `docs/docker-template/Dockerfile`

1.  **Build Stage**: `eclipse-temurin:17-jdk-alpine` 사용. 소스 컴파일 및 빌드 수행.
2.  **Run Stage**: `eclipse-temurin:17-jre-alpine` 사용. 실행에 필요한 JAR만 복사.

## 3. 환경 설정 전략 (Configuration)

### 로컬 환경 (Local)

- `application.yml` 사용
- 개발 편의성을 위해 고정된 값(localhost 등) 사용 가능

### 도커 환경 (Docker)

- `application-docker.yml` 사용
- **반드시 환경 변수(`${VAR_NAME}`)를 통해 민감 정보를 주입**해야 합니다.
- 실행 시 프로파일 지정: `--spring.profiles.active=docker`

## 4. .dockerignore

프로젝트 루트의 `.dockerignore` 파일은 모든 서비스 빌드 시 공통으로 적용됩니다.
불필요한 파일(`.git`, `.agent`, `local config` 등)이 빌드 컨텍스트에 포함되지 않도록 관리합니다.

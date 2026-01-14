# Backend Convention & Strategy

NoSpoiler 프로젝트의 백엔드 개발 표준 및 전략 가이드입니다.
모든 마이크로서비스는 이 가이드를 준수하여 개발되어야 합니다.

---

## 1. 아키텍처 및 패키지 구조

### 기술 스택 (Tech Stack)

- **Language**: Java 17
- **Framework**: Spring Boot 3.x
- **Persistence**: MyBatis 3.x, MySQL 8.x
- **Build**: Gradle (Multi-module 권장)

### 패키지 구조 (Package Structure)

도메인 중심의 레이어드 아키텍처를 따릅니다.

```text
com.nospoiler.{service-name}/
├── config/              # 글로벌 설정 (Swagger, WebMvc 등)
├── common/              # 공통 유틸리티 (Exception, Response)
├── controller/          # [Controller Layer] 웹 요청 진입점
├── service/             # [Service Layer] 비즈니스 로직, 트랜잭션 관리
├── domain/              # [Domain Layer] 핵심 비즈니스 객체 (POJO 권장)
├── mapper/              # [Persistence Layer] MyBatis Interface
└── dto/                 # [DTO] 계층 간 데이터 전송 객체
    ├── request/
    └── response/
```

> **규칙**: MyBatis XML 파일은 Java 소스가 아닌 `src/main/resources/mapper/{ServiceName}/*.xml` 경로에 위치시킵니다.

---

## 2. 핵심 개발 전략 (Core Strategies)

### 2.1 API 문서화 (Swagger / Springdoc)

**[Why?]**

- 코드와 문서의 불일치(Sync 문제)를 해결하고, 실시간 테스트 환경을 제공하기 위함입니다.
- Notion에는 기획 의도만 적고, 상세 명세는 Swagger 링크로 대체하여 유지보수성을 높입니다.

**[Rule]**

- 모든 Controller와 DTO에는 `@Tag`, `@Operation`, `@Schema` 어노테이션을 사용하여 설명을 명시해야 합니다.

### 2.2 통신 전략 (OpenFeign)

**[Why?]**

- `RestTemplate`의 하드코딩된 URL 방식은 관리가 어렵고 가독성이 떨어집니다.
- `OpenFeign`은 인터페이스 선언만으로 호출이 가능하여 비즈니스 로직에 집중할 수 있게 합니다.

**[Rule]**

- **인증 헤더 전파**: Gateway에서 넘어온 `X-User-Id` 등의 헤더를 다른 서비스로 넘길 때는 `FeignRequestInterceptor`를 사용하여 자동으로 전파해야 합니다.

### 2.3 DB 마이그레이션 (Flyway)

**[Why?]**

- MSA 환경에서 서비스별 DB 스키마 버전 파편화 문제를 방지합니다.
- 서버 구동 시점에 DB 스키마 상태를 강제로 검증하여, 코드와 DB의 불일치로 인한 런타임 에러를 원천 차단합니다.

**[Rule]**

- `src/main/resources/db/migration` 경로에 `V1__init.sql` 형식으로 스크립트를 관리합니다.
- 로컬 개발 시에도 Workbench 등을 통한 수동 변경(DDL)을 지양하고, 반드시 마이그레이션 파일을 추가하여 반영합니다.

---

## 3. 코드 컨벤션 (Code Convention)

### 3.1 DTO (Data Transfer Object)

- **Map 사용 금지**: `Map<String, Object>` 형태의 파라미터 전달을 엄격히 금지합니다.
- **Record 사용 고려**: 불변 객체인 경우 Java 14+ `record` 타입을 적극 활용합니다.
- **네이밍**: `~Request`, `~Response`, `~Dto` 접미사를 명확히 사용합니다.

### 3.2 Lombok 사용 가이드

- `@Data` **사용 지양**: 무분별한 Setter 노출을 방지합니다.
- **권장 조합**:
  ```java
  @Getter
  @Builder
  @NoArgsConstructor(access = AccessLevel.PROTECTED)
  @AllArgsConstructor
  ```

### 3.3 로깅 (Logging)

- **AOP 적용**: Controller의 진입/종료 로그는 AOP로 자동화합니다. (수동 로그 최소화)
- **환경별 레벨**:
  - `local`: **DEBUG** (SQL, 파라미터 상세 확인)
  - `prod`: **INFO** (주요 흐름 및 ERROR만 기록)

---

## [Appendix] Code Snippets (샘플 코드)

아래 코드를 템플릿으로 활용하십시오.

### 1. 공통 응답 객체 (ApiResponse.java)

```java
@Getter
@Builder
@AllArgsConstructor
public class ApiResponse<T> {
    private final String result; // "SUCCESS" or "ERROR"
    private final T data;
    private final String message;
    private final String errorCode;

    public static <T> ApiResponse<T> success(T data) {
        return ApiResponse.<T>builder()
                .result("SUCCESS")
                .data(data)
                .build();
    }

    public static <T> ApiResponse<T> error(ErrorCode errorCode) {
        return ApiResponse.<T>builder()
                .result("ERROR")
                .message(errorCode.getMessage())
                .errorCode(errorCode.getCode())
                .build();
    }
}
```

### 2. Controller 템플릿 (Swagger 적용)

```java
@Tag(name = "사용자 API", description = "사용자 가입 및 프로필 관리")
@RestController
@RequestMapping("/api/v1/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @Operation(summary = "회원 가입", description = "신규 사용자를 등록합니다.")
    @PostMapping("/signup")
    public ApiResponse<Long> signup(@RequestBody @Valid UserSignupRequest request) {
        Long userId = userService.signup(request);
        return ApiResponse.success(userId);
    }
}
```

### 3. MyBatis XML 구조

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
"http://mybatis.org/dtd/mybatis-3-mapper.dtd">

<!-- Namespace는 Mapper Interface의 Full Path와 일치해야 함 -->
<mapper namespace="com.nospoiler.userservice.mapper.UserMapper">

    <insert id="save" useGeneratedKeys="true" keyProperty="id">
        INSERT INTO users (email, nickname)
        VALUES (#{email}, #{nickname})
    </insert>

</mapper>
```

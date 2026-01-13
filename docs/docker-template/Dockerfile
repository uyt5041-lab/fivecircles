# ==============================================================================
# Dockerfile Template for Spring Boot / Gradle Projects
# Based on: Multi-stage build pattern using eclipse-temurin:17
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1: Build
# ------------------------------------------------------------------------------
FROM eclipse-temurin:17-jdk-alpine AS build
WORKDIR /app

# Gradle Wrapper & Settings Coping (Leverage Docker Cache)
COPY gradlew .
COPY gradle gradle
COPY build.gradle settings.gradle ./

# Grant Execution Permission
RUN chmod +x gradlew

# Download Dependencies (Cached if build.gradle hasn't changed)
RUN ./gradlew dependencies --no-daemon

# Copy Source Code
COPY src src

# Build Application (Skip Tests for faster build)
# Tip: You might want to remove '-x test' in CI/CD pipelines
RUN ./gradlew bootJar -x test --no-daemon

# ------------------------------------------------------------------------------
# Stage 2: Run
# ------------------------------------------------------------------------------
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app

# Copy executable jar from build stage
COPY --from=build /app/build/libs/*.jar app.jar

# Expose Application Port
EXPOSE 8080

# Run Application
# Tip: Pass profiles or other arguments via CMD or ENTRYPOINT
CMD ["java", "-jar", "app.jar", "--spring.profiles.active=docker"]

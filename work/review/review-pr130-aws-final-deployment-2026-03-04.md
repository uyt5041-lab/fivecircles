# Review: PR #130 `fix/aws-final-deployment` (2026-03-04)

## Scope
- Target: `PR #130` (`fix/aws-final-deployment`)
- Compare: `pr-130-merge^1..pr-130-head`
- Main areas reviewed:
  - API gateway/service routing for docker profile
  - auth/user/wiki/notification runtime config changes
  - frontend auth flow adjustments

## Findings
1. [HIGH] Docker profile service discovery regresses the current compose environment.
- The PR changes docker-profile defaults from existing compose-resolvable names like `nospoiler-user-service` to `user-service.nospoiler.local` and similar names in multiple services.
- Current compose only defines container/service names on the `nospoiler-network`; it does not add any `*.nospoiler.local` aliases.
- As a result, gateway/auth/wiki inter-service calls will fail in the current docker setup unless every service URL env is explicitly overridden or compose is updated together.
- Refs:
  - `/tmp/nospoiler-pr130/services/api-gateway/src/main/resources/application-docker.yml:22`
  - `/tmp/nospoiler-pr130/services/api-gateway/src/main/resources/application-docker.yml:30`
  - `/tmp/nospoiler-pr130/services/api-gateway/src/main/resources/application-docker.yml:42`
  - `/tmp/nospoiler-pr130/services/auth-service/src/main/resources/application-docker.yml:82`
  - `/tmp/nospoiler-pr130/services/wiki-service/src/main/resources/application-docker.yml:20`
  - `/tmp/nospoiler-pr130/infra/docker-compose.yml:102`
  - `/tmp/nospoiler-pr130/infra/docker-compose.yml:126`
  - `/tmp/nospoiler-pr130/infra/docker-compose.yml:151`

2. [HIGH] Notification API route is renamed to singular only in gateway, breaking existing frontend and backend contracts.
- Gateway now routes only `/api/notification/**`.
- Frontend notification API and SSE still call `/api/notifications/v1...` (plural), and notification-service controllers also expose `/api/notifications/v1...`.
- In docker/prod behind gateway, notification list/read/SSE calls will 404 or miss the route.
- Refs:
  - `/tmp/nospoiler-pr130/services/api-gateway/src/main/resources/application-docker.yml:61`
  - `/tmp/nospoiler-pr130/front/common/services/notificationApi.ts:35`
  - `/tmp/nospoiler-pr130/front/hooks/useNotificationSource.ts:12`
  - `/tmp/nospoiler-pr130/services/notification-service/src/main/java/com/nospoiler/notificationservice/controller/NotificationController.java:27`

3. [HIGH] auth-service Redis config now forces cluster mode against the repo's current standalone Redis.
- `RedisConfig` unconditionally builds `RedisClusterConfiguration` from `spring.data.redis.host/port`.
- The checked-in compose still runs plain `redis:alpine` as a standalone node, not a Redis Cluster deployment.
- That means auth-service token/logout/blacklist flows risk failing with cluster-topology errors in the default docker environment.
- Refs:
  - `/tmp/nospoiler-pr130/services/auth-service/src/main/java/com/nospoiler/authservice/config/RedisConfig.java:24`
  - `/tmp/nospoiler-pr130/infra/docker-compose.yml:22`

4. [MEDIUM] OAuth callback handler now logs the raw access token to the browser console.
- `fetchUserProfile` logs the full token string before requesting `/api/user/v1/me`.
- This is a security regression because tokens become visible in browser console history, remote debugging sessions, and captured logs.
- Refs:
  - `/tmp/nospoiler-pr130/front/features/auth/OAuth2RedirectHandler.tsx:85`

## Decision
- REQUEST_CHANGES

## Next actions
1. Keep docker profile defaults compatible with the checked-in compose (`nospoiler-*`) or update compose/service-discovery aliases in the same PR.
2. Restore gateway notification route to `/api/notifications/**` unless frontend/backend are changed together.
3. Make Redis connection selectable: standalone by default, cluster only when explicit cluster nodes/config are provided.
4. Remove raw token logging from OAuth redirect flow and keep only redacted diagnostics.

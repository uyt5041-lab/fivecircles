Timestamp: 2026-01-20 12:31
Context: test server curl

Issues
1) POST http://localhost:8090/policy/check reset by peer

Resolution
- Fix docker-compose port mapping for spoiler-policy-service to 8090:8090

Prevention
- Keep container port aligned with app server.port or add docker profile config

# Test Server Connection Policy

Purpose
- Define how Team C services connect to test servers without diverging from local defaults.
- Keep connection config explicit and reproducible for integration checks.

Scope
- Applies to event-service and spoiler-policy-service test runs.
- QnA (qa-service) is excluded for now.

Defaults (Local)
- Event service: http://localhost:8089
- Spoiler policy service: http://localhost:8090

Environment Variables
- EVENT_SERVICE_URL: overrides the event-service base URL.
- POLICY_SERVICE_URL: overrides the spoiler-policy-service base URL.

Example (Local)
- EVENT_SERVICE_URL=http://localhost:8089
- POLICY_SERVICE_URL=http://localhost:8090

Example (Remote Test Server)
- EVENT_SERVICE_URL=https://test-event.nospoiler.local
- POLICY_SERVICE_URL=https://test-policy.nospoiler.local

Notes
- Use these variables in service configs when running integration checks.
- Keep the production URLs out of this file.

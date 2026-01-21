# Optimization Notes (Scoring)

Purpose
- Collect score-maximizing optimizations discovered during work.
- Reference this file when scoring to capture any applicable upgrade paths.

Log format (append each optimization):

Timestamp:
Area:
Optimization:
Why it increases score:
When to apply:
Related tasks/files:

Timestamp: 2026-01-16
Area: API/QnA endpoints
Optimization: Run backend tests after API changes to claim mandatory test scenario points.
Why it increases score: Test success yields +40 per agent-scoring-policy.md.
When to apply: After endpoint changes are merged.
Related tasks/files: services/event-service/src/main/java/com/nospoiler/eventservice/controller/EventController.java
Timestamp: 2026-01-21 09:57:19
Area: API versioning
Optimization: Confirm version prefix (/v1, /v2) and base path in api-contract + gateway before changing controller routes
Why it increases score: Avoids rework from path mismatch and duplicate deploy/test cycles
When to apply: Before editing controller mappings
Related tasks/files: services/event-service/src/main/java/com/nospoiler/eventservice/controller/EventController.java

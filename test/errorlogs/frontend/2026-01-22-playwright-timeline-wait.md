Timestamp: 2026-01-22 14:20
Context: Playwright dev login -> timeline check

Issues
1) Timeline list assertion ran before event API response, so event count was zero

Resolution
- Wait for /api/event/v2/dramas/{id}/events response and list render before asserting

Prevention
- Add explicit response waits for API-backed list assertions

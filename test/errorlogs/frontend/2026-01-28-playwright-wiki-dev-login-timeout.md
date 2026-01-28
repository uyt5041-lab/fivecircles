timestamp: 2026-01-28 18:21
area: frontend
page: Login/Wiki

summary:
- Wiki Playwright flow timed out after dev login

symptoms:
- Playwright waited for drama selection heading after clicking dev login; timeout hit

root_cause:
- DevAuth accounts not available on server, login stayed on /login without redirect

fix:
- Seed or use valid test account; avoid relying on devAuth in automation

result:
- Pending: adjust test to use API seed or ensure test user

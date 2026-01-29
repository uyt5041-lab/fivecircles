# Frontend Test Error Log

- **Timestamp**: 2026-01-28 17:07:49 +0900
- **Test**: Playwright `front/check_console.spec.js` (server URL)
- **Target**: http://100.120.44.64:3000
- **Result**: FAIL

## Summary
- Frontend console shows 502 Bad Gateway when fetching dramas; page did not render expected `h1` header.

## Repro
1. Deploy server with `docker compose up -d --build` on `bit-ts`.
2. Run:
   `PW_BASE_URL=http://100.120.44.64:3000 npx playwright test check_console.spec.js`

## Error
- Console: `Failed to load resource: the server responded with a status of 502 (Bad Gateway)`
- Console: `Failed to fetch dramas Error: HTTP 502`
- Playwright: `page.waitForSelector('h1')` timed out (30s)

## Suspected Cause
- Gateway/backend route not responding or upstream service down for drama list request.

## Next Fix
- Check gateway route + drama-service health on server.

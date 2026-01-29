# Frontend Test Error Log

- **Timestamp**: 2026-01-28 16:29:29 +0900
- **Test**: Playwright `front/check_console.spec.js`
- **Result**: FAIL

## Summary
- `page.waitForLoadState('networkidle')` timed out after 30s on initial page load.

## Repro
1. Start Vite dev server on `http://localhost:3000`.
2. Run `npx playwright test check_console.spec.js` in `front/`.

## Error
- `page.waitForLoadState: Test timeout of 30000ms exceeded` (line 21)
- Follow-up error when reading page content after timeout.

## Suspected Cause
- Network never goes idle (ongoing polling or websocket activity), so `networkidle` is not reached.

## Next Fix
- Switch to `domcontentloaded` or wait for a stable selector instead of `networkidle`.

# Frontend Test Error Log

- **Timestamp**: 2026-01-28 16:38:07 +0900
- **Test**: Playwright `front/check_console.spec.js`
- **Result**: FAIL

## Summary
- `page.waitForLoadState('networkidle')` timed out after 30s on initial page load during local preview.

## Repro
1. `cd front`
2. `npm run build`
3. `npm run preview -- --port 3000 --strictPort`
4. `npx playwright test check_console.spec.js`

## Error
- `page.waitForLoadState: Test timeout of 30000ms exceeded` (line 21)
- Follow-up error reading page content after timeout.

## Suspected Cause
- Network never goes idle (preview server keeps connections alive), so `networkidle` is not reached.

## Next Fix
- Replace `networkidle` with `domcontentloaded` or wait for a stable selector instead.

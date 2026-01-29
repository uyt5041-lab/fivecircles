timestamp: 2026-01-28 17:53
area: frontend
page: Playwright CLI

summary:
- Root Playwright run failed due to missing @playwright/test

symptoms:
- npx playwright test front/check_console.spec.js failed with module not found and test() called unexpectedly

root_cause:
- Repo root uses playwright package without @playwright/test; config/test runner resolved wrong context

fix:
- Run Playwright from front using @playwright/test and use root config without @playwright/test import

result:
- Playwright server flow passes when run from front

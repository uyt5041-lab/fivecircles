Timestamp: 2026-01-22 13:17
Context: Playwright dashboard modal check

Issues
1) getByText("타임라인") matched both nav and modal tab (strict mode violation)

Resolution
- Scope locator to Event V2 section container before checking tab

Prevention
- Use container-scoped locators when labels appear in multiple UI regions

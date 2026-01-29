timestamp: 2026-01-28 18:21
area: frontend
page: Timeline

summary:
- Timeline Playwright strict-mode error on cause text

symptoms:
- locator.getByText(expectedCause) matched both timeline card and detail list

root_cause:
- Locator scope not narrowed to detail panel section

fix:
- Scope to the '원인 사건' section and list items

result:
- Pending: update test selectors

Timestamp: 2026-01-29 13:32
Context: Playwright qa_widgets.spec.js

Issues
1) Drawer close click timed out; backdrop overlay intercepted pointer events

Resolution
- Use drawer backdrop selector for close in qa_widgets.spec.js

Prevention
- Close drawers via backdrop or stable selector to avoid overlay pointer interception

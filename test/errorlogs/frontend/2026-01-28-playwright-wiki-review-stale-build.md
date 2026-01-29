timestamp: 2026-01-28 18:28
area: frontend
page: Wiki Review

summary:
- Wiki review UI did not show seeded submission

symptoms:
- Playwright could not find submitted content on /wiki/reviews despite API showing it

root_cause:
- Server frontend still hard-coded dramaId=1; updated code not deployed

fix:
- Deploy latest frontend build before server Playwright run

result:
- Pending: redeploy and rerun

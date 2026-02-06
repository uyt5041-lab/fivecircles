# Frontend Browser Test Policy (4C)

Purpose
- Define how Team C runs frontend browser tests with Playwright.
- Keep server and local test routes consistent and reproducible.

Scope
- Frontend browser checks for the Team C web app.

Server Browser Test (Playwright)
- Push latest commits to the remote.
- Pull on the server before testing.
- Open the server URL with Playwright: http://100.120.44.64:3000/
- Note: `100.120.44.64` is the Windows host. Ubuntu/WSL base: `http://100.79.74.49:8080`. DB connections should use the Ubuntu host address (`DB_HOST`), not this IP.

Local Build Test (Playwright)
- Build the local frontend and run it on localhost.
- Open the local URL with Playwright: http://localhost:3000/

Notes
- Use Playwright MCP when available; otherwise run Playwright via CLI.
- Keep screenshots or traces only when needed for defect evidence.

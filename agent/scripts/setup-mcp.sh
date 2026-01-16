#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
ENV_FILE="$ROOT_DIR/.mcp-env.sh"

if [ ! -f "$ENV_FILE" ]; then
  cat <<'EOF' > "$ENV_FILE"
# MCP env vars (fill in values)
export NOTION_API_TOKEN=""
export GITHUB_TOKEN=""
export GITHUB_PERSONAL_ACCESS_TOKEN="$GITHUB_TOKEN"
export NOTION_MCP_PATH="$HOME/nospoiler-mcp-tools/notion-mcp/bin/cli.mjs"
EOF
  echo "Created $ENV_FILE"
else
  echo "Found $ENV_FILE (no changes)"
fi

if [ -z "${NOTION_API_TOKEN:-}" ]; then
  echo "NOTE: NOTION_API_TOKEN is not set. Edit $ENV_FILE."
fi

if [ -z "${GITHUB_TOKEN:-}" ]; then
  echo "NOTE: GITHUB_TOKEN is not set. Edit $ENV_FILE."
fi

if [ -z "${NOTION_MCP_PATH:-}" ] || [ ! -x "${NOTION_MCP_PATH:-}" ]; then
  echo "Notion MCP not found at ${NOTION_MCP_PATH:-<unset>}"
  echo "Install Notion MCP locally and update NOTION_MCP_PATH in $ENV_FILE."
fi

echo "Add to ~/.zshrc: source $ENV_FILE"

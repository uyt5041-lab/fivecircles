#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: agent-tmux.sh [--session NAME] [--layout windows|panes] [--attach|--no-attach] [--kill]

Environment overrides:
  AGENT_PLAN_CMD   (default: agent-plan)
  AGENT_CODE_CMD   (default: agent-code)
  AGENT_CODEX_CMD  (default: agent-codex)
  AGENT_REVIEW_CMD (default: agent-review)
EOF
}

SESSION="agents"
LAYOUT="windows"
ATTACH=1
KILL_EXISTING=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --session)
      SESSION="$2"
      shift 2
      ;;
    --layout)
      LAYOUT="$2"
      shift 2
      ;;
    --attach)
      ATTACH=1
      shift
      ;;
    --no-attach)
      ATTACH=0
      shift
      ;;
    --kill)
      KILL_EXISTING=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown arg: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if ! command -v tmux >/dev/null 2>&1; then
  echo "tmux not found. Install tmux first (e.g., 'brew install tmux')." >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"

PLAN_CMD="${AGENT_PLAN_CMD:-agent-plan}"
CODE_CMD="${AGENT_CODE_CMD:-agent-code}"
CODEX_CMD="${AGENT_CODEX_CMD:-agent-codex}"
REVIEW_CMD="${AGENT_REVIEW_CMD:-agent-review}"

if tmux has-session -t "$SESSION" 2>/dev/null; then
  if [[ "$KILL_EXISTING" -eq 1 ]]; then
    tmux kill-session -t "$SESSION"
  else
    echo "tmux session '$SESSION' already exists." >&2
    if [[ "$ATTACH" -eq 1 ]]; then
      tmux attach -t "$SESSION"
    fi
    exit 0
  fi
fi

if [[ "$LAYOUT" == "panes" ]]; then
  tmux new-session -d -s "$SESSION" -n agents -c "$REPO_DIR"
  tmux split-window -t "$SESSION:agents" -h -c "$REPO_DIR"
  tmux split-window -t "$SESSION:agents" -v -c "$REPO_DIR"
  tmux select-pane -t "$SESSION:agents".0
  tmux split-window -t "$SESSION:agents" -v -c "$REPO_DIR"
  tmux select-layout -t "$SESSION:agents" tiled

  tmux send-keys -t "$SESSION:agents".0 "$PLAN_CMD" C-m
  tmux send-keys -t "$SESSION:agents".1 "$CODE_CMD" C-m
  tmux send-keys -t "$SESSION:agents".2 "$CODEX_CMD" C-m
  tmux send-keys -t "$SESSION:agents".3 "$REVIEW_CMD" C-m
else
  tmux new-session -d -s "$SESSION" -n planner -c "$REPO_DIR"
  tmux new-window -t "$SESSION" -n coder -c "$REPO_DIR"
  tmux new-window -t "$SESSION" -n ops -c "$REPO_DIR"
  tmux new-window -t "$SESSION" -n reviewer -c "$REPO_DIR"

  tmux send-keys -t "$SESSION:planner" "$PLAN_CMD" C-m
  tmux send-keys -t "$SESSION:coder" "$CODE_CMD" C-m
  tmux send-keys -t "$SESSION:ops" "$CODEX_CMD" C-m
  tmux send-keys -t "$SESSION:reviewer" "$REVIEW_CMD" C-m
fi

if [[ "$ATTACH" -eq 1 ]]; then
  tmux attach -t "$SESSION"
fi

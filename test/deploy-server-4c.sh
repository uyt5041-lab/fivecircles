#!/bin/bash

# Server Deployment Script (4C fast-build, opt-in)
# - Uses infra/docker-compose.4c.yml override (new Dockerfile.4c per service)
# - Keeps default docker-compose.yml + service Dockerfiles untouched
#
# Usage:
#   fivecircles/test/deploy-server-4c.sh                # deploy ALL services with 4c dockerfiles
#   fivecircles/test/deploy-server-4c.sh event-service  # deploy only specific services

set -euo pipefail

SERVER_ALIAS="bit-ts"
PROJECT_PATH="~/nospoiler"
INFRA_PATH="~/nospoiler/infra"
BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)
SERVICES="$*"

echo "=========================================="
echo "[4C] 🚀 Deploying to Test Server: $SERVER_ALIAS"
echo "[4C] 📂 Project Path: $PROJECT_PATH"
echo "[4C] 🌿 Current Branch: $BRANCH_NAME"
echo "=========================================="

echo "[4C] Step 1: Check Git Status on Local"
git status -s
if [ -n "$(git status --porcelain)" ]; then
  echo "[4C] ❌ Error: You have uncommitted changes. Please commit or stash them before deploying."
  exit 1
fi

echo "[4C] Step 2: Push Current Branch to Remote"
echo "[4C] Pushing $BRANCH_NAME..."
git push origin "$BRANCH_NAME"

echo "[4C] Step 3: SSH Connection & Deployment"
ssh $SERVER_ALIAS "bash -s" <<EOF
  set -euo pipefail

  echo "  [Server/4C] cd $PROJECT_PATH"
  cd $PROJECT_PATH || exit 1

  echo "  [Server/4C] git fetch origin"
  git fetch origin

  echo "  [Server/4C] git checkout $BRANCH_NAME"
  git checkout $BRANCH_NAME

  echo "  [Server/4C] git pull origin $BRANCH_NAME"
  git pull origin $BRANCH_NAME

  echo "  [Server/4C] working tree clean check"
  if [ -n "\$(git status --porcelain)" ]; then
    echo "  [Server/4C] ❌ Working tree is dirty (untracked/modified files exist)."
    git status -sb
    exit 1
  fi

  echo "  [Server/4C] cd $INFRA_PATH"
  cd $INFRA_PATH || exit 1

  echo "  [Server/4C] docker compose (override=4c) up -d --build $SERVICES"
  if [ -n "$SERVICES" ]; then
    docker compose -f docker-compose.yml -f docker-compose.4c.yml up -d --build $SERVICES
  else
    docker compose -f docker-compose.yml -f docker-compose.4c.yml up -d --build
  fi

  echo "  [Server/4C] docker compose ps"
  docker compose ps
EOF

echo "=========================================="
echo "[4C] ✅ Deployment Completed!"
echo "=========================================="


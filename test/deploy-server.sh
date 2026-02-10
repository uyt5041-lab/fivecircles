#!/bin/bash

# Server Deployment Script
# Based on fivecircles/architecture/specs/test-server-policy-4C.md
# Reference: Step Id 326 (ssh bit-ts "cd ~/nospoiler/infra && git pull && docker compose up -d --build")

SERVER_ALIAS="bit-ts"
PROJECT_PATH="~/nospoiler"
INFRA_PATH="~/nospoiler/infra"
BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)

echo "=========================================="
echo "🚀 Deploying to Test Server: $SERVER_ALIAS"
echo "📂 Project Path: $PROJECT_PATH"
echo "🌿 Current Branch: $BRANCH_NAME"
echo "=========================================="

echo "Step 1: Check Git Status on Local"
git status -s
if [ -n "$(git status --porcelain)" ]; then
  echo "❌ Error: You have uncommitted changes. Please commit or stash them before deploying."
  exit 1
fi

echo "Step 2: Push Current Branch to Remote"
echo "Pushing $BRANCH_NAME..."
git push origin "$BRANCH_NAME"

echo "Step 3: SSH Connection & Deployment"
# 1. Fetch latest changes
# 2. Checkout the specific branch (same as local)
# 3. Pull latest changes
# 4. Rebuild and restart docker containers

ssh $SERVER_ALIAS "bash -s" <<EOF
  echo "  [Server] Navigating to project directory..."
  cd $PROJECT_PATH || exit 1

  echo "  [Server] Fetching origin..."
  git fetch origin

  echo "  [Server] Checking out branch: $BRANCH_NAME"
  git checkout $BRANCH_NAME
  
  echo "  [Server] Pulling latest changes..."
  git pull origin $BRANCH_NAME

  echo "  [Server] Navigating to infra directory..."
  cd $INFRA_PATH || exit 1

  echo "  [Server] Rebuilding and restarting containers..."
  docker compose up -d --build

  echo "  [Server] Checking running services..."
  docker compose ps
EOF

echo "=========================================="
echo "✅ Deployment Completed!"
echo "=========================================="

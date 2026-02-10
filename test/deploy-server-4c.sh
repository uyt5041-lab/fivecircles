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

  echo "  [Server/4C] generate 4C override files (gitignored)"
  # 1) compose override
  cat > infra/docker-compose.4c.yml <<'YML'
version: "3.8"

# 4C fast-build override (generated).
# - keeps default docker-compose.yml untouched
# - opt-in via: docker compose -f docker-compose.yml -f docker-compose.4c.yml up -d --build <services...>

services:
  auth-service:
    build:
      context: ..
      dockerfile: services/auth-service/Dockerfile.4c

  user-service:
    build:
      context: ..
      dockerfile: services/user-service/Dockerfile.4c

  api-gateway:
    build:
      context: ..
      dockerfile: services/api-gateway/Dockerfile.4c

  drama-service:
    build:
      context: ..
      dockerfile: services/drama-service/Dockerfile.4c

  character-service:
    build:
      context: ..
      dockerfile: services/character-service/Dockerfile.4c

  wiki-service:
    build:
      context: ..
      dockerfile: services/wiki-service/Dockerfile.4c

  event-service:
    build:
      context: ..
      dockerfile: services/event-service/Dockerfile.4c

  spoiler-policy-service:
    build:
      context: ..
      dockerfile: services/spoiler-policy-service/Dockerfile.4c

  qa-service:
    build:
      context: ..
      dockerfile: services/qa-service/Dockerfile.4c

  intelligence-service:
    build:
      context: ..
      dockerfile: services/intelligence-service/Dockerfile.4c

  frontend:
    build:
      context: ..
      dockerfile: front/Dockerfile.4c
YML

  # 2) service dockerfiles: transform existing Dockerfile -> Dockerfile.4c
  for svc in api-gateway auth-service character-service drama-service event-service intelligence-service qa-service spoiler-policy-service user-service wiki-service; do
    src="services/$svc/Dockerfile"
    dst="services/$svc/Dockerfile.4c"
    if [ ! -f "$src" ]; then
      echo "  [Server/4C] ❌ missing $src"
      exit 1
    fi
    SVC="$svc" perl -0777 -pe '
      $svc = $ENV{"SVC"} // "service";
      if ($_ !~ /# syntax=docker\/dockerfile:1\.4/) { $_ = "# syntax=docker/dockerfile:1.4\n" . $_; }

      s/\nRUN\s+--mount=type=cache,target=\/root\/\.gradle\s+\.\/gradlew(.*?)(\n)/
        "\nRUN --mount=type=cache,id=gradle-wrapper,target=\/root\/.gradle\/wrapper \\\\\n" .
        "    --mount=type=cache,id=gradle-caches-$svc,target=\/root\/.gradle\/caches \\\\\n" .
        "    .\/gradlew$1$2"
      /sg;

      s/\nRUN\s+\.\/gradlew(.*?)(\n)/
        "\nRUN --mount=type=cache,id=gradle-wrapper,target=\/root\/.gradle\/wrapper \\\\\n" .
        "    --mount=type=cache,id=gradle-caches-$svc,target=\/root\/.gradle\/caches \\\\\n" .
        "    .\/gradlew$1$2"
      /sg;
    ' "$src" > "$dst"
  done

  # 3) frontend dockerfile (lockfile + npm cache)
  cat > front/Dockerfile.4c <<'DOCKER'
# syntax=docker/dockerfile:1.4

FROM node:20-alpine as build
WORKDIR /app

COPY front/package.json front/package-lock.json ./
RUN --mount=type=cache,id=npm-cache,target=/root/.npm npm ci

COPY front/ .
RUN npm run build

FROM nginx:alpine
WORKDIR /usr/share/nginx/html
COPY --from=build /app/dist ./
COPY front/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx","-g","daemon off;"]
DOCKER

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

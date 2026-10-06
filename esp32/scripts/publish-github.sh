#!/usr/bin/env bash
# Publica esta pasta como https://github.com/avilarezende/esp32
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

REPO_NAME="${ESP32_REPO_NAME:-esp32}"
OWNER="${ESP32_REPO_OWNER:-avilarezende}"
FULL="$OWNER/$REPO_NAME"
VISIBILITY="${ESP32_REPO_VISIBILITY:-public}"

STAGE="$(mktemp -d /tmp/esp32-publish.XXXXXX)"
(
  cd "$ROOT"
  tar -cf - \
    --exclude='.pio' \
    --exclude='.git' \
    --exclude='include/secrets.h' \
    . | tar -xf - -C "$STAGE"
)
cd "$STAGE"
git init -b main
git add -A
git -c user.email="${GIT_AUTHOR_EMAIL:-avilarezende@users.noreply.github.com}" \
    -c user.name="${GIT_AUTHOR_NAME:-Rodrigo Rezende}" \
    commit -m "Initial commit: ESP32-CYD Calisto + Grok (standalone)."

if gh repo view "$FULL" >/dev/null 2>&1; then
  echo "==> Repo $FULL já existe — push"
  git remote remove origin 2>/dev/null || true
  git remote add origin "https://github.com/$FULL.git"
  git push -u origin main
else
  echo "==> Criando $FULL ($VISIBILITY)"
  gh repo create "$FULL" "--$VISIBILITY" --source=. --remote=origin --push
fi

echo
echo "OK: https://github.com/$FULL"
echo "Environment Cursor: crie um environment chamado 'esp32' apontando só para este repo."

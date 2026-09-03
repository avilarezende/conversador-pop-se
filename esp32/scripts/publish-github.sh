#!/usr/bin/env bash
# Publica esta pasta como https://github.com/avilarezende/esp32
# Requer: gh autenticado com permissão createRepository.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

REPO_NAME="${ESP32_REPO_NAME:-esp32}"
OWNER="${ESP32_REPO_OWNER:-avilarezende}"
FULL="$OWNER/$REPO_NAME"
VISIBILITY="${ESP32_REPO_VISIBILITY:-public}"

if [[ -n "$(git -C "$ROOT/.." rev-parse --show-toplevel 2>/dev/null || true)" ]] && \
   [[ "$(basename "$(git -C "$ROOT/.." rev-parse --show-toplevel)")" == "conversador-pop-se" ]]; then
  echo "==> Detectado monorepo conversador-pop-se; preparando repo Git isolado em /tmp"
  STAGE="$(mktemp -d /tmp/esp32-publish.XXXXXX)"
  rsync -a --exclude '.pio' --exclude '.git' "$ROOT/" "$STAGE/"
  cd "$STAGE"
  git init -b main
  git add -A
  git -c user.email="${GIT_AUTHOR_EMAIL:-avilarezende@users.noreply.github.com}" \
      -c user.name="${GIT_AUTHOR_NAME:-Rodrigo Rezende}" \
      commit -m "Initial commit: ESP32 PoP-SE companion firmware."
else
  if [[ ! -d .git ]]; then
    git init -b main
    git add -A
    git commit -m "Initial commit: ESP32 PoP-SE companion firmware."
  fi
fi

if gh repo view "$FULL" >/dev/null 2>&1; then
  echo "==> Repo $FULL já existe — configurando remote e push"
  git remote remove origin 2>/dev/null || true
  git remote add origin "https://github.com/$FULL.git"
  git push -u origin main
else
  echo "==> Criando $FULL ($VISIBILITY) e fazendo push"
  gh repo create "$FULL" "--$VISIBILITY" --source=. --remote=origin --push
fi

echo
echo "OK: https://github.com/$FULL"
echo "Próximo passo: Cloud Agent em https://cursor.com/agents → New Agent → $FULL"

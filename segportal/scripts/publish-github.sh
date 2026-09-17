#!/usr/bin/env bash
# Publica o SegPortal no GitHub (avilarezende/segportal)
# Pré-requisito: gh autenticado com conta pessoal (gh auth login)

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v gh &>/dev/null; then
  echo "Instale o GitHub CLI: https://cli.github.com/"
  exit 1
fi

gh auth status || { echo "Execute: gh auth login -h github.com"; exit 1; }

DESC="$(tr -d '\n' < .github/REPOSITORY_DESCRIPTION.txt)"
REPO="avilarezende/segportal"

if ! gh repo view "$REPO" &>/dev/null; then
  echo "Criando repositório $REPO..."
  gh repo create segportal \
    --public \
    --description "$DESC" \
    --source . \
    --remote origin \
    --push
else
  echo "Repositório já existe. Enviando alterações..."
  git remote get-url origin &>/dev/null || git remote add origin "https://github.com/$REPO.git"
  git push -u origin main
fi

# Topics
TOPICS=$(tr '\n' ',' < .github/REPOSITORY_TOPICS.txt | sed 's/,$//')
IFS=',' read -ra TOPIC_ARR <<< "$TOPICS"
TOPIC_ARGS=()
for t in "${TOPIC_ARR[@]}"; do
  [ -n "$t" ] && TOPIC_ARGS+=(--add-topic "$t")
done
gh repo edit "$REPO" --description "$DESC" "${TOPIC_ARGS[@]}"

echo ""
echo "Repositório publicado: https://github.com/$REPO"

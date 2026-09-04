#!/usr/bin/env bash
# Aplica seeds de navegador padrão + tabela de pedidos de conexão.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

PG_HOST="${POSTGRES_HOSTNAME:-localhost}"
PG_PORT="${POSTGRES_PORT:-5432}"
PG_DB="${POSTGRES_DATABASE:-guacamole_db}"
PG_USER="${POSTGRES_USER:-guacamole_user}"
PG_PASS="${POSTGRES_PASSWORD:-devpassword}"
export PGPASSWORD="$PG_PASS"

for f in 004-default-browser.sql 005-connection-requests.sql; do
  echo "==> Aplicando $f"
  psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" -v ON_ERROR_STOP=1 \
    -f "$ROOT/scripts/sql/$f"
done

echo "OK: navegador padrão e fluxo de pedidos prontos."

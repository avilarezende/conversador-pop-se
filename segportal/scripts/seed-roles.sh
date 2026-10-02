#!/usr/bin/env bash
# Aplica papéis SegPortal (admin / usuário) no PostgreSQL do Guacamole.
# Pré-requisito: schema Guacamole já inicializado (001/002 ou POSTGRES_INIT_DB).
#
# Uso:
#   export POSTGRES_PASSWORD=devpassword
#   ./scripts/seed-roles.sh
#
# Variáveis opcionais: POSTGRES_HOSTNAME, POSTGRES_PORT, POSTGRES_DATABASE, POSTGRES_USER
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SQL_FILE="$ROOT/scripts/sql/003-segportal-roles.sql"

PG_HOST="${POSTGRES_HOSTNAME:-localhost}"
PG_PORT="${POSTGRES_PORT:-5432}"
PG_DB="${POSTGRES_DATABASE:-guacamole_db}"
PG_USER="${POSTGRES_USER:-guacamole_user}"
PG_PASS="${POSTGRES_PASSWORD:-devpassword}"

export PGPASSWORD="$PG_PASS"

if [[ ! -f "$SQL_FILE" ]]; then
  echo "ERROR: arquivo SQL não encontrado: $SQL_FILE" >&2
  exit 1
fi

if ! command -v psql >/dev/null 2>&1; then
  echo "ERROR: psql é necessário. Use: docker compose exec postgres ..." >&2
  exit 1
fi

echo "==> Aplicando papéis SegPortal em ${PG_HOST}:${PG_PORT}/${PG_DB}"
psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" -v ON_ERROR_STOP=1 -f "$SQL_FILE"

echo ""
echo "Papéis aplicados:"
echo "  Admin   → guacadmin / guacadmin  (grupo segportal-admins)"
echo "  Usuário → usuario   / usuario    (grupo segportal-users + financeiro)"
echo ""
echo "Mapeamento AD (produção): ver config/roles/roles.yaml"

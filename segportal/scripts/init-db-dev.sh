#!/usr/bin/env bash
# Inicializa o schema do Guacamole 1.5.5 no PostgreSQL (modo dev)
# Uso: ./scripts/init-db-dev.sh
# Pré-requisito: postgres em execução via docker-compose.dev.yml
set -euo pipefail

GUAC_VERSION="1.5.5"
BASE_URL="https://raw.githubusercontent.com/apache/guacamole-client/${GUAC_VERSION}/extensions/guacamole-auth-jdbc/modules/guacamole-auth-jdbc-postgresql/schema"
PG_HOST="${POSTGRES_HOSTNAME:-localhost}"
PG_PORT="${POSTGRES_PORT:-5432}"
PG_DB="${POSTGRES_DATABASE:-guacamole_db}"
PG_USER="${POSTGRES_USER:-guacamole_user}"
PG_PASS="${POSTGRES_PASSWORD:-devpassword}"

export PGPASSWORD="$PG_PASS"

echo "==> Baixando schema Guacamole ${GUAC_VERSION}..."
TMP=$(mktemp -d)
for f in 001-create-schema.sql 002-create-admin-user.sql; do
  curl -fsSL "${BASE_URL}/${f}" -o "${TMP}/${f}"
done

echo "==> Aplicando schema no PostgreSQL (${PG_HOST}:${PG_PORT}/${PG_DB})..."
for f in 001-create-schema.sql 002-create-admin-user.sql; do
  psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" -f "${TMP}/${f}" 2>&1 \
    | grep -v "^$" || true
done

rm -rf "$TMP"
echo ""
echo "Schema inicializado."
echo "Login padrão: guacadmin / guacadmin"
echo "Acesse: http://localhost:8080/guacamole"

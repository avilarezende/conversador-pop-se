#!/usr/bin/env bash
# Bootstrap SegPortal — schema JDBC (se necessário) + papéis + navegador HTML + pedidos.
# Roda automaticamente no boot (serviço segportal-bootstrap / Job K8s).
# Idempotente.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Compose/K8s montam em /scripts (com /scripts/sql); no repo fica em scripts/
if [ -d "${SCRIPT_DIR}/sql" ]; then
  SQL_DIR="${SCRIPT_DIR}/sql"
  ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
else
  ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
  SQL_DIR="${ROOT}/scripts/sql"
fi

PG_HOST="${POSTGRES_HOSTNAME:-${POSTGRES_HOST:-localhost}}"
PG_PORT="${POSTGRES_PORT:-5432}"
PG_DB="${POSTGRES_DATABASE:-${POSTGRES_DB:-guacamole_db}}"
PG_USER="${POSTGRES_USER:-guacamole_user}"
PG_PASS="${POSTGRES_PASSWORD:-devpassword}"
WAIT_MAX="${SEGPORTAL_BOOTSTRAP_WAIT_SECONDS:-300}"
GUAC_VERSION="${GUACAMOLE_VERSION:-1.5.5}"
SCHEMA_BASE="https://raw.githubusercontent.com/apache/guacamole-client/${GUAC_VERSION}/extensions/guacamole-auth-jdbc/modules/guacamole-auth-jdbc-postgresql/schema"

export PGPASSWORD="$PG_PASS"

# Em alpine (compose bootstrap) garante curl
if ! command -v curl >/dev/null 2>&1; then
  if command -v apk >/dev/null 2>&1; then
    apk add --no-cache curl >/dev/null
  fi
fi

psql_q() {
  psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" -v ON_ERROR_STOP=1 "$@"
}

echo "==> SegPortal bootstrap: aguardando PostgreSQL em ${PG_HOST}:${PG_PORT}/${PG_DB}..."
elapsed=0
until pg_isready -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" >/dev/null 2>&1; do
  if [ "$elapsed" -ge "$WAIT_MAX" ]; then
    echo "ERRO: PostgreSQL indisponível após ${WAIT_MAX}s" >&2
    exit 1
  fi
  sleep 2
  elapsed=$((elapsed + 2))
done

table_exists() {
  psql_q -tAc "SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='$1'" 2>/dev/null | grep -q 1
}

if ! table_exists guacamole_connection; then
  echo "==> Schema Guacamole ausente — baixando e aplicando ${GUAC_VERSION}..."
  TMP=$(mktemp -d)
  trap 'rm -rf "$TMP"' EXIT
  curl -fsSL "${SCHEMA_BASE}/001-create-schema.sql" -o "${TMP}/001-create-schema.sql"
  curl -fsSL "${SCHEMA_BASE}/002-create-admin-user.sql" -o "${TMP}/002-create-admin-user.sql"
  psql_q -f "${TMP}/001-create-schema.sql"
  psql_q -f "${TMP}/002-create-admin-user.sql"
  echo "==> Schema Guacamole aplicado (guacadmin / guacadmin)."
else
  echo "==> Schema Guacamole já presente."
fi

# Garante guacadmin (caso só 001 tenha rodado)
if ! psql_q -tAc "SELECT 1 FROM guacamole_entity WHERE name='guacadmin' AND type='USER'" 2>/dev/null | grep -q 1; then
  echo "==> Criando usuário admin padrão..."
  TMP2=$(mktemp -d)
  curl -fsSL "${SCHEMA_BASE}/002-create-admin-user.sql" -o "${TMP2}/002-create-admin-user.sql"
  psql_q -f "${TMP2}/002-create-admin-user.sql"
  rm -rf "$TMP2"
fi

for f in 003-segportal-roles.sql 004-default-browser.sql 005-connection-requests.sql; do
  echo "==> Aplicando $f"
  psql_q -f "${SQL_DIR}/${f}"
done

NAME="$(psql_q -tAc "SELECT connection_name FROM guacamole_connection WHERE connection_name='Navegador Web SegPortal'" | tr -d '[:space:]')"
if [ "$NAME" != "Navegador Web SegPortal" ]; then
  echo "ERRO: conexão Navegador Web SegPortal não foi criada" >&2
  exit 1
fi

HOST="$(psql_q -tAc "SELECT parameter_value FROM guacamole_connection_parameter cp JOIN guacamole_connection c ON c.connection_id=cp.connection_id WHERE c.connection_name='Navegador Web SegPortal' AND cp.parameter_name='hostname'" | tr -d '[:space:]')"
if [ "$HOST" != "web-browser" ]; then
  echo "ERRO: hostname VNC esperado 'web-browser', obtido '${HOST}'" >&2
  exit 1
fi

READERS="$(psql_q -tAc "SELECT COUNT(*) FROM guacamole_connection_permission cp JOIN guacamole_connection c ON c.connection_id=cp.connection_id WHERE c.connection_name='Navegador Web SegPortal' AND cp.permission='READ'")"
echo "OK: Firefox/VNC padrão habilitado (${READERS} permissões READ). Login: http://localhost:8080/guacamole"

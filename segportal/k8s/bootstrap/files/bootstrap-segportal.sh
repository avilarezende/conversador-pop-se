#!/bin/sh
# Bootstrap SegPortal — schema JDBC (se necessário) + papéis + navegador HTML + pedidos.
# Roda automaticamente no boot (serviço segportal-bootstrap / Job K8s).
# Idempotente. Compatível com /bin/sh (Alpine ash).
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
# Compose/K8s montam em /scripts (com /scripts/sql); no repo fica em scripts/
if [ -d "${SCRIPT_DIR}/sql" ]; then
  SQL_DIR="${SCRIPT_DIR}/sql"
else
  SQL_DIR="${SCRIPT_DIR}/../scripts/sql"
fi

PG_HOST="${POSTGRES_HOSTNAME:-${POSTGRES_HOST:-localhost}}"
PG_PORT="${POSTGRES_PORT:-5432}"
PG_DB="${POSTGRES_DATABASE:-${POSTGRES_DB:-guacamole_db}}"
PG_USER="${POSTGRES_USER:-guacamole_user}"
PG_PASS="${POSTGRES_PASSWORD:-devpassword}"
WAIT_MAX="${SEGPORTAL_BOOTSTRAP_WAIT_SECONDS:-300}"

export PGPASSWORD="$PG_PASS"

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
  echo "==> Schema Guacamole ausente — aplicando SQL local (001/002)..."
  if [ ! -f "${SQL_DIR}/001-create-schema.sql" ] || [ ! -f "${SQL_DIR}/002-create-admin-user.sql" ]; then
    echo "ERRO: arquivos 001/002 ausentes em ${SQL_DIR}" >&2
    exit 1
  fi
  psql_q -f "${SQL_DIR}/001-create-schema.sql"
  psql_q -f "${SQL_DIR}/002-create-admin-user.sql"
  echo "==> Schema Guacamole aplicado (guacadmin / guacadmin)."
else
  echo "==> Schema Guacamole já presente."
fi

# Garante guacadmin (caso só 001 tenha rodado)
if ! psql_q -tAc "SELECT 1 FROM guacamole_entity WHERE name='guacadmin' AND type='USER'" 2>/dev/null | grep -q 1; then
  echo "==> Criando usuário admin padrão..."
  psql_q -f "${SQL_DIR}/002-create-admin-user.sql"
fi

for f in 003-segportal-roles.sql 004-default-browser.sql 005-connection-requests.sql; do
  echo "==> Aplicando $f"
  psql_q -f "${SQL_DIR}/${f}"
done

# BusyBox tr não trata bem [:space:] — limpa só whitespace ASCII
trim() { tr -d '\n\r\t '; }

NAME=$(psql_q -tAc "SELECT connection_name FROM guacamole_connection WHERE connection_name='Navegador Web SegPortal'" | trim)
if [ "$NAME" != "Navegador Web SegPortal" ]; then
  echo "ERRO: conexão Navegador Web SegPortal não foi criada (obtido='${NAME}')" >&2
  exit 1
fi

HOST=$(psql_q -tAc "SELECT parameter_value FROM guacamole_connection_parameter cp JOIN guacamole_connection c ON c.connection_id=cp.connection_id WHERE c.connection_name='Navegador Web SegPortal' AND cp.parameter_name='hostname'" | trim)
if [ "$HOST" != "web-browser" ]; then
  echo "ERRO: hostname VNC esperado 'web-browser', obtido '${HOST}'" >&2
  exit 1
fi

PASS=$(psql_q -tAc "SELECT parameter_value FROM guacamole_connection_parameter cp JOIN guacamole_connection c ON c.connection_id=cp.connection_id WHERE c.connection_name='Navegador Web SegPortal' AND cp.parameter_name='password'" | trim)
if [ -z "$PASS" ]; then
  echo "ERRO: parâmetro password VNC ausente na conexão" >&2
  exit 1
fi

READERS=$(psql_q -tAc "SELECT COUNT(*) FROM guacamole_connection_permission cp JOIN guacamole_connection c ON c.connection_id=cp.connection_id WHERE c.connection_name='Navegador Web SegPortal' AND cp.permission='READ'" | trim)
echo "OK: Firefox/VNC padrão habilitado (${READERS} permissões READ, password=***). Login: http://localhost:8080/guacamole"

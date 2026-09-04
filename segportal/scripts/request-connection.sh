#!/usr/bin/env bash
# Usuário solicita um novo terminal/aplicação (fica pending até o admin aprovar).
# Uso:
#   ./scripts/request-connection.sh usuario "Meu RDP" rdp 10.10.20.50 3389 "Acesso ao sistema X"
set -euo pipefail

USER_NAME="${1:-}"
CONN_NAME="${2:-}"
PROTOCOL="${3:-}"
HOSTNAME="${4:-}"
PORT="${5:-}"
JUSTIFICATION="${6:-}"

if [[ -z "$USER_NAME" || -z "$CONN_NAME" || -z "$PROTOCOL" || -z "$HOSTNAME" || -z "$JUSTIFICATION" ]]; then
  echo "Uso: $0 <username> <nome_conexao> <rdp|vnc|ssh|browser> <host> [porta] <justificativa>" >&2
  exit 1
fi

PG_HOST="${POSTGRES_HOSTNAME:-localhost}"
PG_PORT="${POSTGRES_PORT:-5432}"
PG_DB="${POSTGRES_DATABASE:-guacamole_db}"
PG_USER="${POSTGRES_USER:-guacamole_user}"
PG_PASS="${POSTGRES_PASSWORD:-devpassword}"
export PGPASSWORD="$PG_PASS"

PORT_SQL="NULL"
[[ -n "$PORT" ]] && PORT_SQL="$PORT"

psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" -v ON_ERROR_STOP=1 <<SQL
INSERT INTO segportal_connection_request (
  requester_username, connection_name, protocol, hostname, port, justification
) VALUES (
  '${USER_NAME}',
  '${CONN_NAME}',
  lower('${PROTOCOL}'),
  '${HOSTNAME}',
  ${PORT_SQL},
  '${JUSTIFICATION}'
)
RETURNING request_id, status;
SQL

echo "Pedido registrado como pending. O administrador deve aprovar com:"
echo "  ./scripts/approve-connection-request.sh <request_id>"

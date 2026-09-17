#!/usr/bin/env bash
# Aprova um pedido de terminal/aplicação e cria a conexão Guacamole.
# Uso:
#   ./scripts/approve-connection-request.sh <request_id>
#   ./scripts/approve-connection-request.sh <request_id> --reject "motivo"
set -euo pipefail

REQUEST_ID="${1:-}"
ACTION="${2:---approve}"
NOTES="${3:-}"

if [[ -z "$REQUEST_ID" ]]; then
  echo "Uso: $0 <request_id> [--approve|--reject] [notas]" >&2
  exit 1
fi

PG_HOST="${POSTGRES_HOSTNAME:-localhost}"
PG_PORT="${POSTGRES_PORT:-5432}"
PG_DB="${POSTGRES_DATABASE:-guacamole_db}"
PG_USER="${POSTGRES_USER:-guacamole_user}"
PG_PASS="${POSTGRES_PASSWORD:-devpassword}"
REVIEWER="${REVIEWER_USERNAME:-guacadmin}"
export PGPASSWORD="$PG_PASS"

if [[ "$ACTION" == "--reject" ]]; then
  psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" -v ON_ERROR_STOP=1 <<SQL
UPDATE segportal_connection_request
SET status = 'rejected',
    reviewed_by = '${REVIEWER}',
    review_notes = '${NOTES:-rejeitado}',
    reviewed_at = CURRENT_TIMESTAMP,
    updated_at = CURRENT_TIMESTAMP
WHERE request_id = ${REQUEST_ID} AND status = 'pending';
SELECT 'OK: pedido '${REQUEST_ID}' rejeitado' AS resultado;
SQL
  exit 0
fi

# Aprovar: cria conexão + READ para o solicitante
eval "$(psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" -v ON_ERROR_STOP=1 -At <<SQL
SELECT
  'REQ_USER=' || requester_username,
  'REQ_NAME=' || replace(connection_name, '''', ''),
  'REQ_PROTO=' || lower(protocol),
  'REQ_HOST=' || hostname,
  'REQ_PORT=' || COALESCE(port::text, '0')
FROM segportal_connection_request
WHERE request_id = ${REQUEST_ID} AND status = 'pending';
SQL
)"

if [[ -z "${REQ_USER:-}" ]]; then
  echo "ERRO: pedido ${REQUEST_ID} não encontrado ou não está pending" >&2
  exit 1
fi

DEFAULT_PORT=3389
case "$REQ_PROTO" in
  vnc|browser) DEFAULT_PORT=5900; REQ_PROTO=vnc ;;
  ssh) DEFAULT_PORT=22 ;;
  rdp) DEFAULT_PORT=3389 ;;
esac
if [[ "$REQ_PORT" == "0" ]]; then REQ_PORT="$DEFAULT_PORT"; fi

psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" -v ON_ERROR_STOP=1 <<SQL
BEGIN;

INSERT INTO guacamole_connection (connection_name, protocol, max_connections_per_user)
SELECT '${REQ_NAME}', '${REQ_PROTO}', 1
WHERE NOT EXISTS (
  SELECT 1 FROM guacamole_connection WHERE connection_name = '${REQ_NAME}'
);

INSERT INTO guacamole_connection_parameter (connection_id, parameter_name, parameter_value)
SELECT c.connection_id, p.n, p.v
FROM guacamole_connection c
CROSS JOIN (VALUES
  ('hostname', '${REQ_HOST}'),
  ('port', '${REQ_PORT}')
) AS p(n, v)
WHERE c.connection_name = '${REQ_NAME}'
  AND NOT EXISTS (
    SELECT 1 FROM guacamole_connection_parameter cp
    WHERE cp.connection_id = c.connection_id AND cp.parameter_name = p.n
  );

-- Garante entidade do usuário
INSERT INTO guacamole_entity (name, type)
SELECT '${REQ_USER}', 'USER'
WHERE NOT EXISTS (
  SELECT 1 FROM guacamole_entity WHERE name = '${REQ_USER}' AND type = 'USER'
);

INSERT INTO guacamole_connection_permission (entity_id, connection_id, permission)
SELECT e.entity_id, c.connection_id, 'READ'::guacamole_object_permission_type
FROM guacamole_entity e
JOIN guacamole_connection c ON c.connection_name = '${REQ_NAME}'
WHERE e.name = '${REQ_USER}' AND e.type = 'USER'
  AND NOT EXISTS (
    SELECT 1 FROM guacamole_connection_permission cp
    WHERE cp.entity_id = e.entity_id AND cp.connection_id = c.connection_id
      AND cp.permission = 'READ'::guacamole_object_permission_type
  );

UPDATE segportal_connection_request r
SET status = 'approved',
    reviewed_by = '${REVIEWER}',
    review_notes = COALESCE(NULLIF('${NOTES}', ''), 'aprovado'),
    reviewed_at = CURRENT_TIMESTAMP,
    updated_at = CURRENT_TIMESTAMP,
    guacamole_connection_id = c.connection_id
FROM guacamole_connection c
WHERE r.request_id = ${REQUEST_ID}
  AND c.connection_name = '${REQ_NAME}';

COMMIT;
SELECT 'OK: pedido ${REQUEST_ID} aprovado — conexão ${REQ_NAME} liberada para ${REQ_USER}' AS resultado;
SQL

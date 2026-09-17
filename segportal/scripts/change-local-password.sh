#!/usr/bin/env bash
# Altera a senha de um usuário LOCAL do Guacamole (JDBC).
# Uso:
#   ./scripts/change-local-password.sh guacadmin 'NovaSenhaForte!'
#   ./scripts/change-local-password.sh usuario 'OutraSenha'
#
# Requer: python3, psql, acesso ao PostgreSQL.
set -euo pipefail

USERNAME="${1:-}"
NEW_PASSWORD="${2:-}"

if [[ -z "$USERNAME" || -z "$NEW_PASSWORD" ]]; then
  echo "Uso: $0 <username> <nova_senha>" >&2
  exit 1
fi

PG_HOST="${POSTGRES_HOSTNAME:-localhost}"
PG_PORT="${POSTGRES_PORT:-5432}"
PG_DB="${POSTGRES_DATABASE:-guacamole_db}"
PG_USER="${POSTGRES_USER:-guacamole_user}"
PG_PASS="${POSTGRES_PASSWORD:-devpassword}"
export PGPASSWORD="$PG_PASS"

# salt aleatório + hash SHA-256(password || salt) — formato Guacamole
eval "$(NEW_PASSWORD="$NEW_PASSWORD" python3 <<'PY'
import hashlib, os
password = os.environ["NEW_PASSWORD"].encode("utf-8")
salt = os.urandom(32)
h = hashlib.sha256()
h.update(password)
h.update(salt)
print(f"SALT_HEX={salt.hex().upper()}")
print(f"HASH_HEX={h.hexdigest().upper()}")
PY
)"

RESULT="$(psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" -v ON_ERROR_STOP=1 -At <<SQL
UPDATE guacamole_user u
SET
  password_hash = decode('${HASH_HEX}', 'hex'),
  password_salt = decode('${SALT_HEX}', 'hex'),
  password_date = CURRENT_TIMESTAMP
FROM guacamole_entity e
WHERE u.entity_id = e.entity_id
  AND e.name = '${USERNAME}'
  AND e.type = 'USER';

SELECT CASE WHEN EXISTS (
  SELECT 1 FROM guacamole_user u
  JOIN guacamole_entity e ON e.entity_id = u.entity_id
  WHERE e.name = '${USERNAME}' AND e.type = 'USER'
) THEN 'OK'
  ELSE 'MISSING'
END;
SQL
)"

if [[ "$RESULT" != "OK" ]]; then
  echo "ERRO: usuário local não encontrado: ${USERNAME}" >&2
  exit 1
fi

echo "OK: senha local de '${USERNAME}' alterada."
echo "Faça login no portal para validar."

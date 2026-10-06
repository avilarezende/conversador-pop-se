#!/usr/bin/env bash
# Desativa ou exclui um usuário LOCAL do Guacamole.
#
# Uso:
#   ./scripts/delete-local-user.sh guacadmin --disable   # recomendado (desativa)
#   ./scripts/delete-local-user.sh guacadmin --delete    # remove do banco
#
# ATENÇÃO: não exclua o último administrador sem criar outro admin antes.
set -euo pipefail

USERNAME="${1:-}"
MODE="${2:---disable}"

if [[ -z "$USERNAME" ]]; then
  echo "Uso: $0 <username> [--disable|--delete]" >&2
  exit 1
fi

PG_HOST="${POSTGRES_HOSTNAME:-localhost}"
PG_PORT="${POSTGRES_PORT:-5432}"
PG_DB="${POSTGRES_DATABASE:-guacamole_db}"
PG_USER="${POSTGRES_USER:-guacamole_user}"
PG_PASS="${POSTGRES_PASSWORD:-devpassword}"
export PGPASSWORD="$PG_PASS"

case "$MODE" in
  --disable)
    psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" -v ON_ERROR_STOP=1 <<SQL
UPDATE guacamole_user u
SET disabled = TRUE
FROM guacamole_entity e
WHERE u.entity_id = e.entity_id
  AND e.name = '${USERNAME}'
  AND e.type = 'USER';
SELECT 'OK: usuário ${USERNAME} desativado (disabled=true)' AS resultado;
SQL
    ;;
  --delete)
    echo "Removendo usuário local '${USERNAME}' e entidade associada..."
    psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" -v ON_ERROR_STOP=1 <<SQL
-- Remove entidade USER (CASCADE remove guacamole_user e permissões)
DELETE FROM guacamole_entity
WHERE name = '${USERNAME}' AND type = 'USER';
SELECT 'OK: usuário ${USERNAME} excluído' AS resultado;
SQL
    ;;
  *)
    echo "Modo inválido: $MODE (use --disable ou --delete)" >&2
    exit 1
    ;;
esac

echo ""
echo "Concluído. Confirme que existe outro administrador ativo antes de sair."

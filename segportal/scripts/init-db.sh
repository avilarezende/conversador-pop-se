#!/bin/bash
# Initialize Guacamole PostgreSQL schema
set -euo pipefail

POSTGRES_HOST="${POSTGRES_HOSTNAME:-postgres}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_DB="${POSTGRES_DB:-guacamole_db}"
POSTGRES_USER="${POSTGRES_USER:-guacamole_user}"
GUACAMOLE_VERSION="${GUACAMOLE_VERSION:-1.5.5}"

echo "==> Waiting for PostgreSQL at ${POSTGRES_HOST}:${POSTGRES_PORT}..."
until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" >/dev/null 2>&1; do
  sleep 2
done

SCHEMA_URL="https://raw.githubusercontent.com/apache/guacamole-client/${GUACAMOLE_VERSION}/extensions/guacamole-auth-jdbc/modules/guacamole-auth-jdbc-postgresql/schema/001-create-schema.sql"
UPGRADE_URL="https://raw.githubusercontent.com/apache/guacamole-client/${GUACAMOLE_VERSION}/extensions/guacamole-auth-jdbc/modules/guacamole-auth-jdbc-postgresql/schema/002-create-schema-upgrade.sql"

TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

echo "==> Downloading Guacamole ${GUACAMOLE_VERSION} schema..."
curl -fsSL "$SCHEMA_URL" -o "$TMPDIR/001-create-schema.sql"
curl -fsSL "$UPGRADE_URL" -o "$TMPDIR/002-create-schema-upgrade.sql" || true

echo "==> Applying schema to ${POSTGRES_DB}..."
export PGPASSWORD="${POSTGRES_PASSWORD:?POSTGRES_PASSWORD is required}"
psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
  -f "$TMPDIR/001-create-schema.sql"

if [ -f "$TMPDIR/002-create-schema-upgrade.sql" ]; then
  psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
    -f "$TMPDIR/002-create-schema-upgrade.sql" || true
fi

echo "==> Guacamole database initialized successfully."

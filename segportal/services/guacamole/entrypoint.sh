#!/bin/sh
set -eu

GUACAMOLE_HOME="${GUACAMOLE_HOME:-/etc/guacamole}"
TEMPLATE="${GUACAMOLE_HOME}/guacamole.properties.template"
TARGET="${GUACAMOLE_HOME}/guacamole.properties"

# Render guacamole.properties from template with environment substitution
if [ -f "$TEMPLATE" ]; then
  envsubst < "$TEMPLATE" > "$TARGET"
fi

# Optional MFA: remove RADIUS settings when disabled
if [ "${MFA_ENABLED:-true}" != "true" ]; then
  sed -i '/^radius-/d' "$TARGET" 2>/dev/null || true
fi

exec "$@"

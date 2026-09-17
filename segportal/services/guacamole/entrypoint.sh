#!/bin/sh
# SegPortal Guacamole entrypoint — LDAP opcional + truststore de certificados
set -eu

GUACAMOLE_HOME="${GUACAMOLE_HOME:-/etc/guacamole}"
TEMPLATE="${GUACAMOLE_HOME}/guacamole.properties.template"
TARGET="${GUACAMOLE_HOME}/guacamole.properties"
CERT_DIR="${GUACAMOLE_HOME}/certs"
LDAP_ENABLED="${LDAP_ENABLED:-false}"

mkdir -p "$CERT_DIR"

# Render guacamole.properties a partir do template
if [ -f "$TEMPLATE" ]; then
  envsubst < "$TEMPLATE" > "$TARGET"
fi

# ---------------------------------------------------------------------------
# LDAP desligado: remove propriedades ldap-* (usuários locais / JDBC apenas)
# ---------------------------------------------------------------------------
if [ "$LDAP_ENABLED" != "true" ]; then
  echo "[segportal] LDAP_ENABLED=false — autenticação apenas com usuários locais"
  if [ -f "$TARGET" ]; then
    grep -v '^ldap-' "$TARGET" > "${TARGET}.tmp" && mv "${TARGET}.tmp" "$TARGET"
  fi
else
  echo "[segportal] LDAP_ENABLED=true — hostname=${LDAP_HOSTNAME:-} port=${LDAP_PORT:-636}"

  # Importa cadeia de CAs no truststore Java (se fornecida)
  CA_CHAIN="${LDAP_CA_CHAIN_FILE:-$CERT_DIR/ldap-ca-chain.pem}"
  TRUSTSTORE="${LDAP_TRUSTSTORE_FILE:-$CERT_DIR/ldap-truststore.jks}"
  TRUSTSTORE_PASS="${LDAP_TRUSTSTORE_PASSWORD:-changeit}"

  if [ -f "$CA_CHAIN" ]; then
    echo "[segportal] Importando cadeia CA LDAP em $TRUSTSTORE"
    # Remove truststore anterior para reimportação idempotente
    rm -f "$TRUSTSTORE"
    # Divide PEM em certificados individuais e importa
    awk 'BEGIN{n=0} /BEGIN CERTIFICATE/{n++} {print > ("'"$CERT_DIR"'/ca-" n ".pem")}' "$CA_CHAIN"
    for cert in "$CERT_DIR"/ca-*.pem; do
      [ -f "$cert" ] || continue
      alias="ldap-ca-$(basename "$cert" .pem)"
      keytool -importcert -noprompt \
        -alias "$alias" \
        -file "$cert" \
        -keystore "$TRUSTSTORE" \
        -storepass "$TRUSTSTORE_PASS" 2>/dev/null || true
    done
    export JAVA_OPTS="${JAVA_OPTS:-} -Djavax.net.ssl.trustStore=${TRUSTSTORE} -Djavax.net.ssl.trustStorePassword=${TRUSTSTORE_PASS}"
  fi

  # Certificado do servidor (opcional)
  if [ -n "${LDAP_SERVER_CERTIFICATE_FILE:-}" ] && [ -f "$LDAP_SERVER_CERTIFICATE_FILE" ]; then
    keytool -importcert -noprompt \
      -alias ldap-server \
      -file "$LDAP_SERVER_CERTIFICATE_FILE" \
      -keystore "$TRUSTSTORE" \
      -storepass "$TRUSTSTORE_PASS" 2>/dev/null || true
  fi
fi

# MFA desligado: remove radius-*
if [ "${MFA_ENABLED:-false}" != "true" ]; then
  if [ -f "$TARGET" ]; then
    grep -v '^radius-' "$TARGET" > "${TARGET}.tmp" && mv "${TARGET}.tmp" "$TARGET"
  fi
fi

exec "$@"

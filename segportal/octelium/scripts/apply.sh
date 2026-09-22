#!/bin/sh
# Aplica o estado declarativo do ZTNA no Cluster Octelium já instalado.
# Pré-requisito: https://octelium.com/docs/octelium/latest/overview/quick-install
set -eu

ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"

if ! command -v octeliumctl >/dev/null 2>&1; then
  echo "Instale o CLI: curl -fsSL https://octelium.com/install.sh | bash" >&2
  exit 1
fi

if [ -z "${OCTELIUM_DOMAIN:-}" ]; then
  echo "Defina OCTELIUM_DOMAIN (domínio do Cluster Octelium)." >&2
  exit 1
fi

octeliumctl apply --domain "${OCTELIUM_DOMAIN}" "${ROOT}/cluster"
echo "Serviços públicos: https://portal.${OCTELIUM_DOMAIN}"
echo "Sessões (cliente WireGuard, só admins): http://sessoes.local.${OCTELIUM_DOMAIN}"

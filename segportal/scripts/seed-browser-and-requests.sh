#!/usr/bin/env bash
# Reaplica navegador padrão + tabela de pedidos (atalho para bootstrap parcial).
# Preferencialmente use: ./scripts/bootstrap-segportal.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec "$ROOT/scripts/bootstrap-segportal.sh"

#!/usr/bin/env bash
# Aplica os recursos ZTNA do SegPortal num Cluster Octelium já instalado.
# Sem octeliumctl, apenas valida o YAML.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLUSTER="${ROOT}/cluster"
PROFILE="cluster"
UPSTREAM_HOST="${SEGPORTAL_UPSTREAM_HOST:-10.0.2.2}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile)
      PROFILE="${2:?perfil ausente}"
      shift 2
      ;;
    --upstream-host)
      UPSTREAM_HOST="${2:?host ausente}"
      shift 2
      ;;
    *)
      echo "uso: $0 [--profile cluster|instance] [--upstream-host HOST]" >&2
      exit 1
      ;;
  esac
done

SERVICES="${CLUSTER}/services.yaml"
if [[ "$PROFILE" == "instance" ]]; then
  SERVICES="$(mktemp)"
  trap 'rm -f "$SERVICES"' EXIT
  sed \
    -e "s|__UPSTREAM_HOST__|${UPSTREAM_HOST}|g" \
    -e "s|__GUACAMOLE_PORT__|${SEGPORTAL_GUACAMOLE_PORT:-8080}|g" \
    -e "s|__PORTAL_PORT__|${SEGPORTAL_PORTAL_PORT:-8090}|g" \
    -e "s|__DESKTOP_FINANCEIRO__|${SEGPORTAL_DESKTOP_FINANCEIRO:-10.10.20.51}|g" \
    -e "s|__DESKTOP_ADMIN__|${SEGPORTAL_DESKTOP_ADMIN:-10.10.20.10}|g" \
    -e "s|__JUMP_HOST__|${SEGPORTAL_JUMP_HOST:-10.10.20.10}|g" \
    "${ROOT}/instance/services.yaml.tpl" > "$SERVICES"
elif [[ "$PROFILE" != "cluster" ]]; then
  echo "perfil desconhecido: ${PROFILE}" >&2
  exit 1
fi

python3 - "$CLUSTER" "$SERVICES" <<'PY'
import sys
from pathlib import Path

import yaml

root = Path(sys.argv[1])
services = Path(sys.argv[2])
docs = []
for path in sorted(root.glob("*.yaml")):
    if path.name == "services.yaml" and path.resolve() != services.resolve():
        continue
    if path.resolve() == services.resolve():
        continue
    docs.extend(d for d in yaml.safe_load_all(path.read_text(encoding="utf-8")) if d)
docs.extend(d for d in yaml.safe_load_all(services.read_text(encoding="utf-8")) if d)
kinds = {d["kind"] for d in docs}
required = {"Group", "User", "Policy", "Service"}
missing = required - kinds
if missing:
    raise SystemExit(f"recursos ausentes: {sorted(missing)}")
print(f"YAML ok: {len(docs)} recursos ({', '.join(sorted(kinds))})")
PY

if ! command -v octeliumctl >/dev/null 2>&1; then
  echo "octeliumctl não está no PATH. Instale com:"
  echo "  curl -fsSL https://octelium.com/install.sh | bash"
  echo "Depois autentique no Cluster e rode este script de novo."
  exit 0
fi

for file in "$CLUSTER"/groups.yaml "$CLUSTER"/policies.yaml "$CLUSTER"/users.yaml "$SERVICES"; do
  echo "octeliumctl apply ${file}"
  octeliumctl apply "$file"
done

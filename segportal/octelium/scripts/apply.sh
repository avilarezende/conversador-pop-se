#!/usr/bin/env bash
# Aplica os recursos ZTNA do SegPortal num Cluster Octelium já instalado.
# Sem octeliumctl, apenas valida o YAML.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLUSTER="${ROOT}/cluster"

python3 - "$CLUSTER" <<'PY'
import sys
from pathlib import Path

import yaml

root = Path(sys.argv[1])
docs = []
for path in sorted(root.glob("*.yaml")):
    docs.extend(d for d in yaml.safe_load_all(path.read_text(encoding="utf-8")) if d)
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

for file in "$CLUSTER"/groups.yaml "$CLUSTER"/policies.yaml "$CLUSTER"/users.yaml "$CLUSTER"/services.yaml; do
  echo "octeliumctl apply ${file}"
  octeliumctl apply "$file"
done

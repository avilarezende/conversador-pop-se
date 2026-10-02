#!/bin/bash
# Validate Kubernetes manifests with kustomize build and kubeconform
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OVERLAYS=(
  "$ROOT/k8s/overlays/development"
  "$ROOT/k8s/overlays/staging"
  "$ROOT/k8s/overlays/production"
)

echo "==> SegPortal K8s manifest validation"

if ! command -v kubectl >/dev/null 2>&1; then
  echo "ERROR: kubectl is required" >&2
  exit 1
fi

for overlay in "${OVERLAYS[@]}"; do
  echo "--- Building $overlay"
  kubectl kustomize "$overlay" > /dev/null
done

if command -v kubeconform >/dev/null 2>&1; then
  for overlay in "${OVERLAYS[@]}"; do
    echo "--- kubeconform $overlay"
    kubectl kustomize "$overlay" | kubeconform -strict -summary
  done
else
  echo "WARN: kubeconform not installed; skipping schema validation"
fi

echo "==> All overlays built successfully."

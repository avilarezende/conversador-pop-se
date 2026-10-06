"""Tests for SegPortal Kubernetes manifests."""

import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
OVERLAYS = [
    ROOT / "k8s" / "overlays" / "development",
    ROOT / "k8s" / "overlays" / "staging",
    ROOT / "k8s" / "overlays" / "production",
]


def kustomize_build(overlay: Path) -> str:
    result = subprocess.run(
        ["kubectl", "kustomize", str(overlay)],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def parse_manifests(manifest_yaml: str) -> list[dict]:
    return list(yaml.safe_load_all(manifest_yaml))


@pytest.mark.parametrize("overlay", OVERLAYS, ids=lambda p: p.name)
class TestKustomizeOverlays:
    def test_kustomize_build_succeeds(self, overlay: Path) -> None:
        output = kustomize_build(overlay)
        assert output.strip()

    def test_namespace_segportal(self, overlay: Path) -> None:
        docs = parse_manifests(kustomize_build(overlay))
        namespaces = [d for d in docs if d.get("kind") == "Namespace"]
        assert any(d["metadata"]["name"] == "segportal" for d in namespaces)

    def test_core_deployments_present(self, overlay: Path) -> None:
        docs = parse_manifests(kustomize_build(overlay))
        deployments = {d["metadata"]["name"] for d in docs if d.get("kind") == "Deployment"}
        assert "guacamole" in deployments
        assert "guacd" in deployments
        assert "proxy-egress" in deployments
        assert "web-browser" in deployments

    def test_bootstrap_job_present(self, overlay: Path) -> None:
        docs = parse_manifests(kustomize_build(overlay))
        jobs = {d["metadata"]["name"] for d in docs if d.get("kind") == "Job"}
        assert "segportal-bootstrap" in jobs
        cms = {d["metadata"]["name"] for d in docs if d.get("kind") == "ConfigMap"}
        assert "segportal-bootstrap-scripts" in cms

    def test_ingress_host(self, overlay: Path) -> None:
        docs = parse_manifests(kustomize_build(overlay))
        ingresses = [d for d in docs if d.get("kind") == "Ingress"]
        assert len(ingresses) >= 1
        rules = ingresses[0]["spec"]["rules"]
        assert any("aqne.jus.br" in r["host"] for r in rules)


class TestBootstrapK8sFiles:
    def test_bootstrap_files_in_sync(self) -> None:
        """Cópias em k8s/bootstrap/files devem espelhar scripts/ (limite do kustomize)."""
        for rel in (
            "bootstrap-segportal.sh",
            "sql/003-segportal-roles.sql",
            "sql/004-default-browser.sql",
            "sql/005-connection-requests.sql",
        ):
            src = (ROOT / "scripts" / rel).read_text(encoding="utf-8")
            dst = (ROOT / "k8s" / "bootstrap" / "files" / rel).read_text(encoding="utf-8")
            assert src == dst, f"Desatualizado: k8s/bootstrap/files/{rel}"


class TestFleetManifests:
    def test_fleet_yaml_exists(self) -> None:
        assert (ROOT / "k8s" / "rancher-fleet" / "fleet.yaml").is_file()

    def test_gitrepo_exists(self) -> None:
        assert (ROOT / "k8s" / "rancher-fleet" / "gitrepo.yaml").is_file()

    def test_gitrepo_points_to_production_overlay(self) -> None:
        content = (ROOT / "k8s" / "rancher-fleet" / "gitrepo.yaml").read_text()
        assert "k8s/overlays/production" in content

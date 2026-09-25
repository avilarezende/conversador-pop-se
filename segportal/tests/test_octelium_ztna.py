"""Manifestos ZTNA do fork SegPortal + Octelium."""

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
CLUSTER = ROOT / "octelium" / "cluster"
OVERLAY = ROOT / "k8s" / "overlays" / "octelium"


def _load_cluster() -> list[dict]:
    docs: list[dict] = []
    for path in sorted(CLUSTER.glob("*.yaml")):
        docs.extend(doc for doc in yaml.safe_load_all(path.read_text(encoding="utf-8")) if doc)
    return docs


@pytest.fixture(scope="module")
def resources() -> list[dict]:
    return _load_cluster()


def test_required_kinds(resources: list[dict]) -> None:
    kinds = {doc["kind"] for doc in resources}
    assert {"Group", "User", "Policy", "Service"} <= kinds


def test_groups_and_demo_users(resources: list[dict]) -> None:
    groups = {doc["metadata"]["name"] for doc in resources if doc["kind"] == "Group"}
    assert groups == {"segportal-users", "segportal-admins"}
    users = {doc["metadata"]["name"]: doc for doc in resources if doc["kind"] == "User"}
    assert set(users) == {"admin", "usuario"}
    assert "segportal-admins" in users["admin"]["spec"]["groups"]
    assert users["usuario"]["spec"]["groups"] == ["segportal-users"]
    assert "allow-all" in users["admin"]["spec"]["authorization"]["policies"]
    assert "authorization" not in users["usuario"]["spec"]


def test_services_are_private_upstreams_with_policy(resources: list[dict]) -> None:
    services = {doc["metadata"]["name"]: doc for doc in resources if doc["kind"] == "Service"}
    assert set(services) == {
        "segportal",
        "portal-auth",
        "desktop-financeiro",
        "desktop-admin",
        "jump-ssh",
    }
    for name, doc in services.items():
        policies = doc["spec"]["authorization"]["policies"]
        assert policies, name
        upstream = doc["spec"]["config"]["upstream"]["url"]
        assert not upstream.startswith("https://segportal."), name
        assert "svc.cluster.local" in upstream or upstream.startswith(("tcp://", "ssh://")), name
    assert services["segportal"]["spec"]["isPublic"] is True
    assert services["portal-auth"]["spec"]["isPublic"] is True
    admin_desktop = services["desktop-admin"]["spec"]["authorization"]["policies"]
    assert admin_desktop == ["allow-segportal-admins"]
    assert services["jump-ssh"]["spec"]["mode"] == "SSH"
    assert "authorization" not in services["jump-ssh"]["spec"]["config"]


def test_policies_allow_expected_groups(resources: list[dict]) -> None:
    policies = {doc["metadata"]["name"]: doc for doc in resources if doc["kind"] == "Policy"}
    users_rules = " ".join(
        rule["condition"]["match"] for rule in policies["allow-segportal-users"]["spec"]["rules"]
    )
    assert "segportal-users" in users_rules
    assert "segportal-admins" in users_rules
    admin_rules = policies["allow-segportal-admins"]["spec"]["rules"]
    assert len(admin_rules) == 1
    assert "segportal-admins" in admin_rules[0]["condition"]["match"]
    assert admin_rules[0]["effect"] == "ALLOW"


def test_apply_script_exists() -> None:
    script = ROOT / "octelium" / "scripts" / "apply.sh"
    assert script.is_file()
    text = script.read_text(encoding="utf-8")
    assert "octeliumctl apply" in text
    assert "--profile" in text


def test_octelium_is_a_separate_instance_not_compose() -> None:
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert "Octelium não é um serviço deste Compose" in compose
    assert "image: octelium" not in compose
    user_data = (ROOT / "octelium" / "instance" / "cloud-init" / "user-data").read_text(encoding="utf-8")
    assert "install-cluster.sh" in user_data
    assert "--nat" in user_data
    assert "--force-machine-ip" in user_data
    assert "docker compose" not in user_data
    creator = (ROOT / "octelium" / "instance" / "create-instance.sh").read_text(encoding="utf-8")
    assert "qemu-system-x86_64" in creator
    template = (ROOT / "octelium" / "instance" / "services.yaml.tpl").read_text(encoding="utf-8")
    assert "http://__UPSTREAM_HOST__:8080" in template
    assert "http://__UPSTREAM_HOST__:8090" in template


def test_octelium_overlay_drops_public_ingress() -> None:
    pytest.importorskip("subprocess")
    import subprocess

    result = subprocess.run(
        ["kubectl", "kustomize", str(OVERLAY)],
        capture_output=True,
        text=True,
        check=True,
    )
    docs = [doc for doc in yaml.safe_load_all(result.stdout) if doc]
    kinds = [doc.get("kind") for doc in docs]
    assert "Ingress" not in kinds
    policies = [doc for doc in docs if doc.get("kind") == "NetworkPolicy"]
    assert policies
    assert policies[0]["metadata"]["name"] == "allow-octelium-and-same-namespace"
    ingress = policies[0]["spec"]["ingress"][0]["from"]
    assert any(
        item.get("namespaceSelector", {})
        .get("matchLabels", {})
        .get("kubernetes.io/metadata.name")
        == "octelium"
        for item in ingress
    )

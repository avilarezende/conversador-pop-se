"""Manifestos declarativos do ZTNA Octelium."""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CLUSTER = ROOT / "octelium" / "cluster"


def _docs(name: str) -> list[dict]:
    text = (CLUSTER / name).read_text(encoding="utf-8")
    return [doc for doc in yaml.safe_load_all(text) if doc]


def test_cluster_files_exist() -> None:
    for name in ("policies.yaml", "groups.yaml", "services.yaml"):
        assert (CLUSTER / name).is_file()
    assert (ROOT / "octelium" / "scripts" / "apply.sh").is_file()
    assert (ROOT / "docs" / "OCTELIUM.md").is_file()


def test_policies_cover_users_and_admins() -> None:
    names = {doc["metadata"]["name"] for doc in _docs("policies.yaml")}
    assert names == {"segportal-usuarios", "segportal-admins"}
    for doc in _docs("policies.yaml"):
        assert doc["kind"] == "Policy"
        assert doc["spec"]["rules"][0]["effect"] == "ALLOW"


def test_portal_is_public_web_and_sessions_stay_private() -> None:
    services = {doc["metadata"]["name"]: doc for doc in _docs("services.yaml")}
    portal = services["portal"]
    assert portal["spec"]["mode"] == "WEB"
    assert portal["spec"]["isPublic"] is True
    upstream = portal["spec"]["config"]["upstream"]["url"]
    assert "portal-auth.segportal.svc.cluster.local:8090" in upstream
    assert "segportal-usuarios" in portal["spec"]["authorization"]["policies"]

    sessoes = services["sessoes"]
    assert sessoes["spec"].get("isPublic") is not True
    assert sessoes["spec"]["mode"] == "HTTP"
    upstream = sessoes["spec"]["config"]["upstream"]["url"]
    assert "guacamole.segportal.svc.cluster.local:8080" in upstream
    assert sessoes["spec"]["authorization"]["policies"] == ["segportal-admins"]


def test_referenced_policies_exist() -> None:
    policy_names = {doc["metadata"]["name"] for doc in _docs("policies.yaml")}
    for doc in _docs("services.yaml"):
        for name in doc["spec"]["authorization"]["policies"]:
            assert name in policy_names


def test_examples_do_not_embed_client_secret() -> None:
    text = (ROOT / "octelium" / "examples" / "identityprovider.example.yaml").read_text(
        encoding="utf-8"
    )
    assert "fromSecret:" in text
    assert "client_secret:" not in text.lower()
    assert "aqne-oidc-client-secret" in text

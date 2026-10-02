"""Testes do portal-auth (dashboard de arquivos + nuvem)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services" / "portal-auth"))

from app.auth import authenticate  # noqa: E402
from app.cloud_drives import mount_demo, unmount, user_cloud_state  # noqa: E402
from app.config import settings  # noqa: E402
from app.files import list_dir, mkdir  # noqa: E402
from app.ldap_shares import ensure_demo_tree, list_user_shares  # noqa: E402
from app.main import app  # noqa: E402

fastapi_test = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture()
def shares_root(tmp_path, monkeypatch):
    root = tmp_path / "shares"
    root.mkdir()
    monkeypatch.setattr(settings, "demo_shares_root", root)
    ensure_demo_tree()
    return root


@pytest.fixture()
def client(shares_root):
    return TestClient(app)


def test_authenticate_ad_flag():
    user = authenticate("usuario", "usuario", prefer_ldap=True)
    assert user.auth_source == "ldap"
    assert user.username == "usuario"


def test_ad_shares_listed(shares_root):
    user = authenticate("usuario", "usuario", prefer_ldap=True)
    shares = list_user_shares(user)
    ids = {s["id"] for s in shares}
    assert "home" in ids
    assert "dept" in ids
    assert any(s.get("from_active_directory") for s in shares)


def test_file_mkdir_and_list(shares_root):
    user = authenticate("usuario", "usuario", prefer_ldap=True)
    mkdir(user, "home", "", "PastaNova")
    listing = list_dir(user, "home", "")
    names = {e["name"] for e in listing["entries"]}
    assert "PastaNova" in names


def test_cloud_mount_demo(shares_root):
    user = authenticate("usuario", "usuario")
    drives = mount_demo(user, "onedrive")
    od = next(d for d in drives if d["id"] == "onedrive")
    assert od["mounted"] is True
    shares = list_user_shares(user)
    assert any(s["id"] == "cloud-onedrive" for s in shares)
    listing = list_dir(user, "cloud-onedrive", "")
    assert listing["entries"]
    unmount(user, "onedrive")
    assert not any(d["mounted"] for d in user_cloud_state(user) if d["id"] == "onedrive")


def test_api_login_and_dashboard(client):
    r = client.post(
        "/api/login",
        json={"username": "usuario", "password": "usuario", "use_active_directory": True},
    )
    assert r.status_code == 200
    assert r.json()["auth_source"] == "ldap"
    dash = client.get("/api/dashboard")
    assert dash.status_code == 200
    body = dash.json()
    assert body["shares"]
    assert body["cloud_drives"]
    assert body["features"]["embedded_browser"] is True
    assert body["features"]["computers"] is True
    assert body["features"]["reminders"] is True
    assert body["features"]["calendar"] is True
    assert "guacamole" not in json.dumps(body).lower()
    health = client.get("/api/health")
    assert health.json()["status"] == "ok"


def test_ui_hides_session_backend_and_labels_computers(client):
    html = client.get("/").text.lower()
    assert "abrir computadores" in html
    assert 'data-panel="browser"' in html
    assert 'data-panel="computers"' in html
    assert "reminders-panel" in html
    assert "calendar-drawer" in html
    assert "lembretes" in html
    assert "calendário" in html or "calendario" in html
    assert "guacamole" not in html
    assert "guacadmin" not in html
    assert "abrir guacamole" not in html


def test_api_cloud_mount_and_files(client):
    client.post("/api/login", json={"username": "admin", "password": "admin"})
    m = client.post("/api/cloud/onedrive/mount")
    assert m.status_code == 200
    assert m.json()["mode"] == "demo"
    files = client.get("/api/files/cloud-onedrive")
    assert files.status_code == 200
    assert "entries" in files.json()

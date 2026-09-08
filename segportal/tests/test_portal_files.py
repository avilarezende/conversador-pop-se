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


def test_computers_allocated_per_user(client):
    client.post("/api/login", json={"username": "usuario", "password": "usuario"})
    dash = client.get("/api/dashboard").json()
    ids = {c["id"] for c in dash["computers"]}
    assert "browser-html" in ids
    assert "desktop-financeiro" in ids
    assert "desktop-admin" not in ids
    assert dash["features"]["admin"] is False

    client.post("/api/logout", json={})
    client.post("/api/login", json={"username": "admin", "password": "admin"})
    admin_dash = client.get("/api/dashboard").json()
    assert admin_dash["features"]["admin"] is True
    admin_ids = {c["id"] for c in admin_dash["computers"]}
    assert "desktop-admin" in admin_ids


def test_admin_can_create_and_allocate_computer(client):
    client.post("/api/login", json={"username": "usuario", "password": "usuario"})
    denied = client.post(
        "/api/admin/computers",
        json={
            "title": "PC Negado",
            "protocol": "rdp",
            "host": "10.1.1.1",
            "assignees": ["usuario"],
        },
    )
    assert denied.status_code == 403

    client.post("/api/logout", json={})
    client.post("/api/login", json={"username": "admin", "password": "admin"})
    users = client.get("/api/admin/users")
    assert users.status_code == 200
    usernames = {u["username"] for u in users.json()["users"]}
    assert "usuario" in usernames
    assert "maria.silva" in usernames

    created = client.post(
        "/api/admin/computers",
        json={
            "title": "Desktop Contábil",
            "protocol": "rdp",
            "host": "10.10.30.12",
            "port": 3389,
            "description": "Estação contábil",
            "assignees": ["usuario", "maria.silva"],
        },
    )
    assert created.status_code == 200
    body = created.json()
    assert body["title"] == "Desktop Contábil"
    assert set(body["assignees"]) == {"usuario", "maria.silva"}
    computer_id = body["id"]

    client.post("/api/logout", json={})
    client.post("/api/login", json={"username": "usuario", "password": "usuario"})
    comps = client.get("/api/computers").json()["computers"]
    assert any(c["id"] == computer_id for c in comps)

    client.post("/api/logout", json={})
    client.post("/api/login", json={"username": "admin", "password": "admin"})
    patched = client.patch(
        f"/api/admin/computers/{computer_id}",
        json={"assignees": ["admin"]},
    )
    assert patched.status_code == 200
    assert patched.json()["assignees"] == ["admin"]

    client.post("/api/logout", json={})
    client.post("/api/login", json={"username": "usuario", "password": "usuario"})
    comps_after = client.get("/api/computers").json()["computers"]
    assert not any(c["id"] == computer_id for c in comps_after)

    client.post("/api/logout", json={})
    client.post("/api/login", json={"username": "admin", "password": "admin"})
    deleted = client.delete(f"/api/admin/computers/{computer_id}")
    assert deleted.status_code == 200


def test_browser_proxy_requires_auth_and_fetches(client, monkeypatch):
    denied = client.get("/api/browser/proxy", params={"url": "https://example.com"})
    assert denied.status_code == 401

    client.post("/api/login", json={"username": "usuario", "password": "usuario"})

    class FakeResp:
        status_code = 200
        headers = {"content-type": "text/html; charset=utf-8"}
        text = '<html><body><a href="/next">Next</a></body></html>'
        content = text.encode()
        url = "https://example.com/"

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def get(self, url):
            assert url.startswith("https://example.com")
            return FakeResp()

    import app.browser_proxy as browser_proxy

    monkeypatch.setattr(browser_proxy.httpx, "AsyncClient", FakeClient)
    ok = client.get("/api/browser/proxy", params={"url": "https://example.com"})
    assert ok.status_code == 200
    assert "example.com" in ok.text
    assert "/api/browser/proxy?url=" in ok.text


def test_ui_has_admin_panel(client):
    html = client.get("/").text.lower()
    assert 'data-panel="admin"' in html
    assert "novo acesso a computador" in html
    assert "alocar a usuários" in html
    assert "admin-computer-form" in html
    assert "proxy de navegação" in html
    assert "admin-proxy-form" in html
    assert "proxy-allowed-domains" in html


def test_admin_proxy_policy_and_enforcement(client, monkeypatch):
    client.post("/api/login", json={"username": "usuario", "password": "usuario"})
    denied = client.put(
        "/api/admin/proxy-policy",
        json={"mode": "allowlist", "allowed_domains": ["example.com"]},
    )
    assert denied.status_code == 403

    client.post("/api/logout", json={})
    client.post("/api/login", json={"username": "admin", "password": "admin"})
    saved = client.put(
        "/api/admin/proxy-policy",
        json={
            "mode": "allowlist",
            "default_action": "deny",
            "exception_mode": "per_user",
            "admin_bypass": True,
            "allowed_domains": [".gov.br", "example.com"],
            "allowed_url_prefixes": [],
            "blocked_domains": ["blocked.test"],
            "blocked_url_prefixes": [],
            "blocked_keywords": ["evil"],
            "exceptions": [
                {
                    "label": "Docs",
                    "domains": ["docs.google.com"],
                    "assignees": ["usuario"],
                    "enabled": True,
                }
            ],
            "schedules": [
                {
                    "label": "Sempre",
                    "enabled": False,
                    "days": [0, 1, 2, 3, 4, 5, 6],
                    "start": "00:00",
                    "end": "23:59",
                    "timezone": "America/Sao_Paulo",
                    "outside_action": "deny",
                }
            ],
        },
    )
    assert saved.status_code == 200
    policy = saved.json()["policy"]
    assert policy["mode"] == "allowlist"
    assert "example.com" in policy["allowed_domains"]

    class FakeResp:
        status_code = 200
        headers = {"content-type": "text/html; charset=utf-8"}
        text = "<html><body>ok</body></html>"
        content = text.encode()
        url = "https://example.com/"

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def get(self, url):
            return FakeResp()

    import app.browser_proxy as browser_proxy

    monkeypatch.setattr(browser_proxy.httpx, "AsyncClient", FakeClient)

    # admin bypass
    ok_admin = client.get("/api/browser/proxy", params={"url": "https://blocked.test"})
    assert ok_admin.status_code == 200

    client.post("/api/logout", json={})
    client.post("/api/login", json={"username": "usuario", "password": "usuario"})
    blocked = client.get("/api/browser/proxy", params={"url": "https://blocked.test/page"})
    assert blocked.status_code == 403
    assert "filtrado" in blocked.json()["detail"].lower() or "filtrado" in blocked.json()["detail"]

    not_allowed = client.get("/api/browser/proxy", params={"url": "https://random-site.xyz"})
    assert not_allowed.status_code == 403

    allowed = client.get("/api/browser/proxy", params={"url": "https://example.com"})
    assert allowed.status_code == 200

    exception_ok = client.get("/api/browser/proxy", params={"url": "https://docs.google.com/doc"})
    assert exception_ok.status_code == 200

    summary = client.get("/api/proxy-policy")
    assert summary.status_code == 200
    assert summary.json()["policy"]["mode"] == "allowlist"

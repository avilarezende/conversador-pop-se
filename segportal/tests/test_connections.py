"""Testes do navegador padrão e pedidos de conexão."""

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent


class TestDefaultBrowserAndRequests:
    def test_requests_policy(self) -> None:
        data = yaml.safe_load(
            (ROOT / "config" / "connections" / "requests.yaml").read_text(encoding="utf-8")
        )
        assert data["requests"]["require_admin_approval"] is True
        assert data["default_browser"]["enabled"] is True
        assert data["default_browser"]["connection_name"] == "Navegador Web SegPortal"
        assert data["default_browser"]["port"] == 5900

    def test_default_browser_sql(self) -> None:
        text = (ROOT / "scripts" / "sql" / "004-default-browser.sql").read_text(encoding="utf-8")
        assert "Navegador Web SegPortal" in text
        assert "web-browser" in text
        assert "segportal-browser-default" in text

    def test_connection_requests_sql(self) -> None:
        text = (ROOT / "scripts" / "sql" / "005-connection-requests.sql").read_text(encoding="utf-8")
        assert "segportal_connection_request" in text
        assert "pending" in text

    def test_scripts_exist(self) -> None:
        for name in (
            "bootstrap-segportal.sh",
            "request-connection.sh",
            "approve-connection-request.sh",
            "seed-browser-and-requests.sh",
        ):
            assert (ROOT / "scripts" / name).is_file()

    def test_bootstrap_is_wired_in_compose(self) -> None:
        for name in ("docker-compose.yml", "docker-compose.dev.yml"):
            text = (ROOT / name).read_text(encoding="utf-8")
            assert "segportal-bootstrap:" in text
            assert "bootstrap-segportal.sh" in text
            assert "web-browser:" in text

    def test_bootstrap_grants_all_users(self) -> None:
        text = (ROOT / "scripts" / "sql" / "004-default-browser.sql").read_text(encoding="utf-8")
        assert "e.type = 'USER'" in text
        assert "hostname', 'web-browser'" in text or "('hostname', 'web-browser')" in text

    def test_web_browser_dockerfile(self) -> None:
        text = (ROOT / "services" / "web-browser" / "Dockerfile").read_text(encoding="utf-8")
        assert "jlesage/firefox" in text
        assert "SECURE_CONNECTION=0" in text
        assert "VNC_LISTENING_PORT=5900" in text

    def test_connections_doc(self) -> None:
        text = (ROOT / "docs" / "CONNECTIONS.md").read_text(encoding="utf-8")
        assert "aprov" in text.lower()
        assert "Navegador Web SegPortal" in text
        assert "bootstrap" in text.lower()
        assert "Não é necessário seed manual" in text or "nao e necessario seed manual" in text.lower()

    def test_user_can_request_but_needs_approval(self) -> None:
        roles = yaml.safe_load(
            (ROOT / "config" / "roles" / "roles.yaml").read_text(encoding="utf-8")
        )
        assert "request_new_connections" in roles["roles"]["user"]["capabilities"]
        assert "approve_connection_requests" in roles["roles"]["admin"]["capabilities"]
        assert "use_default_html_browser" in roles["roles"]["user"]["capabilities"]

"""Testes dos papéis SegPortal (admin / usuário)."""

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent


class TestRolesConfig:
    @pytest.fixture
    def roles(self) -> dict:
        path = ROOT / "config" / "roles" / "roles.yaml"
        assert path.is_file()
        return yaml.safe_load(path.read_text(encoding="utf-8"))

    def test_admin_and_user_roles_defined(self, roles: dict) -> None:
        assert "admin" in roles["roles"]
        assert "user" in roles["roles"]

    def test_admin_has_system_permissions(self, roles: dict) -> None:
        perms = roles["roles"]["admin"]["system_permissions"]
        assert "ADMINISTER" in perms
        assert "CREATE_CONNECTION" in perms
        assert "CREATE_USER" in perms

    def test_user_has_no_system_permissions(self, roles: dict) -> None:
        assert roles["roles"]["user"]["system_permissions"] == []

    def test_user_only_read_connections(self, roles: dict) -> None:
        assert roles["roles"]["user"]["connection_permissions"] == ["READ"]

    def test_user_restricted_from_other_sessions(self, roles: dict) -> None:
        restrictions = roles["roles"]["user"]["restrictions"]
        assert "no_view_other_sessions" in restrictions
        assert "no_configure_connections_without_approval" in restrictions

    def test_ad_groups_mapped(self, roles: dict) -> None:
        assert roles["roles"]["admin"]["ad_group"] == "GG-SegPortal-Admin"
        assert roles["roles"]["user"]["ad_group"] == "GG-SegPortal-Usuarios"

    def test_seed_sql_exists(self) -> None:
        path = ROOT / "scripts" / "sql" / "003-segportal-roles.sql"
        assert path.is_file()
        text = path.read_text(encoding="utf-8")
        assert "segportal-admins" in text
        assert "segportal-users" in text
        assert "usuario" in text

    def test_roles_doc_exists(self) -> None:
        assert (ROOT / "docs" / "ROLES.md").is_file()

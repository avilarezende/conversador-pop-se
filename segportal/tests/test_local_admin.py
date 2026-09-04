"""Testes de LDAP opcional e admin local."""

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent


class TestLdapSettings:
    @pytest.fixture
    def settings(self) -> dict:
        path = ROOT / "config" / "ldap" / "ldap-settings.yaml"
        assert path.is_file()
        return yaml.safe_load(path.read_text(encoding="utf-8"))

    def test_ldap_disabled_by_default(self, settings: dict) -> None:
        assert settings["ldap"]["enabled"] is False

    def test_ldap_has_server_port_domain_uid(self, settings: dict) -> None:
        ldap = settings["ldap"]
        assert "hostname" in ldap
        assert "port" in ldap
        assert "domain" in ldap
        assert "username_attribute" in ldap
        assert "encryption_method" in ldap

    def test_ldap_tls_cert_and_chain_fields(self, settings: dict) -> None:
        tls = settings["ldap"]["tls"]
        assert "ca_chain_file" in tls
        assert "server_certificate_file" in tls
        assert "truststore_file" in tls

    def test_local_users_always_enabled(self, settings: dict) -> None:
        local = settings["local_users"]
        assert local["enabled"] is True
        assert local["default_admin"]["username"] == "guacadmin"
        assert local["default_admin"]["initial_password"] == "guacadmin"


class TestLocalAdminDocsAndScripts:
    def test_local_admin_doc(self) -> None:
        text = (ROOT / "docs" / "LOCAL_ADMIN.md").read_text(encoding="utf-8")
        assert "guacadmin" in text
        assert "change-local-password" in text
        assert "delete-local-user" in text
        assert "LDAP_ENABLED" in text

    def test_password_script_exists(self) -> None:
        path = ROOT / "scripts" / "change-local-password.sh"
        assert path.is_file()
        assert "password_hash" in path.read_text(encoding="utf-8")

    def test_delete_script_exists(self) -> None:
        path = ROOT / "scripts" / "delete-local-user.sh"
        assert path.is_file()
        text = path.read_text(encoding="utf-8")
        assert "--disable" in text
        assert "--delete" in text

    def test_entrypoint_strips_ldap_when_disabled(self) -> None:
        text = (ROOT / "services" / "guacamole" / "entrypoint.sh").read_text(encoding="utf-8")
        assert 'LDAP_ENABLED' in text
        assert "grep -v '^ldap-'" in text

    def test_env_example_ldap_disabled_by_default(self) -> None:
        text = (ROOT / ".env.example").read_text(encoding="utf-8")
        assert "LDAP_ENABLED=false" in text
        assert "LDAP_CA_CHAIN_FILE" in text

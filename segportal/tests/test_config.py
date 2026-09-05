"""Tests for SegPortal configuration files."""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def config_root() -> Path:
    return ROOT / "config"


class TestGuacamoleProperties:
    def test_guacamole_properties_exists(self, config_root: Path) -> None:
        path = config_root / "guacamole" / "guacamole.properties"
        assert path.is_file()

    def test_guacamole_properties_has_ldap(self, config_root: Path) -> None:
        content = (config_root / "guacamole" / "guacamole.properties").read_text()
        assert "ldap-hostname" in content
        assert "ldap-user-base-dn" in content
        assert "${LDAP_HOSTNAME" in content

    def test_guacamole_properties_has_postgresql(self, config_root: Path) -> None:
        content = (config_root / "guacamole" / "guacamole.properties").read_text()
        assert "postgresql-hostname" in content
        assert "postgresql-database" in content

    def test_guacamole_properties_has_session_timeout(self, config_root: Path) -> None:
        content = (config_root / "guacamole" / "guacamole.properties").read_text()
        assert "api-session-timeout" in content


class TestLdapProperties:
    def test_ldap_properties_exists(self, config_root: Path) -> None:
        path = config_root / "ldap" / "ldap.properties"
        assert path.is_file()

    def test_ldap_domain_tjse(self, config_root: Path) -> None:
        content = (config_root / "ldap" / "ldap.properties").read_text()
        assert "tjse.jus.br" in content
        assert "sAMAccountName" in content


class TestSquidConfig:
    def test_squid_conf_exists(self, config_root: Path) -> None:
        path = config_root / "proxy" / "squid.conf"
        assert path.is_file()

    def test_squid_whitelist_tjse(self, config_root: Path) -> None:
        content = (config_root / "proxy" / "squid.conf").read_text()
        assert "tjse_whitelist" in content
        assert ".tjse.jus.br" in content


class TestDockerCompose:
    def test_docker_compose_exists(self) -> None:
        assert (ROOT / "docker-compose.yml").is_file()

    def test_guacamole_build_context_root(self) -> None:
        content = (ROOT / "docker-compose.yml").read_text()
        assert "context: ." in content
        assert "services/guacamole/Dockerfile" in content

    def test_required_services(self) -> None:
        content = (ROOT / "docker-compose.yml").read_text()
        for service in (
            "postgres",
            "guacd",
            "guacamole",
            "proxy-egress",
            "web-browser",
            "portal-auth",
            "segportal-bootstrap",
        ):
            assert f"{service}:" in content

    def test_dev_compose_auto_browser(self) -> None:
        content = (ROOT / "docker-compose.dev.yml").read_text()
        assert "segportal-bootstrap:" in content
        assert "web-browser:" in content
        assert "Navegador Web SegPortal" in content


class TestGuacamoleDockerfile:
    def test_ldap_extension_version(self) -> None:
        dockerfile = (ROOT / "services" / "guacamole" / "Dockerfile").read_text()
        assert "guacamole-auth-ldap-${LDAP_EXTENSION_VERSION}.jar" in dockerfile
        assert "guacamole-auth-ldap-${LDAP_EXTENSION_VERSION}.tar.gz" in dockerfile
        assert "GUACAMOLE_VERSION=1.5.5" in dockerfile

    def test_build_from_repo_root(self) -> None:
        dockerfile = (ROOT / "services" / "guacamole" / "Dockerfile").read_text()
        assert "COPY config/guacamole/" in dockerfile
        assert "COPY services/guacamole/" in dockerfile


class TestDocumentationImages:
    """Imagens JPG para exibição no GitHub."""

    @pytest.fixture
    def images_dir(self) -> Path:
        return ROOT / "docs" / "images"

    @pytest.mark.parametrize(
        "name",
        [
            "architecture-overview.jpg",
            "auth-flow.jpg",
            "k8s-pods.jpg",
            "segportal-mockup.jpg",
            "usage-login.jpg",
            "usage-portal.jpg",
            "usage-session.jpg",
            "usage-browser.jpg",
            "usage-browser-bacen.jpg",
            "admin-approvals.jpg",
            "portal-files.jpg",
            "portal-home-ad.jpg",
        ],
    )
    def test_jpg_images_exist(self, images_dir: Path, name: str) -> None:
        assert (images_dir / name).is_file(), f"Imagem ausente: {name}"

    def test_manual_exists(self) -> None:
        assert (ROOT / "docs" / "MANUAL.md").is_file()
        assert (ROOT / "docs" / "USER_MANUAL.md").is_file()
        assert (ROOT / "docs" / "ADMIN_MANUAL.md").is_file()

    def test_docs_mention_default_browser(self) -> None:
        for rel in (
            "docs/MANUAL.md",
            "docs/USAGE.md",
            "docs/CONNECTIONS.md",
            "docs/CONFIGURATION.md",
            "docs/ROLES.md",
            "README.md",
        ):
            text = (ROOT / rel).read_text(encoding="utf-8")
            assert "Navegador Web SegPortal" in text, f"Falta navegador padrão em {rel}"

    def test_docs_mention_bacen_example(self) -> None:
        for rel in ("docs/USAGE.md", "docs/USER_MANUAL.md", "README.md"):
            text = (ROOT / rel).read_text(encoding="utf-8")
            assert "bcb.gov.br" in text or "Bacen" in text, f"Falta exemplo Bacen em {rel}"

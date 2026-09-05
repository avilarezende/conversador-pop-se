"""Configuração do portal-auth SegPortal."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[3]
SHARES_YAML = ROOT / "config" / "files" / "shares.yaml"
LDAP_YAML = ROOT / "config" / "ldap" / "ldap-settings.yaml"


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


@lru_cache
def shares_config() -> dict[str, Any]:
    return _load_yaml(SHARES_YAML)


@lru_cache
def ldap_config() -> dict[str, Any]:
    return _load_yaml(LDAP_YAML)


def env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


class Settings:
    def __init__(self) -> None:
        demo = shares_config().get("shares", {}).get("demo", {})
        ui = shares_config().get("ui", {})
        ldap_on = bool(ldap_config().get("ldap", {}).get("enabled", False))
        demo_root = demo.get("root", "/tmp/segportal-shares")
        self.session_secret = os.getenv("PORTAL_SESSION_SECRET", "segportal-dev-secret-change-me")
        self.ldap_enabled = env_bool("LDAP_ENABLED", ldap_on)
        self.guacamole_url = os.getenv("GUACAMOLE_PUBLIC_URL", "http://localhost:8080/guacamole")
        self.demo_shares_root = Path(os.getenv("DEMO_SHARES_ROOT", demo_root))
        max_upload = str(ui.get("max_upload_mb", 100))
        self.max_upload_mb = int(os.getenv("PORTAL_MAX_UPLOAD_MB", max_upload))
        self.portal_port = int(os.getenv("PORTAL_PORT", "8090"))


settings = Settings()

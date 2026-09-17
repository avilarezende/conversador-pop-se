"""OneDrive e Google Drive no dashboard principal."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

from .auth import PortalUser
from .config import settings, shares_config

_MOUNTS: dict[str, dict[str, Any]] = {}


def _cloud_root(username: str, provider: str) -> Path:
    root = settings.demo_shares_root / "cloud" / username / provider
    root.mkdir(parents=True, exist_ok=True)
    return root


def _seed_cloud_files(provider: str, root: Path) -> None:
    samples = {
        "onedrive": [
            ("Documentos/Contrato.txt", "Rascunho OneDrive (demo)\n"),
            ("Imagens/.keep", ""),
            ("README.txt", "Pasta OneDrive montada no SegPortal (modo demonstração).\n"),
        ],
        "google_drive": [
            ("Meu Drive/Anotacoes.txt", "Notas do Google Drive (demo)\n"),
            ("Compartilhados/.keep", ""),
            ("README.txt", "Pasta Google Drive montada no SegPortal (modo demonstração).\n"),
        ],
    }
    for name, content in samples.get(provider, []):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(content, encoding="utf-8")


def list_providers() -> list[dict[str, Any]]:
    cfg = shares_config().get("cloud_drives", {})
    items = []
    for key in ("onedrive", "google_drive"):
        item = cfg.get(key) or {}
        if not item.get("enabled", False):
            continue
        items.append(
            {
                "id": key,
                "label": item.get("label", key),
                "description": item.get("description", ""),
                "oauth_configured": bool(item.get("client_id")),
            }
        )
    return items


def user_cloud_state(user: PortalUser) -> list[dict[str, Any]]:
    mounts = _MOUNTS.get(user.username, {})
    out = []
    for provider in list_providers():
        mounted = mounts.get(provider["id"])
        out.append(
            {
                **provider,
                "mounted": bool(mounted),
                "mounted_at": (mounted or {}).get("mounted_at"),
                "account": (mounted or {}).get("account"),
                "mode": (mounted or {}).get("mode"),
                "share_id": f"cloud-{provider['id']}" if mounted else None,
            }
        )
    return out


def mounted_shares(user: PortalUser) -> list[dict[str, Any]]:
    """Shares navegáveis das nuvens já montadas."""
    items: list[dict[str, Any]] = []
    mounts = _MOUNTS.get(user.username, {})
    cfg = shares_config().get("cloud_drives", {})
    for provider, meta in mounts.items():
        label = (cfg.get(provider) or {}).get("label", provider)
        root = _cloud_root(user.username, provider)
        rel = str(root.relative_to(settings.demo_shares_root))
        items.append(
            {
                "id": f"cloud-{provider}",
                "label": label,
                "source": "cloud",
                "backend": "demo",
                "path": rel,
                "provider": provider,
                "unc": None,
                "read_only": False,
                "available": True,
                "from_active_directory": False,
                "mode": meta.get("mode", "demo"),
                "account": meta.get("account"),
            }
        )
    return items


def start_oauth(user: PortalUser, provider: str, public_base: str) -> dict[str, Any]:
    cfg = shares_config().get("cloud_drives", {}).get(provider)
    if not cfg or not cfg.get("enabled"):
        raise ValueError("Provedor indisponível")

    if not cfg.get("client_id"):
        return {
            "mode": "demo",
            "authorize_url": None,
            "message": (
                f"{cfg.get('label')} montado em modo demonstração. "
                "Configure client_id em config/files/shares.yaml para OAuth real."
            ),
        }

    redirect_uri = public_base + cfg.get("redirect_path", f"/api/cloud/{provider}/callback")
    if provider == "onedrive":
        tenant = cfg.get("tenant_id", "common")
        params = {
            "client_id": cfg["client_id"],
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "response_mode": "query",
            "scope": " ".join(cfg.get("scopes", [])),
            "state": f"{user.username}:{provider}",
        }
        url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize?{urlencode(params)}"
    else:
        params = {
            "client_id": cfg["client_id"],
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(cfg.get("scopes", [])),
            "access_type": "offline",
            "prompt": "consent",
            "state": f"{user.username}:{provider}",
        }
        url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return {"mode": "oauth", "authorize_url": url, "message": "Redirecionando"}


def mount_demo(user: PortalUser, provider: str) -> list[dict[str, Any]]:
    cfg = shares_config().get("cloud_drives", {}).get(provider) or {}
    root = _cloud_root(user.username, provider)
    _seed_cloud_files(provider, root)
    _MOUNTS.setdefault(user.username, {})[provider] = {
        "mounted_at": int(time.time()),
        "account": f"{user.username}@demo.local",
        "mode": "demo",
        "label": cfg.get("label", provider),
        "path": str(root),
    }
    return user_cloud_state(user)


def unmount(user: PortalUser, provider: str) -> list[dict[str, Any]]:
    _MOUNTS.get(user.username, {}).pop(provider, None)
    return user_cloud_state(user)

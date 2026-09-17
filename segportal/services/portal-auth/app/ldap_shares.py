"""Resolução de shares AD / corporativas para o dashboard pessoal."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .auth import PortalUser
from .cloud_drives import mounted_shares
from .config import settings, shares_config


def _demo_root() -> Path:
    root = settings.demo_shares_root
    root.mkdir(parents=True, exist_ok=True)
    return root


def ensure_demo_tree() -> None:
    cfg = shares_config().get("shares", {}).get("demo", {})
    if not cfg.get("enabled", True):
        return
    root = _demo_root()
    samples = {
        "admin/home": [
            ("Relatorio_mensal.docx.txt", "Relatório mensal — rascunho\n"),
            ("Notas.txt", "Anotações do administrador\n"),
            ("Projetos/README.md", "# Projetos\nPasta de projetos do home AD.\n"),
        ],
        "admin/dept": [
            ("Normas/Politica_Acesso.txt", "Política de acesso remoto AQNE\n"),
            ("Planilhas/Controle.csv", "item;valor\nVPN;desativado\nSegPortal;ativo\n"),
        ],
        "usuario/home": [
            ("Curriculo.txt", "Documento pessoal do usuário\n"),
            ("Fotos/.keep", ""),
            ("Trabalho/Tarefas.txt", "1. Revisar processo\n2. Enviar despacho\n"),
        ],
        "usuario/dept": [
            ("Comunicados/Aviso.txt", "Comunicado interno\n"),
        ],
    }
    for rel, files in samples.items():
        base = root / rel
        base.mkdir(parents=True, exist_ok=True)
        for name, content in files:
            path = base / name
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                path.write_text(content, encoding="utf-8")


def list_user_shares(user: PortalUser) -> list[dict[str, Any]]:
    ensure_demo_tree()
    cfg = shares_config().get("shares", {})
    demo = cfg.get("demo", {})
    items: list[dict[str, Any]] = []

    if demo.get("enabled", True):
        for share in demo.get("users", {}).get(user.username, []):
            item = {
                "id": share["id"],
                "label": share["label"],
                "source": share.get("source", "demo"),
                "backend": "demo",
                "path": share["path"],
                "unc": None,
                "read_only": False,
                "available": True,
                "from_active_directory": share.get("source") == "ad-home"
                or user.auth_source == "ldap",
            }
            if share.get("source") == "ad-home":
                item["unc"] = f"\\\\fs01\\homes\\{user.username}"
                item["drive_letter"] = "H:"
                item["ad_attribute"] = cfg.get("ad_attributes", {}).get(
                    "home_directory", "homeDirectory"
                )
            items.append(item)

    if settings.ldap_enabled or user.auth_source == "ldap":
        for corp in cfg.get("corporate", []):
            if any(i["id"] == corp["id"] for i in items):
                # enriquece item demo existente
                for i in items:
                    if i["id"] == corp["id"]:
                        i["unc"] = corp.get("unc")
                        i["read_only"] = bool(corp.get("read_only", False))
                        i["mount_hint"] = corp.get("mount_hint")
                        i["from_active_directory"] = True
                continue
            items.append(
                {
                    "id": corp["id"],
                    "label": corp["label"],
                    "source": "corporate",
                    "backend": "demo",
                    "path": f"{user.username}/dept",
                    "unc": corp.get("unc"),
                    "read_only": bool(corp.get("read_only", False)),
                    "available": True,
                    "from_active_directory": True,
                    "mount_hint": corp.get("mount_hint"),
                }
            )

    items.extend(mounted_shares(user))
    return items


def resolve_share_root(user: PortalUser, share_id: str) -> tuple[Path, dict[str, Any]]:
    shares = {s["id"]: s for s in list_user_shares(user)}
    if share_id not in shares:
        raise FileNotFoundError(f"Share '{share_id}' não disponível")
    meta = shares[share_id]
    root = (_demo_root() / meta["path"]).resolve()
    demo_root = _demo_root().resolve()
    if not str(root).startswith(str(demo_root)):
        raise PermissionError("Caminho inválido")
    root.mkdir(parents=True, exist_ok=True)
    return root, meta

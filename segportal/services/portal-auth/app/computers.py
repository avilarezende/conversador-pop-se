"""Persistência de acessos a computadores (alocações admin → usuários)."""

from __future__ import annotations

import json
import threading
import time
import uuid
from pathlib import Path
from typing import Any

from fastapi import HTTPException

from .auth import DEMO_USERS, PortalUser
from .config import settings

_LOCK = threading.Lock()

DEFAULT_COMPUTERS: list[dict[str, Any]] = [
    {
        "id": "browser-html",
        "title": "Navegador Web SegPortal",
        "description": "Navegação corporativa HTML5 já disponível na aba Navegador.",
        "kind": "browser",
        "protocol": "browser",
        "badge": "Padrão",
        "host": "",
        "port": None,
        "assignees": ["*"],
        "embed": "",
        "created_by": "system",
        "created_at": 0,
        "builtin": True,
    },
    {
        "id": "desktop-financeiro",
        "title": "Desktop Financeiro",
        "description": "Estação remota com sistemas financeiros (liberação sob demanda).",
        "kind": "desktop",
        "protocol": "rdp",
        "badge": "RDP",
        "host": "10.10.20.51",
        "port": 3389,
        "assignees": ["usuario", "admin"],
        "embed": "/browser/desktop.html?name=Desktop%20Financeiro",
        "created_by": "system",
        "created_at": 0,
        "builtin": True,
    },
    {
        "id": "desktop-admin",
        "title": "Desktop Administrativo",
        "description": "Estação remota para tarefas administrativas.",
        "kind": "desktop",
        "protocol": "rdp",
        "badge": "RDP",
        "host": "10.10.20.10",
        "port": 3389,
        "assignees": ["admin"],
        "embed": "/browser/desktop.html?name=Desktop%20Administrativo",
        "created_by": "system",
        "created_at": 0,
        "builtin": True,
    },
]


def _store_path() -> Path:
    root = Path(settings.demo_shares_root)
    root.mkdir(parents=True, exist_ok=True)
    return root / "computers.json"


def _load() -> list[dict[str, Any]]:
    path = _store_path()
    if not path.is_file():
        _save(DEFAULT_COMPUTERS)
        return [dict(c) for c in DEFAULT_COMPUTERS]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list) or not data:
            _save(DEFAULT_COMPUTERS)
            return [dict(c) for c in DEFAULT_COMPUTERS]
        return data
    except (json.JSONDecodeError, OSError):
        _save(DEFAULT_COMPUTERS)
        return [dict(c) for c in DEFAULT_COMPUTERS]


def _save(items: list[dict[str, Any]]) -> None:
    path = _store_path()
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def _normalize_assignees(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, str):
        raw = [raw]
    out: list[str] = []
    for item in raw:
        name = str(item).strip().lower()
        if name and name not in out:
            out.append(name)
    return out


def require_admin(user: PortalUser) -> None:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores")


def list_directory_users() -> list[dict[str, str]]:
    """Usuários locais demo + exemplos de AD para alocação."""
    users: list[dict[str, str]] = []
    for username, meta in DEMO_USERS.items():
        users.append(
            {
                "username": username,
                "display_name": meta["display_name"],
                "role": meta["role"],
                "source": "local",
            }
        )
    # Contas AD de exemplo (visíveis para o admin alocar)
    ad_examples = [
        ("maria.silva", "Maria Silva", "user"),
        ("joao.souza", "João Souza", "user"),
        ("financeiro.svc", "Conta Serviço Financeiro", "user"),
    ]
    known = {u["username"] for u in users}
    for username, display, role in ad_examples:
        if username not in known:
            users.append(
                {
                    "username": username,
                    "display_name": display,
                    "role": role,
                    "source": "ad",
                }
            )
    # Inclui assignees já usados que não estejam na lista
    with _LOCK:
        for computer in _load():
            for assignee in computer.get("assignees") or []:
                if assignee in {"*", ""} or assignee in known:
                    continue
                known.add(assignee)
                users.append(
                    {
                        "username": assignee,
                        "display_name": assignee,
                        "role": "user",
                        "source": "ad",
                    }
                )
    return users


def list_for_user(user: PortalUser) -> list[dict[str, Any]]:
    with _LOCK:
        items = _load()
    username = user.username.lower()
    is_admin = user.role == "admin"
    visible: list[dict[str, Any]] = []
    for item in items:
        assignees = [a.lower() for a in (item.get("assignees") or [])]
        if is_admin or "*" in assignees or username in assignees:
            visible.append(_public_computer(item, include_assignees=is_admin))
    return visible


def list_all(user: PortalUser) -> list[dict[str, Any]]:
    require_admin(user)
    with _LOCK:
        items = _load()
    return [_public_computer(item, include_assignees=True) for item in items]


def _public_computer(item: dict[str, Any], include_assignees: bool = False) -> dict[str, Any]:
    out = {
        "id": item["id"],
        "title": item.get("title") or "Computador",
        "description": item.get("description") or "",
        "kind": item.get("kind") or "desktop",
        "protocol": item.get("protocol") or "rdp",
        "badge": item.get("badge") or (item.get("protocol") or "RDP").upper(),
        "host": item.get("host") or "",
        "port": item.get("port"),
        "embed": item.get("embed")
        or f"/browser/desktop.html?name={item.get('title', 'Sessão').replace(' ', '%20')}",
        "builtin": bool(item.get("builtin")),
        "created_by": item.get("created_by") or "",
        "created_at": item.get("created_at") or 0,
    }
    if include_assignees:
        out["assignees"] = list(item.get("assignees") or [])
    return out


def create_computer(user: PortalUser, body: dict[str, Any]) -> dict[str, Any]:
    require_admin(user)
    title = str(body.get("title") or "").strip()
    if not title:
        raise HTTPException(status_code=400, detail="Informe o título do acesso")
    protocol = str(body.get("protocol") or "rdp").strip().lower()
    if protocol not in {"rdp", "vnc", "ssh", "browser"}:
        raise HTTPException(status_code=400, detail="Protocolo inválido")
    assignees = _normalize_assignees(body.get("assignees"))
    if not assignees:
        raise HTTPException(status_code=400, detail="Selecione ao menos um usuário")
    kind = "browser" if protocol == "browser" else "desktop"
    host = str(body.get("host") or "").strip()
    port_raw = body.get("port")
    port = int(port_raw) if port_raw not in (None, "") else None
    if kind == "desktop" and not host:
        raise HTTPException(status_code=400, detail="Informe o host do computador")
    computer = {
        "id": f"pc-{uuid.uuid4().hex[:10]}",
        "title": title,
        "description": str(body.get("description") or "").strip(),
        "kind": kind,
        "protocol": protocol,
        "badge": protocol.upper(),
        "host": host,
        "port": port,
        "assignees": assignees,
        "embed": f"/browser/desktop.html?name={title.replace(' ', '%20')}",
        "created_by": user.username,
        "created_at": int(time.time()),
        "builtin": False,
    }
    with _LOCK:
        items = _load()
        items.append(computer)
        _save(items)
    return _public_computer(computer, include_assignees=True)


def update_computer(user: PortalUser, computer_id: str, body: dict[str, Any]) -> dict[str, Any]:
    require_admin(user)
    with _LOCK:
        items = _load()
        found = None
        for item in items:
            if item["id"] == computer_id:
                found = item
                break
        if not found:
            raise HTTPException(status_code=404, detail="Acesso não encontrado")
        if "title" in body and str(body["title"]).strip():
            found["title"] = str(body["title"]).strip()
            found["embed"] = f"/browser/desktop.html?name={found['title'].replace(' ', '%20')}"
        if "description" in body:
            found["description"] = str(body["description"] or "").strip()
        if "host" in body:
            found["host"] = str(body["host"] or "").strip()
        if "port" in body:
            port_raw = body.get("port")
            found["port"] = int(port_raw) if port_raw not in (None, "") else None
        if "protocol" in body and str(body["protocol"]).strip():
            protocol = str(body["protocol"]).strip().lower()
            if protocol not in {"rdp", "vnc", "ssh", "browser"}:
                raise HTTPException(status_code=400, detail="Protocolo inválido")
            found["protocol"] = protocol
            found["kind"] = "browser" if protocol == "browser" else "desktop"
            found["badge"] = protocol.upper()
        if "assignees" in body:
            assignees = _normalize_assignees(body.get("assignees"))
            if not assignees:
                raise HTTPException(status_code=400, detail="Selecione ao menos um usuário")
            found["assignees"] = assignees
        _save(items)
        return _public_computer(found, include_assignees=True)


def delete_computer(user: PortalUser, computer_id: str) -> dict[str, Any]:
    require_admin(user)
    with _LOCK:
        items = _load()
        found = next((i for i in items if i["id"] == computer_id), None)
        if not found:
            raise HTTPException(status_code=404, detail="Acesso não encontrado")
        if found.get("builtin"):
            raise HTTPException(status_code=400, detail="Não é possível excluir acessos padrão do sistema")
        items = [i for i in items if i["id"] != computer_id]
        _save(items)
    return {"ok": True, "id": computer_id}

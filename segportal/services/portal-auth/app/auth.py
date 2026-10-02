"""Autenticação do portal (sessão cookie + usuários demo)."""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import asdict, dataclass
from typing import Any

from fastapi import HTTPException, Request, Response

from .config import ldap_config, settings

DEMO_USERS: dict[str, dict[str, Any]] = {
    "admin": {
        "password": "admin",
        "display_name": "Administrador SegPortal",
        "role": "admin",
        "email": "admin@aqne.jus.br",
    },
    "usuario": {
        "password": "usuario",
        "display_name": "Usuário Demonstração",
        "role": "user",
        "email": "usuario@aqne.jus.br",
    },
}


@dataclass
class PortalUser:
    username: str
    display_name: str
    role: str
    email: str
    auth_source: str  # local | ldap


def _sign(payload: str) -> str:
    return hmac.new(settings.session_secret.encode(), payload.encode(), hashlib.sha256).hexdigest()


def create_session_token(user: PortalUser) -> str:
    body = json.dumps(
        {**asdict(user), "exp": int(time.time()) + 8 * 3600},
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return f"{body}.{_sign(body)}"


def parse_session_token(token: str | None) -> PortalUser | None:
    if not token or "." not in token:
        return None
    body, sig = token.rsplit(".", 1)
    if not hmac.compare_digest(_sign(body), sig):
        return None
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return None
    if int(data.get("exp", 0)) < int(time.time()):
        return None
    return PortalUser(
        username=data["username"],
        display_name=data["display_name"],
        role=data["role"],
        email=data["email"],
        auth_source=data.get("auth_source", "local"),
    )


def authenticate(username: str, password: str, prefer_ldap: bool = False) -> PortalUser:
    user = username.strip().lower()
    demo = DEMO_USERS.get(user)
    if not demo or not hmac.compare_digest(demo["password"], password):
        raise HTTPException(status_code=401, detail="Usuário ou senha inválidos")

    ldap_on = settings.ldap_enabled or bool(ldap_config().get("ldap", {}).get("enabled"))
    source = "ldap" if (prefer_ldap or ldap_on) else "local"
    return PortalUser(
        username=user,
        display_name=demo["display_name"],
        role=demo["role"],
        email=demo["email"],
        auth_source=source,
    )


def current_user(request: Request) -> PortalUser:
    user = parse_session_token(request.cookies.get("segportal_session"))
    if not user:
        raise HTTPException(status_code=401, detail="Não autenticado")
    return user


def set_session_cookie(response: Response, user: PortalUser) -> None:
    response.set_cookie(
        key="segportal_session",
        value=create_session_token(user),
        httponly=True,
        samesite="lax",
        max_age=8 * 3600,
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie("segportal_session", path="/")

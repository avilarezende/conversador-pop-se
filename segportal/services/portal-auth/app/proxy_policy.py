"""Política de proxy do navegador embutido (gerenciável pelo admin)."""

from __future__ import annotations

import json
import threading
import time
import uuid
from datetime import datetime
from typing import Any
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

from fastapi import HTTPException

from .auth import PortalUser
from .computers import require_admin
from .config import settings

_LOCK = threading.Lock()

DEFAULT_POLICY: dict[str, Any] = {
    "version": 1,
    "mode": "allowlist",
    "default_action": "deny",
    "exception_mode": "per_user",
    "admin_bypass": True,
    "allowed_domains": [
        ".aqne.jus.br",
        ".jus.br",
        ".gov.br",
        ".pje.jus.br",
        ".cnj.jus.br",
        "example.com",
        "www.example.com",
        "www.bcb.gov.br",
    ],
    "allowed_url_prefixes": [
        "https://www.bcb.gov.br/",
        "https://example.com/",
    ],
    "blocked_domains": [
        "malicious.example",
        "phishing.example",
    ],
    "blocked_url_prefixes": [],
    "blocked_keywords": ["malware", "torrent"],
    "exceptions": [
        {
            "id": "ex-docs-google",
            "label": "Documentos Google (equipe financeira)",
            "domains": ["docs.google.com", "drive.google.com"],
            "assignees": ["admin", "usuario"],
            "reason": "Planilhas compartilhadas",
            "expires_at": None,
            "enabled": True,
        }
    ],
    "schedules": [
        {
            "id": "sch-business",
            "label": "Horário comercial",
            "enabled": False,
            "days": [1, 2, 3, 4, 5],
            "start": "08:00",
            "end": "19:00",
            "timezone": "America/Sao_Paulo",
            "outside_action": "deny",
        }
    ],
    "updated_at": 0,
    "updated_by": "system",
}

DAY_LABELS = {
    0: "Dom",
    1: "Seg",
    2: "Ter",
    3: "Qua",
    4: "Qui",
    5: "Sex",
    6: "Sáb",
}


def _store_path():
    root = settings.demo_shares_root
    from pathlib import Path

    path = Path(root)
    path.mkdir(parents=True, exist_ok=True)
    return path / "proxy_policy.json"


def _save(policy: dict[str, Any]) -> None:
    _store_path().write_text(json.dumps(policy, ensure_ascii=False, indent=2), encoding="utf-8")


def _load() -> dict[str, Any]:
    path = _store_path()
    if not path.is_file():
        data = json.loads(json.dumps(DEFAULT_POLICY))
        _save(data)
        return data
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("invalid")
        merged = json.loads(json.dumps(DEFAULT_POLICY))
        merged.update(data)
        for key in (
            "allowed_domains",
            "allowed_url_prefixes",
            "blocked_domains",
            "blocked_url_prefixes",
            "blocked_keywords",
            "exceptions",
            "schedules",
        ):
            if key not in data:
                merged[key] = DEFAULT_POLICY[key]
        return merged
    except (json.JSONDecodeError, OSError, ValueError):
        data = json.loads(json.dumps(DEFAULT_POLICY))
        _save(data)
        return data


def _normalize_list(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, str):
        raw = [line.strip() for line in raw.replace(",", "\n").splitlines()]
    out: list[str] = []
    for item in raw:
        value = str(item).strip().lower()
        if value and value not in out:
            out.append(value)
    return out


def _normalize_domain(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("http://") or value.startswith("https://"):
        value = urlparse(value).netloc or value
    value = value.split("/")[0].split(":")[0]
    return value


def _host_matches(host: str, pattern: str) -> bool:
    host = host.lower().rstrip(".")
    pattern = _normalize_domain(pattern)
    if not pattern:
        return False
    if pattern.startswith("."):
        suffix = pattern[1:]
        return host == suffix or host.endswith("." + suffix)
    return host == pattern or host.endswith("." + pattern)


def _url_matches_prefix(url: str, prefix: str) -> bool:
    return url.lower().startswith(prefix.strip().lower())


def get_policy(user: PortalUser | None = None, *, public: bool = False) -> dict[str, Any]:
    with _LOCK:
        policy = _load()
    if public:
        return {
            "mode": policy.get("mode"),
            "default_action": policy.get("default_action"),
            "exception_mode": policy.get("exception_mode"),
            "admin_bypass": bool(policy.get("admin_bypass")),
            "allowed_domains": list(policy.get("allowed_domains") or []),
            "blocked_domains": list(policy.get("blocked_domains") or []),
            "schedules": [
                {
                    "id": s.get("id"),
                    "label": s.get("label"),
                    "enabled": bool(s.get("enabled", True)),
                    "days": list(s.get("days") or []),
                    "start": s.get("start"),
                    "end": s.get("end"),
                    "timezone": s.get("timezone") or "America/Sao_Paulo",
                    "outside_action": s.get("outside_action") or "deny",
                }
                for s in (policy.get("schedules") or [])
            ],
        }
    if user is not None:
        require_admin(user)
    return policy


def update_policy(user: PortalUser, body: dict[str, Any]) -> dict[str, Any]:
    require_admin(user)
    mode = str(body.get("mode") or "allowlist").strip().lower()
    if mode not in {"allowlist", "blocklist", "allow_all"}:
        raise HTTPException(status_code=400, detail="Modo inválido (allowlist|blocklist|allow_all)")
    exception_mode = str(body.get("exception_mode") or "per_user").strip().lower()
    if exception_mode not in {"disabled", "per_user", "open"}:
        raise HTTPException(status_code=400, detail="Modo de exceções inválido")
    default_action = str(body.get("default_action") or "deny").strip().lower()
    if default_action not in {"deny", "allow"}:
        raise HTTPException(status_code=400, detail="Ação padrão inválida")

    exceptions_in = body.get("exceptions")
    if exceptions_in is None:
        exceptions_in = []
    if not isinstance(exceptions_in, list):
        raise HTTPException(status_code=400, detail="exceptions deve ser uma lista")
    exceptions: list[dict[str, Any]] = []
    for item in exceptions_in:
        if not isinstance(item, dict):
            continue
        domains = [_normalize_domain(d) for d in _normalize_list(item.get("domains"))]
        assignees = _normalize_list(item.get("assignees"))
        if not domains:
            continue
        exceptions.append(
            {
                "id": str(item.get("id") or f"ex-{uuid.uuid4().hex[:8]}"),
                "label": str(item.get("label") or "").strip() or "Exceção",
                "domains": domains,
                "assignees": assignees,
                "reason": str(item.get("reason") or "").strip(),
                "expires_at": item.get("expires_at"),
                "enabled": bool(item.get("enabled", True)),
            }
        )

    schedules_in = body.get("schedules")
    if schedules_in is None:
        schedules_in = []
    if not isinstance(schedules_in, list):
        raise HTTPException(status_code=400, detail="schedules deve ser uma lista")
    schedules: list[dict[str, Any]] = []
    for item in schedules_in:
        if not isinstance(item, dict):
            continue
        days_raw = item.get("days") or []
        days = sorted({int(d) for d in days_raw if str(d).isdigit() or isinstance(d, int)})
        days = [d for d in days if 0 <= d <= 6]
        start = str(item.get("start") or "00:00").strip()
        end = str(item.get("end") or "23:59").strip()
        if not _valid_hhmm(start) or not _valid_hhmm(end):
            raise HTTPException(status_code=400, detail="Horário inválido (use HH:MM)")
        outside = str(item.get("outside_action") or "deny").strip().lower()
        if outside not in {"deny", "allow"}:
            raise HTTPException(status_code=400, detail="outside_action inválido")
        tz = str(item.get("timezone") or "America/Sao_Paulo").strip() or "America/Sao_Paulo"
        try:
            ZoneInfo(tz)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Timezone inválido: {tz}") from exc
        schedules.append(
            {
                "id": str(item.get("id") or f"sch-{uuid.uuid4().hex[:8]}"),
                "label": str(item.get("label") or "").strip() or "Janela",
                "enabled": bool(item.get("enabled", True)),
                "days": days or [1, 2, 3, 4, 5],
                "start": start,
                "end": end,
                "timezone": tz,
                "outside_action": outside,
            }
        )

    policy = {
        "version": 1,
        "mode": mode,
        "default_action": default_action,
        "exception_mode": exception_mode,
        "admin_bypass": bool(body.get("admin_bypass", True)),
        "allowed_domains": [_normalize_domain(d) for d in _normalize_list(body.get("allowed_domains"))],
        "allowed_url_prefixes": _normalize_list(body.get("allowed_url_prefixes")),
        "blocked_domains": [_normalize_domain(d) for d in _normalize_list(body.get("blocked_domains"))],
        "blocked_url_prefixes": _normalize_list(body.get("blocked_url_prefixes")),
        "blocked_keywords": _normalize_list(body.get("blocked_keywords")),
        "exceptions": exceptions,
        "schedules": schedules,
        "updated_at": int(time.time()),
        "updated_by": user.username,
    }
    with _LOCK:
        _save(policy)
    return policy


def _valid_hhmm(value: str) -> bool:
    try:
        hour, minute = value.split(":")
        h, m = int(hour), int(minute)
        return 0 <= h <= 23 and 0 <= m <= 59
    except Exception:
        return False


def _parse_hhmm(value: str) -> tuple[int, int]:
    hour, minute = value.split(":")
    return int(hour), int(minute)


def _within_schedule(schedule: dict[str, Any], now: datetime | None = None) -> bool:
    tz_name = schedule.get("timezone") or "America/Sao_Paulo"
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = ZoneInfo("America/Sao_Paulo")
    current = now.astimezone(tz) if now else datetime.now(tz)
    days = schedule.get("days") or []
    # days: 0=Domingo .. 6=Sábado; Python weekday: Monday=0 .. Sunday=6
    our_day = (current.weekday() + 1) % 7
    if days and our_day not in days:
        return False
    start_h, start_m = _parse_hhmm(schedule.get("start") or "00:00")
    end_h, end_m = _parse_hhmm(schedule.get("end") or "23:59")
    minutes = current.hour * 60 + current.minute
    start = start_h * 60 + start_m
    end = end_h * 60 + end_m
    if start <= end:
        return start <= minutes <= end
    return minutes >= start or minutes <= end


def _exception_allows(policy: dict[str, Any], host: str, user: PortalUser) -> bool:
    mode = policy.get("exception_mode") or "per_user"
    if mode == "disabled":
        return False
    username = user.username.lower()
    now_ts = int(time.time())
    for item in policy.get("exceptions") or []:
        if not item.get("enabled", True):
            continue
        expires = item.get("expires_at")
        if expires not in (None, ""):
            try:
                if int(expires) < now_ts:
                    continue
            except (TypeError, ValueError):
                pass
        domains = item.get("domains") or []
        if not any(_host_matches(host, d) for d in domains):
            continue
        if mode == "open":
            return True
        assignees = [a.lower() for a in (item.get("assignees") or [])]
        if "*" in assignees or username in assignees:
            return True
    return False


def evaluate_url(url: str, user: PortalUser, *, now: datetime | None = None) -> dict[str, Any]:
    """Avalia se a URL pode ser navegada. Retorna {allowed, reason, matched}."""
    with _LOCK:
        policy = _load()
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    full = url.lower()

    if policy.get("admin_bypass") and user.role == "admin":
        return {"allowed": True, "reason": "Admin com bypass de proxy", "matched": "admin_bypass"}

    # Bloqueios explícitos (sempre, salvo bypass admin acima)
    for pattern in policy.get("blocked_domains") or []:
        if _host_matches(host, pattern):
            return {"allowed": False, "reason": f"Domínio filtrado: {pattern}", "matched": "blocked_domain"}
    for prefix in policy.get("blocked_url_prefixes") or []:
        if _url_matches_prefix(full, prefix):
            return {"allowed": False, "reason": f"URL filtrada: {prefix}", "matched": "blocked_prefix"}
    for keyword in policy.get("blocked_keywords") or []:
        if keyword and keyword in full:
            return {"allowed": False, "reason": f"Palavra filtrada: {keyword}", "matched": "blocked_keyword"}

    # Horários
    for schedule in policy.get("schedules") or []:
        if not schedule.get("enabled", True):
            continue
        if _within_schedule(schedule, now=now):
            continue
        outside = schedule.get("outside_action") or "deny"
        if outside == "deny":
            label = schedule.get("label") or schedule.get("id") or "janela"
            return {
                "allowed": False,
                "reason": f"Fora do horário permitido ({label})",
                "matched": "schedule",
            }

    # Exceções
    if _exception_allows(policy, host, user):
        return {"allowed": True, "reason": "Exceção de proxy", "matched": "exception"}

    mode = policy.get("mode") or "allowlist"
    if mode == "allow_all":
        return {"allowed": True, "reason": "Modo allow_all", "matched": "mode"}

    allowed_domain = any(_host_matches(host, p) for p in (policy.get("allowed_domains") or []))
    allowed_prefix = any(_url_matches_prefix(full, p) for p in (policy.get("allowed_url_prefixes") or []))
    in_allow = allowed_domain or allowed_prefix

    if mode == "allowlist":
        if in_allow:
            return {"allowed": True, "reason": "Permitido na allowlist", "matched": "allowlist"}
        return {
            "allowed": False,
            "reason": "Domínio não está na lista de URLs permitidas",
            "matched": "default",
        }

    # blocklist: permite tudo que não foi bloqueado acima
    if mode == "blocklist":
        return {"allowed": True, "reason": "Não está na lista de filtrados", "matched": "blocklist"}

    default = policy.get("default_action") or "deny"
    return {
        "allowed": default == "allow",
        "reason": f"Ação padrão: {default}",
        "matched": "default",
    }


def assert_url_allowed(url: str, user: PortalUser) -> None:
    result = evaluate_url(url, user)
    if not result["allowed"]:
        raise HTTPException(status_code=403, detail=result["reason"])

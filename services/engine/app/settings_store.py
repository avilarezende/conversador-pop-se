"""Armazenamento persistente de configurações editáveis pela administração.

Guarda, em um arquivo JSON, o provedor de IA ativo, credenciais/modelos por
provedor e a lista de guardrails. É lido pelo pipeline de conversa e escrito
pela API de administração.
"""

from __future__ import annotations

import json
import threading
import uuid
from typing import Any

from app.config import settings

# Atributos de credencial válidos por provedor (nomes iguais aos de Settings).
_CREDENTIAL_FIELDS = {
    "ollama_host",
    "gemini_api_key",
    "openai_api_key",
    "openai_base_url",
    "azure_openai_api_key",
    "azure_openai_endpoint",
    "azure_openai_deployment",
    "grok_api_key",
    "grok_base_url",
}

_MODEL_ATTR = {
    "ollama": "ollama_model",
    "gemini": "gemini_model",
    "openai": "openai_model",
    "grok": "grok_model",
}

_lock = threading.Lock()


def _default_data() -> dict[str, Any]:
    from app.guardrails import DEFAULT_GUARDRAILS

    return {
        "llm": {"provider": None, "models": {}, "credentials": {}},
        "guardrails": [dict(g) for g in DEFAULT_GUARDRAILS],
    }


def load() -> dict[str, Any]:
    """Carrega o arquivo (criando os defaults na primeira execução)."""
    path = settings.store_path
    with _lock:
        if not path.exists():
            data = _default_data()
            _write_unlocked(data)
            return data
        try:
            with path.open(encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            data = _default_data()
        # Garante chaves esperadas
        data.setdefault("llm", {"provider": None, "models": {}, "credentials": {}})
        data["llm"].setdefault("models", {})
        data["llm"].setdefault("credentials", {})
        data.setdefault("guardrails", [])
        return data


def _write_unlocked(data: dict[str, Any]) -> None:
    path = settings.store_path
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp.replace(path)


def save(data: dict[str, Any]) -> None:
    with _lock:
        _write_unlocked(data)


# --- Guardrails ----------------------------------------------------------------


def list_guardrails() -> list[dict]:
    return load().get("guardrails", [])


def add_guardrail(payload: dict) -> dict:
    data = load()
    guardrail = {
        "id": uuid.uuid4().hex[:12],
        "name": str(payload.get("name", "")).strip() or "Nova regra",
        "type": payload.get("type", "blocked_keywords"),
        "enabled": bool(payload.get("enabled", True)),
        "keywords": [k.strip().lower() for k in payload.get("keywords", []) if k.strip()],
        "message": str(payload.get("message", "")).strip()
        or "Desculpe, só posso ajudar com assuntos do PoP-SE/RNP.",
    }
    data.setdefault("guardrails", []).append(guardrail)
    save(data)
    return guardrail


def update_guardrail(guardrail_id: str, patch: dict) -> dict | None:
    data = load()
    for g in data.get("guardrails", []):
        if g.get("id") == guardrail_id:
            if "enabled" in patch:
                g["enabled"] = bool(patch["enabled"])
            if "name" in patch:
                g["name"] = str(patch["name"]).strip() or g["name"]
            if "message" in patch:
                g["message"] = str(patch["message"]).strip() or g["message"]
            if "keywords" in patch:
                g["keywords"] = [k.strip().lower() for k in patch["keywords"] if k.strip()]
            save(data)
            return g
    return None


def delete_guardrail(guardrail_id: str) -> bool:
    data = load()
    before = len(data.get("guardrails", []))
    data["guardrails"] = [g for g in data.get("guardrails", []) if g.get("id") != guardrail_id]
    if len(data["guardrails"]) != before:
        save(data)
        return True
    return False


# --- Configuração de IA --------------------------------------------------------


def get_llm_config() -> dict:
    return load().get("llm", {"provider": None, "models": {}, "credentials": {}})


def update_llm_config(provider: str | None, model: str | None, credentials: dict) -> dict:
    data = load()
    llm = data.setdefault("llm", {"provider": None, "models": {}, "credentials": {}})
    if provider:
        llm["provider"] = provider
        if model:
            llm.setdefault("models", {})[provider] = model
    # Guarda apenas credenciais válidas e não vazias (não apaga as existentes).
    for field, value in (credentials or {}).items():
        if field in _CREDENTIAL_FIELDS and value:
            llm.setdefault("credentials", {})[field] = value
    save(data)
    return llm


def apply_overrides(target_settings) -> None:
    """Aplica provedor/modelo/credenciais salvos sobre o objeto Settings.

    Só sobrescreve quando há valores salvos; caso contrário mantém o ambiente.
    """
    llm = get_llm_config()
    provider = llm.get("provider")
    credentials = llm.get("credentials", {})
    models = llm.get("models", {})

    for field, value in credentials.items():
        if field in _CREDENTIAL_FIELDS and value:
            setattr(target_settings, field, value)

    if provider:
        target_settings.llm_provider = provider
        model = models.get(provider)
        attr = _MODEL_ATTR.get(provider)
        if model and attr:
            setattr(target_settings, attr, model)

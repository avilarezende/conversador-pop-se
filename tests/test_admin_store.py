"""Testes do armazenamento de configurações de administração."""

from types import SimpleNamespace

import pytest
from app import settings_store
from app.config import settings


@pytest.fixture(autouse=True)
def temp_store(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "admin_store_path", str(tmp_path / "admin.json"))


def test_defaults_created_on_first_load():
    data = settings_store.load()
    assert "guardrails" in data
    assert any(g["type"] == "scope" for g in data["guardrails"])


def test_add_and_delete_guardrail():
    created = settings_store.add_guardrail(
        {"name": "Bloqueio financeiro", "type": "blocked_keywords", "keywords": ["Bitcoin"]}
    )
    assert created["id"]
    assert created["keywords"] == ["bitcoin"]  # normalizado para minúsculas

    ids = [g["id"] for g in settings_store.list_guardrails()]
    assert created["id"] in ids

    assert settings_store.delete_guardrail(created["id"]) is True
    assert settings_store.delete_guardrail(created["id"]) is False


def test_toggle_guardrail():
    updated = settings_store.update_guardrail("scope-popse", {"enabled": False})
    assert updated is not None
    assert updated["enabled"] is False


def test_llm_config_and_overrides():
    settings_store.update_llm_config(
        "gemini", "gemini-flash-latest", {"gemini_api_key": "secret-123"}
    )
    target = SimpleNamespace(
        llm_provider="ollama", gemini_model="old", gemini_api_key=None
    )
    settings_store.apply_overrides(target)
    assert target.llm_provider == "gemini"
    assert target.gemini_model == "gemini-flash-latest"
    assert target.gemini_api_key == "secret-123"

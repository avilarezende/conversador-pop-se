from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def project_config_path(monkeypatch):
    root = Path(__file__).resolve().parents[1]
    monkeypatch.setenv("CONFIG_PATH", str(root / "config"))
    monkeypatch.setenv("ENGINE_API_TOKEN", "test-engine-token")
    monkeypatch.setenv("ENGINE_RATE_LIMIT_ENABLED", "0")
    # Recarrega settings após alterar env
    from app.config import settings

    monkeypatch.setattr(settings, "config_path", str(root / "config"))
    monkeypatch.setattr(settings, "engine_api_token", "test-engine-token")

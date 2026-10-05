"""Production must reject development settings without exposing credentials."""

import hashlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BASE_ENV = {
    "ENGINE_ENV": "production",
    "ENGINE_API_TOKEN": "fixture-token",
    "DATABASE_URL": "postgresql+asyncpg://app:fixture-password@db:5432/app",
}


def load_config(overrides):
    env = os.environ.copy()
    env.update(BASE_ENV)
    credential = hashlib.sha256(b"production-config-fixture").hexdigest()
    for name in ("ENGINE_API_TOKEN", "CIEM_SECRET_KEY", "PORTAL_SESSION_SECRET"):
        if name in BASE_ENV:
            env[name] = credential
    if "DATABASE_URL" in BASE_ENV:
        env["DATABASE_URL"] = "postgresql+asyncpg://app:" + credential + "@db:5432/app"
    env.update(overrides)
    env["PYTHONPATH"] = str(ROOT / "services/engine")
    result = subprocess.run(
        [sys.executable, "-c", "import app.config"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    assert credential not in result.stderr
    return result


def test_production_accepts_explicit_secure_configuration():
    result = load_config({})
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    "overrides",
    [
        {"ENGINE_API_TOKEN": "change-me-engine-token"},
        {"DATABASE_URL": "postgresql+asyncpg://app:devpassword@db:5432/app"},
        {"DATABASE_URL": "postgresql+asyncpg://app:%61ltere_em_producao@db:5432/app"},
        {"CORS_ORIGINS": "*"},
    ],
)
def test_production_rejects_development_configuration(overrides):
    assert load_config(overrides).returncode != 0

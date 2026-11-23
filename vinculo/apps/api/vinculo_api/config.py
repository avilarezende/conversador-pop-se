from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    modules_config_path: str = str(
        Path(__file__).resolve().parents[3] / "config" / "modules.yaml"
    )
    app_name: str = "Vínculo API"


def load_modules_config(path: str | None = None) -> dict[str, Any]:
    cfg_path = Path(path or Settings().modules_config_path)
    with cfg_path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return data.get("modules", {})

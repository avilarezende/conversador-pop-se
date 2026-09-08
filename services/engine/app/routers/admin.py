"""API de administração: configuração de IA/API keys e guardrails.

Protegida por um token simples no header ``X-Admin-Token`` (env ``ADMIN_TOKEN``).
As credenciais são somente-escrita: nas leituras retornam mascaradas.
"""

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field

from app import settings_store
from app.config import settings
from app.llm.catalog import PROVIDER_CATALOG, PROVIDER_IDS

router = APIRouter()


def require_admin(x_admin_token: str | None = Header(default=None)) -> None:
    if x_admin_token != settings.admin_token:
        raise HTTPException(status_code=401, detail="Token de administração inválido.")


def _mask(value: str | None) -> str:
    if not value:
        return ""
    return "••••" + value[-4:] if len(value) > 4 else "••••"


class LlmUpdate(BaseModel):
    provider: str
    model: str | None = None
    credentials: dict[str, str] = Field(default_factory=dict)


class GuardrailCreate(BaseModel):
    name: str
    type: str = "blocked_keywords"
    keywords: list[str] = Field(default_factory=list)
    message: str = ""
    enabled: bool = True


class GuardrailPatch(BaseModel):
    enabled: bool | None = None
    name: str | None = None
    message: str | None = None
    keywords: list[str] | None = None


@router.get("/config")
def get_config(_: None = Depends(require_admin)) -> dict:
    llm = settings_store.get_llm_config()
    creds = llm.get("credentials", {})
    return {
        "providers": PROVIDER_CATALOG,
        "active": {"provider": llm.get("provider"), "models": llm.get("models", {})},
        "credentials_set": {k: bool(v) for k, v in creds.items()},
        "credentials_masked": {k: _mask(v) for k, v in creds.items()},
        "guardrails": settings_store.list_guardrails(),
    }


@router.put("/llm")
def set_llm(body: LlmUpdate, _: None = Depends(require_admin)) -> dict:
    if body.provider not in PROVIDER_IDS:
        raise HTTPException(status_code=400, detail="Provedor desconhecido.")
    llm = settings_store.update_llm_config(body.provider, body.model, body.credentials)
    return {"ok": True, "provider": llm.get("provider"), "models": llm.get("models", {})}


@router.get("/guardrails")
def list_guardrails(_: None = Depends(require_admin)) -> list[dict]:
    return settings_store.list_guardrails()


@router.post("/guardrails")
def create_guardrail(body: GuardrailCreate, _: None = Depends(require_admin)) -> dict:
    if body.type not in ("blocked_keywords", "scope"):
        raise HTTPException(status_code=400, detail="Tipo de guardrail inválido.")
    return settings_store.add_guardrail(body.model_dump())


@router.patch("/guardrails/{guardrail_id}")
def patch_guardrail(
    guardrail_id: str, body: GuardrailPatch, _: None = Depends(require_admin)
) -> dict:
    patch = {k: v for k, v in body.model_dump().items() if v is not None}
    updated = settings_store.update_guardrail(guardrail_id, patch)
    if not updated:
        raise HTTPException(status_code=404, detail="Guardrail não encontrado.")
    return updated


@router.delete("/guardrails/{guardrail_id}")
def delete_guardrail(guardrail_id: str, _: None = Depends(require_admin)) -> dict:
    if not settings_store.delete_guardrail(guardrail_id):
        raise HTTPException(status_code=404, detail="Guardrail não encontrado.")
    return {"ok": True}

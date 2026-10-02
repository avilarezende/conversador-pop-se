"""Segurança da API do engine (autenticação por token entre serviços)."""

from fastapi import Header, HTTPException, status

from app.config import settings

_WEAK_TOKENS = {"", "change-me-engine-token", "change-me", "changeme", "secret"}


def require_api_token(x_api_token: str = Header(default="")) -> None:
    """Exige o token interno (X-API-Token) nos endpoints do engine.

    A falha é fail-closed: sem token válido, a requisição é recusada.
    Se ENGINE_API_TOKEN estiver com valor fraco/padrão em produção, recusa
    também (a menos que ENGINE_ALLOW_WEAK_TOKEN=1 esteja explicitamente
    definido para desenvolvimento local).
    """
    configured = settings.engine_api_token
    if configured in _WEAK_TOKENS:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ENGINE_API_TOKEN não configurado (use um token forte em produção)",
        )

    if not x_api_token or x_api_token != configured:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de API inválido",
        )
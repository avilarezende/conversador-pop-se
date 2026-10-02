"""Cliente HTTP para o engine de conversação (autenticado por token)."""

import os

import httpx

ENGINE_URL = os.getenv("ENGINE_URL", "http://engine:8000")
ENGINE_API_TOKEN = os.getenv("ENGINE_API_TOKEN", "")


def _headers() -> dict[str, str]:
    # O token é compartilhado com o ENGINE_API_TOKEN do engine; sem ele,
    # os módulos não conseguem chamar a API (fail-closed do lado do engine).
    if not ENGINE_API_TOKEN:
        raise ValueError("ENGINE_API_TOKEN não configurado nos módulos")
    return {"X-API-Token": ENGINE_API_TOKEN}


async def send_chat(message: str, user_id: str, channel: str) -> str:
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            f"{ENGINE_URL}/api/v1/chat",
            headers=_headers(),
            json={"message": message, "user_id": user_id, "channel": channel},
        )
        resp.raise_for_status()
        return resp.json()["reply"]


async def ingest_rag(collection: str, documents: list[dict]) -> int:
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{ENGINE_URL}/api/v1/rag/ingest",
            headers=_headers(),
            json={"collection": collection, "documents": documents},
        )
        resp.raise_for_status()
        return resp.json()["ingested"]
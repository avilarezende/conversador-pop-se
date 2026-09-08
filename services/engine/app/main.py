"""Aplicação FastAPI principal."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import admin, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Conversador PoP-SE — Engine (Calisto)",
    description=(
        "Motor de conversação do assistente Calisto: RAG, memória persistente, "
        "guardrails de escopo PoP-SE/RNP e administração de IA/guardrails/RAG."
    ),
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1/admin")


@app.get("/health")
async def health() -> dict:
    from app.config import settings

    return {
        "status": "ok",
        "service": "conversador-engine",
        "llm_provider": settings.llm_provider,
    }

"""Armazenamento vetorial simples para RAG."""

from __future__ import annotations

from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings

# Coleções usadas pelo pipeline de conversa (ver chat_service).
KNOWN_COLLECTIONS = ["operacional", "institucional", "manutencoes"]

_client: chromadb.PersistentClient | None = None


def get_chroma() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        Path(settings.chroma_path).mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(
            path=settings.chroma_path,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
    return _client


def get_collection(name: str = "operacional"):
    return get_chroma().get_or_create_collection(name=name, metadata={"hnsw:space": "cosine"})


def ingest_documents(collection: str, docs: list[dict]) -> int:
    """docs: [{id, text, metadata}]"""
    if not docs:
        return 0
    col = get_collection(collection)
    col.upsert(
        ids=[d["id"] for d in docs],
        documents=[d["text"] for d in docs],
        metadatas=[d.get("metadata", {}) for d in docs],
    )
    return len(docs)


def list_documents(collection: str) -> list[dict]:
    """Retorna os documentos de uma coleção: [{id, text, metadata}]."""
    col = get_collection(collection)
    data = col.get(include=["documents", "metadatas"])
    ids = data.get("ids", []) or []
    docs = data.get("documents", []) or []
    metas = data.get("metadatas", []) or []
    out = []
    for i, doc_id in enumerate(ids):
        out.append(
            {
                "id": doc_id,
                "text": docs[i] if i < len(docs) else "",
                "metadata": metas[i] if i < len(metas) else {},
            }
        )
    return out


def delete_document(collection: str, doc_id: str) -> bool:
    """Remove um documento pelo id. Retorna False se não existir."""
    col = get_collection(collection)
    existing = col.get(ids=[doc_id])
    if not existing.get("ids"):
        return False
    col.delete(ids=[doc_id])
    return True


def collection_counts() -> list[dict]:
    """Coleções conhecidas com a contagem de documentos."""
    counts = []
    for name in KNOWN_COLLECTIONS:
        try:
            counts.append({"name": name, "count": get_collection(name).count()})
        except Exception:
            counts.append({"name": name, "count": 0})
    return counts


def query_context(collection: str, question: str, top_k: int = 6) -> str:
    col = get_collection(collection)
    if col.count() == 0:
        return ""
    result = col.query(query_texts=[question], n_results=min(top_k, col.count()))
    docs = result.get("documents", [[]])[0]
    metas = result.get("metadatas", [[]])[0]
    chunks = []
    for doc, meta in zip(docs, metas):
        source = meta.get("source", "desconhecida") if meta else "desconhecida"
        chunks.append(f"[{source}]\n{doc}")
    return "\n\n---\n\n".join(chunks)

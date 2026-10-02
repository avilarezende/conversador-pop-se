"""Armazenamento vetorial simples para RAG."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings
from app.config_loader import get_clients

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


def _institution_hosts(sigla: str) -> tuple[list[str], dict[str, Any]]:
    """Retorna hosts monitorados (zabbix/cacti) e o filtro de metadados da instituição.

    O filtro usa a sigla da instituição (`instituicao`) como marcador principal;
    se os dados de origem forem marcados por host (coleta futura), `hosts` permite
    uma consulta mais estrita.
    """
    hosts: list[str] = []
    for inst in get_clients():
        if inst.get("sigla", "").lower() != sigla.lower():
            continue
        for link in inst.get("links_monitorados", []):
            if link.get("zabbix_host"):
                hosts.append(link["zabbix_host"])
    return hosts, {"instituicao": sigla.upper()}


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


def query_context(
    collection: str,
    question: str,
    top_k: int = 6,
    instituicao: str | None = None,
) -> str:
    col = get_collection(collection)
    if col.count() == 0:
        return ""

    where: dict[str, Any] | None = None
    if instituicao:
        hosts, where = _institution_hosts(instituicao)
        if hosts:
            # Se houver hosts da instituição, filtra por eles; senão pela sigla.
            if len(hosts) > 1:
                where = {"$or": [{"zabbix_host": h} for h in hosts]}
            else:
                where = {"zabbix_host": hosts[0]}

    if where:
        try:
            result = col.query(
                query_texts=[question],
                n_results=min(top_k, col.count()),
                where=where,
            )
        except Exception:
            # Filtro de metadados pode não existir ainda nas coleções antigas;
            # cai para consulta sem filtro em vez de quebrar a resposta.
            result = col.query(query_texts=[question], n_results=min(top_k, col.count()))
    else:
        result = col.query(query_texts=[question], n_results=min(top_k, col.count()))

    docs = result.get("documents", [[]])[0]
    metas = result.get("metadatas", [[]])[0]
    chunks = []
    for doc, meta in zip(docs, metas):
        source = meta.get("source", "desconhecida") if meta else "desconhecida"
        chunks.append(f"[{source}]\n{doc}")
    return "\n\n---\n\n".join(chunks)

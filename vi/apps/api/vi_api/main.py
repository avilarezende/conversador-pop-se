from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request

from vi_api.config import Settings, load_modules_config
from vi_api.container import AppContainer, build_container
from vi_api.schemas import (
    AddEdgeRequest,
    AppendMessageRequest,
    AppendMessageResponse,
    CanOpenRequest,
    CanOpenResponse,
    ExportMediaRequest,
    ExportMediaResponse,
    HealthResponse,
    ImportMediaRequest,
    RegisterIdentityRequest,
    RegisterIdentityResponse,
)
from vi_core.errors import DomainError, PolicyDenied
from vi_core.types import ConversationId, NodeId, NodeKind
from vi_identity.models import IdentityRecord
from vi_ledger.models import EntryType
from vi_media.models import MediaBlob
from vi_trust_graph.models import Edge, EdgeType

settings = Settings()
modules = load_modules_config(settings.modules_config_path)
container: AppContainer = build_container(modules)

app = FastAPI(title=settings.app_name, version="0.1.0")
app.state.container = container


def _ctr(request: Request) -> AppContainer:
    return request.app.state.container


@app.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    mods = _ctr(request).modules
    return HealthResponse(
        status="ok",
        service="vi-api",
        modules={name: bool(cfg.get("enabled", False)) for name, cfg in mods.items()},
    )


@app.post("/api/v1/identity/register", response_model=RegisterIdentityResponse)
def register_identity(
    body: RegisterIdentityRequest, request: Request
) -> RegisterIdentityResponse:
    c = _ctr(request)
    kem_pk, _kem_sk = c.crypto.generate_kem_keypair()
    sig_pk, _sig_sk = c.crypto.generate_sign_keypair()
    kind = NodeKind(body.kind)
    record = IdentityRecord(
        node_id=NodeId(body.node_id),
        kind=kind,
        display_name=body.display_name,
        pqc_sign_public_key=sig_pk,
        pqc_kem_public_key=kem_pk,
    )
    try:
        c.identity.register(record)
    except DomainError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    c.trust_graph.register_node(record.node_id, kind)
    return RegisterIdentityResponse(
        node_id=record.node_id,
        kind=record.kind.value,
        display_name=record.display_name,
        kem_public_key_hex=kem_pk.hex(),
        sign_public_key_hex=sig_pk.hex(),
    )


@app.post("/api/v1/graph/edges")
def add_edge(body: AddEdgeRequest, request: Request) -> dict[str, str]:
    c = _ctr(request)
    try:
        edge_type = EdgeType(body.edge_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid edge_type") from exc
    c.trust_graph.add_edge(
        Edge(
            src=NodeId(body.src),
            dst=NodeId(body.dst),
            edge_type=edge_type,
            pair_with=NodeId(body.pair_with) if body.pair_with else None,
            anchor_id=body.anchor_id,  # type: ignore[arg-type]
        )
    )
    return {"status": "ok"}


@app.post("/api/v1/channels/can-open", response_model=CanOpenResponse)
def can_open(body: CanOpenRequest, request: Request) -> CanOpenResponse:
    decision = _ctr(request).trust_graph.can_open_channel(
        NodeId(body.a), NodeId(body.b)
    )
    return CanOpenResponse(
        allowed=decision.allowed,
        reason=decision.reason,
        entity=decision.entity,
        path=list(decision.path),
    )


@app.post("/api/v1/ledger/messages", response_model=AppendMessageResponse)
def append_message(
    body: AppendMessageRequest, request: Request
) -> AppendMessageResponse:
    c = _ctr(request)
    conv = ConversationId(body.conversation_id)
    # Esqueleto: chave de época fixa derivada do conversation_id
    epoch_key = hashlib.sha256(f"epoch|{conv}".encode()).digest()
    ciphertext = c.crypto.aead_encrypt(epoch_key, body.plaintext.encode())
    content_hash = hashlib.sha256(body.plaintext.encode()).hexdigest()
    _, sig_sk = c.crypto.generate_sign_keypair()  # demo: assinatura efêmera
    signature = c.crypto.sign(sig_sk, content_hash.encode())
    c.ledger.ensure_conversation(conv)
    entry = c.ledger.append(
        conv,
        entry_type=EntryType.MESSAGE,
        payload_ciphertext=ciphertext,
        content_hash=content_hash,
        sender_id=NodeId(body.sender_id),
        sender_sig_pqc=signature,
    )
    return AppendMessageResponse(
        seq=entry.seq,
        entry_hash=entry.entry_hash,
        chain_valid=c.ledger.verify_chain(conv),
    )


@app.post("/api/v1/media/import")
def import_media(body: ImportMediaRequest, request: Request) -> dict[str, str]:
    c = _ctr(request)
    conv = ConversationId(body.conversation_id)
    epoch_key = hashlib.sha256(f"epoch|{conv}".encode()).digest()
    raw = body.gallery_payload.encode()
    ciphertext = c.crypto.aead_encrypt(epoch_key, raw)
    content_hash = hashlib.sha256(raw).hexdigest()
    blob = MediaBlob(
        blob_id=body.blob_id,
        conversation_id=conv,
        creator_id=NodeId(body.creator_id),
        content_type=body.content_type,
        ciphertext=ciphertext,
        content_hash=content_hash,
        created_at=datetime.now(timezone.utc),
    )
    c.media.store(blob)
    c.ledger.ensure_conversation(conv)
    c.ledger.append(
        conv,
        entry_type=EntryType.MEDIA_REF,
        payload_ciphertext=ciphertext[:32],
        content_hash=content_hash,
        sender_id=NodeId(body.creator_id),
        sender_sig_pqc=b"\x00" * 32,
    )
    return {"status": "stored", "blob_id": body.blob_id, "content_hash": content_hash}


@app.post("/api/v1/media/export", response_model=ExportMediaResponse)
def export_media(body: ExportMediaRequest, request: Request) -> ExportMediaResponse:
    c = _ctr(request)
    try:
        exported = c.media.export_with_watermark(
            body.blob_id, NodeId(body.exporter_id)
        )
    except PolicyDenied as exc:
        raise HTTPException(status_code=403, detail=exc.reason) from exc

    entry = c.ledger.append(
        exported.conversation_id,
        entry_type=EntryType.EXPORT_EVENT,
        payload_ciphertext=exported.watermark_payload.encode(),
        content_hash=hashlib.sha256(exported.watermark_payload.encode()).hexdigest(),
        sender_id=NodeId(body.exporter_id),
        sender_sig_pqc=b"\x00" * 32,
    )
    return ExportMediaResponse(
        watermark_payload=exported.watermark_payload,
        metadata=exported.metadata,
        export_ledger_seq=entry.seq,
    )

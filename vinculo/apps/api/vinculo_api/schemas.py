from __future__ import annotations

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str
    modules: dict[str, bool]


class RegisterIdentityRequest(BaseModel):
    node_id: str
    kind: str = Field(pattern="^(individual|entity)$")
    display_name: str


class RegisterIdentityResponse(BaseModel):
    node_id: str
    kind: str
    display_name: str
    kem_public_key_hex: str
    sign_public_key_hex: str


class AddEdgeRequest(BaseModel):
    src: str
    dst: str
    edge_type: str
    pair_with: str | None = None
    anchor_id: str | None = None


class CanOpenRequest(BaseModel):
    a: str
    b: str


class CanOpenResponse(BaseModel):
    allowed: bool
    reason: str
    entity: str | None = None
    path: list[str] = []


class AppendMessageRequest(BaseModel):
    conversation_id: str
    sender_id: str
    plaintext: str


class AppendMessageResponse(BaseModel):
    seq: int
    entry_hash: str
    chain_valid: bool


class ImportMediaRequest(BaseModel):
    conversation_id: str
    creator_id: str
    blob_id: str
    content_type: str = "application/octet-stream"
    # Conteúdo da galeria (esqueleto: base64 ou texto); aqui usamos texto simples
    gallery_payload: str


class ExportMediaRequest(BaseModel):
    blob_id: str
    exporter_id: str


class ExportMediaResponse(BaseModel):
    watermark_payload: str
    metadata: dict[str, str]
    export_ledger_seq: int

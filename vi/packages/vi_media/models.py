from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from vi_core.types import ConversationId, NodeId


@dataclass(frozen=True)
class MediaBlob:
    blob_id: str
    conversation_id: ConversationId
    creator_id: NodeId
    content_type: str
    ciphertext: bytes
    content_hash: str
    created_at: datetime


@dataclass(frozen=True)
class ExportedMedia:
    blob_id: str
    exporter_id: NodeId
    creator_id: NodeId
    conversation_id: ConversationId
    watermark_payload: str
    metadata: dict[str, str]
    bytes_out: bytes

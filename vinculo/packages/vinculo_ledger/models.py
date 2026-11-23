from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum

from vinculo_core.types import ConversationId, NodeId


class EntryType(StrEnum):
    MESSAGE = "message"
    MEDIA_REF = "media_ref"
    AV_SESSION = "av_session"
    POLICY = "policy"
    EXPORT_EVENT = "export_event"


@dataclass(frozen=True)
class LedgerEntry:
    conversation_id: ConversationId
    seq: int
    prev_hash: str
    entry_hash: str
    entry_type: EntryType
    payload_ciphertext: bytes
    content_hash: str
    sender_id: NodeId
    sender_sig_pqc: bytes
    created_at: datetime

    @staticmethod
    def genesis_prev_hash() -> str:
        return "0" * 64

from __future__ import annotations

from typing import Protocol

from vinculo_core.types import ConversationId, NodeId
from vinculo_ledger.models import EntryType, LedgerEntry


class ConversationLedgerPort(Protocol):
    def ensure_conversation(self, conversation_id: ConversationId) -> None: ...

    def append(
        self,
        conversation_id: ConversationId,
        *,
        entry_type: EntryType,
        payload_ciphertext: bytes,
        content_hash: str,
        sender_id: NodeId,
        sender_sig_pqc: bytes,
    ) -> LedgerEntry: ...

    def verify_chain(self, conversation_id: ConversationId) -> bool: ...

    def list_entries(self, conversation_id: ConversationId) -> list[LedgerEntry]: ...

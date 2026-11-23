from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from vi_core.errors import DomainError
from vi_core.types import ConversationId, NodeId
from vi_ledger.models import EntryType, LedgerEntry


class InMemoryLedger:
    """Ledger hash-chain in-memory (esqueleto). Payload já chega cifrado."""

    def __init__(self) -> None:
        self._chains: dict[ConversationId, list[LedgerEntry]] = {}

    def ensure_conversation(self, conversation_id: ConversationId) -> None:
        self._chains.setdefault(conversation_id, [])

    def append(
        self,
        conversation_id: ConversationId,
        *,
        entry_type: EntryType,
        payload_ciphertext: bytes,
        content_hash: str,
        sender_id: NodeId,
        sender_sig_pqc: bytes,
    ) -> LedgerEntry:
        chain = self._chains.setdefault(conversation_id, [])
        prev = (
            chain[-1].entry_hash if chain else LedgerEntry.genesis_prev_hash()
        )
        seq = len(chain) + 1
        created_at = datetime.now(timezone.utc)
        material = "|".join(
            [
                conversation_id,
                str(seq),
                prev,
                entry_type.value,
                content_hash,
                sender_id,
                created_at.isoformat(),
                hashlib.sha256(payload_ciphertext).hexdigest(),
            ]
        )
        entry_hash = hashlib.sha256(material.encode()).hexdigest()
        entry = LedgerEntry(
            conversation_id=conversation_id,
            seq=seq,
            prev_hash=prev,
            entry_hash=entry_hash,
            entry_type=entry_type,
            payload_ciphertext=payload_ciphertext,
            content_hash=content_hash,
            sender_id=sender_id,
            sender_sig_pqc=sender_sig_pqc,
            created_at=created_at,
        )
        chain.append(entry)
        return entry

    def verify_chain(self, conversation_id: ConversationId) -> bool:
        chain = self._chains.get(conversation_id)
        if chain is None:
            raise DomainError(f"unknown conversation: {conversation_id}")
        prev = LedgerEntry.genesis_prev_hash()
        for entry in chain:
            if entry.prev_hash != prev:
                return False
            material = "|".join(
                [
                    entry.conversation_id,
                    str(entry.seq),
                    entry.prev_hash,
                    entry.entry_type.value,
                    entry.content_hash,
                    entry.sender_id,
                    entry.created_at.isoformat(),
                    hashlib.sha256(entry.payload_ciphertext).hexdigest(),
                ]
            )
            if hashlib.sha256(material.encode()).hexdigest() != entry.entry_hash:
                return False
            prev = entry.entry_hash
        return True

    def list_entries(self, conversation_id: ConversationId) -> list[LedgerEntry]:
        return list(self._chains.get(conversation_id, []))

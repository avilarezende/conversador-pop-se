from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from vi_core.types import ConversationId, NodeId
from vi_crypto_pqc import MockPqcProvider
from vi_ledger import EntryType, InMemoryLedger
from vi_media import MediaBlob, MediaIntegrityService


def test_ledger_chain_valid_after_appends() -> None:
    ledger = InMemoryLedger()
    conv = ConversationId("c1")
    ledger.ensure_conversation(conv)
    for i in range(3):
        ledger.append(
            conv,
            entry_type=EntryType.MESSAGE,
            payload_ciphertext=f"cipher-{i}".encode(),
            content_hash=hashlib.sha256(f"p-{i}".encode()).hexdigest(),
            sender_id=NodeId("alice"),
            sender_sig_pqc=b"\x01" * 32,
        )
    assert ledger.verify_chain(conv) is True
    assert len(ledger.list_entries(conv)) == 3


def test_export_requires_watermark_metadata() -> None:
    media = MediaIntegrityService(watermark_required=True)
    blob = MediaBlob(
        blob_id="m1",
        conversation_id=ConversationId("c1"),
        creator_id=NodeId("alice"),
        content_type="image/png",
        ciphertext=b"encrypted-bytes",
        content_hash=hashlib.sha256(b"raw").hexdigest(),
        created_at=datetime.now(timezone.utc),
    )
    media.store(blob)
    exported = media.export_with_watermark("m1", NodeId("bob"))
    assert "exporter=bob" in exported.watermark_payload
    assert "creator=alice" in exported.watermark_payload
    assert exported.metadata["X-Vi-Exporter"] == "bob"
    assert exported.metadata["X-Vi-Watermark"] == "required"
    assert exported.bytes_out.startswith(b"\n<!-- WATERMARK:")


def test_mock_pqc_sign_and_kem_roundtrip() -> None:
    crypto = MockPqcProvider()
    sig_pk, sig_sk = crypto.generate_sign_keypair()
    msg = b"ledger-entry"
    signature = crypto.sign(sig_sk, msg)
    assert crypto.verify(sig_pk, msg, signature) is True

    kem_pk, kem_sk = crypto.generate_kem_keypair()
    ct, ss1 = crypto.kem_encapsulate(kem_pk)
    ss2 = crypto.kem_decapsulate(kem_sk, ct)
    assert ss1 == ss2

    key = ss1
    blob = crypto.aead_encrypt(key, b"hello", aad=b"conv")
    assert crypto.aead_decrypt(key, blob, aad=b"conv") == b"hello"

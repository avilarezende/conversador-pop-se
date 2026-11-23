from __future__ import annotations

from datetime import datetime, timezone

from vi_core.errors import PolicyDenied
from vi_core.types import NodeId
from vi_media.models import ExportedMedia, MediaBlob


class MediaIntegrityService:
    """Cofre de mídia + exportação fail-closed com marca d'água (esqueleto)."""

    def __init__(self, *, watermark_required: bool = True) -> None:
        self.watermark_required = watermark_required
        self._blobs: dict[str, MediaBlob] = {}

    def store(self, blob: MediaBlob) -> MediaBlob:
        self._blobs[blob.blob_id] = blob
        return blob

    def export_with_watermark(self, blob_id: str, exporter: NodeId) -> ExportedMedia:
        blob = self._blobs.get(blob_id)
        if blob is None:
            raise PolicyDenied(f"unknown blob: {blob_id}")
        if self.watermark_required is False:
            raise PolicyDenied("WATERMARK_DISABLED_NOT_ALLOWED")

        exported_at = datetime.now(timezone.utc).isoformat()
        watermark_payload = (
            f"vi|exporter={exporter}|creator={blob.creator_id}|"
            f"conv={blob.conversation_id}|at={exported_at}|hash={blob.content_hash[:16]}"
        )
        # Esqueleto: prefixa os bytes com o payload (substitui pipeline real de WM)
        marker = f"\n<!-- WATERMARK:{watermark_payload} -->\n".encode()
        bytes_out = marker + blob.ciphertext

        metadata = {
            "X-Vi-Exporter": str(exporter),
            "X-Vi-Creator": str(blob.creator_id),
            "X-Vi-Conversation": str(blob.conversation_id),
            "X-Vi-Content-Hash": blob.content_hash,
            "X-Vi-Exported-At": exported_at,
            "X-Vi-Watermark": "required",
        }
        return ExportedMedia(
            blob_id=blob.blob_id,
            exporter_id=exporter,
            creator_id=blob.creator_id,
            conversation_id=blob.conversation_id,
            watermark_payload=watermark_payload,
            metadata=metadata,
            bytes_out=bytes_out,
        )

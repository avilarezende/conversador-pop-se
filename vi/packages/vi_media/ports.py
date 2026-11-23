from __future__ import annotations

from typing import Protocol

from vi_core.types import NodeId
from vi_media.models import ExportedMedia, MediaBlob


class MediaExportPort(Protocol):
    def store(self, blob: MediaBlob) -> MediaBlob: ...

    def export_with_watermark(self, blob_id: str, exporter: NodeId) -> ExportedMedia: ...

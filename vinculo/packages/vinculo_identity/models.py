from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from vinculo_core.types import NodeId, NodeKind


@dataclass(frozen=True)
class IdentityRecord:
    node_id: NodeId
    kind: NodeKind
    display_name: str
    pqc_sign_public_key: bytes
    pqc_kem_public_key: bytes
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class DeviceRecord:
    device_id: str
    node_id: NodeId
    device_kem_public_key: bytes
    label: str = "primary"

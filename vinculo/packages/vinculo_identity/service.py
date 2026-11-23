from __future__ import annotations

from vinculo_core.errors import DomainError
from vinculo_core.types import NodeId, NodeKind
from vinculo_identity.models import IdentityRecord


class IdentityService:
    """Registro in-memory de identidades (esqueleto)."""

    def __init__(self) -> None:
        self._by_id: dict[NodeId, IdentityRecord] = {}

    def register(self, record: IdentityRecord) -> IdentityRecord:
        if record.node_id in self._by_id:
            raise DomainError(f"identity already registered: {record.node_id}")
        self._by_id[record.node_id] = record
        return record

    def get(self, node_id: NodeId) -> IdentityRecord:
        try:
            return self._by_id[node_id]
        except KeyError as exc:
            raise DomainError(f"unknown identity: {node_id}") from exc

    def list_by_kind(self, kind: NodeKind) -> list[IdentityRecord]:
        return [r for r in self._by_id.values() if r.kind == kind]

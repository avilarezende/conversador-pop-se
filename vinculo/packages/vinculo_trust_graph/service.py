from __future__ import annotations

from datetime import datetime, timezone

from vinculo_core.types import NodeId, NodeKind
from vinculo_trust_graph.models import Anchor, Decision, Edge
from vinculo_trust_graph.policy import TrustPolicy


class InMemoryTrustGraph:
    """Adapter in-memory do TrustGraphPort (esqueleto / testes)."""

    def __init__(
        self,
        policy: TrustPolicy | None = None,
        *,
        node_kinds: dict[NodeId, NodeKind] | None = None,
    ) -> None:
        self.policy = policy or TrustPolicy()
        self._edges: list[Edge] = []
        self._anchors: dict[str, Anchor] = {}
        self._node_kinds: dict[NodeId, NodeKind] = dict(node_kinds or {})

    def register_node(self, node_id: NodeId, kind: NodeKind) -> None:
        self._node_kinds[node_id] = kind

    def add_edge(self, edge: Edge) -> None:
        self._edges.append(edge)

    def add_anchor(self, anchor: Anchor) -> None:
        self._anchors[str(anchor.anchor_id)] = anchor

    def can_open_channel(
        self, a: NodeId, b: NodeId, at: datetime | None = None
    ) -> Decision:
        when = at or datetime.now(timezone.utc)
        entity_ids = {
            nid for nid, kind in self._node_kinds.items() if kind == NodeKind.ENTITY
        }
        return self.policy.decide(
            a,
            b,
            at=when,
            edges=list(self._edges),
            anchors=dict(self._anchors),
            entity_ids=entity_ids,
        )

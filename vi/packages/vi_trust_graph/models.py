from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from vi_core.types import AnchorId, NodeId


class EdgeType(StrEnum):
    RECOGNIZES = "recognizes"
    DIRECT_CONTACT = "direct_contact"
    MEMBER_OF = "member_of"
    AUTHORIZES_PAIR = "authorizes_pair"


@dataclass(frozen=True)
class Anchor:
    anchor_id: AnchorId
    label: str
    issued_by: NodeId
    valid_from: datetime
    valid_until: datetime

    def is_valid_at(self, at: datetime) -> bool:
        return self.valid_from <= at <= self.valid_until


@dataclass(frozen=True)
class Edge:
    src: NodeId
    dst: NodeId
    edge_type: EdgeType
    anchor_id: AnchorId | None = None
    # Para AUTHORIZES_PAIR: dst é a entidade emissora; pair_with é o outro indivíduo
    pair_with: NodeId | None = None


@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str
    entity: NodeId | None = None
    path: tuple[NodeId, ...] = ()

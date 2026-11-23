from __future__ import annotations

from datetime import datetime
from typing import Protocol

from vi_core.types import NodeId
from vi_trust_graph.models import Anchor, Decision, Edge


class TrustGraphPort(Protocol):
    def add_edge(self, edge: Edge) -> None: ...

    def add_anchor(self, anchor: Anchor) -> None: ...

    def can_open_channel(self, a: NodeId, b: NodeId, at: datetime) -> Decision: ...

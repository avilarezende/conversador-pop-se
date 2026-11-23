from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from vinculo_core.types import NodeId
from vinculo_trust_graph.models import Anchor, Decision, Edge, EdgeType


@dataclass
class TrustPolicy:
    """Regras R1–R4: 1º grau, entidade, ponte ≤2 arestas, âncora opcional."""

    max_path_edges: int = 2
    require_anchor_for_entity_bridge: bool = False

    def decide(
        self,
        a: NodeId,
        b: NodeId,
        *,
        at: datetime,
        edges: list[Edge],
        anchors: dict[str, Anchor],
        entity_ids: set[NodeId],
    ) -> Decision:
        if a == b:
            return Decision(False, "SAME_NODE")

        if self._mutual_direct(a, b, edges):
            return Decision(True, "DIRECT_1ST_DEGREE", path=(a, b))

        # Entidade como endpoint (R2)
        if b in entity_ids and self._recognizes(a, b, edges):
            return Decision(True, "ENTITY_TO_INDIVIDUAL", entity=b, path=(a, b))
        if a in entity_ids and self._recognizes(b, a, edges):
            return Decision(True, "ENTITY_TO_INDIVIDUAL", entity=a, path=(b, a))

        # Ponte por entidade (R3), máx. 2 saltos: A → E → B
        shared = self._shared_recognized_entities(a, b, edges, entity_ids)
        for entity in shared:
            if not self._entity_permits_pair(entity, a, b, edges):
                continue
            path = (a, entity, b)
            if len(path) - 1 > self.max_path_edges:
                continue
            if self.require_anchor_for_entity_bridge:
                if not self._bridge_anchor_valid(entity, a, b, edges, anchors, at):
                    continue
            return Decision(True, "ENTITY_BRIDGE", entity=entity, path=path)

        return Decision(False, "NO_VALID_PATH")

    def _mutual_direct(self, a: NodeId, b: NodeId, edges: list[Edge]) -> bool:
        ab = any(
            e.edge_type == EdgeType.DIRECT_CONTACT and e.src == a and e.dst == b for e in edges
        )
        ba = any(
            e.edge_type == EdgeType.DIRECT_CONTACT and e.src == b and e.dst == a for e in edges
        )
        return ab and ba

    def _recognizes(self, person: NodeId, entity: NodeId, edges: list[Edge]) -> bool:
        return any(
            e.edge_type in (EdgeType.RECOGNIZES, EdgeType.MEMBER_OF)
            and e.src == person
            and e.dst == entity
            for e in edges
        )

    def _shared_recognized_entities(
        self,
        a: NodeId,
        b: NodeId,
        edges: list[Edge],
        entity_ids: set[NodeId],
    ) -> list[NodeId]:
        a_ents = {e.dst for e in edges if e.src == a and e.dst in entity_ids
                  and e.edge_type in (EdgeType.RECOGNIZES, EdgeType.MEMBER_OF)}
        b_ents = {e.dst for e in edges if e.src == b and e.dst in entity_ids
                  and e.edge_type in (EdgeType.RECOGNIZES, EdgeType.MEMBER_OF)}
        return sorted(a_ents & b_ents)

    def _entity_permits_pair(
        self, entity: NodeId, a: NodeId, b: NodeId, edges: list[Edge]
    ) -> bool:
        # autoriza_par explícito (qualquer direção de par)
        for e in edges:
            if e.edge_type != EdgeType.AUTHORIZES_PAIR or e.src != entity:
                continue
            pair = {e.dst, e.pair_with}
            if pair == {a, b}:
                return True
        # ambos membros → peer intramembro permitido por padrão
        a_member = any(
            e.edge_type == EdgeType.MEMBER_OF and e.src == a and e.dst == entity for e in edges
        )
        b_member = any(
            e.edge_type == EdgeType.MEMBER_OF and e.src == b and e.dst == entity for e in edges
        )
        return a_member and b_member

    def _bridge_anchor_valid(
        self,
        entity: NodeId,
        a: NodeId,
        b: NodeId,
        edges: list[Edge],
        anchors: dict[str, Anchor],
        at: datetime,
    ) -> bool:
        for e in edges:
            if e.edge_type != EdgeType.AUTHORIZES_PAIR or e.src != entity:
                continue
            if {e.dst, e.pair_with} != {a, b}:
                continue
            if e.anchor_id is None:
                return False
            anchor = anchors.get(str(e.anchor_id))
            if anchor and anchor.is_valid_at(at):
                return True
        return False

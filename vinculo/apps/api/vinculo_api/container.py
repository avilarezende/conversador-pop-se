from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from vinculo_crypto_pqc import MockPqcProvider
from vinculo_identity import IdentityService
from vinculo_ledger import InMemoryLedger
from vinculo_media import MediaIntegrityService
from vinculo_realtime import RealtimeSessionService
from vinculo_trust_graph import InMemoryTrustGraph, TrustPolicy


@dataclass
class AppContainer:
    """Wiring explícito dos módulos (composition root)."""

    identity: IdentityService
    trust_graph: InMemoryTrustGraph
    ledger: InMemoryLedger
    media: MediaIntegrityService
    realtime: RealtimeSessionService
    crypto: MockPqcProvider
    modules: dict[str, Any]


def build_container(modules: dict[str, Any]) -> AppContainer:
    tg_cfg = modules.get("trust_graph", {})
    policy = TrustPolicy(
        max_path_edges=int(tg_cfg.get("max_path_edges", 2)),
        require_anchor_for_entity_bridge=bool(
            tg_cfg.get("require_anchor_for_entity_bridge", False)
        ),
    )
    realtime_enabled = bool(modules.get("realtime_av", {}).get("enabled", False))
    return AppContainer(
        identity=IdentityService(),
        trust_graph=InMemoryTrustGraph(policy=policy),
        ledger=InMemoryLedger(),
        media=MediaIntegrityService(watermark_required=True),
        realtime=RealtimeSessionService(enabled=realtime_enabled),
        crypto=MockPqcProvider(),
        modules=modules,
    )

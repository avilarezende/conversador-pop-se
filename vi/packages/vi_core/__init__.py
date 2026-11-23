"""Núcleo compartilhado: tipos, erros e eventos base."""

from vi_core.errors import DomainError, PolicyDenied
from vi_core.types import AnchorId, ConversationId, NodeId, NodeKind

__all__ = [
    "AnchorId",
    "ConversationId",
    "DomainError",
    "NodeId",
    "NodeKind",
    "PolicyDenied",
]

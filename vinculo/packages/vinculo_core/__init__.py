"""Núcleo compartilhado: tipos, erros e eventos base."""

from vinculo_core.errors import DomainError, PolicyDenied
from vinculo_core.types import AnchorId, ConversationId, NodeId, NodeKind

__all__ = [
    "AnchorId",
    "ConversationId",
    "DomainError",
    "NodeId",
    "NodeKind",
    "PolicyDenied",
]

from __future__ import annotations


class DomainError(Exception):
    """Erro de domínio genérico do Vínculo."""


class PolicyDenied(DomainError):
    """Operação bloqueada pela política de confiança ou de mídia."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(reason)

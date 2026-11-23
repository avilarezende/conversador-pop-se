from __future__ import annotations

from typing import Protocol


class PqcCryptoPort(Protocol):
    """Contrato estável; implementação real virá via liboqs."""

    def generate_kem_keypair(self) -> tuple[bytes, bytes]:
        """Retorna (public_key, secret_key)."""
        ...

    def generate_sign_keypair(self) -> tuple[bytes, bytes]:
        """Retorna (public_key, secret_key)."""
        ...

    def kem_encapsulate(self, public_key: bytes) -> tuple[bytes, bytes]:
        """Retorna (ciphertext, shared_secret)."""
        ...

    def kem_decapsulate(self, secret_key: bytes, ciphertext: bytes) -> bytes:
        """Retorna shared_secret."""
        ...

    def sign(self, secret_key: bytes, message: bytes) -> bytes: ...

    def verify(self, public_key: bytes, message: bytes, signature: bytes) -> bool: ...

    def aead_encrypt(self, key: bytes, plaintext: bytes, aad: bytes = b"") -> bytes: ...

    def aead_decrypt(self, key: bytes, ciphertext: bytes, aad: bytes = b"") -> bytes: ...

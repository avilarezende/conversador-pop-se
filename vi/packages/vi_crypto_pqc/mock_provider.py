from __future__ import annotations

import hashlib
import hmac
import os


class MockPqcProvider:
    """
    Provider determinístico para o esqueleto.

    NÃO é criptografia pós-quântica real — apenas exercita os ports.
    Trocar por adapter liboqs sem alterar callers (hexagonal).
    """

    name = "mock"

    def generate_kem_keypair(self) -> tuple[bytes, bytes]:
        sk = os.urandom(32)
        pk = hashlib.sha256(b"kem-pk|" + sk).digest()
        return pk, sk

    def generate_sign_keypair(self) -> tuple[bytes, bytes]:
        sk = os.urandom(32)
        pk = hashlib.sha256(b"sig-pk|" + sk).digest()
        return pk, sk

    def kem_encapsulate(self, public_key: bytes) -> tuple[bytes, bytes]:
        ephemeral = os.urandom(16)
        ciphertext = hashlib.sha256(b"ct|" + public_key + ephemeral).digest() + ephemeral
        shared = hashlib.sha256(b"ss|" + public_key + ephemeral).digest()
        return ciphertext, shared

    def kem_decapsulate(self, secret_key: bytes, ciphertext: bytes) -> bytes:
        pk = hashlib.sha256(b"kem-pk|" + secret_key).digest()
        ephemeral = ciphertext[-16:]
        return hashlib.sha256(b"ss|" + pk + ephemeral).digest()

    def sign(self, secret_key: bytes, message: bytes) -> bytes:
        pk = hashlib.sha256(b"sig-pk|" + secret_key).digest()
        return hashlib.sha256(b"sig|" + pk + message).digest()

    def verify(self, public_key: bytes, message: bytes, signature: bytes) -> bool:
        expected = hashlib.sha256(b"sig|" + public_key + message).digest()
        return hmac.compare_digest(expected, signature)

    def aead_encrypt(self, key: bytes, plaintext: bytes, aad: bytes = b"") -> bytes:
        nonce = os.urandom(12)
        digest = hmac.new(key, nonce + aad + plaintext, hashlib.sha256).digest()
        stream = hashlib.sha256(key + nonce + aad).digest()
        cipher = bytes(p ^ stream[i % len(stream)] for i, p in enumerate(plaintext))
        return nonce + digest + cipher

    def aead_decrypt(self, key: bytes, ciphertext: bytes, aad: bytes = b"") -> bytes:
        nonce, digest, cipher = ciphertext[:12], ciphertext[12:44], ciphertext[44:]
        stream = hashlib.sha256(key + nonce + aad).digest()
        plain = bytes(c ^ stream[i % len(stream)] for i, c in enumerate(cipher))
        check = hmac.new(key, nonce + aad + plain, hashlib.sha256).digest()
        if not hmac.compare_digest(check, digest):
            raise ValueError("AEAD auth failed")
        return plain

"""RAG client creation must work with Chroma's public factory API."""

from app import rag


def test_get_chroma_creates_and_reuses_client(tmp_path, monkeypatch):
    monkeypatch.setattr(rag.settings, "chroma_path", str(tmp_path / "chroma"))
    monkeypatch.setattr(rag, "_client", None)

    client = rag.get_chroma()

    assert client.heartbeat() > 0
    assert rag.get_chroma() is client

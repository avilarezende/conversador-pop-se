from __future__ import annotations

from fastapi.testclient import TestClient

from vi_api.main import app

client = TestClient(app)


def test_health_lists_modules() -> None:
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["service"] == "vi-api"
    assert body["modules"]["trust_graph"] is True
    assert body["modules"]["realtime_av"] is False


def test_register_and_direct_channel_flow() -> None:
    assert client.post(
        "/api/v1/identity/register",
        json={"node_id": "u1", "kind": "individual", "display_name": "Ana"},
    ).status_code == 200
    assert client.post(
        "/api/v1/identity/register",
        json={"node_id": "u2", "kind": "individual", "display_name": "Bruno"},
    ).status_code == 200

    denied = client.post(
        "/api/v1/channels/can-open", json={"a": "u1", "b": "u2"}
    ).json()
    assert denied["allowed"] is False

    client.post(
        "/api/v1/graph/edges",
        json={"src": "u1", "dst": "u2", "edge_type": "direct_contact"},
    )
    client.post(
        "/api/v1/graph/edges",
        json={"src": "u2", "dst": "u1", "edge_type": "direct_contact"},
    )
    allowed = client.post(
        "/api/v1/channels/can-open", json={"a": "u1", "b": "u2"}
    ).json()
    assert allowed["allowed"] is True
    assert allowed["reason"] == "DIRECT_1ST_DEGREE"

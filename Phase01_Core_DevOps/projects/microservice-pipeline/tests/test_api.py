from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_ready():
    r = client.get("/ready")
    assert r.status_code == 200


def test_list_items():
    r = client.get("/v1/items")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) >= 1


def test_create_and_get_item():
    created = client.post("/v1/items", json={"name": "ship helm chart", "done": False})
    assert created.status_code == 201
    item_id = created.json()["id"]

    fetched = client.get(f"/v1/items/{item_id}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "ship helm chart"


def test_missing_item():
    r = client.get("/v1/items/999999")
    assert r.status_code == 404

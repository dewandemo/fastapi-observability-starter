"""Tests for /items CRUD endpoints."""


def test_list_is_empty_initially(client):
    r = client.get("/items")
    assert r.status_code == 200
    assert r.json() == []


def test_create_returns_201_with_id_and_body(client):
    r = client.post("/items", json={"name": "widget", "quantity": 3})
    assert r.status_code == 201
    assert r.json() == {"id": 1, "name": "widget", "quantity": 3}


def test_create_defaults_quantity_to_one(client):
    r = client.post("/items", json={"name": "widget"})
    assert r.status_code == 201
    assert r.json()["quantity"] == 1


def test_create_assigns_sequential_ids(client):
    ids = [
        client.post("/items", json={"name": n}).json()["id"]
        for n in ("a", "b", "c")
    ]
    assert ids == [1, 2, 3]


def test_get_by_id_returns_created_item(client):
    client.post("/items", json={"name": "widget", "quantity": 5})
    r = client.get("/items/1")
    assert r.status_code == 200
    assert r.json() == {"id": 1, "name": "widget", "quantity": 5}


def test_get_missing_id_returns_404(client):
    r = client.get("/items/999")
    assert r.status_code == 404
    assert r.json()["detail"] == "Item not found"


def test_delete_returns_204_and_removes_item(client):
    client.post("/items", json={"name": "widget"})
    r = client.delete("/items/1")
    assert r.status_code == 204
    assert client.get("/items/1").status_code == 404


def test_delete_missing_id_returns_404(client):
    r = client.delete("/items/999")
    assert r.status_code == 404


def test_list_reflects_creates_and_deletes(client):
    client.post("/items", json={"name": "a"})
    client.post("/items", json={"name": "b"})
    client.post("/items", json={"name": "c"})
    client.delete("/items/2")

    body = client.get("/items").json()
    assert [item["id"] for item in body] == [1, 3]


def test_create_rejects_empty_name_with_422(client):
    r = client.post("/items", json={"name": "", "quantity": 1})
    assert r.status_code == 422


def test_create_rejects_negative_quantity_with_422(client):
    r = client.post("/items", json={"name": "widget", "quantity": -1})
    assert r.status_code == 422

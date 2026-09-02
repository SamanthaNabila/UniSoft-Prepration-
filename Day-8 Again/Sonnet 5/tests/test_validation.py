"""Validation and error-handling tests."""


def test_missing_title_is_rejected(client):
    res = client.post("/api/tasks", json={"description": "no title"})
    assert res.status_code == 400
    assert "title" in res.get_json()["details"]


def test_blank_title_is_rejected(client):
    res = client.post("/api/tasks", json={"title": "   "})
    assert res.status_code == 400
    assert "title" in res.get_json()["details"]


def test_overlong_description_is_rejected(client):
    res = client.post(
        "/api/tasks", json={"title": "ok", "description": "x" * 2001}
    )
    assert res.status_code == 400
    assert "description" in res.get_json()["details"]


def test_invalid_priority_is_rejected(client):
    res = client.post("/api/tasks", json={"title": "ok", "priority": "urgent"})
    assert res.status_code == 400
    assert "priority" in res.get_json()["details"]


def test_invalid_status_is_rejected(client):
    res = client.post("/api/tasks", json={"title": "ok", "status": "done"})
    assert res.status_code == 400
    assert "status" in res.get_json()["details"]


def test_invalid_due_date_is_rejected(client):
    res = client.post("/api/tasks", json={"title": "ok", "due_date": "15-09-2026"})
    assert res.status_code == 400
    assert "due_date" in res.get_json()["details"]


def test_valid_due_date_is_accepted(client):
    res = client.post("/api/tasks", json={"title": "ok", "due_date": "2026-12-01"})
    assert res.status_code == 201
    assert res.get_json()["due_date"] == "2026-12-01"


def test_due_date_can_be_cleared_on_update(client, make_task):
    created = make_task(due_date="2026-10-10")
    res = client.patch(f"/api/tasks/{created['id']}", json={"due_date": None})
    assert res.status_code == 200
    assert res.get_json()["due_date"] is None


def test_non_json_body_is_rejected(client):
    res = client.post(
        "/api/tasks", data="not json", content_type="text/plain"
    )
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_empty_partial_update_is_rejected(client, make_task):
    created = make_task()
    res = client.patch(f"/api/tasks/{created['id']}", json={"unknown_field": 1})
    assert res.status_code == 400


def test_unknown_route_returns_json_404(client):
    res = client.get("/api/does-not-exist")
    assert res.status_code == 404
    assert res.is_json
    assert "error" in res.get_json()


def test_wrong_method_returns_405(client):
    res = client.delete("/api/tasks")
    assert res.status_code == 405
    assert "error" in res.get_json()

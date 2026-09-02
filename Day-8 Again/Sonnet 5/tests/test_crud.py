"""CRUD lifecycle tests for the task API."""


def test_create_task_returns_201_and_full_object(client):
    res = client.post(
        "/api/tasks",
        json={
            "title": "Write report",
            "description": "Quarterly summary",
            "priority": "high",
            "due_date": "2026-09-15",
        },
    )
    assert res.status_code == 201
    body = res.get_json()

    assert body["id"] > 0
    assert body["title"] == "Write report"
    assert body["description"] == "Quarterly summary"
    assert body["priority"] == "high"
    assert body["status"] == "pending"  # default
    assert body["due_date"] == "2026-09-15"
    assert body["created_at"] and body["updated_at"]


def test_create_task_trims_title_and_applies_defaults(client):
    res = client.post("/api/tasks", json={"title": "   Tidy desk   "})
    body = res.get_json()
    assert body["title"] == "Tidy desk"
    assert body["priority"] == "medium"
    assert body["status"] == "pending"
    assert body["due_date"] is None


def test_get_single_task(client, make_task):
    created = make_task(title="Buy milk")
    res = client.get(f"/api/tasks/{created['id']}")
    assert res.status_code == 200
    assert res.get_json()["title"] == "Buy milk"


def test_get_missing_task_returns_404(client):
    res = client.get("/api/tasks/999")
    assert res.status_code == 404
    assert "error" in res.get_json()


def test_list_returns_all_tasks(client, make_task):
    make_task(title="One")
    make_task(title="Two")
    res = client.get("/api/tasks")
    assert res.status_code == 200
    assert len(res.get_json()) == 2


def test_update_task_changes_fields(client, make_task):
    created = make_task(title="Draft", priority="low")
    res = client.put(
        f"/api/tasks/{created['id']}",
        json={"title": "Final draft", "priority": "high"},
    )
    assert res.status_code == 200
    body = res.get_json()
    assert body["title"] == "Final draft"
    assert body["priority"] == "high"
    assert body["updated_at"] >= created["updated_at"]


def test_partial_update_leaves_other_fields_untouched(client, make_task):
    created = make_task(title="Keep me", description="original")
    res = client.patch(f"/api/tasks/{created['id']}", json={"status": "completed"})
    body = res.get_json()
    assert body["status"] == "completed"
    assert body["title"] == "Keep me"
    assert body["description"] == "original"


def test_update_missing_task_returns_404(client):
    res = client.put("/api/tasks/12345", json={"title": "Nope"})
    assert res.status_code == 404


def test_toggle_status_via_patch(client, make_task):
    created = make_task()
    done = client.patch(
        f"/api/tasks/{created['id']}", json={"status": "completed"}
    ).get_json()
    assert done["status"] == "completed"
    reopened = client.patch(
        f"/api/tasks/{created['id']}", json={"status": "pending"}
    ).get_json()
    assert reopened["status"] == "pending"


def test_delete_task(client, make_task):
    created = make_task()
    res = client.delete(f"/api/tasks/{created['id']}")
    assert res.status_code == 204
    assert client.get(f"/api/tasks/{created['id']}").status_code == 404


def test_delete_missing_task_returns_404(client):
    res = client.delete("/api/tasks/777")
    assert res.status_code == 404


def test_invalid_task_id_in_path_returns_404(client):
    res = client.get("/api/tasks/not-a-number")
    assert res.status_code == 404
    assert "error" in res.get_json()

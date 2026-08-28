def _create_ticket(client, headers, **overrides):
    payload = {
        "title": "Printer is jammed",
        "description": "The printer on floor 3 is jammed and needs service.",
        "priority": "medium",
    }
    payload.update(overrides)
    response = client.post("/api/v1/tickets", json=payload, headers=headers)
    assert response.status_code == 201
    return response.json()


def test_employee_can_create_ticket(client, employee_a):
    response = client.post(
        "/api/v1/tickets",
        json={
            "title": "VPN not connecting",
            "description": "Cannot connect to the office VPN from home.",
            "priority": "high",
        },
        headers=employee_a,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "open"
    assert body["priority"] == "high"


def test_support_agent_blocked_from_creating_ticket(client, agent_a):
    response = client.post(
        "/api/v1/tickets",
        json={
            "title": "VPN not connecting",
            "description": "Cannot connect to the office VPN from home.",
        },
        headers=agent_a,
    )

    assert response.status_code == 403
    assert (
        response.json()["detail"]
        == "Access denied: Support Agents are not allowed to create tickets."
    )


def test_support_agent_can_update_status_and_priority_on_any_ticket(
    client, employee_a, agent_a
):
    ticket = _create_ticket(client, employee_a)

    response = client.patch(
        f"/api/v1/tickets/{ticket['id']}/status",
        json={"status": "in_progress", "priority": "high"},
        headers=agent_a,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "in_progress"
    assert body["priority"] == "high"


def test_support_agent_can_assign_ticket_to_agent(
    client, employee_a, agent_a, agent_b
):
    ticket = _create_ticket(client, employee_a)
    agent_b_id = client.get("/api/v1/auth/me", headers=agent_b).json()["id"]

    response = client.patch(
        f"/api/v1/tickets/{ticket['id']}/assignment",
        json={"assigned_to": agent_b_id},
        headers=agent_a,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["assigned_to"] == agent_b_id
    assert body["assigned_to_name"]


def test_support_agent_can_reassign_ticket(client, employee_a, agent_a, agent_b):
    ticket = _create_ticket(client, employee_a)
    agent_a_id = client.get("/api/v1/auth/me", headers=agent_a).json()["id"]
    agent_b_id = client.get("/api/v1/auth/me", headers=agent_b).json()["id"]

    client.patch(
        f"/api/v1/tickets/{ticket['id']}/assignment",
        json={"assigned_to": agent_a_id},
        headers=agent_a,
    )
    response = client.patch(
        f"/api/v1/tickets/{ticket['id']}/assignment",
        json={"assigned_to": agent_b_id},
        headers=agent_a,
    )

    assert response.status_code == 200
    assert response.json()["assigned_to"] == agent_b_id


def test_assigned_agent_can_release_own_assignment(client, employee_a, agent_a):
    ticket = _create_ticket(client, employee_a)
    agent_id = client.get("/api/v1/auth/me", headers=agent_a).json()["id"]
    endpoint = f"/api/v1/tickets/{ticket['id']}/assignment"

    client.patch(endpoint, json={"assigned_to": agent_id}, headers=agent_a)
    response = client.patch(endpoint, json={"assigned_to": None}, headers=agent_a)

    assert response.status_code == 200
    assert response.json()["assigned_to"] is None
    assert response.json()["assigned_to_name"] is None


def test_employee_cannot_assign_ticket(client, employee_a, agent_a):
    ticket = _create_ticket(client, employee_a)
    agent_id = client.get("/api/v1/auth/me", headers=agent_a).json()["id"]

    response = client.patch(
        f"/api/v1/tickets/{ticket['id']}/assignment",
        json={"assigned_to": agent_id},
        headers=employee_a,
    )

    assert response.status_code == 403


def test_assignment_rejects_employee_target(client, employee_a, agent_a):
    ticket = _create_ticket(client, employee_a)
    employee_id = client.get("/api/v1/auth/me", headers=employee_a).json()["id"]

    response = client.patch(
        f"/api/v1/tickets/{ticket['id']}/assignment",
        json={"assigned_to": employee_id},
        headers=agent_a,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Tickets can only be assigned to Support Agents."


def test_assignment_returns_404_for_missing_assignee(client, employee_a, agent_a):
    ticket = _create_ticket(client, employee_a)

    response = client.patch(
        f"/api/v1/tickets/{ticket['id']}/assignment",
        json={"assigned_to": 99999},
        headers=agent_a,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Assignee not found."


def test_assignment_returns_404_for_missing_ticket(client, agent_a):
    response = client.patch(
        "/api/v1/tickets/99999/assignment",
        json={"assigned_to": 1},
        headers=agent_a,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found."


def test_support_agent_can_follow_ticket_lifecycle(client, employee_a, agent_a):
    ticket = _create_ticket(client, employee_a)

    for current_status, next_status in [
        ("open", "in_progress"),
        ("in_progress", "resolved"),
        ("resolved", "closed"),
        ("closed", "open"),
        ("open", "in_progress"),
        ("in_progress", "resolved"),
        ("resolved", "in_progress"),
    ]:
        response = client.patch(
            f"/api/v1/tickets/{ticket['id']}/status",
            json={"status": next_status},
            headers=agent_a,
        )

        assert response.status_code == 200
        assert response.json()["status"] == next_status


def test_support_agent_cannot_skip_ticket_lifecycle_statuses(
    client, employee_a, agent_a
):
    ticket = _create_ticket(client, employee_a)

    response = client.patch(
        f"/api/v1/tickets/{ticket['id']}/status",
        json={"status": "resolved"},
        headers=agent_a,
    )

    assert response.status_code == 409
    assert (
        response.json()["detail"]
        == "Invalid ticket status transition: open -> resolved."
    )


def test_priority_only_update_does_not_require_status_transition(
    client, employee_a, agent_a
):
    ticket = _create_ticket(client, employee_a)

    response = client.patch(
        f"/api/v1/tickets/{ticket['id']}/status",
        json={"priority": "high"},
        headers=agent_a,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "open"
    assert response.json()["priority"] == "high"


def test_employee_blocked_from_updating_status(client, employee_a):
    ticket = _create_ticket(client, employee_a)

    response = client.patch(
        f"/api/v1/tickets/{ticket['id']}/status",
        json={"status": "resolved"},
        headers=employee_a,
    )

    assert response.status_code == 403
    assert (
        response.json()["detail"]
        == "Access denied: Only Support Agents can update ticket status or priority."
    )


def test_owner_employee_can_update_own_ticket(client, employee_a):
    ticket = _create_ticket(client, employee_a)

    response = client.put(
        f"/api/v1/tickets/{ticket['id']}",
        json={
            "title": "Updated title here",
            "description": "Updated description that is long enough.",
        },
        headers=employee_a,
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated title here"


def test_non_owner_employee_blocked_from_updating_ticket(
    client, employee_a, employee_b
):
    ticket = _create_ticket(client, employee_a)

    response = client.put(
        f"/api/v1/tickets/{ticket['id']}",
        json={
            "title": "Hijacked title attempt",
            "description": "Trying to edit someone else's ticket.",
        },
        headers=employee_b,
    )

    assert response.status_code == 403
    assert (
        response.json()["detail"]
        == "Forbidden: You are only allowed to modify or delete your own tickets."
    )


def test_agent_blocked_from_updating_ticket_title(client, employee_a, agent_a):
    ticket = _create_ticket(client, employee_a)

    response = client.put(
        f"/api/v1/tickets/{ticket['id']}",
        json={
            "title": "Agent should not be able to do this",
            "description": "Agents cannot edit ticket title/description.",
        },
        headers=agent_a,
    )

    assert response.status_code == 403


def test_owner_employee_can_delete_own_ticket(client, employee_a):
    ticket = _create_ticket(client, employee_a)

    response = client.delete(f"/api/v1/tickets/{ticket['id']}", headers=employee_a)

    assert response.status_code == 204
    get_response = client.get(f"/api/v1/tickets/{ticket['id']}", headers=employee_a)
    assert get_response.status_code == 404


def test_non_owner_employee_blocked_from_deleting_ticket(
    client, employee_a, employee_b
):
    ticket = _create_ticket(client, employee_a)

    response = client.delete(f"/api/v1/tickets/{ticket['id']}", headers=employee_b)

    assert response.status_code == 403
    assert (
        response.json()["detail"]
        == "Forbidden: You are only allowed to modify or delete your own tickets."
    )


def test_agent_blocked_from_deleting_ticket(client, employee_a, agent_a):
    ticket = _create_ticket(client, employee_a)

    response = client.delete(f"/api/v1/tickets/{ticket['id']}", headers=agent_a)

    assert response.status_code == 403


def test_employee_can_view_all_tickets_not_just_own(client, employee_a, employee_b):
    _create_ticket(client, employee_a, title="Employee A ticket one")
    _create_ticket(client, employee_b, title="Employee B ticket one")

    response = client.get("/api/v1/tickets", headers=employee_a)

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_agent_can_view_all_tickets(client, employee_a, employee_b, agent_a):
    _create_ticket(client, employee_a, title="Employee A ticket one")
    _create_ticket(client, employee_b, title="Employee B ticket one")

    response = client.get("/api/v1/tickets", headers=agent_a)

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_employee_can_view_ticket_detail_of_others_ticket(
    client, employee_a, employee_b
):
    ticket = _create_ticket(client, employee_b)

    response = client.get(f"/api/v1/tickets/{ticket['id']}", headers=employee_a)

    assert response.status_code == 200


def test_get_ticket_not_found_returns_404(client, employee_a):
    response = client.get("/api/v1/tickets/99999", headers=employee_a)

    assert response.status_code == 404


def test_list_tickets_filters_by_status(client, employee_a, agent_a):
    ticket = _create_ticket(client, employee_a)
    client.patch(
        f"/api/v1/tickets/{ticket['id']}/status",
        json={"status": "in_progress"},
        headers=agent_a,
    )
    client.patch(
        f"/api/v1/tickets/{ticket['id']}/status",
        json={"status": "resolved"},
        headers=agent_a,
    )
    _create_ticket(client, employee_a, title="Second open ticket here")

    response = client.get("/api/v1/tickets?status=resolved", headers=employee_a)

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["status"] == "resolved"


def test_ticket_stats_endpoint(client, employee_a, agent_a):
    ticket = _create_ticket(client, employee_a)
    _create_ticket(client, employee_a, title="Another ticket for stats test")
    client.patch(
        f"/api/v1/tickets/{ticket['id']}/status",
        json={"status": "in_progress"},
        headers=agent_a,
    )
    client.patch(
        f"/api/v1/tickets/{ticket['id']}/status",
        json={"status": "resolved"},
        headers=agent_a,
    )

    response = client.get("/api/v1/tickets/stats", headers=employee_a)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert body["resolved"] == 1
    assert body["open"] == 1

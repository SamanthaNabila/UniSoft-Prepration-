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


def _user_id(client, headers) -> int:
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    return response.json()["id"]


def test_agent_can_assign_unassigned_ticket_to_self(client, employee_a, agent_a):
    ticket = _create_ticket(client, employee_a)
    agent_id = _user_id(client, agent_a)

    response = client.patch(
        f"/api/v1/tickets/{ticket['id']}/assignment",
        json={"assigned_to": agent_id},
        headers=agent_a,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["assigned_to"] == agent_id
    assert body["assigned_to_name"] is not None


def test_agent_can_assign_ticket_to_another_agent(client, employee_a, agent_a, agent_b):
    ticket = _create_ticket(client, employee_a)
    agent_b_id = _user_id(client, agent_b)

    response = client.patch(
        f"/api/v1/tickets/{ticket['id']}/assignment",
        json={"assigned_to": agent_b_id},
        headers=agent_a,
    )

    assert response.status_code == 200
    assert response.json()["assigned_to"] == agent_b_id


def test_agent_can_reassign_ticket_to_different_agent(
    client, employee_a, agent_a, agent_b
):
    ticket = _create_ticket(client, employee_a)
    agent_a_id = _user_id(client, agent_a)
    agent_b_id = _user_id(client, agent_b)

    first = client.patch(
        f"/api/v1/tickets/{ticket['id']}/assignment",
        json={"assigned_to": agent_a_id},
        headers=agent_a,
    )
    assert first.status_code == 200
    assert first.json()["assigned_to"] == agent_a_id

    second = client.patch(
        f"/api/v1/tickets/{ticket['id']}/assignment",
        json={"assigned_to": agent_b_id},
        headers=agent_b,
    )
    assert second.status_code == 200
    assert second.json()["assigned_to"] == agent_b_id


def test_agent_can_release_own_assignment(client, employee_a, agent_a):
    ticket = _create_ticket(client, employee_a)
    agent_id = _user_id(client, agent_a)
    client.patch(
        f"/api/v1/tickets/{ticket['id']}/assignment",
        json={"assigned_to": agent_id},
        headers=agent_a,
    )

    response = client.patch(
        f"/api/v1/tickets/{ticket['id']}/assignment",
        json={"assigned_to": None},
        headers=agent_a,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["assigned_to"] is None
    assert body["assigned_to_name"] is None


def test_employee_blocked_from_assigning_ticket(client, employee_a, agent_a):
    ticket = _create_ticket(client, employee_a)
    agent_id = _user_id(client, agent_a)

    response = client.patch(
        f"/api/v1/tickets/{ticket['id']}/assignment",
        json={"assigned_to": agent_id},
        headers=employee_a,
    )

    assert response.status_code == 403
    assert (
        response.json()["detail"]
        == "Access denied: Only Support Agents can assign or release tickets."
    )


def test_employee_blocked_from_releasing_assignment(client, employee_a, agent_a):
    ticket = _create_ticket(client, employee_a)
    agent_id = _user_id(client, agent_a)
    client.patch(
        f"/api/v1/tickets/{ticket['id']}/assignment",
        json={"assigned_to": agent_id},
        headers=agent_a,
    )

    response = client.patch(
        f"/api/v1/tickets/{ticket['id']}/assignment",
        json={"assigned_to": None},
        headers=employee_a,
    )

    assert response.status_code == 403


def test_assign_to_nonexistent_user_returns_404(client, employee_a, agent_a):
    ticket = _create_ticket(client, employee_a)

    response = client.patch(
        f"/api/v1/tickets/{ticket['id']}/assignment",
        json={"assigned_to": 999999},
        headers=agent_a,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Assignment target user not found."


def test_assign_to_employee_returns_400(client, employee_a, employee_b, agent_a):
    ticket = _create_ticket(client, employee_a)
    employee_b_id = _user_id(client, employee_b)

    response = client.patch(
        f"/api/v1/tickets/{ticket['id']}/assignment",
        json={"assigned_to": employee_b_id},
        headers=agent_a,
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"] == "Only Support Agents can be assigned to tickets."
    )


def test_assignment_on_nonexistent_ticket_returns_404(client, agent_a):
    agent_id = _user_id(client, agent_a)

    response = client.patch(
        "/api/v1/tickets/99999/assignment",
        json={"assigned_to": agent_id},
        headers=agent_a,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found."


def test_assignment_requires_assigned_to_field(client, employee_a, agent_a):
    ticket = _create_ticket(client, employee_a)

    response = client.patch(
        f"/api/v1/tickets/{ticket['id']}/assignment",
        json={},
        headers=agent_a,
    )

    assert response.status_code == 422


def test_new_ticket_is_unassigned_by_default(client, employee_a):
    ticket = _create_ticket(client, employee_a)

    assert ticket["assigned_to"] is None
    assert ticket["assigned_to_name"] is None


def test_list_tickets_filters_unassigned(client, employee_a, agent_a):
    unassigned = _create_ticket(client, employee_a, title="Unassigned ticket here")
    assigned = _create_ticket(client, employee_a, title="Assigned ticket here")
    agent_id = _user_id(client, agent_a)
    client.patch(
        f"/api/v1/tickets/{assigned['id']}/assignment",
        json={"assigned_to": agent_id},
        headers=agent_a,
    )

    response = client.get("/api/v1/tickets?assigned_to=unassigned", headers=employee_a)

    assert response.status_code == 200
    ids = [t["id"] for t in response.json()]
    assert unassigned["id"] in ids
    assert assigned["id"] not in ids


def test_list_tickets_filters_assigned_to_me(client, employee_a, agent_a, agent_b):
    ticket_for_a = _create_ticket(client, employee_a, title="Ticket for agent A")
    ticket_for_b = _create_ticket(client, employee_a, title="Ticket for agent B")
    agent_a_id = _user_id(client, agent_a)
    agent_b_id = _user_id(client, agent_b)
    client.patch(
        f"/api/v1/tickets/{ticket_for_a['id']}/assignment",
        json={"assigned_to": agent_a_id},
        headers=agent_a,
    )
    client.patch(
        f"/api/v1/tickets/{ticket_for_b['id']}/assignment",
        json={"assigned_to": agent_b_id},
        headers=agent_b,
    )

    response = client.get("/api/v1/tickets?assigned_to=me", headers=agent_a)

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == ticket_for_a["id"]

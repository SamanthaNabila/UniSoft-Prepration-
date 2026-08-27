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


def test_owner_employee_can_comment_on_own_ticket(client, employee_a):
    ticket = _create_ticket(client, employee_a)

    response = client.post(
        f"/api/v1/tickets/{ticket['id']}/comments",
        json={"content": "Following up on this issue."},
        headers=employee_a,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["content"] == "Following up on this issue."
    assert body["ticket_id"] == ticket["id"]


def test_employee_blocked_from_commenting_on_others_ticket(
    client, employee_a, employee_b
):
    ticket = _create_ticket(client, employee_a)

    response = client.post(
        f"/api/v1/tickets/{ticket['id']}/comments",
        json={"content": "I should not be able to post this."},
        headers=employee_b,
    )

    assert response.status_code == 403
    assert (
        response.json()["detail"]
        == "Forbidden: You can only comment on tickets you created."
    )


def test_support_agent_can_comment_on_any_ticket(client, employee_a, agent_a):
    ticket = _create_ticket(client, employee_a)

    response = client.post(
        f"/api/v1/tickets/{ticket['id']}/comments",
        json={"content": "We are looking into this now."},
        headers=agent_a,
    )

    assert response.status_code == 201


def test_support_agent_can_comment_on_multiple_employees_tickets(
    client, employee_a, employee_b, agent_a
):
    ticket_a = _create_ticket(client, employee_a, title="Employee A ticket")
    ticket_b = _create_ticket(client, employee_b, title="Employee B ticket")

    response_a = client.post(
        f"/api/v1/tickets/{ticket_a['id']}/comments",
        json={"content": "Handling employee A's ticket."},
        headers=agent_a,
    )
    response_b = client.post(
        f"/api/v1/tickets/{ticket_b['id']}/comments",
        json={"content": "Handling employee B's ticket."},
        headers=agent_a,
    )

    assert response_a.status_code == 201
    assert response_b.status_code == 201


def test_comment_on_nonexistent_ticket_returns_404(client, employee_a):
    response = client.post(
        "/api/v1/tickets/99999/comments",
        json={"content": "This ticket does not exist."},
        headers=employee_a,
    )

    assert response.status_code == 404


def test_list_comments_returns_chronological_order(client, employee_a, agent_a):
    ticket = _create_ticket(client, employee_a)
    client.post(
        f"/api/v1/tickets/{ticket['id']}/comments",
        json={"content": "First comment."},
        headers=employee_a,
    )
    client.post(
        f"/api/v1/tickets/{ticket['id']}/comments",
        json={"content": "Second comment."},
        headers=agent_a,
    )

    response = client.get(f"/api/v1/tickets/{ticket['id']}/comments", headers=employee_a)

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert body[0]["content"] == "First comment."
    assert body[1]["content"] == "Second comment."


def test_employee_can_view_comments_on_others_ticket(client, employee_a, employee_b, agent_a):
    ticket = _create_ticket(client, employee_a)
    client.post(
        f"/api/v1/tickets/{ticket['id']}/comments",
        json={"content": "Agent response here."},
        headers=agent_a,
    )

    response = client.get(f"/api/v1/tickets/{ticket['id']}/comments", headers=employee_b)

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_comment_content_validation_rejects_empty_string(client, employee_a):
    ticket = _create_ticket(client, employee_a)

    response = client.post(
        f"/api/v1/tickets/{ticket['id']}/comments",
        json={"content": "   "},
        headers=employee_a,
    )

    assert response.status_code == 422

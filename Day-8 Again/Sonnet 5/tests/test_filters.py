"""Filtering, search and dashboard tests."""

import pytest


@pytest.fixture
def seeded(make_task):
    make_task(title="Buy groceries", priority="low", status="pending")
    make_task(title="Buy plane tickets", priority="high", status="pending")
    make_task(title="Finish groceries report", priority="high", status="completed")
    make_task(title="Call plumber", priority="medium", status="completed")


def _titles(res):
    return sorted(t["title"] for t in res.get_json())


def test_filter_by_status(client, seeded):
    res = client.get("/api/tasks?status=completed")
    assert res.status_code == 200
    assert _titles(res) == ["Call plumber", "Finish groceries report"]


def test_filter_by_priority(client, seeded):
    res = client.get("/api/tasks?priority=high")
    assert _titles(res) == ["Buy plane tickets", "Finish groceries report"]


def test_search_by_title_is_case_insensitive(client, seeded):
    res = client.get("/api/tasks?search=GROCERIES")
    assert _titles(res) == ["Buy groceries", "Finish groceries report"]


def test_combined_filters(client, seeded):
    res = client.get("/api/tasks?search=groceries&priority=high&status=completed")
    assert _titles(res) == ["Finish groceries report"]


def test_invalid_filter_value_is_rejected(client, seeded):
    res = client.get("/api/tasks?status=archived")
    assert res.status_code == 400


def test_no_matches_returns_empty_list(client, seeded):
    res = client.get("/api/tasks?search=nonexistent")
    assert res.status_code == 200
    assert res.get_json() == []


def test_dashboard_counts(client, seeded):
    res = client.get("/api/dashboard")
    assert res.status_code == 200
    assert res.get_json() == {
        "total_tasks": 4,
        "pending_tasks": 2,
        "completed_tasks": 2,
        "high_priority_tasks": 2,
    }


def test_dashboard_on_empty_database(client):
    res = client.get("/api/dashboard")
    assert res.get_json() == {
        "total_tasks": 0,
        "pending_tasks": 0,
        "completed_tasks": 0,
        "high_priority_tasks": 0,
    }

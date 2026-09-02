"""REST API for tasks.

All endpoints live under the ``/api`` prefix (see ``create_app``).
"""

from flask import Blueprint, current_app, jsonify, request

from .errors import NotFoundError, ValidationError
from .extensions import db
from .models import Task
from .validators import ALLOWED_PRIORITY, ALLOWED_STATUS, validate_task_payload

api = Blueprint("api", __name__)

_SORT_OPTIONS = {
    "created_desc": lambda: Task.created_at.desc(),
    "created_asc": lambda: Task.created_at.asc(),
    "due_asc": lambda: Task.due_date.asc(),
    "due_desc": lambda: Task.due_date.desc(),
}


def _get_task_or_404(task_id):
    task = db.session.get(Task, task_id)
    if task is None:
        raise NotFoundError(f"Task {task_id} was not found.")
    return task


def _json_body():
    data = request.get_json(silent=True)
    if data is None:
        raise ValidationError({"body": "Request body must be valid JSON."})
    return data


def _limits():
    return {
        "max_title": current_app.config["MAX_TITLE_LENGTH"],
        "max_description": current_app.config["MAX_DESCRIPTION_LENGTH"],
    }


@api.get("/health")
def health():
    return jsonify({"status": "ok"})


@api.get("/tasks")
def list_tasks():
    query = Task.query

    status = request.args.get("status")
    priority = request.args.get("priority")
    search = request.args.get("search", "").strip()

    if status:
        if status not in ALLOWED_STATUS:
            raise ValidationError({"status": "Unknown status filter."})
        query = query.filter(Task.status == status)

    if priority:
        if priority not in ALLOWED_PRIORITY:
            raise ValidationError({"priority": "Unknown priority filter."})
        query = query.filter(Task.priority == priority)

    if search:
        query = query.filter(Task.title.ilike(f"%{search}%"))

    sort = request.args.get("sort", "created_desc")
    order_by = _SORT_OPTIONS.get(sort, _SORT_OPTIONS["created_desc"])()
    tasks = query.order_by(order_by).all()

    return jsonify([t.to_dict() for t in tasks])


@api.post("/tasks")
def create_task():
    data = _json_body()
    cleaned = validate_task_payload(data, **_limits())

    task = Task(**cleaned)
    db.session.add(task)
    db.session.commit()

    current_app.logger.info(
        "Task created: id=%s priority=%s status=%s", task.id, task.priority, task.status
    )
    return jsonify(task.to_dict()), 201


@api.get("/tasks/<int:task_id>")
def get_task(task_id):
    return jsonify(_get_task_or_404(task_id).to_dict())


@api.route("/tasks/<int:task_id>", methods=["PUT", "PATCH"])
def update_task(task_id):
    task = _get_task_or_404(task_id)
    data = _json_body()
    cleaned = validate_task_payload(data, partial=True, **_limits())

    previous_status = task.status
    for field, value in cleaned.items():
        setattr(task, field, value)
    db.session.commit()

    current_app.logger.info(
        "Task updated: id=%s fields=%s", task.id, sorted(cleaned)
    )
    if "status" in cleaned and cleaned["status"] != previous_status:
        current_app.logger.info(
            "Task status changed: id=%s %s -> %s",
            task.id,
            previous_status,
            task.status,
        )
    return jsonify(task.to_dict())


@api.delete("/tasks/<int:task_id>")
def delete_task(task_id):
    task = _get_task_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    current_app.logger.info("Task deleted: id=%s", task_id)
    return "", 204


@api.get("/dashboard")
def dashboard():
    return jsonify(
        {
            "total_tasks": Task.query.count(),
            "pending_tasks": Task.query.filter_by(status="pending").count(),
            "completed_tasks": Task.query.filter_by(status="completed").count(),
            "high_priority_tasks": Task.query.filter_by(priority="high").count(),
        }
    )

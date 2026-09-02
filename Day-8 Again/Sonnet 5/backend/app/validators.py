"""Input validation for task payloads.

``validate_task_payload`` returns a dict of cleaned values ready to assign to a
``Task``. It raises :class:`ValidationError` (HTTP 400) with a per-field
``details`` map when something is wrong.
"""

from datetime import date

from .errors import ValidationError

ALLOWED_STATUS = {"pending", "completed"}
ALLOWED_PRIORITY = {"low", "medium", "high"}


def _parse_due_date(value, errors):
    if value in (None, ""):
        return None
    if not isinstance(value, str):
        errors["due_date"] = "Must be a string in YYYY-MM-DD format."
        return None
    try:
        return date.fromisoformat(value.strip())
    except ValueError:
        errors["due_date"] = "Must be a valid date in YYYY-MM-DD format."
        return None


def validate_task_payload(data, *, partial=False, max_title=200, max_description=2000):
    """Validate and normalise a task payload.

    :param partial: when True (updates), only the supplied fields are checked and
        missing fields are left untouched.
    """
    if not isinstance(data, dict):
        raise ValidationError({"body": "Request body must be a JSON object."})

    errors = {}
    cleaned = {}

    # --- title (required on create) ---
    if "title" in data:
        title = data["title"]
        if not isinstance(title, str) or not title.strip():
            errors["title"] = "Title is required and must be a non-empty string."
        elif len(title.strip()) > max_title:
            errors["title"] = f"Title must be at most {max_title} characters."
        else:
            cleaned["title"] = title.strip()
    elif not partial:
        errors["title"] = "Title is required."

    # --- description (optional) ---
    if "description" in data:
        description = data["description"]
        if description is None:
            cleaned["description"] = ""
        elif not isinstance(description, str):
            errors["description"] = "Description must be a string."
        elif len(description) > max_description:
            errors["description"] = (
                f"Description must be at most {max_description} characters."
            )
        else:
            cleaned["description"] = description
    elif not partial:
        cleaned["description"] = ""

    # --- status ---
    if "status" in data:
        status = data["status"]
        if status not in ALLOWED_STATUS:
            errors["status"] = (
                f"Status must be one of: {', '.join(sorted(ALLOWED_STATUS))}."
            )
        else:
            cleaned["status"] = status
    elif not partial:
        cleaned["status"] = "pending"

    # --- priority ---
    if "priority" in data:
        priority = data["priority"]
        if priority not in ALLOWED_PRIORITY:
            errors["priority"] = (
                f"Priority must be one of: {', '.join(sorted(ALLOWED_PRIORITY))}."
            )
        else:
            cleaned["priority"] = priority
    elif not partial:
        cleaned["priority"] = "medium"

    # --- due_date (optional, nullable) ---
    if "due_date" in data:
        cleaned["due_date"] = _parse_due_date(data["due_date"], errors)
    elif not partial:
        cleaned["due_date"] = None

    if errors:
        raise ValidationError(errors)

    if partial and not cleaned:
        raise ValidationError({"body": "No valid fields supplied to update."})

    return cleaned

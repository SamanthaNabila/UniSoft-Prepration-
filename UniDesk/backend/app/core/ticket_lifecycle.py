from typing import Literal

TicketStatus = Literal["open", "in_progress", "resolved", "closed"]

ALLOWED_STATUS_TRANSITIONS: dict[TicketStatus, set[TicketStatus]] = {
    "open": {"in_progress"},
    "in_progress": {"resolved"},
    "resolved": {"closed", "in_progress"},
    "closed": {"open"},
}


def is_allowed_status_transition(
    current_status: TicketStatus, requested_status: TicketStatus
) -> bool:
    if current_status == requested_status:
        return True
    return requested_status in ALLOWED_STATUS_TRANSITIONS[current_status]
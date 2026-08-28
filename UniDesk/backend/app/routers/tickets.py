from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.core.ticket_lifecycle import is_allowed_status_transition
from app.models import Ticket, User
from app.schemas.ticket import (
    Priority,
    Status,
    TicketAssignmentUpdate,
    TicketCreate,
    TicketResponse,
    TicketStatsResponse,
    TicketStatusUpdate,
    TicketUpdate,
)

router = APIRouter(prefix="/api/v1/tickets", tags=["tickets"])

OWNERSHIP_DENIED_DETAIL = "Forbidden: You are only allowed to modify or delete your own tickets."


def get_ticket_or_404(ticket_id: int, db: Session) -> Ticket:
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found."
        )
    return ticket


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(
    payload: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Ticket:
    if current_user.role != "employee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Support Agents are not allowed to create tickets.",
        )

    ticket = Ticket(
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        created_by=current_user.id,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.get("/stats", response_model=TicketStatsResponse)
def get_ticket_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    counts = dict(
        db.query(Ticket.status, func.count(Ticket.id)).group_by(Ticket.status).all()
    )
    return {
        "total": sum(counts.values()),
        "open": counts.get("open", 0),
        "in_progress": counts.get("in_progress", 0),
        "resolved": counts.get("resolved", 0),
        "closed": counts.get("closed", 0),
    }


@router.get("", response_model=list[TicketResponse])
def list_tickets(
    status_filter: Optional[Status] = Query(None, alias="status"),
    priority_filter: Optional[Priority] = Query(None, alias="priority"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Ticket]:
    query = db.query(Ticket)
    if status_filter is not None:
        query = query.filter(Ticket.status == status_filter)
    if priority_filter is not None:
        query = query.filter(Ticket.priority == priority_filter)
    return query.order_by(Ticket.created_at.desc()).all()


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Ticket:
    return get_ticket_or_404(ticket_id, db)


@router.put("/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: int,
    payload: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Ticket:
    ticket = get_ticket_or_404(ticket_id, db)
    if current_user.role != "employee" or ticket.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=OWNERSHIP_DENIED_DETAIL
        )

    ticket.title = payload.title
    ticket.description = payload.description
    db.commit()
    db.refresh(ticket)
    return ticket


@router.patch("/{ticket_id}/status", response_model=TicketResponse)
def update_ticket_status(
    ticket_id: int,
    payload: TicketStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Ticket:
    if current_user.role != "support_agent":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Only Support Agents can update ticket status or priority.",
        )

    ticket = get_ticket_or_404(ticket_id, db)
    if payload.status is not None:
        if not is_allowed_status_transition(ticket.status, payload.status):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Invalid ticket status transition: {ticket.status} -> {payload.status}.",
            )
        ticket.status = payload.status
    if payload.priority is not None:
        ticket.priority = payload.priority
    db.commit()
    db.refresh(ticket)
    return ticket


@router.patch("/{ticket_id}/assignment", response_model=TicketResponse)
def update_ticket_assignment(
    ticket_id: int,
    payload: TicketAssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Ticket:
    if current_user.role != "support_agent":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Only Support Agents can assign tickets.",
        )

    ticket = get_ticket_or_404(ticket_id, db)
    if payload.assigned_to is None:
        if ticket.assigned_to != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only release your own ticket assignment.",
            )
        ticket.assigned_to = None
    else:
        assignee = db.get(User, payload.assigned_to)
        if assignee is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignee not found.",
            )
        if assignee.role != "support_agent":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tickets can only be assigned to Support Agents.",
            )
        ticket.assigned_to = assignee.id

    db.commit()
    db.refresh(ticket)
    return ticket


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    ticket = get_ticket_or_404(ticket_id, db)
    if current_user.role != "employee" or ticket.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=OWNERSHIP_DENIED_DETAIL
        )

    db.delete(ticket)
    db.commit()

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Comment, User
from app.routers.tickets import get_ticket_or_404
from app.schemas.comment import CommentCreate, CommentResponse

router = APIRouter(prefix="/api/v1/tickets", tags=["comments"])


@router.get("/{ticket_id}/comments", response_model=list[CommentResponse])
def list_comments(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Comment]:
    get_ticket_or_404(ticket_id, db)
    return (
        db.query(Comment)
        .filter(Comment.ticket_id == ticket_id)
        .order_by(Comment.created_at.asc())
        .all()
    )


@router.post(
    "/{ticket_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    ticket_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Comment:
    ticket = get_ticket_or_404(ticket_id, db)

    if current_user.role == "employee" and ticket.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You can only comment on tickets you created.",
        )

    comment = Comment(
        ticket_id=ticket_id, user_id=current_user.id, content=payload.content
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

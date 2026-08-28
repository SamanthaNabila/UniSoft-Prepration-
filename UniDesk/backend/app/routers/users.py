from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_support_agent
from app.models import User
from app.schemas.user import UserResponse

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/support-agents", response_model=list[UserResponse])
def list_support_agents(
    db: Session = Depends(get_db), current_user: User = Depends(require_support_agent)
) -> list[User]:
    return db.query(User).filter(User.role == "support_agent").order_by(User.name).all()
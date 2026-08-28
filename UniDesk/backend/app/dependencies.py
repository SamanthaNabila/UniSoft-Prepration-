from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database import get_db
from app.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        raise credentials_exception from exc

    user_id = payload.get("sub")
    if not isinstance(user_id, str) or not user_id.isdigit():
        raise credentials_exception

    # The database role is authoritative: a JWT issued before a role change
    # must not grant access based on its stale "role" claim.
    user = db.get(User, int(user_id))
    if user is None:
        raise credentials_exception

    return user


def require_role(role: str, detail: str):
    """Build a reusable dependency that only admits users with the given role.

    Centralizes employee-only / support-agent-only gating so each protected
    endpoint doesn't repeat its own role check, while still letting each
    call site keep its own error message.
    """

    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
        return current_user

    return dependency

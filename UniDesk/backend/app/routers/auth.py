from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.core.whitelist import MOCK_EMPLOYEE_WHITELIST
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas.user import Token, UserCreate, UserLogin, UserResponse

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

WHITELIST_DENIED_DETAIL = "Registration denied: Name or email not found in company records."


def _find_whitelist_entry(name: str, email: str) -> dict | None:
    normalized_name = name.strip().lower()
    normalized_email = email.strip().lower()
    for entry in MOCK_EMPLOYEE_WHITELIST:
        if (
            entry["name"].lower() == normalized_name
            and entry["email"].lower() == normalized_email
        ):
            return entry
    return None


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    entry = _find_whitelist_entry(payload.name, payload.email)
    if entry is None or entry["role"] != payload.role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=WHITELIST_DENIED_DETAIL
        )

    normalized_email = payload.email.strip().lower()
    existing_user = db.query(User).filter(User.email == normalized_email).first()
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered."
        )

    user = User(
        name=payload.name.strip(),
        email=normalized_email,
        password_hash=hash_password(payload.password),
        role=entry["role"],
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> Token:
    normalized_email = payload.email.strip().lower()
    user = db.query(User).filter(User.email == normalized_email).first()

    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user

from sqlalchemy import CheckConstraint, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "role IN ('employee', 'support_agent')", name="ck_users_role"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="employee")
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    tickets = relationship(
        "Ticket",
        foreign_keys="Ticket.created_by",
        back_populates="creator",
        cascade="all, delete-orphan",
    )
    assigned_tickets = relationship(
        "Ticket", foreign_keys="Ticket.assigned_to", back_populates="assignee"
    )
    comments = relationship(
        "Comment", back_populates="author", cascade="all, delete-orphan"
    )

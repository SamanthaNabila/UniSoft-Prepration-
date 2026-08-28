from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = (
        CheckConstraint(
            "status IN ('open', 'in_progress', 'resolved', 'closed')",
            name="ck_tickets_status",
        ),
        CheckConstraint(
            "priority IN ('low', 'medium', 'high')", name="ck_tickets_priority"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="open")
    priority = Column(String(10), nullable=False, default="medium")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    creator = relationship(
        "User", foreign_keys=[created_by], back_populates="tickets"
    )
    assignee = relationship(
        "User", foreign_keys=[assigned_to], back_populates="assigned_tickets"
    )
    comments = relationship(
        "Comment", back_populates="ticket", cascade="all, delete-orphan"
    )

    @property
    def created_by_name(self) -> str:
        return self.creator.name

    @property
    def assigned_to_name(self) -> str | None:
        return self.assignee.name if self.assignee else None

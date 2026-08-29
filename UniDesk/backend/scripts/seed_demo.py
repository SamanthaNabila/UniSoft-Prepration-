"""Seed a small, entirely fictional dataset for the UniDesk public demo.

Idempotent: if any users already exist it does nothing, so it is safe to run on
every container start. Run AFTER `alembic upgrade head`.

All identities below come from the mock employee whitelist in
`app/core/whitelist.py`, so demo visitors can also log in as them.
Shared demo password for every seeded account: Demo1234
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.security import hash_password  # noqa: E402
from app.database import SessionLocal  # noqa: E402
import app.models  # noqa: E402,F401  (registers mappers)
from app.models import Comment, Ticket, User  # noqa: E402

DEMO_PASSWORD = "Demo1234"  # meets the policy: >=8 chars, has a digit and an uppercase

DEMO_USERS = [
    ("Alice Johnson", "alice.johnson@unidesk.com", "employee"),
    ("Bob Martinez", "bob.martinez@unidesk.com", "employee"),
    ("Charlie Nguyen", "charlie.nguyen@unidesk.com", "support_agent"),
    ("Diana Osei", "diana.osei@unidesk.com", "support_agent"),
]


def main() -> None:
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            print("seed_demo: users already present — skipping.")
            return

        users: dict[str, User] = {}
        for name, email, role in DEMO_USERS:
            u = User(
                name=name,
                email=email,
                password_hash=hash_password(DEMO_PASSWORD),
                role=role,
            )
            db.add(u)
            users[email] = u
        db.flush()

        alice = users["alice.johnson@unidesk.com"].id
        bob = users["bob.martinez@unidesk.com"].id
        charlie = users["charlie.nguyen@unidesk.com"].id
        diana = users["diana.osei@unidesk.com"].id

        tickets = [
            Ticket(title="Cannot connect to the office VPN from home",
                   description="VPN client shows 'authentication failed' since this morning. Worked fine yesterday.",
                   status="open", priority="high", created_by=alice),
            Ticket(title="Request a second monitor for my desk",
                   description="Would like a 24-inch monitor for the new project. Desk 4B.",
                   status="open", priority="low", created_by=alice),
            Ticket(title="Outlook keeps asking for my password",
                   description="Every 10 minutes Outlook pops a credential prompt. Re-entering does not help.",
                   status="in_progress", priority="medium", created_by=bob, assigned_to=charlie),
            Ticket(title="Shared drive 'Marketing' is read-only",
                   description="I can open files on the Marketing share but cannot save changes back.",
                   status="in_progress", priority="medium", created_by=bob, assigned_to=diana),
            Ticket(title="Laptop battery drains in under an hour",
                   description="ThinkPad battery went from full to empty in about 45 minutes during a meeting.",
                   status="resolved", priority="high", created_by=alice, assigned_to=charlie),
            Ticket(title="Onboarding: set up accounts for new hire",
                   description="New hire starts Monday. Needs email, VPN and Jira access.",
                   status="closed", priority="medium", created_by=bob, assigned_to=diana),
        ]
        db.add_all(tickets)
        db.flush()

        db.add_all([
            Comment(ticket_id=tickets[2].id, user_id=charlie,
                    content="Thanks for the report — can you tell me which Outlook version you are on? Help > About."),
            Comment(ticket_id=tickets[2].id, user_id=bob,
                    content="It says Microsoft 365, Version 2404."),
            Comment(ticket_id=tickets[3].id, user_id=diana,
                    content="Looks like a permissions group change. I've requested write access for you, should apply within the hour."),
            Comment(ticket_id=tickets[4].id, user_id=charlie,
                    content="Replaced the battery and updated the power firmware. Please charge to 100% overnight and let me know."),
            Comment(ticket_id=tickets[4].id, user_id=alice,
                    content="Battery held up all day today. Thank you!"),
        ])

        db.commit()
        print(f"seed_demo: created {len(DEMO_USERS)} users, {len(tickets)} tickets, 5 comments.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

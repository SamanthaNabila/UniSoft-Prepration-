# UniDesk Agent Instructions

## Source of Truth

- Read `spec.md` before starting any task.
- Treat the existing implementation and tests as the current behavioral baseline.
- If `spec.md`, code, and tests disagree, report the conflict and ask before changing business behavior.
- Do not invent requirements, permissions, status rules, or data structures.

## Project Overview

UniDesk is an internal IT support ticketing system. Employees report IT problems; Support Agents manage resolution. The application has a FastAPI backend and a React frontend.

## Tech Stack

- Backend: Python, FastAPI, SQLAlchemy, PostgreSQL, Alembic, Pydantic.
- Authentication: JWT with `python-jose`; Bcrypt password hashing with `passlib`.
- Frontend: React, Vite, React Router, Axios, Tailwind CSS.
- Testing: pytest, pytest-cov, HTTPX/TestClient.



## Roles and Permissions

### Employee

Employees may:

- Register only with a matching approved whitelist name and email.
- Log in and view all tickets and dashboard statistics.
- Create tickets with a title, description, and initial priority.
- Edit and delete only tickets they created.
- Comment only on tickets they created.

Employees may not:

- Change ticket status.
- Change ticket priority through agent controls.
- Create tickets for other users.
- Edit, delete, or comment on another employee's ticket.
- Assign tickets.

### Support Agent

Support Agents may:

- Register only with a matching approved Support Agent whitelist entry.
- View all tickets, comments, and statistics.
- Change ticket status and priority.
- Comment on any ticket.
- Assign or reassign tickets to Support Agents.
- Release their own ticket assignment.

Support Agents may not create tickets or edit/delete ticket content as an employee owner.

Backend authorization is authoritative. Frontend restrictions are for navigation and user experience only.

## Business Rules

Valid ticket statuses:

- `open`
- `in_progress`
- `resolved`
- `closed`

Valid priorities:

- `low`
- `medium`
- `high`

Tickets are created with status `open`. The implemented lifecycle is:

- `open -> in_progress`
- `in_progress -> resolved`
- `resolved -> closed`
- `resolved -> in_progress` for reopening
- `closed -> open` for reopening

Same-status updates and priority-only updates remain valid. Invalid lifecycle transitions return `409 Conflict`. Do not alter these rules without approval.

Comments belong to a ticket and user. Employees can comment only on their own tickets; Support Agents can comment on any ticket.

The approved registration list is maintained in `backend/app/core/whitelist.py`. Matching is case-insensitive and trims surrounding whitespace. Do not add or remove whitelist users without an explicit request.

## Database Rules

The core database tables are `users`, `tickets`, and `comments`. Do not add a new table unless explicitly approved.

Assignment uses the existing `tickets` table with nullable `assigned_to` referencing `users.id`. Assignment deletion behavior is `ON DELETE SET NULL`. Only Support Agents may be assignment targets.

When changing models:

1. Add or update an Alembic migration.
2. Preserve existing data.
3. Configure explicit `foreign_keys` when two models have multiple foreign-key relationships.
4. Test the model with the SQLite test database.
5. Apply and verify the migration against the configured database with `alembic upgrade head` and `alembic current`.

Do not change the database schema, add tables, or make destructive migrations without approval.

## Backend Responsibilities

- Validate request data with Pydantic schemas.
- Enforce authentication, roles, ownership, and business rules in the API.
- Use existing SQLAlchemy session and router patterns.
- Return consistent `401`, `403`, `404`, `409`, and validation responses.
- Keep reusable business rules in focused helpers when they are used outside one endpoint.
- Treat the database user record as authoritative for the current role.
- Preserve existing API contracts unless a breaking change is requested.

## Frontend Responsibilities

- Use existing React views, components, `AuthContext`, and Axios service patterns.
- Keep UI role restrictions consistent with backend permissions.
- Keep client-only filtering client-side when the complete data is already loaded.
- Preserve loading, error, success, and empty states.
- Do not duplicate authentication or API behavior in individual views.
- Do not change backend behavior for a frontend-only task.
- Use accessible labels and controls and preserve existing Tailwind conventions.

## Security Requirements

- Never store or log plain-text passwords, JWTs, authorization headers, or secrets.
- Do not use a fallback or placeholder JWT secret.
- Require a configured secret with at least 32 characters.
- Reject malformed, expired, incorrectly signed, missing-subject, non-integer-subject, and nonexistent-user JWTs with consistent `401 Unauthorized` behavior.
- Do not allow malformed claims to raise uncaught conversion or database errors.
- Centralize reusable employee and Support Agent authorization dependencies.
- Do not trust a stale JWT role claim over the database user role.
- Frontend `401` responses must clear the session without automatic retry loops or redirect loops.
- Do not expose sensitive details in error responses.

## Required Inspection Before Editing

Before making a change:

1. Read the relevant section of `spec.md`.
2. Inspect the file that directly controls the behavior.
3. Inspect one nearby caller, schema, model, or component as applicable.
4. Inspect related tests before changing backend behavior.
5. Check whether the requested behavior already exists.
6. Identify whether the change is frontend-only, backend-only, or cross-stack.
7. State any ambiguity that affects permissions, workflow, schema, or security.

Prefer the smallest change that satisfies the request. Add a new helper, component, test module, or migration only when the existing ownership boundary cannot reasonably contain the behavior.

## Approval Required Before Changing

Ask for approval before changing:

- Employee or Support Agent permissions.
- Ticket status lifecycle or comment rules.
- Authentication storage, JWT format, token expiry, or secret policy.
- Public API paths, request/response contracts, or error messages.
- Database tables, columns, relationships, or destructive migration behavior.
- Whitelist entries, existing user data, or environment files.
- Out-of-scope features listed in `spec.md`.
- Existing user changes or unrelated files.

## Testing and Validation

Run commands from the correct project directory.

Backend from `backend/`:

```powershell
.\venv\Scripts\activate
pytest -q
pytest --cov=app --cov-report=term-missing --cov-fail-under=70
```

Frontend from `frontend/`:

```powershell
npm install
npm run build
npm run lint
```

After a backend behavior change, run the focused test first, then the full backend suite. After a frontend change, run the frontend build and relevant lint check. Report warnings separately from failures.

Tests should cover successful behavior, invalid input, missing resources, authentication failures, role restrictions, ownership restrictions, and new edge cases.



## Final Response

Always report:

- What changed.
- Every file created or modified and why.
- Tests, builds, migrations, or checks run and their results.
- Assumptions and unresolved ambiguities.
- Any required manual steps, such as applying a migration or configuring `SECRET_KEY`.

Do not claim a command passed unless it was actually run. Do not commit or push changes unless explicitly requested.

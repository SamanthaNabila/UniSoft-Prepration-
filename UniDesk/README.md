# UniDesk

**An internal IT support ticketing system** — built as a full-stack demonstration project (FastAPI + PostgreSQL + React) with authentication, role-based permissions, and automated testing.

---

## 1. What is UniDesk? (For everyone)

Inside most companies, IT problems get reported in messy, informal ways — a Slack message here, a hallway conversation there, an email that gets buried. Nobody can tell what's been fixed, what's still broken, or who's supposed to be looking at it.

**UniDesk fixes that** by giving a company two simple things:

- A place for **employees** to log a problem ("my laptop won't boot") and track it until it's resolved.
- A place for **support agents** to see every open problem, pick it up, update its status, and talk to the employee about it — all in one shared system instead of scattered chats.

It's a small, focused ticketing system — not a general project-management tool. Every ticket has one clear owner, one clear status, and a visible conversation thread.

---

## 2. Core Features & User Roles

UniDesk has exactly two kinds of users, and each is deliberately limited to a specific job:

| Capability                                 |       👤 Employee       | 🛠️ Support Agent  |
| ------------------------------------------ | :---------------------: | :---------------: |
| Register (must be pre-approved, see below) |           ✅            |        ✅         |
| View all tickets & dashboard stats         |           ✅            |        ✅         |
| Create a new ticket                        |           ✅            |        ❌         |
| Edit / delete a ticket                     | ✅ _(own tickets only)_ |        ❌         |
| Change a ticket's status or priority       |           ❌            | ✅ _(any ticket)_ |
| Comment on a ticket                        | ✅ _(own tickets only)_ | ✅ _(any ticket)_ |

**Why the split?** Employees _report_ problems; agents _resolve_ them. An employee can't quietly mark their own ticket "resolved" and an agent can't create tickets on someone else's behalf — that separation is what makes the ticket history trustworthy.

Beyond that role split, UniDesk includes:

- **A live dashboard** — total/open/in-progress/resolved/closed counts, plus one-click filters.
- **Colour-coded priority badges** (low / medium / high) so urgent issues stand out at a glance.
- **A full comment thread** per ticket, showing who said what and when, with a role badge next to each name.
- **Secure login** — passwords are never stored in plain text, and every action is authenticated.

---

## 3. Tech Stack

| Layer            | Technology                                               | Why                                                                      |
| ---------------- | -------------------------------------------------------- | ------------------------------------------------------------------------ |
| Backend API      | **FastAPI** (Python)                                     | Fast, type-safe, auto-generates interactive API docs                     |
| Database         | **PostgreSQL**                                           | Reliable relational database for structured ticket data                  |
| ORM & Migrations | **SQLAlchemy** + **Alembic**                             | Defines the data model in Python; tracks schema changes over time        |
| Data validation  | **Pydantic**                                             | Rejects malformed requests before they touch the database                |
| Authentication   | **JWT** (via `python-jose`) + **Bcrypt** (via `passlib`) | Stateless, secure login sessions; passwords are hashed, never stored raw |
| Frontend         | **React** (via **Vite**)                                 | Fast dev experience, component-based UI                                  |
| Styling          | **Tailwind CSS**                                         | Utility-first styling for a consistent, responsive design                |
| Routing          | **React Router**                                         | Client-side navigation with protected/role-gated routes                  |
| HTTP client      | **Axios**                                                | Talks to the API, automatically attaches the JWT to every request        |
| Testing          | **pytest** + **pytest-cov** + **httpx**                  | Automated backend test suite with coverage reporting                     |

---

## 4. How to Run Locally

This section assumes **no prior setup** — follow it top to bottom.

### 4.1 Prerequisites

Install these first if you don't already have them:

| Tool                                    | Check if installed | Download                                               |
| --------------------------------------- | ------------------ | ------------------------------------------------------ |
| **Python 3.10+**                        | `python --version` | [python.org](https://www.python.org/downloads/)        |
| **Node.js 18+** (includes npm)          | `node --version`   | [nodejs.org](https://nodejs.org/)                      |
| **Git**                                 | `git --version`    | [git-scm.com](https://git-scm.com/)                    |
| **PostgreSQL** (server running locally) | `psql --version`   | [postgresql.org](https://www.postgresql.org/download/) |

### 4.2 Get the code

```bash
git clone <this-repository-url>
cd UniDesk
```

### 4.3 Backend setup (FastAPI)

```bash
cd backend

# Create an isolated Python environment
python -m venv venv

# Activate it
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux

# Install all backend dependencies
pip install -r requirements.txt
```

**Set up the database.** Create a PostgreSQL database and a user for the app (run this once, using `psql` or any Postgres GUI):

```sql
CREATE ROLE unidesk_user LOGIN PASSWORD 'your_password_here';
CREATE DATABASE unidesk OWNER unidesk_user;
```

**Configure environment variables.** Copy the example file and fill in your real values:

```bash
cp .env.example .env         # macOS / Linux / Git Bash
copy .env.example .env       # Windows Command Prompt or PowerShell
```

Then edit `backend/.env`:

```
DATABASE_URL=postgresql://unidesk_user:your_password_here@localhost:5432/unidesk
SECRET_KEY=<generate a random string — see note below>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

> To generate a strong `SECRET_KEY`, run: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

**Apply the database schema** (creates the `users`, `tickets`, and `comments` tables):

```bash
alembic upgrade head
```

**Start the API server:**

```bash
uvicorn app.main:app --reload --port 8000
```

The API is now running at `http://localhost:8000`. Interactive API docs (Swagger UI) are auto-generated at `http://localhost:8000/docs`.

### 4.4 Frontend setup (React + Vite)

Open a **new terminal** (leave the backend running) and run:

```bash
cd frontend
npm install
npm run dev
```

The app will be running at `http://localhost:5173` — open that in your browser.

> The frontend is pre-configured to talk to the backend at `http://localhost:8000/api/v1`. If you change the backend port, update `baseURL` in `frontend/src/services/api.js`.

---

## 5. Test Accounts (Whitelisted Registration)

UniDesk doesn't allow just anyone to sign up — registration is checked against a pre-approved company list (`backend/app/core/whitelist.py`), simulating an HR-managed employee directory. This is intentional: it demonstrates the "invite-only" registration flow described in the spec.

**Important:** these are _not_ ready-made login accounts. No user rows exist in the database until someone registers. To try the app, **register** using one of the exact name + email pairs below (name/email matching is case-insensitive), choosing **your own password** and matching the listed role:

| Name           | Company Email                | Role to select at signup |
| -------------- | ---------------------------- | ------------------------ |
| Alice Johnson  | `alice.johnson@unidesk.com`  | Employee                 |
| Bob Martinez   | `bob.martinez@unidesk.com`   | Employee                 |
| Charlie Nguyen | `charlie.nguyen@unidesk.com` | Support Agent            |
| Diana Osei     | `diana.osei@unidesk.com`     | Support Agent            |

Password requirements: **at least 8 characters, with at least one number and one uppercase letter** (e.g. `Passw0rd!`).

Any name/email combination _not_ on this list will be rejected at registration with a `400 Bad Request` — that's the whitelist doing its job.

**Suggested test flow:** register as Alice (Employee) and Charlie (Support Agent) in two separate browser sessions (or one normal + one incognito window) to see both sides of the workflow — Alice creates a ticket, Charlie picks it up and resolves it.

---

## 6. Testing & Quality

The backend ships with an automated test suite covering authentication, whitelist enforcement, role-based access control, and comment permissions.

Run the full suite with coverage reporting:

```bash
cd backend
source venv/Scripts/activate    # or venv\Scripts\activate on Windows
pytest --cov=app --cov-report=term-missing --cov-fail-under=70
```

- **38 tests** across `tests/test_auth.py`, `tests/test_rbac.py`, and `tests/test_comments.py`
- Enforced minimum coverage: **70%** (current: ~95%)
- Tests run against an isolated in-memory database, so they never touch your real PostgreSQL data

---

## 7. Project Structure
11111111111
```
UniDesk/
├── backend/            # FastAPI application
│   ├── app/
│   │   ├── core/       # config, security (JWT/bcrypt), whitelist
│   │   ├── models/     # SQLAlchemy tables (User, Ticket, Comment)
│   │   ├── schemas/    # Pydantic request/response shapes
│   │   ├── routers/    # API endpoints (auth, tickets, comments)
│   │   └── main.py     # app entrypoint
│   ├── alembic/        # database migrations
│   └── tests/          # pytest suite
└── frontend/            # React (Vite) application
    └── src/
        ├── components/  # reusable UI pieces
        ├── views/       # pages (Auth, Dashboard, Ticket Detail, etc.)
        ├── context/     # auth session state
        └── services/    # API client
```

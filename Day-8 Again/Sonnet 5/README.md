# Task Manager

A small full-stack task management application. Create, view, edit, complete,
filter and delete tasks through a REST API and a lightweight web UI, backed by
SQLite.

It is intentionally small and easy to experiment with, but organised like a real
project: separate backend, frontend, database, tests and configuration.

## Features

- **Task CRUD** — create, list, view one, edit, delete.
- **Status toggle** — mark a task `pending` or `completed`.
- **Task fields** — `id`, `title`, `description`, `status`, `priority`,
  `due_date`, `created_at`, `updated_at`.
- **Filtering & search** — by status, by priority, by title substring
  (case-insensitive), and any combination of these; plus sorting by creation or
  due date.
- **Dashboard** — total, pending, completed and high-priority task counts.
- **Validation** — title required, description length capped, `priority` limited
  to `low|medium|high`, `status` limited to `pending|completed`, `due_date` must
  be a valid `YYYY-MM-DD` date.
- **Error handling** — consistent JSON errors (`{"error": ..., "details": ...}`)
  for invalid input, missing tasks, bad IDs, unknown routes, wrong methods and
  database/unexpected failures. Raw exceptions are never returned to the client.
- **Logging** — task creation, updates, deletions, status changes and errors are
  logged to stdout and a rotating file (`logs/app.log`). Only operational data
  (ids, actions, statuses) is logged — never full task content.

## Technology stack

| Layer     | Choice                                              |
|-----------|----------------------------------------------------|
| Backend   | Python 3, Flask, Flask-SQLAlchemy                   |
| Database  | SQLite (via SQLAlchemy ORM)                         |
| Frontend  | Vanilla HTML / CSS / JavaScript (no build step)     |
| Tests     | pytest                                              |

### Why these choices

- **Flask + SQLAlchemy + SQLite** keeps a single-table CRUD app small and
  readable with zero infrastructure to set up.
- **Application factory pattern** lets the test suite build an isolated app with
  its own temporary database per test.
- **`db.create_all()` at startup** handles schema setup. For one table a
  migration tool (e.g. Alembic) would be over-engineering; add one if the schema
  starts evolving.
- **Vanilla frontend served as static files by Flask** — one process, one
  command to run, no bundler.

## Project structure

```
.
├── backend/
│   ├── app/
│   │   ├── __init__.py       # application factory
│   │   ├── extensions.py     # SQLAlchemy instance
│   │   ├── models.py         # Task model + to_dict()
│   │   ├── validators.py     # payload validation
│   │   ├── routes.py         # REST API blueprint (/api/...)
│   │   ├── errors.py         # custom errors + handlers
│   │   └── logging_config.py # logging setup
│   ├── config.py             # dev / testing / production config
│   └── wsgi.py               # entry point (python backend/wsgi.py)
├── frontend/
│   ├── index.html            # dashboard + list + create/edit dialog
│   ├── styles.css
│   └── app.js                # fetch calls + rendering
├── tests/
│   ├── conftest.py           # app/client fixtures (temp SQLite per test)
│   ├── test_crud.py
│   ├── test_validation.py
│   └── test_filters.py
├── data/                     # SQLite file created here at runtime (gitignored)
├── logs/                     # app.log created here at runtime (gitignored)
├── requirements.txt
├── pytest.ini
└── README.md
```

## API

Base path: `/api`. All request/response bodies are JSON.

| Method            | Path                     | Description                        | Success |
|-------------------|--------------------------|-----------------------------------|---------|
| `GET`             | `/api/health`            | Health check                      | 200     |
| `GET`             | `/api/tasks`             | List tasks (see query params)     | 200     |
| `POST`            | `/api/tasks`             | Create a task                     | 201     |
| `GET`             | `/api/tasks/<id>`        | Get one task                      | 200     |
| `PUT` / `PATCH`   | `/api/tasks/<id>`        | Update task (partial allowed)     | 200     |
| `DELETE`          | `/api/tasks/<id>`        | Delete a task                     | 204     |
| `GET`             | `/api/dashboard`         | Aggregate counts                  | 200     |

**List query parameters** (combinable): `status=pending|completed`,
`priority=low|medium|high`, `search=<title substring>`,
`sort=created_desc|created_asc|due_asc|due_desc`.

**Error codes**: `400` invalid input / malformed JSON / bad filter value,
`404` missing task or unknown route, `405` wrong method, `500` database or
unexpected error.

Example:

```bash
curl -X POST http://127.0.0.1:5000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Write report", "priority": "high", "due_date": "2026-09-15"}'
```

## Setup

Requires Python 3.10+.

```bash
# from the project root
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## Running the application

```bash
python backend/wsgi.py
```

Then open <http://127.0.0.1:5000/> in a browser. The SQLite database is created
automatically at `data/tasks.db` on first run.

Optional environment variables:

- `PORT` — HTTP port (default `5000`)
- `FLASK_ENV` — `development` (default) / `testing` / `production`
- `DATABASE_URL` — override the SQLAlchemy database URI
- `LOG_LEVEL` — e.g. `DEBUG`, `INFO` (default), `WARNING`

## Running the tests

```bash
python -m pytest
```

The suite covers task creation, updating, deletion, invalid input, missing
tasks, and filtering/search/dashboard. Each test runs against its own temporary
SQLite database and does not touch `data/tasks.db`.

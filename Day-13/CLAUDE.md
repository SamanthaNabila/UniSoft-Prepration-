# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

- Install dependencies: `npm install`
- Run the server: `npm start` (or `npm run dev` for auto-reload via nodemon)
- Create/update the database schema: run `schema.sql` against Postgres, e.g. `psql -U postgres -d todo_db -f schema.sql` (it's idempotent — safe to re-run)
- No test suite, lint step, or build step exists.

Configuration is read from environment variables (`PORT`, `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`) via `dotenv`; copy `.env.example` to `.env` and adjust before running. Without a `.env` file, `db.js` falls back to local defaults.

## Architecture

Full-stack Todo app: Express REST API backed by Postgres (via `pg`), serving a static vanilla-JS frontend.

- `db.js` — exports a single shared `pg.Pool`, configured from env vars with local-dev fallback defaults. All queries go through this pool.
- `server.js` — the entire API: `GET/POST/PUT/DELETE /api/todos[/:id]`, plus `express.static` serving `public/`. Route handlers validate input inline (non-empty title) and query the pool directly — there is no separate route/controller/model layering.
  - `PUT /api/todos/:id` does a read-then-write (`SELECT` to fetch the current row, then `UPDATE` with fields merged over it), so partial updates only need to send the field(s) they're changing (`title` and/or `completed`).
- `schema.sql` — defines the `todos` table (`id`, `title`, `completed`, `created_at`). Run manually against Postgres; there is no migration tool.
- `public/index.html` + `public/app.js` — static frontend, no build step or framework. `app.js` calls the REST API with `fetch` and re-renders the full list on every mutation (add/toggle/delete) rather than patching the DOM incrementally.

## Code Conventions & Lab 8 Rules

1. Use arrow functions for all Express route handlers.
2. Add JSDoc comments above every API endpoint in `server.js`.
3. Use Express middleware for input validation instead of helper functions.
4. Do NOT add any unrequested features (no extra UI badges, no idempotent SQL scripts).
5. All error responses MUST strictly return JSON in the format: `{"error": "Message"}`.

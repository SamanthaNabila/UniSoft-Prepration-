# UniDesk Backend — Adversarial Attack Test Log

Record of the four adversarial test passes run directly against the UniDesk
backend API. Each section describes **what was done**, **how it was done**, and
**what was found**.

- **Target:** `backend/app` (FastAPI + SQLAlchemy + Postgres)
- **Test rig:** real `uvicorn app.main:app` on `127.0.0.1:8799`, backed by the
  real Postgres DB (`postgresql://unidesk_user:***@localhost:5432/unidesk`),
  driven with Python + `httpx` / `psycopg2`. No frontend involved.
- **Ground rule:** application code was **never modified**. Every row created by a
  test was deleted afterward; the DB was verified back at its baseline
  (8 users / 6 tickets / 8 comments) after each run.
- **Auth used by the tests:**
  - Employee token — registered the whitelisted user `samantha@unidesk.com`
    with a known password, then logged in.
  - Support-agent token — minted a JWT with the real `SECRET_KEY` from
    `backend/.env` for an existing `support_agent` row (user id 2, Diana Osei).
    Valid because `get_current_user` re-checks the role from the DB.

---

## Attack 1 — Huge-input attack test

### What the agent did
1. Read every router and schema to map user-controlled inputs and their
   validation limits vs. the backing DB columns.
2. Started the real server against real Postgres, created an employee token and
   a baseline ticket.
3. Fired progressively larger payloads at each input and recorded status code,
   response time, and whether a row was persisted:
   - `description` on `POST /api/v1/tickets` and `PUT /api/v1/tickets/{id}` at
     10 KB → 100 KB → 1 MB → 5 MB → 20 MB.
   - Raw JSON body (extra junk field) at 1 MB → 10 MB → 50 MB → 100 MB.
   - Deeply nested JSON object, depth 200 → 20 000 (plus a focused sweep
     200 → 3 000 to find the exact failure window).
   - Huge top-level JSON array (2 000 000 elements).
   - JSON object with 1 000 000 keys.
   - Huge `title` (5 MB) and huge comment `content` (10 MB).
   - Oversized `password` (~5 KB, above passlib's 4096-byte limit) on
     `login` and `register`.
   - Huge integer path param (`GET /api/v1/tickets/<400 digits>`) and huge
     `assigned_to` integer on the assignment PATCH.
   - Huge query string (`?status=<100 KB>`) and huge `Authorization` header
     (~5 MB bearer token).
4. Pulled the server log to capture the exact exception for every `500`.
5. Deleted all created rows, confirmed the DB baseline, stopped the server.

### What was found
| # | Attack | Expected | Actual | PASS/FAIL | Bug |
|---|---|---|---|---|---|
| 1 | `description` 10 KB→20 MB on `POST /api/v1/tickets` (`create_ticket` / `schemas/ticket.py:_TicketTextFields.validate_description`) | Reject `413`/`422` or enforce a max length | `201`; stored in full (20 MB row, 1.76 s), whole blob echoed back; no cap | **FAIL** | Yes — no maximum length on `description` |
| 2 | `description` 10 MB on `PUT /api/v1/tickets/{id}` (`update_ticket`) | Reject `413`/`422` or cap | `200`; 10 MB stored, 1.17 s | **FAIL** | Yes — same missing cap |
| 3 | ~100 MB raw JSON body on `POST /api/v1/tickets` (Starlette buffering; no size middleware in `app/main.py`) | `413` before full buffering | `201` in 1.75 s; whole body buffered in RAM | **FAIL** | Yes — no request body size limit |
| 4 | Oversized `password` (~5 KB) on `POST /api/v1/auth/login` (`login` → `verify_password`) | `401` / `422` | **`500 Internal Server Error`** — `passlib.exc.PasswordSizeError` uncaught | **FAIL** | Yes — unhandled exception on an unauthenticated endpoint |
| 5 | Oversized `password` (~5 KB) on `POST /api/v1/auth/register` (`register` → `hash_password`) | `422` / handled | **`500 Internal Server Error`** — `PasswordSizeError` uncaught | **FAIL** | Yes — same |
| 6 | Nested JSON body, depth ~1000–2900, `POST /api/v1/tickets` (validation-error handler → `jsonable_encoder`) | `422` | **`500 Internal Server Error`** — `RecursionError` in `fastapi/encoders.py` while serializing the echoed nested `input` | **FAIL** | Yes — `500` instead of `422` in the 1000–2900 depth window |
| 7 | Top-level JSON array, 2 000 000 elements, `POST /api/v1/tickets` | Fast `422` | `422` but after **5.95 s** worker-blocking | **PARTIAL** | Minor — no parse/size guard, slow-request DoS vector |
| 8 | JSON object with 1 000 000 keys, `POST /api/v1/tickets` | Handled quickly | `201` in ~2 s (extras ignored) | **PASS** | No (mild CPU cost) |
| 9 | Huge `title` (5 MB) on `POST /api/v1/tickets` | `422` | `422` in 0.78 s | **PASS** | No |
| 10 | Huge comment `content` (10 MB) on `POST /api/v1/tickets/{id}/comments` (`validate_content`) | `422` | `422` in 0.89 s | **PASS** | No |
| 11 | Huge integer path param (400 digits) on `GET /api/v1/tickets/{ticket_id}` (`get_ticket` → `db.get`) | `404`/`422` | `404` in 0.61 s | **PASS** | No |
| 12 | Huge integer `assigned_to` (40 digits) on `PATCH /api/v1/tickets/{id}/assignment` | `404`/`422` | `404` in 0.68 s | **PASS** | No |
| 13 | Huge query param `?status=` (100 KB) on `GET /api/v1/tickets` | `414`/`422` | Rejected (URI too long) | **PASS** | No |
| 14 | Huge `Authorization` header (~5 MB) on `GET /api/v1/auth/me` | `401`/`431` | Connection closed by server (header cap) | **PASS** | No |

**Cross-cutting:** the only field with no upper bound is `description`
(`schemas/ticket.py` checks `len < 10` minimum, no maximum; column is `TEXT`).
Combined with `list_tickets` having **no pagination** (`.all()` in
`routers/tickets.py:84`), a `GET /api/v1/tickets` would return every oversized
description at once. There is no request-body size limit anywhere.

---

## Attack 2 — Two-click / duplicate-request attack test

### What the agent did
1. Listed every state-changing action and its handler; noted which have a
   dedup / concurrency guard (only `DELETE` does).
2. Built two firing helpers:
   - **sequential** — N identical requests back-to-back on one connection
     (a fast double-click).
   - **parallel** — N identical requests from a thread pool (a race).
3. Ran, for each mutating endpoint, a double-click and a burst, then queried
   Postgres directly to count the rows actually created / the final state:
   - `POST /api/v1/tickets` — 2 sequential, then 5 parallel identical creates.
   - `POST /api/v1/tickets/{id}/comments` — 2 sequential + 4 parallel identical.
   - `POST /api/v1/auth/register` — 4 concurrent identical (unique email).
   - `DELETE /api/v1/tickets/{id}` — 2 sequential, then 4 parallel on one id.
   - `PATCH /api/v1/tickets/{id}/status` — 2 sequential + 6 parallel same
     transition.
   - `PATCH /api/v1/tickets/{id}/assignment` — 2 sequential same agent, then a
     concurrent claim by two different agents.
   - `PUT /api/v1/tickets/{id}` — 2 sequential identical edits.
4. Captured the `register` race traceback from the server log.
5. Deleted every created row/user, confirmed the DB baseline, stopped the server.

### What was found
| Attack | Expected | Actual | HTTP | PASS/FAIL | Bug |
|---|---|---|---|---|---|
| Double-click **create ticket** (2 sequential) — `POST /api/v1/tickets` | 1 ticket, or 2nd deduped / `409` | **2 identical ticket rows** created | `201, 201` | **FAIL** | Yes — no idempotency/dedup on ticket creation |
| **Concurrent create ticket** (5 parallel) — `POST /api/v1/tickets` | ≤ 1 ticket | **5 identical ticket rows** created | `201 ×5` | **FAIL** | Yes — race amplifies it |
| Double-click + concurrent **add comment** (6 identical) — `POST /api/v1/tickets/{id}/comments` | Deduped / 1 comment | **6 identical comment rows** | `201 ×6` | **FAIL** | Yes — no dedup, comment-flood |
| Double-submit **registration** (4 concurrent, same email) — `POST /api/v1/auth/register` | 1 user; extras → `409` | 1 user row, extras → **unhandled `IntegrityError`** (`UniqueViolation`) | `201, 500, 500, 500` | **FAIL** | Yes — TOCTOU between the email check (`auth.py:37`) and `commit` (`auth.py:50`); returns `500` |
| Double-click **status change** `open→in_progress` (2 sequential) — `PATCH /api/v1/tickets/{id}/status` | 2nd → `409` (already in state) | 2nd **silently succeeds** again (self-transition allowed, `core/ticket_lifecycle.py:16`) | `200, 200` | **FAIL** | Yes — non-idempotent repeat accepted |
| **Concurrent status change** (6 parallel same transition) — `PATCH /api/v1/tickets/{id}/status` | 1 success, rest `409`; locking prevents lost updates | **all 6 commit** the write; no row lock / version check | `200 ×6` | **FAIL** | Yes — race / lost-update exposure for conflicting transitions |
| Double-click **assign** + **concurrent claim by 2 agents** — `PATCH /api/v1/tickets/{id}/assignment` | Concurrent claim → one wins, other `409` | **Both agents get `200`**; `assigned_to` = last writer; the other agent believes they own it | `200 ×4` | **FAIL** | Yes — last-write-wins, no "claim if unassigned" guard |
| Double-click **delete ticket** (2 sequential) — `DELETE /api/v1/tickets/{id}` | 1st `204`, 2nd `404` | 1st `204`, 2nd `404` | `204, 404` | **PASS** | No |
| **Concurrent delete** (4 parallel) — `DELETE /api/v1/tickets/{id}` | One `204`, rest `404`, no `500` | Exactly one `204`, three `404` | `404, 404, 404, 204` | **PASS** | No |
| Double-click **edit ticket** (2 sequential identical PUTs) — `PUT /api/v1/tickets/{id}` | Both `200`, same final state | Both `200`, identical state (`updated_at` bumped twice) | `200, 200` | **PASS** | No |

**Cross-cutting:** no idempotency-key support, no request de-duplication, no
`SELECT … FOR UPDATE` / optimistic-version column anywhere in the ticket
workflow. Every mutating endpoint except `DELETE` and `PUT` is exploitable by a
fast double-click.

---

## Attack 3 — Missing-authentication attack test

### What the agent did
1. Enumerated the 11 protected routes (everything under `get_current_user` /
   `require_role`) and the 3 public ones (`/health`, `register`, `login`).
2. Sent requests with **no credentials** and with **broken credentials**, and
   checked for any `2xx`/`3xx`-with-data (which would be a bypass):
   - No `Authorization` header on all 11 protected endpoints (GET and mutating).
   - Header variants: empty, `Bearer` with no token, `Basic …`, `Token …`,
     lowercase `bearer`, `Bearer null`, `Bearer undefined`, `Bearer <garbage>`,
     a `Cookie:` instead of a header, and spoofed `X-User-Id` / `X-User-Role`.
   - JWT signed with a **wrong secret**.
   - **`alg:none`** unsigned JWT (algorithm-confusion).
   - **Expired** but correctly-signed JWT.
   - Correctly-signed JWT with a bad `sub` (non-existent id, missing,
     non-numeric, SQL-ish string).
   - Path tricks: trailing slash, double slash, wrong case.
   - Checked whether `/docs`, `/redoc`, `/openapi.json` are reachable
     unauthenticated.
3. Confirmed nothing was created; stopped the server.

### What was found
| Attack | Expected | Actual | HTTP | PASS/FAIL | Weakness |
|---|---|---|---|---|---|
| All 11 protected endpoints with **no `Authorization` header** | `401`, no data, no state change | `401 "Not authenticated"` on every endpoint; nothing created/modified/deleted | `401 ×11` | **PASS** | None |
| **Empty / malformed / wrong-scheme** `Authorization` (Basic, Token, lowercase bearer, `Bearer null`, `Bearer undefined`, garbage) on `GET /api/v1/tickets` | `401` for all | `401` for all | `401` | **PASS** | None |
| **Cookie / session** instead of header | `401` (no cookie auth) | `401 "Not authenticated"` | `401` | **PASS** | None |
| **Spoofed identity headers** `X-User-Id` / `X-User-Role` | ignored → `401` | `401 "Not authenticated"` | `401` | **PASS** | None |
| JWT signed with **wrong secret** → `GET /api/v1/auth/me` | `401` bad signature | `401 "Could not validate credentials"` | `401` | **PASS** | None |
| **`alg:none`** unsigned JWT → `/auth/me` and `POST /comments` | `401` both | `401` both | `401, 401` | **PASS** | None |
| **Expired** JWT (valid signature) → `GET /api/v1/auth/me` | `401` | `401` | `401` | **PASS** | None |
| Correctly-signed JWT with **missing / non-existent / non-numeric `sub`** | `401` for all | `401` for all (DB identity re-check in `get_current_user`) | `401 ×4` | **PASS** | None |
| **Trailing-slash / double-slash / case** path variants, unauthenticated | `401` or `404`, never `200` | `401` (slash variants), `404` (wrong case) | `401 / 404` | **PASS** | None |
| `GET /docs`, `/redoc`, `/openapi.json` **without auth** | (informational) public by FastAPI default | `200` — full API schema readable anonymously | `200` | **PASS** (not a bypass) | Informational only — no data/actions exposed; disable docs in prod if undesired |

**Conclusion:** authentication is correctly and consistently enforced on every
state-changing and data endpoint. **No missing-authentication vulnerability
found.** The only note is the standard FastAPI behavior of serving `/docs` and
`/openapi.json` unauthenticated.

---

## Attack 4 — Empty-input attack test

### What the agent did
1. From the schemas, listed every input and picked the relevant empty forms
   for each: `""`, `" "`, `"\t\n"`, `0`, `null`, `[]`, `{}`, empty request
   body, empty query value.
2. Started the server, created an employee token, an agent token, and a
   baseline ticket.
3. Fired ~70 empty-input probes and recorded the status code and message; after
   the create/comment probes, queried Postgres to confirm **no rows** were
   created:
   - `register` — `{}`, all-`""`, blank `name`, blank `email`, `password=""`
     and 8 spaces, `role=""`, all-`null`, `name=0`, `name=[]`/`email={}`.
   - `login` — `{}`, `email=""`/`" "`, `null`, and valid email + `password=""`/`" "`.
   - `POST /tickets` — `{}`, `title`/`description` = `""` / `"     "` / `"\t\n"`
     / `"0"` / `null` / `0` / `[]` / `{}`; `priority=""` / `null`; raw bodies
     `null` / `[]` / `""` / `{}` / truly empty.
   - `PUT /tickets/{id}` — same empty fields; path id `0`, `" "`, empty segment.
   - `PATCH .../status` — `{}` (empty object), `{status:null,priority:null}`,
     `status`/`priority` = `""` / `" "` / `[]` / `{}`.
   - `PATCH .../assignment` — `{}`, `{"assigned_to": null}`, `0`, `""`, `" "`,
     `[]`, `false`, `"0"`.
   - `POST .../comments` — `{}`, `content` = `""` / `"   "` / `"\n\t "` /
     `null` / `0` / `[]` / raw `{}`.
   - `GET /tickets` — `?status=`, `?priority=`, `?assigned_to=`, `?status=&priority=`.
   - `GET /tickets/{id}` — id `0`, `-1`, empty.
4. Grepped the server log for any `500` (found none), deleted the baseline
   ticket and user, confirmed the DB baseline, stopped the server.

### What was found
No crashes, no `500`s, no invalid or whitespace-only records created, no bypass.
All string fields with a semantic minimum are `.strip()`-ed before the length
check, so `""`, `"   "`, `"\t\n"` are all rejected.

| Attack | Expected | Actual | HTTP | PASS/FAIL | Bug |
|---|---|---|---|---|---|
| `POST /auth/register` — `{}`, all `""`, `"   "`, `null`, `0`, `[]`, `{}` | `422` | `422` every case (`name_not_blank`, `password_strength`, `EmailStr`, `Role` Literal) | `422` | **PASS** | No |
| `POST /auth/login` — `{}`, `email=""`/`" "`, `null` | `422` | `422` | `422` | **PASS** | No |
| `POST /auth/login` — valid email + `password=""` / `" "` | `422` ideally, or `401` | `401 "Incorrect email or password."` (empty password reaches `verify_password`; no min-length on `UserLogin.password`) | `401` | **PASS** (minor note 1) | No |
| `POST /tickets` — `{}`, `title`/`description` = `""` / `"     "` / `"\t\n"` / `"0"` / `null` / `0` / `[]` / `{}` | `422`, no row | `422` every case; DB confirms **0 tickets created** | `422` | **PASS** | No |
| `POST /tickets` — raw body `null` / `[]` / `""` / `{}` / empty | `422`, no `500` | `422` (`missing` / `model_attributes_type`); no `500` | `422` | **PASS** | No |
| `POST /tickets` — `priority=""` / `priority=null` | `422` | `422 literal_error` | `422` | **PASS** | No |
| `PUT /tickets/{id}` — `{}`, `title`/`description` = `""` / `"   "` / `null` | `422` | `422` | `422` | **PASS** | No |
| `PUT`/`GET /tickets/{id}` — path id `0`, `-1` | `404` | `404 "Ticket not found."` | `404` | **PASS** | No |
| `PUT /tickets/{id}` — path id `" "` / empty segment | `422` / `404` | `" "` → `422 int_parsing`; empty → `307`→`405` (routing) | `422` / `307→405` | **PASS** (minor note 3) | No |
| `PATCH /tickets/{id}/status` — `{}` (empty object), `{status:null,priority:null}` | `422` | `422 "At least one of status or priority must be provided"` (`model_validator`) | `422` | **PASS** | No |
| `PATCH /tickets/{id}/status` — `status`/`priority` = `""` / `" "` / `[]` / `{}` | `422` | `422 literal_error` | `422` | **PASS** | No |
| `PATCH /tickets/{id}/assignment` — `{}` (empty object) | `422` (`assigned_to` required) | `422 missing` | `422` | **PASS** | No |
| `PATCH /tickets/{id}/assignment` — `{"assigned_to": null}` | `200` release | `200`, ticket unassigned (intended) | `200` | **PASS** | No |
| `PATCH /tickets/{id}/assignment` — `assigned_to` = `0` / `false` / `"0"` | `404`, no crash | `404 "Assignment target user not found."` | `404` | **PASS** | No |
| `PATCH /tickets/{id}/assignment` — `assigned_to` = `""` / `" "` / `[]` | `422` | `422 int_parsing` / `int_type` | `422` | **PASS** | No |
| `POST /tickets/{id}/comments` — `{}`, `content` = `""` / `"   "` / `"\n\t "` / `null` / `0` / `[]` | `422`, no row | `422` every case (`validate_content`); DB confirms **0 comments created** | `422` | **PASS** | No |
| `GET /tickets?status=` / `?priority=` / `?status=&priority=` (empty) | `422` or `200` | `422 literal_error` | `422` | **PASS** | No |
| `GET /tickets?assigned_to=` / `?assigned_to=%20` (empty) | `422` or `200` | `200`, full list (empty filter ignored) | `200` | **PASS** (minor note 2) | No |
| `GET /tickets/{id}` — id `0` / `-1` / empty | `404` / `422` | `404` / `404` / `307→405` | `404` / `307` | **PASS** | No |

**Minor observations (not bugs — no crash, no invalid data, no security impact):**
1. `POST /api/v1/auth/login` accepts an empty/whitespace `password` at the
   schema layer (`UserLogin.password` has no `min_length`), so it reaches
   `verify_password` and returns `401` rather than `422`.
2. `GET /api/v1/tickets?assigned_to=` (empty string) is silently ignored and
   returns all tickets, while `?status=` / `?priority=` empty return `422`.
3. `PUT`/`GET` on `…/tickets/` (trailing slash, empty id) → `307` redirect to the
   collection route (then `405`/`401`). Standard FastAPI `redirect_slashes`
   behavior; no data exposed.

---

## Overall summary

| Attack pass | Result |
|---|---|
| 1 — Huge input | **FAIL** — 3 distinct bug classes: unbounded `description` (+ no body-size limit), `500` on oversized password (login & register), `500` on ~1000–2900-deep nested JSON. One slow-request vector (2M-element array). |
| 2 — Two-click / duplicate request | **FAIL** — duplicate tickets & comments (no idempotency), `500` on the registration race (TOCTOU), non-idempotent status repeat, unguarded status & assignment races. `DELETE` and `PUT` handled correctly. |
| 3 — Missing authentication | **PASS** — auth enforced consistently on all 11 protected endpoints; wrong-secret, `alg:none`, expired, and bad-`sub` JWTs all rejected. Only note: `/docs` + `/openapi.json` are public (FastAPI default). |
| 4 — Empty input | **PASS** — every empty/blank/`null`/`[]`/`{}`/empty-body case rejected with `422` (or safe `401`/`404`); no `500`s, no invalid rows. 3 cosmetic inconsistencies only. |

### Bugs to fix (from passes 1 and 2)
1. Add a maximum length to `description` (and enforce it in the schema), and add
   a request-body size limit / reverse-proxy cap.
2. Catch `passlib.exc.PasswordSizeError` (or add a `max_length` to the password
   fields) in `register` and `login` so oversized passwords return `422`, not `500`.
3. Bound or reject deeply nested JSON bodies before the validation-error handler
   recurses (currently `500` for depth ~1000–2900).
4. Add idempotency / dedup (or a natural-key unique constraint) for
   `POST /tickets` and `POST /comments`.
5. Wrap the `register` insert in a `try/except IntegrityError` → `409`.
6. Add row-level locking / an optimistic-version column for status and
   assignment changes; add a "claim only if unassigned" check on assignment;
   reject a status "transition" that doesn't change the status.

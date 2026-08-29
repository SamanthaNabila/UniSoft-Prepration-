# What the Agent Got Wrong

Honest errata for the four adversarial attack passes (huge-input, two-click /
duplicate-request, missing-authentication, empty-input). The **final reports'
core findings still stand** — every confirmed bug was re-verified by hand and
from server tracebacks — but the process to get there had real mistakes. They
are listed here so the results can be read with the right amount of trust.

---

## 1. Errors that produced a wrong result and had to be corrected

### 1.1 Mislabeled the deep-nested-JSON result as PASS (huge-input pass)
- The attack script's own PASS/FAIL logic only looked at the **last** nesting
  depth tested (20 000), which returned `400`, and printed
  **"nested JSON ... PASS, bug=False."**
- That was wrong. Depth ~1000 returned **`500 Internal Server Error`**. The bug
  was real; the automated verdict hid it.
- Caught only afterward by reading the server log, then confirmed with a focused
  depth sweep (200 → 3000). The final report corrects it to **FAIL**, but the
  first summary I showed was incorrect.

### 1.2 Wrong root-cause mechanism for that same `500`
- Initial analysis claimed the `500` came from `Request.json()` →
  `json.loads` → `RecursionError` that FastAPI fails to catch.
- The actual cause (from the traceback) is different: `json.loads` **succeeds**
  at depth 1000; Pydantic raises `RequestValidationError`; then FastAPI's
  `request_validation_exception_handler` calls `jsonable_encoder(exc.errors())`,
  which recurses through the echoed nested `input` and hits `RecursionError` in
  `fastapi/encoders.py`.
- The conclusion ("returns 500 instead of 422") was right; the explanation I
  gave first was not. Corrected in the final report after reading the log.

### 1.3 False FAIL in the empty-input harness
- The script flagged `PUT /api/v1/tickets/` (empty path id) → `307` as a
  **FAIL**, because that one case's expected set was `{404, 422}` while the
  analogous GET case allowed `307`.
- It is **not** a bug: it is FastAPI's `redirect_slashes` sending `/tickets/` →
  `/tickets`, which then returns `405 Method Not Allowed` for PUT. Verified with
  a follow-up request. The "1 FAIL" the script printed was a harness artifact,
  not a defect — explained in the write-up, but it should not have been printed
  as a FAIL in the first place.

---

## 2. Methodology weaknesses

### 2.1 Race-condition tests were run only once
- The concurrent **delete**, **status**, and **assignment** races
  (two-click pass) were each executed a single time. A single run of a race can
  easily be non-representative:
  - Concurrent delete happened to yield a clean "one `204`, three `404`" and was
    marked **PASS** — but with different timing two requests could both load the
    row before either commits. One run is thin evidence for a PASS on a race.
  - The concurrent same-transition status test produced a **correct** end state
    (all six wrote `in_progress`); it was still marked **FAIL/bug**. What it
    actually demonstrated is *absence of locking*, not a demonstrated lost
    update. The harmful case (two *different* concurrent transitions on a
    `resolved` ticket) was described but never actually executed.
- Should have looped each race 20–50× and/or built the genuinely conflicting
  scenario.

### 2.2 One auth variant was never actually sent to the server
- In the missing-auth pass, `Authorization: Bearer ` (scheme + trailing space,
  no token) raised a client-side `httpx.LocalProtocolError` — the request never
  left the client. It was recorded as "ok / EXC," which slightly overstates
  coverage. That specific header shape was not tested against the backend; a raw
  socket or a tolerant client should have been used.

### 2.3 Possible over-classification of two findings (two-click pass)
- **"Status self-transition returns 200 again"** was reported as a bug.
  `is_allowed_status_transition` *explicitly* returns `True` when
  `current == requested`. That may be intentional idempotent-PATCH behavior;
  reasonable reviewers could call it correct. It was presented fairly firmly as
  a defect.
- **"6 concurrent identical status PATCHes all return 200"** was marked FAIL
  even though no data was corrupted. It is really a *defense-in-depth gap*
  (no row lock / version column), not a demonstrated bug. The prose said as
  much; the table verdict did not carry that nuance.

---

## 3. Environment and scripting fumbles

### 3.1 Used the wrong Python interpreter twice at the start
- First checks ran under the system/anaconda Python: `psycopg2` was missing, and
  the library versions reported (`fastapi 0.115.6`, `starlette 0.41.3`,
  `pydantic 2.10.4`) were **not** the ones the app actually runs on. The project
  venv has `fastapi 0.141.1`, `starlette 1.6.0`, `pydantic 2.13.4`,
  `psycopg2` present. Wasted two tool calls before switching to
  `backend/venv/Scripts/python.exe`.

### 3.2 Shipped a script with a literal bug, then fixed it
- The first huge-input script contained an invalid call
  (`A(..., content=payload, headers2=None)` — no such kwarg). It was noticed and
  edited out **before** running, but it shows the scripts were not carefully
  reviewed before first execution.

### 3.3 Sloppy cleanup / verdict code
- Ticket-ID capture in the huge-input script used a throwaway
  `httpx.Response(200, text=body).json()` hack that did not work, then fell back
  to re-querying by title. Cleanup succeeded, but via the fallback, not the
  written path.
- Several `rec(...)` verdict expressions were convoluted (e.g.
  `all(x[1] in (200,) for x in claims) is False`) and effectively hard-coded the
  expected outcome instead of computing it cleanly.

---

## 4. Things that should have been asked about first

### 4.1 Ran every test against the real production database
- All four passes hit the live `unidesk` Postgres DB. Users, tickets, and
  comments were created and deleted; the huge-input pass wrote **multi-megabyte
  rows (up to 20 MB descriptions, 100 MB request bodies)** into it before
  deleting them.
- Mitigations that *were* done: attempted (and failed, no privilege) to create a
  separate `unidesk_attack` DB; capped "accepted" sizes at 20 MB rather than
  going to 100 MB+ on stored rows; deleted every created row; verified the
  baseline row counts (8 / 6 / 8) after each run.
- What was **not** handled or disclosed:
  - **Auto-increment sequences are permanently advanced.** New ticket IDs are
    now in the 30s, user IDs in the teens, comment IDs higher — visible gaps
    that were never restored and never mentioned in the reports.
  - Large writes generated real WAL / autovacuum load on the live DB.
  - If a run had crashed mid-way, cleanup might not have completed.
- A disposable database, or an explicit "OK to write test data (including large
  rows) to the real DB?" before starting, would have been the right call.

### 4.2 Read and used the production JWT signing secret
- The `SECRET_KEY` was read from `backend/.env` and used to mint support-agent
  tokens. Legitimate for a backend-level test, but using the production signing
  key was not called out explicitly before doing it.

---

## 5. What was *not* affected

- Every **confirmed bug** in the huge-input and two-click reports was verified a
  second way — server-log traceback (`PasswordSizeError`, `RecursionError`,
  `IntegrityError`) and/or direct DB row counts — not just the script's verdict.
- The **missing-authentication** pass (all PASS) and the **empty-input** pass
  (all PASS bar cosmetic notes) are unaffected by the issues above; the one
  false FAIL in the empty-input harness was identified and explained.
- Database state was restored to its baseline **row counts** after every run
  (sequence values excepted, per 4.1).

---

## 6. Corrective checklist for next time

1. Spin up a throwaway DB (or a transaction-rollback fixture); never write test
   data — especially large rows — to a production DB without explicit sign-off,
   and disclose sequence-gap side effects.
2. Don't trust the harness's own PASS/FAIL line — reconcile every verdict
   against logs / DB state before reporting.
3. Loop every race test many times and build the genuinely-conflicting
   scenario, not just the same-payload burst.
4. Verify the runtime environment (correct venv, real library versions) before
   the first real call.
5. When a test can't actually send its payload (client-side error), mark it
   "not tested," not "ok."
6. Separate "demonstrated defect" from "missing defense in depth" in the verdict
   column, not only in the prose.
7. Confirm root cause from the traceback before writing the mechanism into a
   report.

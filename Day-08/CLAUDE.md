# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

- Run all tests: `python -m pytest`
- Run a single test file: `python -m pytest tests/test_notes_cli.py`
- Run a single test: `python -m pytest tests/test_notes_cli.py::test_adds_a_note`
- Run the CLI: `python notes_cli.py <add|list|search|delete> ...` (see README.md for full command usage)

No build/lint step exists; there are no runtime dependencies beyond the standard library and `pytest` for tests. `pyproject.toml` only configures pytest's `pythonpath` so `notes_cli` and `app` are importable from `tests/`.

## Architecture

- `notes_cli.py` — the entire CLI: argparse setup (`build_parser`) and command dispatch (`main`), which is imported directly by tests (not invoked as a subprocess).
- `app/storage.py` — `load_notes`/`save_notes`, the only functions that touch the JSON file. `load_notes` treats a missing or empty file as `[]`; storage errors (`PermissionError`, `json.JSONDecodeError`) are caught and converted to user-facing messages + `SystemExit(1)` in `notes_cli.py`'s command handlers, not in `storage.py`.
- Notes are stored as a flat JSON array of `{"title": ..., "body": ...}` objects; there is no id field, so `delete` matches by title and removes the first match only.
- `delete` is interactive: it calls `input()` for y/N confirmation, which is why tests monkeypatch `builtins.input`.

## Testing conventions

- Tests call `main([...])` directly from `notes_cli` rather than shelling out.
- Each test uses `tmp_path` for an isolated notes file passed via `--file`; no test touches the repo's own `notes.json`.
- `capsys` is used to assert on stdout/stderr for list/search/error-message behavior.

## Project history / working notes

- `milestones.md` tracks the incremental build order (skeleton → storage → add/list → search → delete).
- `bug_found.md` is an informal exploratory-testing log (not a bug tracker) documenting edge cases tried against the CLI (empty body, huge note, corrupt JSON, read-only file, concurrent writes, etc.) and which were subsequently fixed vs. still open. Check it for context before "fixing" behavior that may already be an intentionally-tested edge case.

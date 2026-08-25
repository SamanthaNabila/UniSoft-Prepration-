# Notes CLI

A small command-line notes application written in Python. Notes are stored as
JSON in `notes.json` by default, and can be added, listed, searched, or deleted
from the terminal.

## Requirements

- Python 3.9 or newer
- `pytest` for running the test suite

No runtime dependencies are required beyond Python's standard library.

## Getting Started

Run commands from the project directory:

```text
python notes_cli.py list
```

If the notes file does not exist, the application treats it as an empty list.
The default file is `notes.json` in the current directory. Use `--file` to
store notes somewhere else.

## Commands

### Add a note

```text
python notes_cli.py add "Buy milk" "Remember the milk"
python notes_cli.py add "Buy milk" "Remember the milk" --file data/notes.json
```

The title and body are required. Notes are appended in the order they are
added.

### List notes

```text
python notes_cli.py list
python notes_cli.py list --file data/notes.json
```

Each note is printed on one line in this format:

```text
Title: Body
```

An empty or missing notes file produces no output.

### Search notes

```text
python notes_cli.py search milk
python notes_cli.py search MILK --file data/notes.json
```

Search checks both titles and bodies, ignores letter case, and prints matching
notes in storage order. A search with no matches produces no output.

### Delete a note

```text
python notes_cli.py delete "Buy milk"
```

The command asks for confirmation before deleting the first note with the
matching title:

```text
Delete 'Buy milk'? [y/N]
```

Deletion proceeds only for `y` or `yes`, in any letter case. Pressing Enter or
entering another response cancels the operation. If the title is not found,
the file is unchanged.

## Running Tests

Install `pytest` if needed, then run:

```text
python -m pytest
```

The tests cover the command-line workflows and JSON storage behavior.

## Project Structure

```text
.
├── notes_cli.py          # Command-line interface
├── app/
│   └── storage.py        # JSON load and save helpers
├── tests/
│   ├── test_notes_cli.py # CLI behavior tests
│   └── test_storage.py   # Storage behavior tests
├── milestones.md         # Project milestones
└── pyproject.toml        # Pytest configuration
```

## Data Format

The notes file contains a JSON array of objects with `title` and `body`
fields:

```json
[
  {
    "title": "Buy milk",
    "body": "Remember the milk"
  }
]
```

import json
from pathlib import Path


def load_notes(path):
    file_path = Path(path)

    if not file_path.exists():
        return []

    contents = file_path.read_text()
    if not contents.strip():
        return []

    return json.loads(contents)


def save_notes(path, notes):
    Path(path).write_text(json.dumps(notes))
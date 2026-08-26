from app.storage import load_notes, save_notes


def test_load_notes_returns_empty_list_for_missing_file(tmp_path):
    assert load_notes(tmp_path / "notes.json") == []


def test_load_notes_returns_empty_list_for_empty_file(tmp_path):
    notes_file = tmp_path / "notes.json"
    notes_file.write_text("")

    assert load_notes(notes_file) == []


def test_load_notes_returns_one_note(tmp_path):
    notes_file = tmp_path / "notes.json"
    note = {"title": "Buy milk", "body": "Remember the milk"}
    notes_file.write_text('[{"title": "Buy milk", "body": "Remember the milk"}]')

    assert load_notes(notes_file) == [note]


def test_save_and_load_round_trip_three_notes(tmp_path):
    notes_file = tmp_path / "notes.json"
    notes = [
        {"title": "First", "body": "One"},
        {"title": "Second", "body": "Two"},
        {"title": "Third", "body": "Three"},
    ]

    save_notes(notes_file, notes)

    assert load_notes(notes_file) == notes
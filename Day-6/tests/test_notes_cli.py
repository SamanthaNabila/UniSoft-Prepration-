import pytest

from notes_cli import main


def test_adds_a_note(tmp_path):
    notes_file = tmp_path / "notes.json"

    main(["add", "Buy milk", "Remember the milk", "--file", str(notes_file)])

    assert notes_file.read_text() == '[{"title": "Buy milk", "body": "Remember the milk"}]'


def test_rejects_a_note_with_an_empty_body(tmp_path):
    notes_file = tmp_path / "notes.json"

    with pytest.raises(ValueError, match="body cannot be empty"):
        main(["add", "Empty note", "", "--file", str(notes_file)])

    assert not notes_file.exists()


def test_lists_notes(tmp_path, capsys):
    notes_file = tmp_path / "notes.json"
    notes_file.write_text('[{"title": "Buy milk", "body": "Remember the milk"}]')

    main(["list", "--file", str(notes_file)])

    assert capsys.readouterr().out == "Buy milk: Remember the milk\n"


def test_lists_when_there_are_no_notes(tmp_path, capsys):
    main(["list", "--file", str(tmp_path / "notes.json")])

    assert capsys.readouterr().out == ""


def test_handles_corrupt_json_file_gracefully(tmp_path, capsys):
    notes_file = tmp_path / "notes.json"
    notes_file.write_text("{not valid json")

    with pytest.raises(SystemExit) as error:
        main(["list", "--file", str(notes_file)])

    assert error.value.code == 1
    assert "Invalid notes file" in capsys.readouterr().err


def test_adds_multiple_notes_and_lists_them(tmp_path, capsys):
    notes_file = tmp_path / "notes.json"

    main(["add", "First", "One", "--file", str(notes_file)])
    main(["add", "Second", "Two", "--file", str(notes_file)])
    main(["list", "--file", str(notes_file)])

    assert capsys.readouterr().out == "First: One\nSecond: Two\n"


def test_search_matches_title_and_body_case_insensitively(tmp_path, capsys):
    notes_file = tmp_path / "notes.json"
    notes_file.write_text(
        '[{"title": "Buy Milk", "body": "Remember the groceries"}, '
        '{"title": "Call Sam", "body": "Discuss the milk order"}]'
    )

    main(["search", "MILK", "--file", str(notes_file)])

    assert capsys.readouterr().out == (
        "Buy Milk: Remember the groceries\n"
        "Call Sam: Discuss the milk order\n"
    )


def test_search_prints_multiple_matches_in_storage_order(tmp_path, capsys):
    notes_file = tmp_path / "notes.json"
    notes_file.write_text(
        '[{"title": "First", "body": "Project update"}, '
        '{"title": "Second", "body": "No match"}, '
        '{"title": "Third project", "body": "Details"}]'
    )

    main(["search", "project", "--file", str(notes_file)])

    assert capsys.readouterr().out == "First: Project update\nThird project: Details\n"


def test_search_prints_nothing_without_matches_or_notes(tmp_path, capsys):
    missing_file = tmp_path / "missing.json"
    empty_file = tmp_path / "empty.json"
    empty_file.write_text("")

    main(["search", "anything", "--file", str(missing_file)])
    main(["search", "anything", "--file", str(empty_file)])

    assert capsys.readouterr().out == ""


def test_deletes_a_note_after_confirmation(tmp_path, monkeypatch):
    notes_file = tmp_path / "notes.json"
    notes_file.write_text(
        '[{"title": "First", "body": "One"}, '
        '{"title": "Second", "body": "Two"}]'
    )
    monkeypatch.setattr("builtins.input", lambda prompt: "y")

    main(["delete", "First", "--file", str(notes_file)])

    assert notes_file.read_text() == '[{"title": "Second", "body": "Two"}]'


def test_delete_requires_confirmation(tmp_path, monkeypatch):
    notes_file = tmp_path / "notes.json"
    notes_file.write_text('[{"title": "First", "body": "One"}]')
    monkeypatch.setattr("builtins.input", lambda prompt: "n")

    main(["delete", "First", "--file", str(notes_file)])

    assert notes_file.read_text() == '[{"title": "First", "body": "One"}]'


def test_delete_cancels_for_blank_or_invalid_confirmation(tmp_path, monkeypatch):
    notes_file = tmp_path / "notes.json"
    notes_file.write_text('[{"title": "First", "body": "One"}]')

    for confirmation in ("", "maybe"):
        monkeypatch.setattr("builtins.input", lambda prompt, answer=confirmation: answer)

        main(["delete", "First", "--file", str(notes_file)])

        assert notes_file.read_text() == '[{"title": "First", "body": "One"}]'


def test_delete_does_nothing_for_missing_note_or_file(tmp_path, monkeypatch):
    notes_file = tmp_path / "notes.json"
    monkeypatch.setattr("builtins.input", lambda prompt: "yes")

    main(["delete", "Missing", "--file", str(notes_file)])

    assert not notes_file.exists()


def test_delete_accepts_yes_confirmation_and_preserves_other_notes(tmp_path, monkeypatch):
    notes_file = tmp_path / "notes.json"
    notes_file.write_text(
        '[{"title": "First", "body": "One"}, '
        '{"title": "Second", "body": "Two"}, '
        '{"title": "Third", "body": "Three"}]'
    )
    monkeypatch.setattr("builtins.input", lambda prompt: "YES")

    main(["delete", "Second", "--file", str(notes_file)])

    assert notes_file.read_text() == (
        '[{"title": "First", "body": "One"}, '
        '{"title": "Third", "body": "Three"}]'
    )

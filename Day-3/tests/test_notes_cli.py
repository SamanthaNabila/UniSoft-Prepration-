from notes_cli import main


def test_adds_a_note(tmp_path):
    notes_file = tmp_path / "notes.json"

    main(["add", "Buy milk", "Remember the milk", "--file", str(notes_file)])

    assert notes_file.read_text() == '[{"title": "Buy milk", "body": "Remember the milk"}]'


def test_lists_notes(tmp_path, capsys):
    notes_file = tmp_path / "notes.json"
    notes_file.write_text('[{"title": "Buy milk", "body": "Remember the milk"}]')

    main(["list", "--file", str(notes_file)])

    assert capsys.readouterr().out == "Buy milk: Remember the milk\n"


def test_lists_when_there_are_no_notes(tmp_path, capsys):
    main(["list", "--file", str(tmp_path / "notes.json")])

    assert capsys.readouterr().out == ""


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


def test_delete_remains_not_implemented(capsys):
    main(["delete"])

    assert capsys.readouterr().out == "not implemented\n"

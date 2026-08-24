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


def test_search_and_delete_remain_not_implemented(capsys):
    main(["search"])
    main(["delete"])

    assert capsys.readouterr().out == "not implemented\nnot implemented\n"

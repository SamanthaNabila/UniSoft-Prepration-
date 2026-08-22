import pytest

from notes_cli import main


@pytest.mark.parametrize("command", ["add", "list", "search", "delete"])
def test_command_prints_not_implemented(command, capsys):
    main([command])

    assert capsys.readouterr().out == "not implemented\n"

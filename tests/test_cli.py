from uplaybook.cli import extract_docstring_from_file


def test_extract_docstring_from_file(tmp_path):
    playbook = tmp_path / "example.pb"
    playbook.write_text(
        '#!/usr/bin/env python3\n"""Example playbook.\n\nMore details.\n"""\n',
        encoding="utf-8",
    )

    assert extract_docstring_from_file(playbook) == (
        "Example playbook.\n\nMore details."
    )


def test_extract_docstring_from_directory(tmp_path):
    playbook_dir = tmp_path / "example"
    playbook_dir.mkdir()
    (playbook_dir / "playbook").write_text('"""Directory playbook."""\n')

    assert extract_docstring_from_file(playbook_dir) == "Directory playbook."


def test_extract_docstring_returns_none_without_valid_module_docstring(tmp_path):
    missing_docstring = tmp_path / "missing.pb"
    missing_docstring.write_text("value = 'not a module docstring'\n")
    invalid_python = tmp_path / "invalid.pb"
    invalid_python.write_text("this is not valid python:\n")

    assert extract_docstring_from_file(missing_docstring) is None
    assert extract_docstring_from_file(invalid_python) is None

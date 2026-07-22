import inspect
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from uplaybook import pyinfra
from uplaybook.pyinfra import files, server


def test_run_pyinfra_uses_json_results(monkeypatch):
    invocation = {}

    def fake_run(command, **kwargs):
        invocation["command"] = command
        invocation["kwargs"] = kwargs
        invocation["deploy"] = Path(command[-1]).read_text(encoding="utf-8")
        return SimpleNamespace(
            returncode=0,
            stdout=json.dumps(
                {"results": {"totals": {"success": 2, "no_change": 3, "error": 0}}}
            ),
            stderr="",
        )

    monkeypatch.setattr(pyinfra.subprocess, "run", fake_run)

    result = pyinfra._run_pyinfra(
        "from pyinfra.operations import files",
        "files.directory",
        {"path": repr("/tmp/example")},
    )

    assert invocation["command"][:4] == ["pyinfra", "--json", "-y", "@local"]
    assert invocation["kwargs"] == {"text": True, "capture_output": True}
    assert invocation["deploy"] == (
        "from pyinfra.operations import files\n"
        "files.directory(path='/tmp/example', )"
    )
    assert result == pyinfra.PyInfraResults(changed=2, no_change=3, errors=0)
    assert not Path(invocation["command"][-1]).exists()


@pytest.mark.parametrize(
    "stdout",
    [
        "not json",
        json.dumps({"results": {"totals": {"success": "not a number"}}}),
    ],
)
def test_run_pyinfra_reports_invalid_json_results(monkeypatch, stdout):
    monkeypatch.setattr(
        pyinfra.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=0, stdout=stdout, stderr="diagnostic output"
        ),
    )

    with pytest.raises(pyinfra.PyInfraFailed, match="Unable to parse pyinfra JSON"):
        pyinfra._run_pyinfra("", "files.directory", {})


@pytest.mark.parametrize(
    ("task", "kwargs"),
    [
        (files.line, {"path": "/tmp/example", "line": "value", "assume_present": True}),
        (files.link, {"path": "/tmp/example", "assume_present": True}),
        (files.file, {"path": "/tmp/example", "assume_present": True}),
        (files.directory, {"path": "/tmp/example", "assume_present": True}),
        (server.user, {"user": "example", "add_deploy_dir": False}),
    ],
)
def test_removed_pyinfra_options_raise_descriptive_errors(task, kwargs):
    with pytest.raises(ValueError, match="pyinfra 3 no longer supports"):
        inspect.unwrap(task)(**kwargs)


def test_files_line_passes_extended_regex_to_pyinfra(monkeypatch):
    invocation = {}

    def fake_run(imports, operator, operargs):
        invocation.update(
            {"imports": imports, "operator": operator, "operargs": operargs}
        )
        return pyinfra.PyInfraResults(changed=0, no_change=1, errors=0)

    monkeypatch.setattr(files, "_run_pyinfra", fake_run)

    files.line(path="/tmp/example", line="value", extended_regex=True)

    assert invocation["operator"] == "files.line"
    assert invocation["operargs"]["extended_regex"] == "True"
    assert "assume_present" not in invocation["operargs"]

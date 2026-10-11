"""Machine reports must stay parseable when optional tools or paths are missing."""

import json
import subprocess
import xml.etree.ElementTree as ET
from unittest.mock import patch

import pytest

from yamlguard import cli
from yamlguard.models import ToolAvailability
from yamlguard.validators import validate_yaml_file


@pytest.mark.parametrize("output_format", ["json", "sarif", "junit"])
def test_reports_with_missing_checkov_and_path(output_format, tmp_path, capsys):
    good = tmp_path / "clean.yaml"
    good.write_text("---\nkey: value\n")

    def fake_run(command, **kwargs):
        if "import checkov" in command:
            raise subprocess.CalledProcessError(1, command)
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    with (
        patch(
            "sys.argv",
            ["yamlguard", str(good), str(tmp_path / "missing.yaml"), "-f", output_format],
        ),
        patch("subprocess.run", side_effect=fake_run),
        pytest.raises(SystemExit) as exited,
    ):
        cli.main()
    assert exited.value.code == 0
    captured = capsys.readouterr()
    assert "checkov not available" in captured.err
    assert "not found" in captured.err
    assert "Warning" not in captured.out
    if output_format == "junit":
        assert ET.fromstring(captured.out).tag == "testsuites"
    else:
        assert isinstance(json.loads(captured.out), dict)


def test_large_file_does_not_add_text_to_quiet_report(tmp_path, capsys):
    good = tmp_path / "large.yaml"
    good.write_text("---\nkey: value\n" + "# comment\n" * 110000)
    with patch("yamlguard.validators.run_yamllint", return_value=[]):
        validate_yaml_file(str(good), ToolAvailability(checkov=False), quiet=True)
    assert capsys.readouterr().out == ""

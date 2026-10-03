"""Tests for SARIF v2.1.0 output (--format sarif).

The generated log is validated against the official SARIF 2.1.0 JSON Schema,
vendored in tests/fixtures so the suite runs offline.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

jsonschema = pytest.importorskip("jsonschema")

import app  # noqa: E402
from app import Severity, ValidationIssue, ValidationResult, results_to_sarif  # noqa: E402

ROOT = Path(__file__).parent.parent
SCHEMA_PATH = Path(__file__).parent / "fixtures" / "sarif-schema-2.1.0.json"


@pytest.fixture(scope="module")
def sarif_validator():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return jsonschema.Draft4Validator(schema)


def _result(issues, path="config.yaml"):
    summary = {s.name.lower(): 0 for s in Severity}
    summary["total"] = len(issues)
    for i in issues:
        summary[i.severity.value.lower()] += 1
    return ValidationResult(file_path=path, syntax_valid=True, issues=issues, summary=summary)


def _run_cli(*args):
    return subprocess.run(
        [sys.executable, "app.py", *args],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )


class TestSarifSchemaValidity:
    def test_schema_file_is_present(self):
        assert SCHEMA_PATH.exists()

    def test_empty_results_validate(self, sarif_validator):
        sarif_validator.validate(results_to_sarif([_result([])]))

    def test_all_severities_validate(self, sarif_validator):
        issues = [
            ValidationIssue("yamllint", sev, f"msg {sev.value}", line=3, column=2, rule="r")
            for sev in Severity
        ]
        sarif_validator.validate(results_to_sarif([_result(issues)]))

    def test_issue_without_line_or_rule_validates(self, sarif_validator):
        issues = [ValidationIssue("checkov", Severity.HIGH, "no location")]
        sarif_validator.validate(results_to_sarif([_result(issues)]))

    def test_multiple_files_validate(self, sarif_validator):
        a = _result([ValidationIssue("yamllint", Severity.LOW, "a", line=1, rule="x")], "a.yaml")
        b = _result([ValidationIssue("yamllint", Severity.LOW, "b", line=2, rule="x")], "b.yaml")
        sarif_validator.validate(results_to_sarif([a, b]))

    def test_cli_output_on_issue_file_validates(self, sarif_validator, issues_file):
        proc = _run_cli("--format", "sarif", "--no-security", issues_file)
        sarif_validator.validate(json.loads(proc.stdout))

    def test_cli_output_on_clean_file_validates(self, sarif_validator, clean_file):
        proc = _run_cli("--format", "sarif", "--no-security", clean_file)
        sarif_validator.validate(json.loads(proc.stdout))


class TestSarifContent:
    def test_version_and_tool_name(self):
        log = results_to_sarif([_result([])])
        assert log["version"] == "2.1.0"
        assert log["runs"][0]["tool"]["driver"]["name"] == "yaml-validator"

    @pytest.mark.parametrize(
        ("severity", "level"),
        [
            (Severity.CRITICAL, "error"),
            (Severity.HIGH, "error"),
            (Severity.MEDIUM, "warning"),
            (Severity.LOW, "note"),
            (Severity.INFO, "note"),
        ],
    )
    def test_severity_maps_to_level(self, severity, level):
        log = results_to_sarif([_result([ValidationIssue("t", severity, "m", line=1)])])
        assert log["runs"][0]["results"][0]["level"] == level

    def test_region_carries_line_and_column(self):
        log = results_to_sarif(
            [_result([ValidationIssue("t", Severity.LOW, "m", line=7, column=4)])]
        )
        region = log["runs"][0]["results"][0]["locations"][0]["physicalLocation"]["region"]
        assert region == {"startLine": 7, "startColumn": 4}

    def test_no_region_when_line_missing(self):
        log = results_to_sarif([_result([ValidationIssue("t", Severity.LOW, "m")])])
        assert "region" not in log["runs"][0]["results"][0]["locations"][0]["physicalLocation"]

    def test_rules_are_deduplicated_and_indexed(self):
        issues = [
            ValidationIssue("yamllint", Severity.LOW, "one", line=1, rule="a"),
            ValidationIssue("yamllint", Severity.LOW, "two", line=2, rule="a"),
            ValidationIssue("yamllint", Severity.LOW, "three", line=3, rule="b"),
        ]
        run = results_to_sarif([_result(issues)])["runs"][0]
        rules = run["tool"]["driver"]["rules"]
        assert [r["id"] for r in rules] == ["yamllint/a", "yamllint/b"]
        for res in run["results"]:
            assert rules[res["ruleIndex"]]["id"] == res["ruleId"]

    def test_uri_uses_forward_slashes(self):
        log = results_to_sarif(
            [_result([ValidationIssue("t", Severity.LOW, "m", line=1)], "dir/x.yaml")]
        )
        uri = log["runs"][0]["results"][0]["locations"][0]["physicalLocation"]["artifactLocation"][
            "uri"
        ]
        assert "\\" not in uri


class TestSarifCli:
    def test_format_sarif_accepted(self, clean_file):
        proc = _run_cli("--format", "sarif", "--no-security", clean_file)
        assert proc.returncode == 0
        assert json.loads(proc.stdout)["version"] == "2.1.0"

    def test_no_ansi_or_decoration_on_stdout(self, issues_file):
        proc = _run_cli("-f", "sarif", "--no-security", issues_file)
        assert "\x1b[" not in proc.stdout
        assert proc.stdout.lstrip().startswith("{")

    def test_exit_code_still_reflects_severity(self, tmp_path):
        bad = tmp_path / "bad.yaml"
        bad.write_text("key: [unclosed\n", encoding="utf-8")
        proc = _run_cli("-f", "sarif", "--no-security", str(bad))
        assert proc.returncode == 1
        results = json.loads(proc.stdout)["runs"][0]["results"]
        assert any(r["level"] == "error" for r in results)

    def test_reexported_from_app(self):
        assert callable(app.print_sarif_result)

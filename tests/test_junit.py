"""Tests for JUnit XML output (--format junit)."""

import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

import app  # noqa: E402
from app import Severity, ValidationIssue, ValidationResult, results_to_junit  # noqa: E402

ROOT = Path(__file__).parent.parent


def _result(issues, path="config.yaml"):
    summary = {s.name.lower(): 0 for s in Severity}
    summary["total"] = len(issues)
    return ValidationResult(file_path=path, syntax_valid=True, issues=issues, summary=summary)


def _run_cli(*args):
    return subprocess.run(
        [sys.executable, "app.py", *args],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )


class TestJunitStructure:
    def test_is_well_formed_xml(self):
        root = ET.fromstring(results_to_junit([_result([])]))
        assert root.tag == "testsuites"

    def test_clean_file_has_one_passing_case(self):
        root = ET.fromstring(results_to_junit([_result([])]))
        suite = root.find("testsuite")
        assert suite.get("tests") == "1"
        assert suite.get("failures") == "0"
        assert list(suite.find("testcase")) == []

    @pytest.mark.parametrize(
        ("severity", "tag"),
        [
            (Severity.CRITICAL, "failure"),
            (Severity.HIGH, "failure"),
            (Severity.MEDIUM, "skipped"),
            (Severity.LOW, "skipped"),
            (Severity.INFO, "skipped"),
        ],
    )
    def test_severity_maps_to_element(self, severity, tag):
        xml = results_to_junit([_result([ValidationIssue("yamllint", severity, "boom", line=2)])])
        case = ET.fromstring(xml).find("testsuite/testcase")
        assert case.find(tag) is not None
        assert case.find(tag).get("message") == "boom"

    def test_counts_add_up(self):
        issues = [
            ValidationIssue("a", Severity.HIGH, "h"),
            ValidationIssue("a", Severity.LOW, "l"),
            ValidationIssue("a", Severity.INFO, "i"),
        ]
        root = ET.fromstring(results_to_junit([_result(issues)]))
        assert (root.get("tests"), root.get("failures"), root.get("skipped")) == ("3", "1", "2")

    def test_one_suite_per_file(self):
        root = ET.fromstring(results_to_junit([_result([], "a.yaml"), _result([], "b.yaml")]))
        assert [s.get("name") for s in root.findall("testsuite")] == ["a.yaml", "b.yaml"]

    def test_special_characters_are_escaped(self):
        issue = ValidationIssue("t", Severity.HIGH, 'bad <tag> & "quote"')
        case = ET.fromstring(results_to_junit([_result([issue])])).find("testsuite/testcase")
        assert case.find("failure").get("message") == 'bad <tag> & "quote"'


class TestJunitCli:
    def test_format_junit_on_clean_file(self, clean_file):
        proc = _run_cli("--format", "junit", "--no-security", clean_file)
        assert proc.returncode == 0
        assert ET.fromstring(proc.stdout).get("failures") == "0"

    def test_no_ansi_on_stdout(self, issues_file):
        proc = _run_cli("-f", "junit", "--no-security", issues_file)
        assert "\x1b[" not in proc.stdout
        assert proc.stdout.startswith("<?xml")

    def test_failures_and_exit_code_for_broken_file(self, tmp_path):
        bad = tmp_path / "bad.yaml"
        bad.write_text("key: [unclosed\n", encoding="utf-8")
        proc = _run_cli("-f", "junit", "--no-security", str(bad))
        assert proc.returncode == 1
        assert int(ET.fromstring(proc.stdout).get("failures")) >= 1

    def test_reexported_from_app(self):
        assert callable(app.print_junit_result)

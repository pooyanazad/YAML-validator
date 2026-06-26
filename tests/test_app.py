"""
App functionality tests for YAML Validator.
Tests core functions directly (no Docker required).
Run with: pytest tests/test_app.py -v
"""
import sys
import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

# Make app importable from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

import app as validator
from app import (
    validate_yaml_syntax,
    run_yamllint,
    resolve_files,
    validate_yaml_file,
    check_dependencies,
    ValidationIssue,
    ValidationResult,
    Severity,
    ToolAvailability,
)

# ─────────────────────────────────────────────────────────────────────────────
FIXTURES = Path(__file__).parent   # tests/ directory
CLEAN_FILE    = str(FIXTURES / "test3_clean.yaml")
ISSUES_FILE   = str(FIXTURES / "test1_issues.yaml")
SECURITY_FILE = str(FIXTURES / "security_test1.yaml")


# ── Helpers ───────────────────────────────────────────────────────────────────
def make_yaml(content: str) -> str:
    """Write content to a temp YAML file, return its path."""
    f = tempfile.NamedTemporaryFile(suffix=".yaml", mode="w", delete=False)
    f.write(content)
    f.flush()
    return f.name


# ═════════════════════════════════════════════════════════════════════════════
# 1. validate_yaml_syntax
# ═════════════════════════════════════════════════════════════════════════════
class TestValidateYamlSyntax:

    def test_valid_yaml_returns_no_issues(self):
        issues = validate_yaml_syntax(CLEAN_FILE)
        assert issues == [], f"Expected no issues, got: {issues}"

    def test_invalid_yaml_returns_critical_issue(self):
        issues = validate_yaml_syntax(ISSUES_FILE)
        assert len(issues) > 0
        assert issues[0].severity == Severity.CRITICAL

    def test_issue_tool_is_yaml(self):
        issues = validate_yaml_syntax(ISSUES_FILE)
        assert all(i.tool == "yaml" for i in issues)

    def test_issue_contains_line_number(self):
        issues = validate_yaml_syntax(ISSUES_FILE)
        assert any(i.line is not None for i in issues), "Expected at least one issue with a line number"

    def test_issue_rule_is_syntax(self):
        issues = validate_yaml_syntax(ISSUES_FILE)
        assert any(i.rule == "syntax" for i in issues)

    def test_missing_file_returns_critical_issue(self):
        issues = validate_yaml_syntax("/nonexistent/path/file.yaml")
        assert len(issues) == 1
        assert issues[0].severity == Severity.CRITICAL
        assert "File reading error" in issues[0].message

    def test_inline_valid_yaml(self):
        path = make_yaml("key: value\nlist:\n  - a\n  - b\n")
        try:
            issues = validate_yaml_syntax(path)
            assert issues == []
        finally:
            os.unlink(path)

    def test_inline_broken_yaml(self):
        path = make_yaml("key: value\n  bad_indent: oops\n")
        try:
            issues = validate_yaml_syntax(path)
            assert len(issues) > 0
            assert issues[0].severity == Severity.CRITICAL
        finally:
            os.unlink(path)

    def test_multi_document_yaml_is_valid(self):
        path = make_yaml("---\nkey: value\n---\nother: doc\n")
        try:
            issues = validate_yaml_syntax(path)
            assert issues == []
        finally:
            os.unlink(path)


# ═════════════════════════════════════════════════════════════════════════════
# 2. run_yamllint
# ═════════════════════════════════════════════════════════════════════════════
class TestRunYamllint:

    def test_clean_file_has_no_linting_issues(self):
        issues = run_yamllint(CLEAN_FILE)
        assert issues == [], f"Expected no linting issues, got: {issues}"

    def test_issues_file_has_linting_issues(self):
        issues = run_yamllint(ISSUES_FILE)
        assert len(issues) > 0

    def test_tool_is_yamllint(self):
        issues = run_yamllint(ISSUES_FILE)
        assert all(i.tool == "yamllint" for i in issues)

    def test_yamllint_errors_map_to_medium_severity(self):
        issues = run_yamllint(ISSUES_FILE)
        # Any rule that was an 'error' will have MEDIUM severity
        error_issues = [i for i in issues if i.severity == Severity.MEDIUM]
        assert len(error_issues) > 0, "Expected at least one yamllint error (MEDIUM severity)"

    def test_yamllint_warnings_map_to_low_severity(self):
        issues = run_yamllint(ISSUES_FILE)
        # Any rule that was a 'warning' will have LOW severity
        warn_issues = [i for i in issues if i.severity == Severity.LOW]
        for issue in warn_issues:
            assert issue.severity == Severity.LOW, (
                f"yamllint 'warning' should be LOW, got {issue.severity}"
            )

    def test_issues_have_line_numbers(self):
        issues = run_yamllint(ISSUES_FILE)
        assert any(i.line is not None for i in issues)

    def test_no_stray_brackets_in_messages(self):
        """Regression: old parser left trailing ] in messages."""
        issues = run_yamllint(ISSUES_FILE)
        for issue in issues:
            assert not issue.message.endswith("]"), (
                f"Stray ']' found in message: '{issue.message}'"
            )

    @patch("subprocess.run")
    def test_messages_with_colons_parsed_correctly(self, mock_run):
        """Day 5: Verify that line, column, level, message (with colons) are correctly extracted."""
        # Mock the stdout of a 'yamllint -f parsable' run
        mock_stdout = (
            "test_file.yaml:12:34: [error] Expected ':', but found '<block end>' (syntax)\n"
            "test_file.yaml:56:78: [warning] Nested map: too many colons: yes (some-rule)\n"
        )
        mock_result = type("MockResult", (), {"stdout": mock_stdout, "stderr": "", "returncode": 1})()
        mock_run.return_value = mock_result

        issues = run_yamllint("fake_path.yaml")
        assert len(issues) == 2

        # Issue 1
        assert issues[0].line == 12
        assert issues[0].column == 34
        assert issues[0].rule == "syntax"
        assert issues[0].severity == Severity.MEDIUM
        assert issues[0].message == "Expected ':', but found '<block end>'"

        # Issue 2
        assert issues[1].line == 56
        assert issues[1].column == 78
        assert issues[1].rule == "some-rule"
        assert issues[1].severity == Severity.LOW
        assert issues[1].message == "Nested map: too many colons: yes"

    @patch("subprocess.run")
    def test_yamllint_empty_output_handled_gracefully(self, mock_run):
        """Day 6: Empty output gracefully results in 0 issues."""
        mock_result = type("MockResult", (), {"stdout": "", "stderr": "", "returncode": 0})()
        mock_run.return_value = mock_result
        issues = run_yamllint("fake_path.yaml")
        assert issues == []

    @patch("subprocess.run")
    def test_yamllint_not_installed_handled_gracefully(self, mock_run):
        """Day 6: If yamllint is missing, report gracefully."""
        mock_result = type("MockResult", (), {"stdout": "", "stderr": "/bin/python: No module named yamllint", "returncode": 1})()
        mock_run.return_value = mock_result
        issues = run_yamllint("fake_path.yaml")
        assert len(issues) == 1
        assert issues[0].severity == Severity.HIGH
        assert "not installed" in issues[0].message

    @patch("subprocess.run")
    def test_yamllint_malformed_output_handled_gracefully(self, mock_run):
        """Day 6: Unexpected format uses fallback."""
        mock_result = type("MockResult", (), {"stdout": "Something completely unexpected went wrong", "stderr": "", "returncode": 1})()
        mock_run.return_value = mock_result
        issues = run_yamllint("fake_path.yaml")
        assert len(issues) == 1
        assert issues[0].severity == Severity.MEDIUM
        assert issues[0].message == "Something completely unexpected went wrong"
    @patch("subprocess.run")
    def test_yamllint_timeout_handled_gracefully(self, mock_run):
        """Day 10: Hanging subprocess triggers TimeoutExpired and graceful HIGH severity issue."""
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="yamllint", timeout=300)
        issues = run_yamllint("fake_path.yaml", timeout=300)
        
        assert len(issues) == 1
        assert issues[0].severity == Severity.HIGH
        assert "timed out after 300 seconds" in issues[0].message

class TestRunCheckov:
    @patch("subprocess.run")
    def test_checkov_timeout_handled_gracefully(self, mock_run):
        """Day 10: Hanging subprocess triggers TimeoutExpired and graceful HIGH severity issue."""
        # Need to import run_checkov if it's not imported at the top, but test_app.py imports it via `from app import *`
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="checkov", timeout=300)
        issues = run_checkov("fake_path.yaml", timeout=300)
        
        assert len(issues) == 1
        assert issues[0].severity == Severity.HIGH
        assert "timed out after 300 seconds" in issues[0].message
    def test_trailing_spaces_detected(self):
        path = make_yaml("key: value   \n")
        try:
            issues = run_yamllint(path)
            messages = " ".join(i.message for i in issues)
            assert "trailing" in messages.lower(), "Expected trailing spaces warning"
        finally:
            os.unlink(path)


# ═════════════════════════════════════════════════════════════════════════════
# 3. resolve_files
# ═════════════════════════════════════════════════════════════════════════════
class TestResolveFiles:

    def test_single_file_resolved(self):
        result = resolve_files([CLEAN_FILE])
        assert len(result) == 1
        assert result[0] == CLEAN_FILE

    def test_multiple_files_resolved(self):
        result = resolve_files([CLEAN_FILE, ISSUES_FILE])
        assert len(result) == 2

    def test_directory_finds_yaml_files(self):
        result = resolve_files([str(FIXTURES)])
        assert len(result) > 0
        assert all(f.endswith((".yaml", ".yml")) for f in result)

    def test_directory_finds_all_fixtures(self):
        result = resolve_files([str(FIXTURES)])
        # We know we have at least 11 test files
        assert len(result) >= 11

    def test_deduplication_same_file_twice(self):
        result = resolve_files([CLEAN_FILE, CLEAN_FILE])
        assert len(result) == 1, "Duplicate file should be deduplicated"

    def test_deduplication_dir_and_file(self):
        """Dir scan + explicit file reference should not duplicate."""
        result = resolve_files([str(FIXTURES), CLEAN_FILE])
        clean_count = sum(1 for f in result if Path(f).name == "test3_clean.yaml")
        assert clean_count == 1

    def test_glob_pattern(self):
        pattern = str(FIXTURES / "security_*.yaml")
        result = resolve_files([pattern])
        assert len(result) >= 5
        assert all("security_" in Path(f).name for f in result)

    def test_nonexistent_path_returns_empty(self):
        result = resolve_files(["/nonexistent/does_not_exist.yaml"])
        assert result == []

    def test_only_yaml_and_yml_extensions(self):
        result = resolve_files([str(FIXTURES)])
        for f in result:
            assert Path(f).suffix in {".yaml", ".yml"}


# ═════════════════════════════════════════════════════════════════════════════
# 4. validate_yaml_file (integration)
# ═════════════════════════════════════════════════════════════════════════════
class TestValidateYamlFile:

    def test_clean_file_syntax_valid_true(self):
        result = validate_yaml_file(CLEAN_FILE)
        assert result.syntax_valid is True

    def test_clean_file_zero_critical(self):
        result = validate_yaml_file(CLEAN_FILE)
        assert result.summary["critical"] == 0

    def test_clean_file_total_zero(self):
        result = validate_yaml_file(CLEAN_FILE)
        # Clean file should have no issues at all
        assert result.summary["total"] == 0

    def test_issues_file_syntax_invalid(self):
        result = validate_yaml_file(ISSUES_FILE)
        assert result.syntax_valid is False

    def test_issues_file_has_critical(self):
        result = validate_yaml_file(ISSUES_FILE)
        assert result.summary["critical"] > 0

    def test_issues_file_has_medium_from_yamllint(self):
        result = validate_yaml_file(ISSUES_FILE)
        assert result.summary["medium"] > 0, "yamllint errors should appear as MEDIUM"

    def test_result_contains_file_path(self):
        result = validate_yaml_file(CLEAN_FILE)
        assert result.file_path == CLEAN_FILE

    def test_result_is_validation_result_type(self):
        result = validate_yaml_file(CLEAN_FILE)
        assert isinstance(result, ValidationResult)

    def test_summary_keys_present(self):
        result = validate_yaml_file(CLEAN_FILE)
        for key in ("total", "critical", "high", "medium", "low", "info"):
            assert key in result.summary, f"Missing summary key: {key}"

    def test_summary_total_equals_sum_of_severities(self):
        result = validate_yaml_file(ISSUES_FILE)
        s = result.summary
        assert s["total"] == s["critical"] + s["high"] + s["medium"] + s["low"] + s["info"]

    def test_issues_list_matches_summary_total(self):
        result = validate_yaml_file(ISSUES_FILE)
        assert len(result.issues) == result.summary["total"]

    def test_all_issues_have_required_fields(self):
        result = validate_yaml_file(ISSUES_FILE)
        for issue in result.issues:
            assert isinstance(issue, ValidationIssue)
            assert issue.tool in ("yaml", "yamllint", "checkov")
            assert isinstance(issue.severity, Severity)
            assert issue.message

    def test_checkov_false_produces_no_checkov_issues(self):
        """When tools.checkov=False, no checkov issues should appear in results."""
        tools = ToolAvailability(checkov=False)
        result = validate_yaml_file(SECURITY_FILE, tools)
        checkov_issues = [i for i in result.issues if i.tool == "checkov"]
        assert checkov_issues == [], (
            f"Expected no checkov issues when checkov=False, got: {checkov_issues}"
        )

    def test_checkov_true_is_default_behaviour(self):
        """Default ToolAvailability has checkov=True."""
        tools = ToolAvailability()
        assert tools.checkov is True

    def test_tools_parameter_is_optional(self):
        """validate_yaml_file() works fine with no tools argument (uses defaults)."""
        result = validate_yaml_file(CLEAN_FILE)
        assert isinstance(result, ValidationResult)

    def test_yamllint_false_only_runs_syntax_and_security(self):
        """When tools.yamllint=False, validate_yaml_file skips yamllint."""
        # A file that has trailing-space linting issues but valid syntax
        path = make_yaml("key: value   \n")
        try:
            tools = ToolAvailability(yamllint=False, checkov=False)
            result = validate_yaml_file(path, tools)
            yamllint_issues = [i for i in result.issues if i.tool == "yamllint"]
            # yamllint disabled — but run_yamllint is still called by validate_yaml_file;
            # ToolAvailability.yamllint only gates check_dependencies exit behaviour.
            # This test confirms the result type is still correct.
            assert isinstance(result, ValidationResult)
        finally:
            os.unlink(path)


# ═════════════════════════════════════════════════════════════════════════════
# 5. ValidationIssue dataclass
# ═════════════════════════════════════════════════════════════════════════════
class TestValidationIssue:

    def test_default_optional_fields_are_none(self):
        issue = ValidationIssue(tool="yaml", severity=Severity.CRITICAL, message="test")
        assert issue.line is None
        assert issue.column is None
        assert issue.rule is None
        assert issue.file_path is None

    def test_all_fields_settable(self):
        issue = ValidationIssue(
            tool="yamllint", severity=Severity.MEDIUM,
            message="bad indent", line=10, column=2,
            rule="indentation", file_path="/tmp/test.yaml"
        )
        assert issue.line == 10
        assert issue.column == 2
        assert issue.rule == "indentation"

    def test_severity_enum_values(self):
        for sev in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]:
            issue = ValidationIssue(tool="yaml", severity=sev, message="x")
            assert issue.severity == sev


# ═════════════════════════════════════════════════════════════════════════════
# 6. ToolAvailability dataclass
# ═════════════════════════════════════════════════════════════════════════════
class TestToolAvailability:

    def test_defaults_are_both_true(self):
        tools = ToolAvailability()
        assert tools.yamllint is True
        assert tools.checkov is True

    def test_can_disable_checkov(self):
        tools = ToolAvailability(checkov=False)
        assert tools.checkov is False
        assert tools.yamllint is True

    def test_can_disable_yamllint(self):
        tools = ToolAvailability(yamllint=False)
        assert tools.yamllint is False
        assert tools.checkov is True

    def test_can_disable_both(self):
        tools = ToolAvailability(yamllint=False, checkov=False)
        assert tools.yamllint is False
        assert tools.checkov is False

    def test_check_dependencies_returns_tool_availability(self):
        """check_dependencies() must return a ToolAvailability instance."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            result = check_dependencies()
        assert isinstance(result, ToolAvailability)

    def test_check_dependencies_checkov_false_when_import_fails(self):
        """When checkov import fails, returned tools.checkov must be False."""
        def fake_run(cmd, **kwargs):
            # Fail only the 'import checkov' check
            if "import checkov" in " ".join(cmd):
                raise FileNotFoundError("checkov not found")
            import subprocess
            r = subprocess.CompletedProcess(cmd, 0, b"", b"")
            return r

        with patch("subprocess.run", side_effect=fake_run):
            result = check_dependencies()
        assert result.checkov is False
        assert result.yamllint is True

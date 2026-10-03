"""
yaml_validator.output
=====================
Coloured printing helpers used throughout the package.

  print_colored()        — print a line with ANSI colour based on Severity
  print_issues()         — grouped, colour-coded issue listing
  print_summary_table()  — tabular summary of severity counts
  result_to_json()       — convert a ValidationResult to a serialisable dict
  print_json_result()    — serialise one-or-more results as JSON to stdout
  results_to_sarif()     — convert results to a SARIF v2.1.0 log (dict)
  print_sarif_result()   — serialise results as SARIF JSON to stdout
"""

from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from yaml_validator.models import ValidationResult

try:
    from colorama import Fore, Style, init

    init(autoreset=True)
except ImportError:

    class Fore:  # type: ignore[no-redef]
        RED = ""
        YELLOW = ""
        GREEN = ""
        CYAN = ""
        WHITE = ""

    class Style:  # type: ignore[no-redef]
        BRIGHT = ""
        RESET_ALL = ""


from yaml_validator import __version__
from yaml_validator.models import SEVERITY_COLORS, Severity, ValidationIssue


# ─────────────────────────────────────────────────────────────────────────────
def print_colored(text: str, severity: Severity | None = None, bold: bool = False) -> None:
    """Print text with colour based on severity."""
    color = SEVERITY_COLORS.get(severity, Fore.WHITE) if severity is not None else Fore.WHITE
    style = Style.BRIGHT if bold else ""
    print(f"{color}{style}{text}{Style.RESET_ALL}")


def print_issues(issues: list[ValidationIssue]) -> None:
    """Print issues with colour coding, grouped by severity (critical first)."""
    if not issues:
        return

    print_colored("\n📋 Issues Found:", Severity.INFO, bold=True)
    print_colored("-" * 60, Severity.INFO)

    # Group issues by severity
    severity_groups: dict[Severity, list[ValidationIssue]] = {}
    for issue in issues:
        severity_groups.setdefault(issue.severity, []).append(issue)

    # Print issues by severity (critical first)
    severity_order = [
        Severity.CRITICAL,
        Severity.HIGH,
        Severity.MEDIUM,
        Severity.LOW,
        Severity.INFO,
    ]

    for severity in severity_order:
        if severity in severity_groups:
            print_colored(f"\n{severity.value}:", severity, bold=True)
            for issue in severity_groups[severity]:
                location = ""
                if issue.line:
                    location = f" (Line {issue.line}"
                    if issue.column:
                        location += f", Col {issue.column}"
                    location += ")"

                rule_info = f" [{issue.rule}]" if issue.rule else ""
                print_colored(
                    f"  • [{issue.tool}]{rule_info} {issue.message}{location}",
                    severity,
                )


def print_summary_table(summary: dict[str, int]) -> None:
    """Print a colour-coded summary table of severity counts."""
    print_colored("\n📊 Summary Report:", Severity.INFO, bold=True)
    print_colored("=" * 60, Severity.INFO)

    # Table header
    print_colored(f"{'Severity':<12} {'Count':<8} {'Status':<20}", Severity.INFO, bold=True)
    print_colored("-" * 40, Severity.INFO)

    # Table rows
    severity_items = [
        ("CRITICAL", summary["critical"], Severity.CRITICAL),
        ("HIGH", summary["high"], Severity.HIGH),
        ("MEDIUM", summary["medium"], Severity.MEDIUM),
        ("LOW", summary["low"], Severity.LOW),
        ("INFO", summary["info"], Severity.INFO),
    ]

    for name, count, severity in severity_items:
        status = "❌ Issues Found" if count > 0 else "✅ Clean"
        print_colored(f"{name:<12} {count:<8} {status:<20}", severity)

    print_colored("-" * 40, Severity.INFO)
    total_color = Severity.CRITICAL if summary["total"] > 0 else Severity.INFO
    print_colored(
        f"{'TOTAL':<12} {summary['total']:<8} "
        f"{'Issues Found' if summary['total'] > 0 else 'All Clean'}",
        total_color,
        bold=True,
    )


def result_to_json(result: ValidationResult) -> dict:
    """Convert a ValidationResult dataclass to a plain, JSON-serialisable dict."""
    return {
        "file_path": result.file_path,
        "syntax_valid": result.syntax_valid,
        "summary": result.summary,
        "issues": [
            {
                "tool": issue.tool,
                "severity": issue.severity.value,
                "message": issue.message,
                "line": issue.line,
                "column": issue.column,
                "rule": issue.rule,
                "file_path": issue.file_path,
            }
            for issue in result.issues
        ],
    }


def print_json_result(results: list) -> None:  # list[ValidationResult]
    """Serialise one or more ValidationResult objects as pretty-printed JSON to stdout.

    No ANSI colour codes are emitted, making the output safe to pipe into
    ``jq``, ``python -m json.tool``, or any other JSON consumer.
    """
    payload = [result_to_json(r) for r in results]
    # Single-file shortcut: unwrap the list so the output is a plain object
    output = payload[0] if len(payload) == 1 else payload
    print(json.dumps(output, indent=2, ensure_ascii=False))


# ─────────────────────────────────────────────────────────────────────────────
# SARIF v2.1.0
# ─────────────────────────────────────────────────────────────────────────────
SARIF_SCHEMA_URI = "https://json.schemastore.org/sarif-2.1.0.json"
SARIF_VERSION = "2.1.0"

# SARIF only knows error / warning / note; GitHub additionally reads the
# numeric "security-severity" rule property to bucket alerts.
_SARIF_LEVEL = {
    Severity.CRITICAL: "error",
    Severity.HIGH: "error",
    Severity.MEDIUM: "warning",
    Severity.LOW: "note",
    Severity.INFO: "note",
}
_SARIF_SECURITY_SEVERITY = {
    Severity.CRITICAL: "9.5",
    Severity.HIGH: "8.0",
    Severity.MEDIUM: "5.0",
    Severity.LOW: "3.0",
    Severity.INFO: "1.0",
}


def _sarif_uri(path: str) -> str:
    """Return a forward-slash URI, relative to the cwd when possible."""
    try:
        rel = os.path.relpath(path)
        if not rel.startswith(".."):
            path = rel
    except ValueError:  # different drive on Windows
        pass
    return path.replace(os.sep, "/")


def results_to_sarif(results: list) -> dict:  # list[ValidationResult]
    """Convert validation results into a SARIF v2.1.0 log (JSON-serialisable dict)."""
    rules: dict[str, dict] = {}
    sarif_results: list[dict] = []

    for result in results:
        for issue in result.issues:
            rule_id = f"{issue.tool}/{issue.rule}" if issue.rule else issue.tool
            if rule_id not in rules:
                rules[rule_id] = {
                    "id": rule_id,
                    "shortDescription": {"text": issue.rule or issue.tool},
                    "defaultConfiguration": {"level": _SARIF_LEVEL[issue.severity]},
                    "properties": {
                        "security-severity": _SARIF_SECURITY_SEVERITY[issue.severity],
                        "tags": [issue.tool],
                    },
                }

            physical: dict = {
                "artifactLocation": {"uri": _sarif_uri(issue.file_path or result.file_path)}
            }
            if issue.line and issue.line >= 1:
                region: dict = {"startLine": issue.line}
                if issue.column and issue.column >= 1:
                    region["startColumn"] = issue.column
                physical["region"] = region

            sarif_results.append(
                {
                    "ruleId": rule_id,
                    "ruleIndex": list(rules).index(rule_id),
                    "level": _SARIF_LEVEL[issue.severity],
                    "message": {"text": issue.message},
                    "locations": [{"physicalLocation": physical}],
                    "properties": {"severity": issue.severity.value},
                }
            )

    return {
        "$schema": SARIF_SCHEMA_URI,
        "version": SARIF_VERSION,
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "yaml-validator",
                        "version": __version__,
                        "informationUri": "https://github.com/pooyanazad/YAML-validator",
                        "rules": list(rules.values()),
                    }
                },
                "results": sarif_results,
            }
        ],
    }


def print_sarif_result(results: list) -> None:  # list[ValidationResult]
    """Serialise results as a SARIF v2.1.0 log to stdout (no ANSI codes)."""
    print(json.dumps(results_to_sarif(results), indent=2, ensure_ascii=False))


__all__ = [
    "print_colored",
    "print_issues",
    "print_summary_table",
    "print_json_result",
    "print_sarif_result",
    "result_to_json",
    "results_to_sarif",
]

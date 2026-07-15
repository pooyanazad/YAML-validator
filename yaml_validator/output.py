"""
yaml_validator.output
=====================
Coloured printing helpers used throughout the package.

  print_colored()        — print a line with ANSI colour based on Severity
  print_issues()         — grouped, colour-coded issue listing
  print_summary_table()  — tabular summary of severity counts
"""

from __future__ import annotations

from typing import Dict, List

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    class Fore:  # type: ignore[no-redef]
        RED = ''
        YELLOW = ''
        GREEN = ''
        CYAN = ''
        WHITE = ''

    class Style:  # type: ignore[no-redef]
        BRIGHT = ''
        RESET_ALL = ''

from yaml_validator.models import Severity, SEVERITY_COLORS, ValidationIssue


# ─────────────────────────────────────────────────────────────────────────────
def print_colored(text: str, severity: Severity = None, bold: bool = False) -> None:
    """Print text with colour based on severity."""
    color = SEVERITY_COLORS.get(severity, Fore.WHITE)
    style = Style.BRIGHT if bold else ''
    print(f"{color}{style}{text}{Style.RESET_ALL}")


def print_issues(issues: List[ValidationIssue]) -> None:
    """Print issues with colour coding, grouped by severity (critical first)."""
    if not issues:
        return

    print_colored("\n📋 Issues Found:", Severity.INFO, bold=True)
    print_colored("-" * 60, Severity.INFO)

    # Group issues by severity
    severity_groups: Dict[Severity, List[ValidationIssue]] = {}
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


def print_summary_table(summary: Dict[str, int]) -> None:
    """Print a colour-coded summary table of severity counts."""
    print_colored("\n📊 Summary Report:", Severity.INFO, bold=True)
    print_colored("=" * 60, Severity.INFO)

    # Table header
    print_colored(f"{'Severity':<12} {'Count':<8} {'Status':<20}", Severity.INFO, bold=True)
    print_colored("-" * 40, Severity.INFO)

    # Table rows
    severity_items = [
        ('CRITICAL', summary['critical'], Severity.CRITICAL),
        ('HIGH', summary['high'], Severity.HIGH),
        ('MEDIUM', summary['medium'], Severity.MEDIUM),
        ('LOW', summary['low'], Severity.LOW),
        ('INFO', summary['info'], Severity.INFO),
    ]

    for name, count, severity in severity_items:
        status = "❌ Issues Found" if count > 0 else "✅ Clean"
        print_colored(f"{name:<12} {count:<8} {status:<20}", severity)

    print_colored("-" * 40, Severity.INFO)
    total_color = Severity.CRITICAL if summary['total'] > 0 else Severity.INFO
    print_colored(
        f"{'TOTAL':<12} {summary['total']:<8} "
        f"{'Issues Found' if summary['total'] > 0 else 'All Clean'}",
        total_color,
        bold=True,
    )


__all__ = ["print_colored", "print_issues", "print_summary_table"]

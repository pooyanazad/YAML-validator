"""
yaml_validator.validators
=========================
Core validation functions.

  validate_yaml_syntax() — PyYAML syntax check
  run_yamllint()         — yamllint linting check
  run_checkov()          — checkov security check
  validate_yaml_file()   — orchestrates all three checks for one file
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from typing import List

import yaml

from yaml_validator.models import (
    Severity,
    ToolAvailability,
    ValidationIssue,
    ValidationResult,
)
from yaml_validator.output import print_colored

# ─────────────────────────────────────────────────────────────────────────────
PYTHON_EXECUTABLE = sys.executable


# ─────────────────────────────────────────────────────────────────────────────
def validate_yaml_syntax(file_path: str) -> List[ValidationIssue]:
    """Validate YAML syntax using PyYAML."""
    issues: List[ValidationIssue] = []

    # Check file existence and read permission before opening
    if not os.path.exists(file_path):
        return [ValidationIssue(
            tool="yaml",
            severity=Severity.CRITICAL,
            message=f"File not found: {file_path}",
            file_path=file_path,
        )]
    if not os.access(file_path, os.R_OK):
        return [ValidationIssue(
            tool="yaml",
            severity=Severity.CRITICAL,
            message=f"Permission denied: {file_path}",
            file_path=file_path,
        )]

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Use safe_load_all to handle multiple documents
            list(yaml.safe_load_all(file))
    except yaml.YAMLError as e:
        mark = getattr(e, 'problem_mark', None)
        line_num = mark.line + 1 if mark else None
        column_num = mark.column + 1 if mark else None
        issues.append(ValidationIssue(
            tool="yaml",
            severity=Severity.CRITICAL,
            message=str(e),
            line=line_num,
            column=column_num,
            rule="syntax",
            file_path=file_path,
        ))
    except FileNotFoundError:
        issues.append(ValidationIssue(
            tool="yaml",
            severity=Severity.CRITICAL,
            message=f"File not found: {file_path}",
            file_path=file_path,
        ))
    except PermissionError:
        issues.append(ValidationIssue(
            tool="yaml",
            severity=Severity.CRITICAL,
            message=f"Permission denied: {file_path}",
            file_path=file_path,
        ))
    except UnicodeDecodeError as e:
        issues.append(ValidationIssue(
            tool="yaml",
            severity=Severity.CRITICAL,
            message=f"File encoding error (not valid UTF-8): {str(e)}",
            file_path=file_path,
        ))
    except OSError as e:
        issues.append(ValidationIssue(
            tool="yaml",
            severity=Severity.CRITICAL,
            message=f"File reading error: {str(e)}",
            file_path=file_path,
        ))

    return issues


# ─────────────────────────────────────────────────────────────────────────────
def run_yamllint(file_path: str, timeout: int = 300) -> List[ValidationIssue]:
    """Run yamllint and parse results."""
    issues: List[ValidationIssue] = []
    pattern = re.compile(r"^(.+?):(\d+):(\d+): \[([^\]]+)\] (.+?)(?: \(([^)]+)\))?$")

    try:
        result = subprocess.run(
            [PYTHON_EXECUTABLE, '-m', 'yamllint', '-f', 'parsable', file_path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        if result.returncode != 0 and "No module named yamllint" in result.stderr:
            issues.append(ValidationIssue(
                tool="yamllint",
                severity=Severity.HIGH,
                message="yamllint is not installed or not available in the Python environment.",
                file_path=file_path,
            ))
            return issues

        for line in result.stdout.strip().split('\n'):
            if line.strip():
                match = pattern.match(line)
                if match:
                    _parsed_file, line_num, col_num, level, message, rule = match.groups()
                    severity = Severity.MEDIUM if level == 'error' else Severity.LOW
                    issues.append(ValidationIssue(
                        tool="yamllint",
                        severity=severity,
                        message=message.strip(),
                        line=int(line_num),
                        column=int(col_num),
                        rule=rule or level,
                        file_path=file_path,
                    ))
                else:
                    # Fallback for unexpected format
                    issues.append(ValidationIssue(
                        tool="yamllint",
                        severity=Severity.MEDIUM,
                        message=line.strip(),
                        file_path=file_path,
                    ))

    except subprocess.TimeoutExpired:
        issues.append(ValidationIssue(
            tool="yamllint",
            severity=Severity.HIGH,
            message=f"yamllint execution timed out after {timeout} seconds.",
            file_path=file_path,
        ))
    except Exception as e:
        issues.append(ValidationIssue(
            tool="yamllint",
            severity=Severity.HIGH,
            message=f"yamllint execution failed: {str(e)}",
            file_path=file_path,
        ))

    return issues


# ─────────────────────────────────────────────────────────────────────────────
def run_checkov(file_path: str, timeout: int = 300) -> List[ValidationIssue]:
    """Run checkov and parse results."""
    issues: List[ValidationIssue] = []

    try:
        result = subprocess.run(
            [PYTHON_EXECUTABLE, '-m', 'checkov.main', '-f', file_path, '--output', 'json'],
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        if result.stdout.strip():
            try:
                data = json.loads(result.stdout)

                for check in data.get('results', {}).get('failed_checks', []):
                    severity = Severity.HIGH
                    if check.get('severity'):
                        severity_map = {
                            'CRITICAL': Severity.CRITICAL,
                            'HIGH': Severity.HIGH,
                            'MEDIUM': Severity.MEDIUM,
                            'LOW': Severity.LOW,
                        }
                        severity = severity_map.get(
                            check.get('severity', 'HIGH').upper(),
                            Severity.HIGH,
                        )

                    line_num = None
                    if check.get('file_line_range') and len(check['file_line_range']) > 0:
                        line_num = check['file_line_range'][0]

                    issues.append(ValidationIssue(
                        tool="checkov",
                        severity=severity,
                        message=check.get('check_name', 'Security check failed'),
                        line=line_num,
                        rule=check.get('check_id', ''),
                        file_path=file_path,
                    ))

            except json.JSONDecodeError as e:
                issues.append(ValidationIssue(
                    tool="checkov",
                    severity=Severity.MEDIUM,
                    message=f"Failed to parse checkov output: {str(e)}",
                    file_path=file_path,
                ))

    except subprocess.TimeoutExpired:
        issues.append(ValidationIssue(
            tool="checkov",
            severity=Severity.HIGH,
            message=f"checkov execution timed out after {timeout} seconds.",
            file_path=file_path,
        ))
    except Exception as e:
        issues.append(ValidationIssue(
            tool="checkov",
            severity=Severity.HIGH,
            message=f"checkov execution failed: {str(e)}",
            file_path=file_path,
        ))

    return issues


# ─────────────────────────────────────────────────────────────────────────────
def validate_yaml_file(
    file_path: str,
    tools: ToolAvailability = None,
    timeout: int = 300,
) -> ValidationResult:
    """Validate a YAML file using all available tools."""
    if tools is None:
        tools = ToolAvailability()

    print_colored(f"\n🔍 Validating: {file_path}", Severity.INFO, bold=True)
    print_colored("=" * 60, Severity.INFO)

    all_issues: List[ValidationIssue] = []
    syntax_valid = True

    # 1. Check YAML syntax
    print_colored("\n📋 Checking YAML syntax...", Severity.INFO)
    syntax_issues = validate_yaml_syntax(file_path)
    all_issues.extend(syntax_issues)

    if syntax_issues:
        syntax_valid = False
        print_colored("❌ Syntax validation failed", Severity.CRITICAL)
    else:
        print_colored("✅ Syntax validation passed", Severity.INFO)

    # 2. Run yamllint
    print_colored("\n🔧 Running yamllint...", Severity.INFO)
    yamllint_issues = run_yamllint(file_path, timeout=timeout)
    all_issues.extend(yamllint_issues)

    if yamllint_issues:
        print_colored(f"⚠️  Found {len(yamllint_issues)} linting issues", Severity.MEDIUM)
    else:
        print_colored("✅ No linting issues found", Severity.INFO)

    # 3. Run checkov (if available)
    if tools.checkov:
        print_colored("\n🔒 Running security checks (checkov)...", Severity.INFO)
        checkov_issues = run_checkov(file_path, timeout=timeout)
        all_issues.extend(checkov_issues)

        if checkov_issues:
            print_colored(f"🚨 Found {len(checkov_issues)} security issues", Severity.HIGH)
        else:
            print_colored("✅ No security issues found", Severity.INFO)
    else:
        print_colored("\n⚠️  Security checks skipped (checkov not available)", Severity.MEDIUM)

    # Generate summary
    summary = {
        'total': len(all_issues),
        'critical': len([i for i in all_issues if i.severity == Severity.CRITICAL]),
        'high': len([i for i in all_issues if i.severity == Severity.HIGH]),
        'medium': len([i for i in all_issues if i.severity == Severity.MEDIUM]),
        'low': len([i for i in all_issues if i.severity == Severity.LOW]),
        'info': len([i for i in all_issues if i.severity == Severity.INFO]),
    }

    return ValidationResult(
        file_path=file_path,
        syntax_valid=syntax_valid,
        issues=all_issues,
        summary=summary,
    )


__all__ = [
    "validate_yaml_syntax",
    "run_yamllint",
    "run_checkov",
    "validate_yaml_file",
]

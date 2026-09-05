#!/usr/bin/env python3
"""
YAML Validator — entry point.

All logic lives in the yaml_validator package:
  yaml_validator/models.py     — Severity, ValidationIssue, ValidationResult, ToolAvailability
  yaml_validator/validators.py — validate_yaml_syntax, run_yamllint, run_checkov, validate_yaml_file
  yaml_validator/output.py     — print_colored, print_issues, print_summary_table
  yaml_validator/cli.py        — check_dependencies, resolve_files, main

This file is kept as the Docker / legacy entry point and re-exports every
public symbol so that ``import app`` still works for existing test code.
"""

# ── version ───────────────────────────────────────────────────────────────────
from yaml_validator import __version__  # noqa: F401

# ── CLI ───────────────────────────────────────────────────────────────────────
from yaml_validator.cli import (  # noqa: F401
    check_dependencies,
    main,
    resolve_files,
)

# ── models ────────────────────────────────────────────────────────────────────
from yaml_validator.models import (  # noqa: F401
    SEVERITY_COLORS,
    Severity,
    ToolAvailability,
    ValidationIssue,
    ValidationResult,
)

# ── output helpers ────────────────────────────────────────────────────────────
from yaml_validator.output import (  # noqa: F401
    print_colored,
    print_issues,
    print_summary_table,
)

# ── validators ────────────────────────────────────────────────────────────────
from yaml_validator.validators import (  # noqa: F401
    run_checkov,
    run_yamllint,
    validate_yaml_file,
    validate_yaml_syntax,
)

# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()

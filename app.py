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

# ── models ────────────────────────────────────────────────────────────────────
from yaml_validator.models import (  # noqa: F401
    Severity,
    SEVERITY_COLORS,
    ValidationIssue,
    ValidationResult,
    ToolAvailability,
)

# ── validators ────────────────────────────────────────────────────────────────
from yaml_validator.validators import (  # noqa: F401
    validate_yaml_syntax,
    run_yamllint,
    run_checkov,
    validate_yaml_file,
)

# ── output helpers ────────────────────────────────────────────────────────────
from yaml_validator.output import (  # noqa: F401
    print_colored,
    print_issues,
    print_summary_table,
)

# ── CLI ───────────────────────────────────────────────────────────────────────
from yaml_validator.cli import (  # noqa: F401
    check_dependencies,
    resolve_files,
    main,
)

# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()

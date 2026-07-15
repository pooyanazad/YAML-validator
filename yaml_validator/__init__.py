"""
yaml_validator package
======================
A modular YAML validation library with syntax, linting, and security checks.

Package layout
--------------
  models.py     — dataclasses and enums (Severity, ValidationIssue, …)
  validators.py — core validation functions (validate_yaml_syntax, run_yamllint, …)
  output.py     — coloured printing helpers (print_colored, print_issues, …)
  cli.py        — argparse entry-point (main, resolve_files)
"""

__version__ = "2.1.0"

"""
yaml_validator.models
=====================
Dataclasses and enums shared across the package.

  Severity         — CRITICAL / HIGH / MEDIUM / LOW / INFO
  ValidationIssue  — one problem found in a YAML file
  ValidationResult — full result for one file
  ToolAvailability — which external tools are present

Note: models are currently imported from app.py for backward compatibility.
      They will be moved here in task #16.
"""
# Populated in task #16 (Move models to models.py).
from app import (  # noqa: F401
    Severity,
    ValidationIssue,
    ValidationResult,
    ToolAvailability,
)

__all__ = ["Severity", "ValidationIssue", "ValidationResult", "ToolAvailability"]

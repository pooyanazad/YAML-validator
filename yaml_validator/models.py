"""
yaml_validator.models
=====================
Dataclasses and enums shared across the package.

  Severity         — CRITICAL / HIGH / MEDIUM / LOW / INFO
  ValidationIssue  — one problem found in a YAML file
  ValidationResult — full result for one file
  ToolAvailability — which external tools are present
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

# ===== IMPORTS & DEPENDENCIES =====
try:
    from colorama import Fore, Style, init

    init(autoreset=True)
except ImportError:
    # Fallback if colorama is not installed
    class Fore:  # type: ignore[no-redef]
        RED = ""
        YELLOW = ""
        GREEN = ""
        CYAN = ""
        WHITE = ""

    class Style:  # type: ignore[no-redef]
        BRIGHT = ""
        RESET_ALL = ""


# ===== ENUMS =====
class Severity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


SEVERITY_COLORS: dict[Severity, str] = {
    Severity.CRITICAL: Fore.RED + Style.BRIGHT,
    Severity.HIGH: Fore.RED,
    Severity.MEDIUM: Fore.YELLOW,
    Severity.LOW: Fore.CYAN,
    Severity.INFO: Fore.GREEN,
}


# ===== DATACLASSES =====
@dataclass
class ValidationIssue:
    tool: str
    severity: Severity
    message: str
    line: int | None = None
    column: int | None = None
    rule: str | None = None
    file_path: str | None = None


@dataclass
class ValidationResult:
    file_path: str
    syntax_valid: bool
    issues: list[ValidationIssue]
    summary: dict[str, int]


@dataclass
class ToolAvailability:
    """Tracks which external tools are available on the system."""

    yamllint: bool = True
    checkov: bool = True


__all__ = [
    "SEVERITY_COLORS",
    "Severity",
    "ToolAvailability",
    "ValidationIssue",
    "ValidationResult",
]

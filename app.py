#!/usr/bin/env python3
"""
YAML Validator Script
Validates YAML files for syntax, linting, and security issues.
Usage: python3 app.py ./conf.yaml
"""

import sys
import os
import subprocess
import glob
import argparse
from pathlib import Path
from typing import Dict, List, Any

__version__ = "2.1.0"

# ===== IMPORTS & DEPENDENCIES =====
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    # Fallback if colorama is not installed
    class Fore:
        RED = ''
        YELLOW = ''
        GREEN = ''
        CYAN = ''
        WHITE = ''

    class Style:
        BRIGHT = ''
        RESET_ALL = ''

# ===== CONFIGURATION & CONSTANTS =====
PYTHON_EXECUTABLE = sys.executable

# ===== TYPES & INTERFACES (canonical home: yaml_validator/models.py) =====
from yaml_validator.models import (  # noqa: E402
    Severity,
    SEVERITY_COLORS,
    ValidationIssue,
    ValidationResult,
    ToolAvailability,
)

# ===== VALIDATORS (canonical home: yaml_validator/validators.py) =====
from yaml_validator.validators import (  # noqa: E402
    validate_yaml_syntax,
    run_yamllint,
    run_checkov,
    validate_yaml_file,
)

# ===== OUTPUT HELPERS (canonical home: yaml_validator/output.py) =====
from yaml_validator.output import (  # noqa: E402
    print_colored,
    print_issues,
    print_summary_table,
)


# ===== DEPENDENCY CHECK =====
def check_dependencies() -> ToolAvailability:
    """Check if required tools are installed and return their availability."""
    missing_tools = []
    tools = ToolAvailability()

    # Check yamllint
    try:
        subprocess.run(
            [PYTHON_EXECUTABLE, '-m', 'yamllint', '--version'],
            capture_output=True, check=True, timeout=30,
        )
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        tools.yamllint = False
        missing_tools.append('yamllint')

    # Check checkov (optional)
    try:
        subprocess.run(
            [PYTHON_EXECUTABLE, '-c', 'import checkov'],
            capture_output=True, check=True, timeout=30,
        )
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        tools.checkov = False
        print_colored("Warning: checkov not available, security checks will be skipped", Severity.MEDIUM)

    if missing_tools:
        print_colored(f"Missing required tools: {', '.join(missing_tools)}", Severity.CRITICAL, bold=True)
        print_colored("Install with: python3 -m pip install yamllint checkov", Severity.INFO)
        sys.exit(1)

    return tools


# ===== FILE RESOLUTION =====
def resolve_files(paths: List[str]) -> List[str]:
    """Resolve file paths, directories, and glob patterns to a list of YAML files."""
    yaml_extensions = {'.yaml', '.yml'}
    resolved = []
    seen = set()

    for path_arg in paths:
        # Try glob expansion first
        expanded = glob.glob(path_arg, recursive=True)

        # If glob didn't match anything, treat as literal path
        if not expanded:
            expanded = [path_arg]

        for item in expanded:
            p = Path(item).resolve()

            if p.is_dir():
                # Recursively find all YAML files in the directory
                for ext in yaml_extensions:
                    for yaml_file in sorted(p.rglob(f'*{ext}')):
                        real = str(yaml_file.resolve())
                        if real not in seen:
                            seen.add(real)
                            resolved.append(str(yaml_file))
            elif p.is_file():
                real = str(p)
                if real not in seen:
                    seen.add(real)
                    resolved.append(str(p))
            else:
                print_colored(f"Warning: '{path_arg}' not found, skipping", Severity.MEDIUM)

    return resolved


# ===== INITIALIZATION & STARTUP =====
def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        prog='yaml-validator',
        description='Validate YAML files for syntax, linting, and security issues.',
        epilog='Examples:\n'
               '  python3 app.py config.yaml\n'
               '  python3 app.py config.yaml deployment.yaml\n'
               '  python3 app.py ./configs/\n'
               '  python3 app.py ./configs/**/*.yaml\n',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'files', nargs='+', metavar='FILE',
        help='YAML files, directories, or glob patterns to validate'
    )
    parser.add_argument(
        '--version', action='version',
        version=f'%(prog)s {__version__}'
    )
    parser.add_argument(
        '--timeout', type=int, default=300,
        help='Timeout in seconds for subprocess calls (default: 300)'
    )

    args = parser.parse_args()

    # Resolve all input paths to actual YAML files
    yaml_files = resolve_files(args.files)

    if not yaml_files:
        print_colored("Error: No YAML files found for the given paths", Severity.CRITICAL, bold=True)
        sys.exit(1)

    # Check dependencies
    tools = check_dependencies()

    # Validate all files
    results = []
    has_critical_high = False
    total_issues = 0

    for yaml_file in yaml_files:
        result = validate_yaml_file(yaml_file, tools, timeout=args.timeout)
        results.append(result)

        # Print detailed issues per file
        print_issues(result.issues)

        # Print per-file summary
        print_summary_table(result.summary)

        critical_high = result.summary['critical'] + result.summary['high']
        if critical_high > 0:
            has_critical_high = True
        total_issues += result.summary['total']

    # Combined summary for multi-file runs
    if len(yaml_files) > 1:
        print_colored("\n" + "=" * 60, Severity.INFO)
        print_colored("📊 Combined Results:", Severity.INFO, bold=True)
        print_colored(f"   Files scanned: {len(yaml_files)}", Severity.INFO)
        print_colored(f"   Total issues:  {total_issues}", Severity.INFO)

        combined = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0, 'total': 0}
        for r in results:
            for key in combined:
                combined[key] += r.summary[key]
        print_summary_table(combined)

        # List files with issues
        files_with_issues = [r for r in results if r.summary['total'] > 0]
        if files_with_issues:
            print_colored("\n📁 Files with issues:", Severity.MEDIUM, bold=True)
            for r in files_with_issues:
                ch = r.summary['critical'] + r.summary['high']
                icon = "💥" if ch > 0 else "⚠️"
                print_colored(f"   {icon} {r.file_path} ({r.summary['total']} issues)", Severity.MEDIUM)

    # Final status
    print_colored("\n" + "=" * 60, Severity.INFO)
    if total_issues == 0:
        print_colored("🎉 Validation completed successfully! No issues found.", Severity.INFO, bold=True)
        sys.exit(0)
    elif has_critical_high:
        print_colored(f"💥 Validation failed! Found critical/high severity issues.", Severity.CRITICAL, bold=True)
        sys.exit(1)
    else:
        print_colored(f"⚠️  Validation completed with {total_issues} minor issues.", Severity.MEDIUM, bold=True)
        sys.exit(0)


if __name__ == "__main__":
    main()

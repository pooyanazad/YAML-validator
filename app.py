#!/usr/bin/env python3
"""
YAML Validator Script
Validates YAML files for syntax, linting, and security issues.
Usage: python app.py ./conf.yaml
"""

import sys
import os
import subprocess
import json
import yaml
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

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
CHECKOV_AVAILABLE = True

class Severity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

SEVERITY_COLORS = {
    Severity.CRITICAL: Fore.RED + Style.BRIGHT,
    Severity.HIGH: Fore.RED,
    Severity.MEDIUM: Fore.YELLOW,
    Severity.LOW: Fore.CYAN,
    Severity.INFO: Fore.GREEN
}

# ===== TYPES & INTERFACES =====
@dataclass
class ValidationIssue:
    tool: str
    severity: Severity
    message: str
    line: int = None
    column: int = None
    rule: str = None
    file_path: str = None

@dataclass
class ValidationResult:
    file_path: str
    syntax_valid: bool
    issues: List[ValidationIssue]
    summary: Dict[str, int]

# ===== UTILITY FUNCTIONS =====
def print_colored(text: str, severity: Severity = None, bold: bool = False):
    """Print text with color based on severity"""
    color = SEVERITY_COLORS.get(severity, Fore.WHITE)
    style = Style.BRIGHT if bold else ''
    print(f"{color}{style}{text}{Style.RESET_ALL}")

def check_dependencies():
    """Check if required tools are installed"""
    missing_tools = []
    global CHECKOV_AVAILABLE
    CHECKOV_AVAILABLE = True
    
    # Check yamllint
    try:
        subprocess.run(['python', '-m', 'yamllint', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing_tools.append('yamllint')
    
    # Check checkov (optional)
    try:
        subprocess.run(['python', '-c', 'import checkov'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        CHECKOV_AVAILABLE = False
        print_colored("Warning: checkov not available, security checks will be skipped", Severity.MEDIUM)
    
    if missing_tools:
        print_colored(f"Missing required tools: {', '.join(missing_tools)}", Severity.CRITICAL, bold=True)
        print_colored("Install with: pip install yamllint checkov", Severity.INFO)
        sys.exit(1)

def validate_yaml_syntax(file_path: str) -> List[ValidationIssue]:
    """Validate YAML syntax"""
    issues = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Use safe_load_all to handle multiple documents
            list(yaml.safe_load_all(file))
    except yaml.YAMLError as e:
        line = getattr(e, 'problem_mark', None)
        line_num = line.line + 1 if line else None
        column_num = line.column + 1 if line else None
        
        issues.append(ValidationIssue(
            tool="yaml",
            severity=Severity.CRITICAL,
            message=str(e),
            line=line_num,
            column=column_num,
            rule="syntax",
            file_path=file_path
        ))
    except Exception as e:
        issues.append(ValidationIssue(
            tool="yaml",
            severity=Severity.CRITICAL,
            message=f"File reading error: {str(e)}",
            file_path=file_path
        ))
    
    return issues

def run_yamllint(file_path: str) -> List[ValidationIssue]:
    """Run yamllint and parse results"""
    issues = []
    try:
        result = subprocess.run(
            ['python', '-m', 'yamllint', '-f', 'parsable', file_path],
            capture_output=True,
            text=True
        )
        
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                parts = line.split(':')
                if len(parts) >= 4:
                    line_num = int(parts[1]) if parts[1].isdigit() else None
                    column_num = int(parts[2]) if parts[2].isdigit() else None
                    level = parts[3].strip().strip('[]')
                    message = ':'.join(parts[4:]).strip()
                    
                    severity = Severity.MEDIUM if level == 'error' else Severity.LOW
                    
                    issues.append(ValidationIssue(
                        tool="yamllint",
                        severity=severity,
                        message=message,
                        line=line_num,
                        column=column_num,
                        rule=level,
                        file_path=file_path
                    ))
    
    except Exception as e:
        issues.append(ValidationIssue(
            tool="yamllint",
            severity=Severity.HIGH,
            message=f"yamllint execution failed: {str(e)}",
            file_path=file_path
        ))
    
    return issues

def run_checkov(file_path: str) -> List[ValidationIssue]:
    """Run checkov and parse results"""
    issues = []
    try:
        result = subprocess.run(
            ['python', '-m', 'checkov.main', '-f', file_path, '--output', 'json'],
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip():
            try:
                data = json.loads(result.stdout)
                
                # Parse failed checks
                for check in data.get('results', {}).get('failed_checks', []):
                    # Map checkov severity or default to HIGH for security issues
                    severity = Severity.HIGH
                    if check.get('severity'):
                        severity_map = {
                            'CRITICAL': Severity.CRITICAL,
                            'HIGH': Severity.HIGH,
                            'MEDIUM': Severity.MEDIUM,
                            'LOW': Severity.LOW
                        }
                        severity = severity_map.get(
                            check.get('severity', 'HIGH').upper(),
                            Severity.HIGH
                        )
                    
                    # Get line number from file_line_range
                    line_num = None
                    if check.get('file_line_range') and len(check['file_line_range']) > 0:
                        line_num = check['file_line_range'][0]
                    
                    issues.append(ValidationIssue(
                        tool="checkov",
                        severity=severity,
                        message=check.get('check_name', 'Security check failed'),
                        line=line_num,
                        rule=check.get('check_id', ''),
                        file_path=file_path
                    ))
            
            except json.JSONDecodeError as e:
                issues.append(ValidationIssue(
                    tool="checkov",
                    severity=Severity.MEDIUM,
                    message=f"Failed to parse checkov output: {str(e)}",
                    file_path=file_path
                ))
    
    except Exception as e:
        issues.append(ValidationIssue(
            tool="checkov",
            severity=Severity.HIGH,
            message=f"checkov execution failed: {str(e)}",
            file_path=file_path
        ))
    
    return issues

# ===== CORE BUSINESS LOGIC =====
def validate_yaml_file(file_path: str) -> ValidationResult:
    """Validate a YAML file using all available tools"""
    print_colored(f"\n🔍 Validating: {file_path}", Severity.INFO, bold=True)
    print_colored("=" * 60, Severity.INFO)
    
    all_issues = []
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
    yamllint_issues = run_yamllint(file_path)
    all_issues.extend(yamllint_issues)
    
    if yamllint_issues:
        print_colored(f"⚠️  Found {len(yamllint_issues)} linting issues", Severity.MEDIUM)
    else:
        print_colored("✅ No linting issues found", Severity.INFO)
    
    # 3. Run checkov (if available)
    if CHECKOV_AVAILABLE:
        print_colored("\n🔒 Running security checks (checkov)...", Severity.INFO)
        checkov_issues = run_checkov(file_path)
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
        'info': len([i for i in all_issues if i.severity == Severity.INFO])
    }
    
    return ValidationResult(
        file_path=file_path,
        syntax_valid=syntax_valid,
        issues=all_issues,
        summary=summary
    )

def print_issues(issues: List[ValidationIssue]):
    """Print issues with color coding"""
    if not issues:
        return
    
    print_colored("\n📋 Issues Found:", Severity.INFO, bold=True)
    print_colored("-" * 60, Severity.INFO)
    
    # Group issues by severity
    severity_groups = {}
    for issue in issues:
        if issue.severity not in severity_groups:
            severity_groups[issue.severity] = []
        severity_groups[issue.severity].append(issue)
    
    # Print issues by severity (critical first)
    severity_order = [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]
    
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
                print_colored(f"  • [{issue.tool}]{rule_info} {issue.message}{location}", severity)

def print_summary_table(summary: Dict[str, int]):
    """Print summary table with colors"""
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
        ('INFO', summary['info'], Severity.INFO)
    ]
    
    for name, count, severity in severity_items:
        status = "❌ Issues Found" if count > 0 else "✅ Clean"
        print_colored(f"{name:<12} {count:<8} {status:<20}", severity)
    
    print_colored("-" * 40, Severity.INFO)
    total_color = Severity.CRITICAL if summary['total'] > 0 else Severity.INFO
    print_colored(f"{'TOTAL':<12} {summary['total']:<8} {'Issues Found' if summary['total'] > 0 else 'All Clean'}", total_color, bold=True)

# ===== INITIALIZATION & STARTUP =====
def main():
    """Main function"""
    if len(sys.argv) != 2:
        print_colored("Usage: python app.py <yaml_file>", Severity.CRITICAL, bold=True)
        print_colored("Example: python app.py ./conf.yaml", Severity.INFO)
        sys.exit(1)
    
    yaml_file = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(yaml_file):
        print_colored(f"Error: File '{yaml_file}' not found", Severity.CRITICAL, bold=True)
        sys.exit(1)
    
    # Check dependencies
    check_dependencies()
    
    # Validate the file
    result = validate_yaml_file(yaml_file)
    
    # Print detailed issues
    print_issues(result.issues)
    
    # Print summary table
    print_summary_table(result.summary)
    
    # Final status
    print_colored("\n" + "=" * 60, Severity.INFO)
    if result.summary['total'] == 0:
        print_colored("🎉 Validation completed successfully! No issues found.", Severity.INFO, bold=True)
        sys.exit(0)
    else:
        critical_high = result.summary['critical'] + result.summary['high']
        if critical_high > 0:
            print_colored(f"💥 Validation failed! Found {critical_high} critical/high severity issues.", Severity.CRITICAL, bold=True)
            sys.exit(1)
        else:
            print_colored(f"⚠️  Validation completed with {result.summary['total']} minor issues.", Severity.MEDIUM, bold=True)
            sys.exit(0)

if __name__ == "__main__":
    main()
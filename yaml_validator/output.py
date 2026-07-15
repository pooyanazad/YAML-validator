"""
yaml_validator.output
=====================
Coloured printing helpers: print_colored, print_issues, print_summary_table.

Note: functions are currently imported from app.py for backward compatibility.
      They will be moved here in task #18.
"""
# Populated in task #18 (Move output to output.py).
# Importing from app keeps backward compatibility in the meantime.
from app import print_colored, print_issues, print_summary_table  # noqa: F401

__all__ = ["print_colored", "print_issues", "print_summary_table"]

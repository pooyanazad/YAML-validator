"""
yaml_validator.cli
==================
Argparse entry-point: main() and resolve_files().

Note: functions are currently imported from app.py for backward compatibility.
      They will be moved here in task #19.
"""
# Populated in task #19 (Move CLI to cli.py).
from app import main, resolve_files  # noqa: F401

__all__ = ["main", "resolve_files"]

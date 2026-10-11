"""Keep existing Python imports and command integrations working after the rename."""

import importlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

import yaml_validator
import yamlguard


def test_legacy_version_matches_the_canonical_package():
    assert yaml_validator.__version__ == yamlguard.__version__


@pytest.mark.parametrize("module_name", ["cli", "models", "output", "validators"])
def test_legacy_submodules_are_the_same_objects(module_name):
    legacy = importlib.import_module(f"yaml_validator.{module_name}")
    canonical = importlib.import_module(f"yamlguard.{module_name}")
    assert legacy is canonical


def test_existing_entrypoints_produce_the_same_report(clean_file):
    root = Path(__file__).resolve().parents[1]
    commands = [
        [sys.executable, "-m", "yamlguard"],
        [sys.executable, "-m", "yaml_validator"],
        [sys.executable, str(root / "app.py")],
    ]
    reports = []
    for command in commands:
        result = subprocess.run(
            [*command, clean_file, "--no-security", "--format", "json"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0, result.stderr
        reports.append(json.loads(result.stdout))
    assert reports[0] == reports[1] == reports[2]

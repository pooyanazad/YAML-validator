"""Read release metadata from its source commit, including pre-rename tags."""

from __future__ import annotations

import re
import subprocess

DEFAULT_IMAGE = "pooyanazad/yamlguard"


def source_file(head: str, path: str) -> str | None:
    result = subprocess.run(
        ["git", "show", f"{head}:{path}"], capture_output=True, text=True, check=False
    )
    return result.stdout if result.returncode == 0 else None


def package_version(head: str) -> str:
    for path in ("yamlguard/__init__.py", "yaml_validator/__init__.py"):
        source = source_file(head, path)
        if source is None:
            continue
        match = re.search(r'^__version__ = "(\d+\.\d+\.\d+)"$', source, re.MULTILINE)
        if not match:
            raise ValueError("Package must define one stable X.Y.Z version")
        return match[1]
    raise ValueError("Cannot locate the package version in the released source")


def docker_image(head: str) -> str:
    workflow = source_file(head, ".github/workflows/docker-build.yml")
    if workflow is not None:
        match = re.search(
            r"^\s+IMAGE_NAME:\s*['\"]?([\w./-]+)['\"]?\s*(?:#.*)?$", workflow, re.MULTILINE
        )
        if match:
            return match[1]
    return DEFAULT_IMAGE

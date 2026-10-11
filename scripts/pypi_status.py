"""Check publication status; only HTTP 404 means an unpublished PyPI version."""

from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen


def is_published(version: str) -> bool:
    try:
        with urlopen(f"https://pypi.org/pypi/yamlguard/{version}/json", timeout=30) as response:  # noqa: S310
            data = json.load(response)
    except HTTPError as error:
        if error.code == HTTPStatus.NOT_FOUND:
            return False
        raise
    if data["info"]["version"] != version:
        raise ValueError("PyPI returned an unexpected package version")
    if not data["urls"]:
        raise ValueError(
            "PyPI version exists without files; inspect it before retrying publication"
        )
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    published = is_published(args.version)
    with args.output.open("a") as output:
        output.write(f"published={str(published).lower()}\n")
    status = "already published; no upload" if published else "not published"
    print(f"yamlguard {args.version}: {status}")


if __name__ == "__main__":
    main()

"""Plan a release from the package version, without inventing a new version."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from scripts.release_metadata import package_version
from scripts.release_notes import TAG_PATTERN, previous_tag, tag_key


def validate_tag(tag: str, head: str) -> str:
    tag_key(tag)
    version = package_version(head)
    if tag.split("-", 1)[0] != f"v{version}":
        raise ValueError(f"Tag {tag!r} does not match package version {version}")
    return version


def plan(head: str, event: str, manual_tag: str, released: list[str], date: str) -> dict[str, str]:
    version = package_version(head)
    tag = manual_tag or f"v{version}-{date}"
    validate_tag(tag, head)
    publishing = event in {"schedule", "workflow_dispatch"}
    published = [t for t in released if TAG_PATTERN.fullmatch(t)]
    same = [t for t in published if tag_key(t)[:3] == tag_key(tag)[:3]]
    if publishing and any(tag_key(t)[:3] > tag_key(tag)[:3] for t in published):
        raise ValueError("Package version is older than a published release; refusing downgrade")
    if event == "workflow_dispatch" and same:
        raise ValueError(
            f"Package {version} already has a GitHub release ({same[0]}). "
            "Bump __version__ for a new release. "
            "To retry PyPI, run release.yml with the existing tag."
        )
    publish = publishing and not same
    # CI and monthly rolling-image refreshes do not create or validate a new immutable tag.
    base = previous_tag(tag, head) if publish else ""
    return {
        "version": tag,
        "package_version": version,
        "latest_tag": base,
        "publish_release": str(publish).lower(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--event", required=True)
    parser.add_argument("--manual-tag", default="")
    parser.add_argument("--releases", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    releases = json.loads(args.releases.read_text())
    released = [r["tag_name"] for r in releases if not r["draft"]]
    result = plan(
        args.head,
        args.event,
        args.manual_tag,
        released,
        datetime.now(timezone.utc).strftime("%Y%m%d"),
    )
    with args.output.open("a") as output:
        for key, value in result.items():
            output.write(f"{key}={value}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

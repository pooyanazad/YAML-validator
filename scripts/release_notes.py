"""Generate release and README notes from one validated Git range (stdlib only)."""

from __future__ import annotations

import argparse
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

try:
    from scripts.release_metadata import docker_image, package_version
except ModuleNotFoundError:
    # The workflows also invoke this file directly from the repository root.
    from release_metadata import docker_image, package_version

TAG_PATTERN = re.compile(r"v(\d+)\.(\d+)\.(\d+)(?:-(\d{8}))?")
START = "<!-- RELEASE_NOTES_START -->"
END = "<!-- RELEASE_NOTES_END -->"


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def tag_key(tag: str) -> tuple[int, ...]:
    match = TAG_PATTERN.fullmatch(tag)
    if not match:
        raise ValueError(f"Invalid release tag: {tag!r}; expected vX.Y.Z[-YYYYMMDD]")
    if match.group(4):
        datetime.strptime(match.group(4), "%Y%m%d")
    return tuple(int(part or 0) for part in match.groups())


def previous_tag(version: str, head: str) -> str:
    """Find the preceding version on this history, excluding the release being built."""
    target_key = tag_key(version)
    head_sha = git("rev-parse", f"{head}^{{commit}}")
    existing = subprocess.run(
        ["git", "rev-parse", "--verify", f"refs/tags/{version}^{{commit}}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if existing.returncode == 0 and existing.stdout.strip() != head_sha:
        raise ValueError("Release tag points to another commit; use a new version")
    tags = git("tag", "--merged", head).splitlines()
    candidates = [tag for tag in tags if TAG_PATTERN.fullmatch(tag) and tag_key(tag) < target_key]
    return max(candidates, key=tag_key) if candidates else ""


def category(subject: str) -> str:
    prefix = subject.split(":", 1)[0].split("(", 1)[0].lower()
    if prefix == "test" or subject.startswith("Add tests "):
        return "Tests"
    if prefix == "feat" or subject.startswith("Add "):
        return "Features"
    if prefix == "fix":
        return "Fixes"
    if prefix == "docs":
        return "Documentation"
    if "deps" in subject.lower() or prefix == "deps":
        return "Dependencies"
    return "Build and maintenance"


def collect_commits(base: str, head: str) -> list[tuple[str, str]]:
    if base:
        # A missing or unrelated base must fail, never silently include all history.
        subprocess.run(["git", "merge-base", "--is-ancestor", base, head], check=True)
    revision = f"{base}..{head}" if base else head
    commits = []
    for line in git("log", revision, "--no-merges", "--format=%H%x09%s").splitlines():
        sha, subject = line.split("\t", 1)
        commits.append((sha, subject))
    return commits


def highlights(version: str, base: str, commits: list[tuple[str, str]]) -> str:
    fragment = Path("release-notes") / f"{version}.md"
    if not fragment.exists():
        fragment = Path("release-notes") / f"{version.split('-', 1)[0]}.md"
    if fragment.exists():
        content = fragment.read_text(encoding="utf-8")
        marker = f"<!-- previous-tag: {base} -->"
        if not content.startswith(marker):
            raise ValueError(f"{fragment} must begin with {marker}")
        return content[len(marker) :].strip()
    if not commits:
        return "No source changes since the previous release."
    # Unknown releases get factual counts, never recycled feature claims.
    counts = Counter(category(subject) for _, subject in commits)
    return "\n".join(f"- {name}: {count} commit(s)." for name, count in counts.items())


def update_readme(path: Path, block: str) -> None:
    content = path.read_text(encoding="utf-8")
    if content.count(START) != 1 or content.count(END) != 1:
        raise ValueError("README must contain exactly one pair of release-note markers")
    updated, count = re.subn(
        re.escape(START) + r".*?" + re.escape(END),
        lambda _: f"{START}\n{block}\n{END}",
        content,
        flags=re.DOTALL,
    )
    if count != 1:
        raise ValueError("README release-note markers are out of order")
    path.write_text(updated, encoding="utf-8")


def generate(args: argparse.Namespace) -> None:  # noqa: PLR0912, PLR0915
    tag_key(args.version)
    match = TAG_PATTERN.fullmatch(args.version)
    assert match is not None
    if not args.date:
        suffix = match.group(4)
        args.date = (
            datetime.strptime(suffix, "%Y%m%d").date().isoformat()
            if suffix
            else datetime.now(timezone.utc).date().isoformat()
        )
    head = git("rev-parse", f"{args.head}^{{commit}}")
    base = previous_tag(args.version, head)
    if args.previous_tag is not None and args.previous_tag != base:
        raise ValueError(f"Expected previous tag {base!r}, got {args.previous_tag!r}")
    commits = collect_commits(base, head)
    summary = highlights(args.version, base, commits)
    repo_url = f"https://github.com/{args.repository}"
    comparison = (
        f"[Full changelog]({repo_url}/compare/{base}...{args.version})"
        if base
        else f"[Initial release history]({repo_url}/commits/{args.version})"
    )
    scope = f"Changes since `{base}`" if base else "Initial release"
    image = args.image or docker_image(head)
    block = (
        f"### {args.version} — {args.date}\n\n"
        f"**{scope}** ({len(commits)} non-merge commits).\n\n"
        f"{summary}\n\n{comparison}\n\n"
        f"**Docker image:** `{image}:{args.version}`\n"
    )
    body = block.replace(f"### {args.version}", f"## yamlguard {args.version}", 1)
    body += "\n### Use this release\n\n"
    # Read the package version from the released source, including historical releases.
    project = subprocess.run(
        ["git", "show", f"{head}:pyproject.toml"], capture_output=True, text=True, check=False
    )
    if project.returncode == 0 and 'name = "yamlguard"' in project.stdout:
        version = package_version(head)
        body += (
            "PyPI installation once this package version is published (syntax and linting):\n\n"
            "```bash\n"
            f"python -m pip install 'yamlguard=={version}'\n"
            "yamlguard myfile.yaml\n```\n\n"
            f"For Checkov scanning, install `yamlguard[security]=={version}`.\n\n"
        )
    body += (
        "Docker (includes Checkov; Linux/macOS shell):\n\n```bash\n"
        f'docker run --rm -v "$(pwd):/data:ro" {image}:{args.version} myfile.yaml\n'
        "```\n\n"
        f"[Usage and options]({repo_url}/blob/{args.version}/README.md)\n"
    )
    if commits:
        body += "\n<details>\n<summary>Commit details for this release</summary>\n\n"
        for name in dict.fromkeys(category(subject) for _, subject in commits):
            body += f"#### {name}\n\n"
            for sha, subject in commits:
                if category(subject) == name:
                    # Escape subject Markdown; replacement is not interpreted by re.sub.
                    title = re.sub(r"([\\`*_\[\]<>])", r"\\\1", subject)
                    body += f"- {title} ([{sha[:7]}]({repo_url}/commit/{sha}))\n"
            body += "\n"
        body += "</details>\n"
    args.output.write_text(body, encoding="utf-8")
    if args.readme:
        update_readme(args.readme, block)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True)
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--previous-tag")
    parser.add_argument("--print-previous-tag", action="store_true")
    parser.add_argument("--date", default="")
    parser.add_argument("--repository", default="pooyanazad/yamlguard")
    parser.add_argument("--image", help="Override the Docker image recorded in the released source")
    parser.add_argument("--readme", type=Path)
    parser.add_argument("--output", type=Path, default=Path("release-body.md"))
    args = parser.parse_args()
    if args.print_previous_tag:
        print(previous_tag(args.version, args.head))
    else:
        generate(args)


if __name__ == "__main__":
    main()

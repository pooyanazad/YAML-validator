"""Release regression tests using real temporary Git histories."""

import argparse
import subprocess

import pytest

from scripts import release_notes as notes


@pytest.fixture
def history(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    subprocess.run(["git", "init", "-q"], check=True)
    subprocess.run(["git", "config", "user.name", "Release Test"], check=True)
    subprocess.run(["git", "config", "user.email", "release@example.invalid"], check=True)

    def commit(subject):
        subprocess.run(["git", "commit", "--allow-empty", "-qm", subject], check=True)
        return notes.git("rev-parse", "HEAD")

    commit("Initial feature, already shipped")
    subprocess.run(["git", "tag", "v3.3.0-20260901"], check=True)
    commit("feat: New output")
    head = commit("fix: New package fix")
    return tmp_path, head, commit


def args(head, output, version="v3.4.0-20261011", base=None, readme=None):
    return argparse.Namespace(
        version=version,
        head=head,
        previous_tag=base,
        date="2026-10-11",
        repository="example/validator",
        image="example/validator",
        readme=readme,
        output=output,
    )


def test_retry_excludes_current_tag_and_old_commits(history):
    root, head, _ = history
    subprocess.run(["git", "tag", "v3.4.0-20261011"], check=True)
    assert notes.previous_tag("v3.4.0-20261011", head) == "v3.3.0-20260901"
    output = root / "body.md"
    notes.generate(args(head, output))
    body = output.read_text()
    assert "2 non-merge commits" in body
    assert "New output" in body and "New package fix" in body
    assert "already shipped" not in body
    assert "compare/v3.3.0-20260901...v3.4.0-20261011" in body
    assert "### Quick Start" not in body


def test_current_release_is_pinned_and_rejects_moved_head(history):
    root, head, commit = history
    subprocess.run(["git", "tag", "v3.4.0-20261011"], check=True)
    later = commit("Unreleased work")
    notes.generate(args(head, root / "body.md"))
    assert "Unreleased work" not in (root / "body.md").read_text()
    with pytest.raises(ValueError, match="another commit"):
        notes.generate(args(later, root / "bad.md"))


def test_tag_on_unrelated_branch_is_not_previous_release(history):
    _, head, commit = history
    subprocess.run(["git", "checkout", "-qb", "unrelated", "v3.3.0-20260901"], check=True)
    commit("Unrelated feature")
    subprocess.run(["git", "tag", "v3.3.1-20260920"], check=True)
    assert notes.previous_tag("v3.4.0-20261011", head) == "v3.3.0-20260901"
    with pytest.raises(subprocess.CalledProcessError):
        notes.collect_commits("v3.3.1-20260920", head)


def test_wrong_or_missing_base_does_not_expand_to_all_history(history):
    root, head, _ = history
    with pytest.raises(ValueError, match="Expected previous tag"):
        notes.generate(args(head, root / "bad.md", base=""))
    with pytest.raises(subprocess.CalledProcessError):
        notes.collect_commits("missing-tag", head)


def test_initial_release_has_explicit_history(history):
    root, _, _ = history
    initial = notes.git("rev-parse", "v3.3.0-20260901")
    notes.generate(args(initial, root / "body.md", version="v3.0.0-20260601"))
    assert "Initial release" in (root / "body.md").read_text()
    assert "already shipped" in (root / "body.md").read_text()


def test_no_changes_does_not_claim_dependency_updates(history):
    root, _, _ = history
    initial = notes.git("rev-parse", "v3.3.0-20260901")
    notes.generate(args(initial, root / "body.md"))
    assert "No source changes" in (root / "body.md").read_text()
    assert "latest dependencies" not in (root / "body.md").read_text()


def test_curated_notes_apply_only_to_their_range(history):
    root, head, _ = history
    fragments = root / "release-notes"
    fragments.mkdir()
    fragment = fragments / "v3.4.0-20261011.md"
    fragment.write_text("<!-- previous-tag: v3.3.0-20260901 -->\n- New output support.\n")
    readme = root / "README.md"
    readme.write_text(f"Intro\n{notes.START}\nOld notes\n{notes.END}\nFooter")
    notes.generate(args(head, root / "body.md", readme=readme))
    assert "New output support." in readme.read_text()
    assert "New output support." in (root / "body.md").read_text()
    assert "Commit details" not in readme.read_text()
    assert "Intro" in readme.read_text() and "Footer" in readme.read_text()
    fragment.write_text("<!-- previous-tag: wrong-tag -->\n- Old feature.")
    with pytest.raises(ValueError, match="must begin"):
        notes.generate(args(head, root / "bad.md"))


def test_readme_replacement_keeps_literal_backslashes(history):
    root, _, _ = history
    readme = root / "README.md"
    readme.write_text(f"{notes.START}\nOld\n{notes.END}")
    notes.update_readme(readme, r"New example: \1 and \n")
    assert r"New example: \1 and \n" in readme.read_text()
    readme.write_text("No markers")
    with pytest.raises(ValueError, match="exactly one pair"):
        notes.update_readme(readme, "New")


@pytest.mark.parametrize("module_name", ["yamlguard", "yaml_validator"])
def test_package_install_version_comes_from_source(history, module_name):
    root, _, _ = history
    package = root / module_name
    package.mkdir()
    (package / "__init__.py").write_text('__version__ = "3.4.0"\n')
    (root / "pyproject.toml").write_text('[project]\nname = "yamlguard"\n')
    subprocess.run(["git", "add", "pyproject.toml", f"{module_name}/__init__.py"], check=True)
    subprocess.run(["git", "commit", "-qm", "chore: Package metadata"], check=True)
    notes.generate(args("HEAD", root / "body.md", version="v3.5.0-20261101"))
    body = (root / "body.md").read_text()
    assert "yamlguard==3.4.0" in body
    assert "example/validator:v3.5.0-20261101" in body


@pytest.mark.parametrize("image", ["pooyanazad/yaml-checker", "pooyanazad/yamlguard"])
def test_refresh_uses_the_image_from_the_released_source(history, image):
    root, _, commit = history
    directory = root / ".github/workflows"
    directory.mkdir(parents=True)
    (directory / "docker-build.yml").write_text(f"env:\n  IMAGE_NAME: {image}\n")
    subprocess.run(["git", "add", ".github/workflows/docker-build.yml"], check=True)
    head = commit("chore: Docker publication configuration")
    options = args(head, root / "body.md")
    options.image = None
    notes.generate(options)
    body = (root / "body.md").read_text()
    assert f"**Docker image:** `{image}:{options.version}`" in body
    assert f"{image}:{options.version} myfile.yaml" in body


def test_annotated_tags_and_numeric_version_order(history):
    _, head, _ = history
    subprocess.run(["git", "tag", "-a", "v3.9.0-20270101", "-m", "Release"], check=True)
    assert notes.previous_tag("v3.10.0-20270201", head) == "v3.9.0-20270101"


def test_new_tests_are_not_presented_as_product_features():
    assert notes.category("Add tests that check SARIF against its schema") == "Tests"
    assert notes.category("Add SARIF output") == "Features"


@pytest.mark.parametrize("version", ["$(whoami)", "--all", "v3.4", "v3.4.0/inject"])
def test_invalid_release_tag_is_rejected(version):
    with pytest.raises(ValueError, match="Invalid release tag"):
        notes.tag_key(version)


def test_version_highlights_fallback_and_dated_override(history):
    root, head, _ = history
    directory = root / "release-notes"
    directory.mkdir()
    marker = "<!-- previous-tag: v3.3.0-20260901 -->\n"
    (directory / "v3.4.0.md").write_text(marker + "- Reviewed release summary.")
    notes.generate(args(head, root / "body.md"))
    assert "Reviewed release summary" in (root / "body.md").read_text()
    (directory / "v3.4.0-20261011.md").write_text(marker + "- Date-specific override.")
    notes.generate(args(head, root / "body.md"))
    assert "Date-specific override" in (root / "body.md").read_text()
    assert "Reviewed release summary" not in (root / "body.md").read_text()

# YAML Validator

[![CI](https://github.com/pooyanazad/YAML-validator/actions/workflows/docker-build.yml/badge.svg)](https://github.com/pooyanazad/YAML-validator/actions/workflows/docker-build.yml)
[![PyPI](https://img.shields.io/pypi/v/yamlguard.svg)](https://pypi.org/project/yamlguard/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Validate YAML files for syntax errors, style issues, and security misconfigurations — all in one command. Available as a Python CLI (`yamlguard`) via PyPI and as a Docker container (`pooyanazad/yaml-checker`).

<img width="881" height="571" alt="YAML Validator output" src="https://github.com/user-attachments/assets/0a3278f9-9f86-431c-90f7-e3d122f0043b" />

---

## Installation & Getting Started

### Option 1: Install from PyPI (Recommended)

Run directly on your host machine without needing Docker:

```bash
# Standard installation (syntax validation + yamllint)
pip install yamlguard

# Or install with Checkov security scanning support
pip install "yamlguard[security]"

# Or run instantly with pipx (isolated environment)
pipx install yamlguard
```

Once installed, use `yamlguard` directly:

```bash
yamlguard myfile.yaml
```

---

### Option 2: Run with Docker

Zero-dependency execution using the official Docker container.

#### One-time setup (Linux/macOS)

Create the `ytest` shortcut:

```bash
# Bash
echo 'alias ytest="docker run --rm -v \"\$(pwd):/data\" pooyanazad/yaml-checker"' >> ~/.bashrc && source ~/.bashrc
```

<details>
<summary>Using Zsh instead?</summary>

```bash
echo 'alias ytest="docker run --rm -v \"\$(pwd):/data\" pooyanazad/yaml-checker"' >> ~/.zshrc && source ~/.zshrc
```

</details>

Now you can use `ytest` anywhere.

<details>
<summary>Windows / without the alias</summary>

**PowerShell / CMD:**
```bash
docker run --rm -v "%cd%:/data" pooyanazad/yaml-checker myfile.yaml
```

**Git Bash:**
```bash
MSYS_NO_PATHCONV=1 docker run --rm -v "$(pwd):/data" pooyanazad/yaml-checker myfile.yaml
```

**Linux/macOS (no alias):**
```bash
docker run --rm -v "$(pwd):/data" pooyanazad/yaml-checker myfile.yaml
```

</details>

---

## Usage

You can run `yamlguard` (if installed via pip) or `ytest` (if using Docker):

```bash
# Single file
yamlguard myfile.yaml

# Multiple files
yamlguard config.yaml deployment.yaml secrets.yaml

# Entire directory (recursive)
yamlguard ./configs/

# Glob pattern
yamlguard ./configs/**/*.yaml
```

### Output Formats

Export results to CI/CD tools and code scanners with `--format` (`-f`):

```bash
# Coloured human-readable summary (default)
yamlguard myfile.yaml --format text

# Machine-readable JSON
yamlguard myfile.yaml --format json

# JUnit XML (compatible with Jenkins, GitLab, Azure DevOps)
yamlguard myfile.yaml --format junit > test-results.xml

# SARIF v2.1.0 (for GitHub Code Scanning)
yamlguard myfile.yaml --format sarif > results.sarif
```

---

## What It Checks

| Layer | Tool | What it catches |
|---|---|---|
| **Syntax** | PyYAML | Parse errors, broken structure, invalid indentation |
| **Linting** | yamllint | Style issues, line length, trailing spaces, consistency |
| **Security** | Checkov | Hardcoded secrets, privileged containers, misconfigurations |

Issues are grouped by severity (**Critical → High → Medium → Low**) with colored output and a summary table. When scanning multiple files, you get a combined report showing which files have problems.

---

## Features

✅ Native Python CLI (`yamlguard`) & Multi-arch Docker image  
✅ Multi-file & directory scanning  
✅ Glob pattern support (`**/*.yaml`)  
✅ Multiple output formats: Text, JSON, JUnit XML, SARIF v2.1.0  
✅ Cross-platform (Windows, Linux, macOS)  
✅ Colored severity-based reporting  
✅ Zero configuration required  

---

## Docker Image

| | |
|---|---|
| **Image** | `pooyanazad/yaml-checker` |
| **Tag** | `latest` is always up to date |
| **Base** | `python:3.12-slim` |
| **Platforms** | `linux/amd64`, `linux/arm64` |

---

## Release Notes

<!-- RELEASE_NOTES_START -->
### v3.4.0-20261011 — 2026-10-11

**Changes since last release:**
* fix(ci): add pull-requests write permission and continue-on-error to release-notes PR step (8fdde93)
* ci: allow manual tag input on dispatch and auto-trigger pypi release workflow (2263602)
* docs: update README with PyPI yamlguard installation, formats, and v3.4.0 release notes (acd57c6)
* chore: bump version to 3.4.0 and fix release workflow python version (a0cbd0e)
* chore: remove redundant ci.yml, docker-build.yml already handles CI (2cf7b61)
* fix: remove black from CI, fix checkov packaging conflict in test deps (afb876f)
* chore: add PyPI packaging as yamlguard (5732bd2)
* chore(deps-dev): bump the dev-deps group across 1 directory with 2 updates (#40) (9bc406a)
* chore(deps): bump checkov (#37) (73cf6ce)
* chore(deps): bump docker/setup-qemu-action from 4.3.0 to 4.4.0 (#36) (2408ec2)
* chore(deps): bump docker/build-push-action from 7.3.0 to 7.4.0 (#35) (a75cc3e)
* chore(deps): bump docker/setup-buildx-action from 4.3.0 to 4.4.1 (#34) (612bad8)
* fix(ci): use setup job's latest_tag output instead of re-running git describe in release-notes (9f6be41)
* docs: fix release notes for v3.3.0-20260901 — show only commits since previous tag (d090737)
* Add JUnit XML output for CI systems that read test reports (eea979a)
* Add tests that check SARIF output against the official 2.1.0 schema (3357f5b)
* Add SARIF output so results show up in GitHub's Security tab (04c882b)
* fix(ci): use PR for release notes on protected main (#39) (2ff5e31)
* style: apply ruff format to test_app.py and output.py (526c9b1)
* fix(lint): resolve all ruff errors introduced by JSON output feature (19b99f0)
* test: verify JSON output — validity, all fields, and round-trip (02d83f6)
* feat(output): implement JSON serialisation for ValidationResult (1db2974)
* feat(cli): add --format / -f flag with text and json choices (b477a3f)
* fix(ci): replace trivy-action with direct Trivy CLI install (6613e4b)
* fix(ci): fix Trivy action SHA and raise image size limit to 700 MB (fcd0d16)
* fix(ci): fix YAML syntax error in Trivy summary step (ebc69eb)
* ci: add Trivy container scan for HIGH/CRITICAL OS-level CVEs (ea54b74)
* ci: add Docker image size check with 500 MB hard limit (fa0f3c6)
* feat(docker): switch to multi-stage build to reduce image size (2c25dce)
* chore(deps-dev): bump ruff from 0.16.6 to 0.16.7 in the dev-deps group (#33) (b74973a)
* chore(deps): bump checkov in the production-deps group (#32) (c1bb167)
* docker: ignore __pycache__, .venv, .pytest_cache to reduce build context (#49) (d95d778)
* docker: run container as non-root 'validator' user for better security (#48) (9fafa77)
* docker: add OCI LABEL metadata (title, description, version, source, licenses) (#47) (07f08a9)
* docker: add HEALTHCHECK to verify yaml and yamllint are importable (#46) (e7989bf)
* ci: remove dependabot-auto-merge workflow (17b5e75)
* chore(deps): bump softprops/action-gh-release from 1 to 3 (#31) (221f575)
* ci: fix pip-audit CVE noise + add Dependabot auto-merge workflow (9e0197d)
* chore(deps): bump docker/login-action from 3.7.0 to 4.6.0 (#23) (c088f27)
* chore(deps): bump docker/build-push-action from 5.4.0 to 7.3.0 (#24) (78fea19)
* chore(deps): bump checkov in the production-deps group (#26) (9fdb5b1)
* chore(deps): bump docker/setup-qemu-action from 3.7.0 to 4.3.0 (#25) (c95bcb9)
* chore(deps): bump actions/setup-python from 5.6.0 to 7.0.0 (#27) (07ad677)
* chore(deps): bump docker/setup-buildx-action from 3.12.0 to 4.3.0 (#21) (364ab81)
* chore(deps): bump actions/checkout from 4.4.0 to 7.0.1 (#22) (98de4c6)
* chore(deps): bump pytest from 9.0.3 to 9.1.1 in the test-deps group (#28) (e67fc86)
* chore(deps): bump softprops/action-gh-release (#30) (26f84c9)
* chore(deps): bump actions/upload-artifact from 4.6.2 to 7.0.1 (#29) (67e067a)
* ci(#45): add pip-audit job to CI for CVE scanning (6cab9a8)
* ci(#44): add Dependabot config for automated dependency updates (a091061)
* deps(#43): add requirements-dev.txt with dev tooling (994f64f)
* deps(#42): pin exact versions in requirements-test.txt (e77ab12)
* deps(#41): pin exact versions in requirements.txt (9e4d820)
* fix: use sys.executable for subprocess tests and add pipefail to CI pytest step (21ea102)
* ci: run lint, app-tests, and docker-tests in parallel after build stage (b0a04cb)
* ci: add dedicated parallel lint and quality stage with ruff and mypy (26511c1)
* fix: handle checkov multi-framework list output and parse errors gracefully (c7feee8)
* docs: add GitHub Actions CI workflow status badge to README (#40) (78137e0)
* ci: pin GitHub Action versions to exact commit SHAs for security (#39) (8f9c092)
* style: auto-format codebase with ruff format and enforce in CI (#38) (0f13cd1)
* ci: add mypy type checking to CI and resolve model type annotations (#37) (b090527)
* ci: add ruff linting to CI and fix initial codebase violations (#36) (c3dc04b)
* ci: add test coverage gate to fail build if below 70% (#35) (1f3f065)

**Docker Image:** `pooyanazad/yaml-checker:v3.4.0-20261011`
<!-- RELEASE_NOTES_END -->

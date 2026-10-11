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
* feat: official PyPI package release as `yamlguard` (`pip install yamlguard`)
* feat: support `--format` outputs (`text`, `json`, `junit`, `sarif`)
* feat: modular Python library structure under `yaml_validator`
* ci: automated PyPI trusted publishing workflow on GitHub Release
* test: comprehensive test suite with 230 passing tests and high coverage

**Docker Image:** `pooyanazad/yaml-checker:v3.4.0-20261011`
<!-- RELEASE_NOTES_END -->

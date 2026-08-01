# YAML Validator

Validate YAML files for syntax errors, style issues, and security misconfigurations — all in one command.

<img width="881" height="571" alt="YAML Validator output" src="https://github.com/user-attachments/assets/0a3278f9-9f86-431c-90f7-e3d122f0043b" />

## Getting Started

**Prerequisites:** [Docker](https://docs.docker.com/get-docker/) installed on your system.

### One-time setup (Linux/macOS)

Run this once to create the `ytest` shortcut:

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

## Usage

> [!NOTE]
> The multiple files and directory scanning features will be available in **v3**, starting on June 1st.

```bash
# Single file
ytest myfile.yaml

# Multiple files
ytest config.yaml deployment.yaml secrets.yaml

# Entire directory (recursive)
ytest ./configs/

# Glob pattern
ytest ./configs/**/*.yaml
```

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

## What It Checks

| Layer | Tool | What it catches |
|---|---|---|
| **Syntax** | PyYAML | Parse errors, broken structure, invalid indentation |
| **Linting** | yamllint | Style issues, line length, trailing spaces, consistency |
| **Security** | Checkov | Hardcoded secrets, privileged containers, misconfigurations |

Issues are grouped by severity (**Critical → High → Medium → Low**) with colored output and a summary table. When scanning multiple files, you get a combined report showing which files have problems.

## Features

✅ Multi-file & directory scanning  
✅ Glob pattern support (`**/*.yaml`)  
✅ Cross-platform (Windows, Linux, macOS)  
✅ Multi-arch Docker image (amd64/arm64)  
✅ Colored severity-based reporting  
✅ Zero configuration required  

## Docker Image

| | |
|---|---|
| **Image** | `pooyanazad/yaml-checker` |
| **Tag** | `latest` is always up to date |
| **Base** | `python:3.12-slim` |
| **Platforms** | `linux/amd64`, `linux/arm64` |

## Release Notes

<!-- RELEASE_NOTES_START -->
### v3.2.0-20260801 — 2026-08-01

**Changes since last release:**
* test: restore missing test fixtures (26925a3)
* ci: fix docker integration tests path for fixtures (f06babb)
* test: add test coverage reporting (f062eb7)
* test: add pytest.ini with standard configuration (12e6222)
* test: move fixtures to tests/fixtures/ (110ce94)
* test: add conftest.py with shared fixtures (c3b007d)
* fix: handle empty and binary YAML files gracefully (#13, #14) (a2fd60e)
* refactor: make app.py a thin entry point, add package __main__ (#20) (54e89e7)
* refactor: move CLI to yaml_validator/cli.py (#19) (a9943e7)
* fix: add yaml_validator package to Docker image and move output helpers (22156f2)
* refactor: move validators and output helpers to package (#17) (0654563)
* refactor: move models to yaml_validator/models.py (#16) (0c69408)
* refactor: create yaml_validator/ package scaffold (#15) (bba3051)
* ci: remove docker image artifact upload/download (Closes #17) (b90d9b6)
* docs: add CONTRIBUTING.md (c6885bf)
* chore: add PR template and update CI triggers (fda6adf)
* cleanup: remove Day N labels from comments and docstrings (4b3ee83)
* feat: add file permission check before opening YAML files (Day 12) (97a1f7a)
* refactor: narrow exception catches in validate_yaml_syntax (Day 11) (223bd1c)

**Docker Image:** `pooyanazad/yaml-checker:v3.2.0-20260801`
<!-- RELEASE_NOTES_END -->

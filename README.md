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
_Release notes are automatically updated on each monthly release._
<!-- RELEASE_NOTES_END -->

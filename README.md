# YAML Validator · yamlguard

[![CI](https://github.com/pooyanazad/YAML-validator/actions/workflows/docker-build.yml/badge.svg)](https://github.com/pooyanazad/YAML-validator/actions/workflows/docker-build.yml)
[![PyPI](https://img.shields.io/pypi/v/yamlguard.svg)](https://pypi.org/project/yamlguard/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Check YAML syntax, catch style problems, and scan supported infrastructure configurations with one command. Install the **`yamlguard`** Python CLI, or run **`pooyanazad/yaml-checker`** with Docker.

## Get started

### Python CLI

Use an isolated environment such as pipx:

```bash
pipx install yamlguard
yamlguard myfile.yaml
```

Or install into your Python environment:

```bash
python -m pip install yamlguard
yamlguard myfile.yaml
```

If your package index reports that `yamlguard` is unavailable, install the tagged source instead (requires Git):

```bash
python -m pip install 'git+https://github.com/pooyanazad/YAML-validator.git@v3.4.0-20261011'
```

The base package includes **PyYAML and yamllint**. To add **Checkov security checks**, install the optional extra in the same environment:

```bash
python -m pip install 'yamlguard[security]'
# With pipx, use: pipx install 'yamlguard[security]'
```

If Checkov is unavailable, validation continues with syntax and lint checks and reports that security scanning was skipped. Python 3.12 is used in CI and Docker; the package declares Python 3.9 or newer, subject to dependency compatibility.

### Docker

Docker includes all three tools, including Checkov. Mount the directory containing your YAML files; paths inside the container are relative to `/data`.

**Linux/macOS:**

```bash
docker run --rm -v "$(pwd):/data:ro" pooyanazad/yaml-checker:latest myfile.yaml
```

**Windows PowerShell:**

```powershell
docker run --rm -v "${PWD}:/data:ro" pooyanazad/yaml-checker:latest myfile.yaml
```

**Windows Command Prompt:**

```bat
docker run --rm -v "%cd%:/data:ro" pooyanazad/yaml-checker:latest myfile.yaml
```

For repeatable runs, replace `latest` with a release tag such as `v3.4.0-20261011`. Images are built for `linux/amd64` and `linux/arm64`, use Python 3.12, and run as a non-root user. Mounted files must be readable by that user.

Optional Bash/Zsh shortcut: add this function to `~/.bashrc` or `~/.zshrc`, then reload your shell. It mounts your current directory each time you run it.

```bash
ytest() {
  docker run --rm -v "$(pwd):/data:ro" pooyanazad/yaml-checker:latest "$@"
}

ytest myfile.yaml
```

## Scan files and directories

```bash
yamlguard config.yaml                         # One file
yamlguard config.yaml deployment.yml          # Multiple files
yamlguard ./configs/                          # Recursively scan .yaml and .yml files
yamlguard './configs/**/*.yaml'               # Quote globs so yamlguard expands them
yamlguard ./configs/ --no-security             # Skip Checkov scanning
yamlguard deployment.yaml --timeout 60        # Limit each validator subprocess to 60 seconds
```

The same arguments work with Docker or `ytest`. Repeated paths are scanned once. Missing paths produce a warning and are skipped; the command fails if no files remain. The default subprocess timeout is 300 seconds; dependency probes have a separate 30-second timeout.

Run `yamlguard --help` for all options or `yamlguard --version` to check the installed version. From a source checkout, `python -m yaml_validator` provides the same CLI.

## What gets checked

| Check | Tool | Behavior |
|---|---|---|
| Syntax | PyYAML | Parses YAML, including multiple documents; reports parse and file-read errors. |
| Style | yamllint | Reports indentation, line length, trailing spaces, duplicate keys, and other lint rules. |
| Security | Checkov, when installed | Runs Checkov's checks for supported infrastructure formats, such as Kubernetes manifests. Findings depend on the file and Checkov version. |

Text reports group findings by **Critical, High, Medium, Low, and Info**. Scanning several files also produces a combined summary. Checkov is not a universal security check for arbitrary application YAML; a clean report covers only the checks that ran.

### Exit codes

| Code | Meaning |
|---|---|
| `0` | No findings, or only Medium/Low/Info findings. |
| `1` | Critical/High findings, no matching files, or a required dependency is unavailable. |
| `2` | Invalid CLI arguments (argparse). |

**Lint findings alone usually do not fail the command:** yamllint errors map to Medium and warnings to Low. Syntax errors are Critical. Checkov findings without an explicit severity default to High.

## Export reports for CI

Choose `--format` (or `-f`):

```bash
yamlguard ./configs/ --format text             # Human-readable report (default)
yamlguard ./configs/ --format json > results.json
yamlguard ./configs/ --format junit > test-results.xml
yamlguard ./configs/ --format sarif > results.sarif
```

- **JSON:** one object for a single file, an array for multiple files. Each result includes the path, syntax status, severity counts, and findings.
- **JUnit XML:** Critical/High findings become failures; less severe findings appear as skipped test cases.
- **SARIF 2.1.0:** a report you can upload to a compatible code-scanning service, including GitHub Code Scanning. Generating the file does not upload it automatically.

Reports go to stdout. In the updated source, diagnostics for machine-readable formats go to stderr; the CLI at the `v3.4.0-20261011` source tag can put missing-tool or path warnings on stdout, so check that version's redirected report before consuming it. Preserve the exit code when your CI collects a report after validation fails.

## Releases and contributing

Starting with 3.5.0, the package version in `yaml_validator/__init__.py` determines both releases: PyPI uses `X.Y.Z`, and GitHub/Docker use `vX.Y.Z-YYYYMMDD` (UTC). Older Docker tags may differ from their Python package version.

The pipeline runs checks on pushes and pull requests. Maintainers publish a new version by running **Docker Build and Push** on `main`; it builds Docker images, creates the GitHub release, and starts **Release & Publish to PyPI** automatically. Check that second workflow's result to confirm publication. Monthly runs refresh Docker `latest` without creating another release if the package version is already released.

The README's latest-release block is updated through a separate PR generated by the pipeline; merge it to update this page. **Refresh Release Notes** is optional: it repairs an existing GitHub release description and is not needed for a new release. See the [maintainer release instructions](release-notes/README.md).

See [all releases](https://github.com/pooyanazad/YAML-validator/releases), [report an issue](https://github.com/pooyanazad/YAML-validator/issues), or read the [contributing guide](CONTRIBUTING.md).

## Latest release

<!-- RELEASE_NOTES_START -->
### v3.4.0-20261011 — 2026-10-11

**Changes since `v3.3.0-20260901`** (63 non-merge commits).

- Add PyPI packaging for the `yamlguard` Python CLI. Syntax validation and yamllint are included; Checkov is available through the optional `security` extra.
- Export validation results as JSON, SARIF 2.1.0, or JUnit XML, alongside the existing text report.
- Handle Checkov reports containing multiple frameworks and malformed output more gracefully.
- Docker now uses a multi-stage build, runs as a non-root user, and includes a health check. CI adds lint/type checks, a coverage gate, image-size checks, and vulnerability reports.
- Update runtime dependencies, development tools, and GitHub Actions; add package build and trusted-publishing workflows.

[Full changelog](https://github.com/pooyanazad/YAML-validator/compare/v3.3.0-20260901...v3.4.0-20261011)

**Docker image:** `pooyanazad/yaml-checker:v3.4.0-20261011`

<!-- RELEASE_NOTES_END -->

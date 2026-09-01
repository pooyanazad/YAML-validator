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
### v3.3.0-20260901 — 2026-09-01

**Changes since last release:**
* test: make sure the tool doesn't choke on a 40k-line YAML file (#34) (bfba1b4)
* test: catch resolve_files edge cases — symlinks, bad dirs, wrong extensions (#33) (e87687e)
* test: #32 add TestMultiFileSummary — multi-file combined summary tests (fc9315c)
* test: #31 add TestHelpVersionFlags — --help and --version verification (172cebd)
* test: #30 add TestMainExitCode1 — verify exit code 1 for issues files (2444f19)
* test: #29 add TestMainEndToEnd — e2e subprocess exit code 0 (4d88ced)
* CI tests run parallel (a4ab8c8)
* fix: #8 suppress redundant large-file warning (c074eb9)
* test: #28 add TestCheckDependenciesMocked — mock yamllint/checkov availability (38fefb2)
* fix: #8 handle large YAML files (2e0f5ff)
* test: #27 add TestPrintSummaryTable — verify table rendering and counts (5dd7e6b)
* test: add TestPrintIssues -- severity grouping order tests for print_issues() (#26) (e65a293)
* test: add TestPrintColored — capsys output tests for print_colored() (#25) (fa41dca)
* docs: update release notes for v3.2.0-20260801 [skip ci] (b77350f)
* test: restore missing test fixtures (7f169d0)
* ci: fix docker integration tests path for fixtures (b011710)
* test: add test coverage reporting (963ab7b)
* test: add pytest.ini with standard configuration (df8a5b0)
* test: move fixtures to tests/fixtures/ (4432519)
* test: add conftest.py with shared fixtures (759baf9)
* fix: handle empty and binary YAML files gracefully (#13, #14) (bf2eb04)
* refactor: make app.py a thin entry point, add package __main__ (#20) (faa74ec)
* refactor: move CLI to yaml_validator/cli.py (#19) (a086281)
* fix: add yaml_validator package to Docker image and move output helpers (d43a30e)
* refactor: move validators and output helpers to package (#17) (cc94449)
* refactor: move models to yaml_validator/models.py (#16) (3e91bf1)
* refactor: create yaml_validator/ package scaffold (#15) (d344fd3)
* ci: remove docker image artifact upload/download (Closes #17) (6c6af0c)
* docs: add CONTRIBUTING.md (bb10d51)
* chore: add PR template and update CI triggers (a797647)
* cleanup: remove Day N labels from comments and docstrings (ceb7d81)
* feat: add file permission check before opening YAML files (Day 12) (7df8166)
* refactor: narrow exception catches in validate_yaml_syntax (Day 11) (d083903)
* docs: update release notes for v3.1.0-20260701 [skip ci] (34c1550)
* test: mock timeout handling correctly (Day 10) (56bb590)
* feat: make timeout configurable (Day 9) (f929f89)
* feat: add timeout to check_dependencies() (Day 8) (1888688)
* feat: add timeouts to subprocess calls (Day 7) (7cb4835)
* fix: add missing stderr to test mock (7254d52)
* feat: handle yamllint edge cases gracefully (Day 6) (f9ad00f)
* test: add Day 5 verification for regex parsing colons (3b7b5d1)
* fix: replace fragile string splitting with robust regex for yamllint parsing (b9aee21)
* test: add Day 2 tests for ToolAvailability and check_dependencies() (a75e99a)
* refactor: replace CHECKOV_AVAILABLE global with ToolAvailability dataclass (a9bd7a3)
* ci: add App Tests stage with pytest report output before Docker tests and release (a1683cc)
* test: add pytest app functionality tests (41 tests across 5 test classes) (74142ff)
* test: improve Docker integration tests with real exit code and output assertions (0b206e8)
* ci: split pipeline into 7 separate jobs for clear stage visibility (99f8927)
* docs: update release notes for v3.0.0-20260601 [skip ci] (7d47cc8)
* fix: fix release notes - use git describe for tag detection and Python for README update (bb5cdf2)
* docs: add notice that multi-file feature is coming in v3 (5357e0f)
* ci: switch versioning to v3.x.0-YYYYMMDD format (f67d040)
* docs: restructure README, simplify install, and add release notes marker (403d556)
* ci: pipeline improvements, multi-arch build, and release notes auto-update (7596d5f)
* feat: multi-file and directory support (879be8c)
* chore: add .gitignore and .dockerignore (1cb75d4)
* Allow Docker actions to run on workflow_dispatch event (1704b46)
* Start automated releases at v2.0 (09f08d0)
* Document Python 3.12 runtime and v2 releases (2632096)
* Use current Python executable (c541afa)
* Update Docker image to Python 3.12 (d6b2281)
* Update README.md (bd3df82)
* Update README with alias definition for yaml-checker (f85ce30)
* Add personal usage section for yaml-checker (a3ffd39)
* Update README.md (b59762d)
* Revert pipeline: Remove email notifications (2e78af5)
* Update README and add email notifications for scheduled releases (c9ce59b)
* Update README.md (16b6bd9)
* Update README: Remove Examples section and maintain current Docker image info (ed8c612)
* Versioning issue fixed: Docker push and GitHub release now schedule-only on 1st of each month (a42947c)
* Remove schedule-only conditions from Docker login and push stages (452978a)
* Trigger v1.0.1 release workflow (7c08a4c)
* Fix release creation for manual triggers and all event types (b42a788)
* Trigger workflow to create first version v1.0.1 (d1839eb)
* Reset version numbering to start from v1.0.1 (02c3a18)
* Update docker-build.yml (8f9f1cc)
* Update docker-build.yml (e01bb72)
* Add timezone debugging step to print current time in workflow (4873048)
* Update docker-build.yml (a7fa91b)
* Add timezone specification for Stockholm to workflow schedule (b020276)
* Fix: Add tag fetching for proper version increment and update cron to run at 11:50 AM Sweden time (weekdays) (b242709)
* Fix: Add fetch-depth and git fetch --tags to ensure proper tag access for version incrementing (fc823c9)
* Update docker-build.yml (85d35a3)
* Update docker-build.yml (510eb20)
* Update docker-build.yml (f7b422c)
* Fix: Improve version generation logic with duplicate tag detection and proper incrementing (907d4f4)
* Update docker-build.yml (94b83e9)
* Update docker-build.yml (be709aa)
* Update README.md (f43b5a9)
* make change to create release just by schedule (4263c25)
* Update README.md (83fd20e)
* Fix: Add auto-incrementing version numbers and GitHub release permissions (924c6a1)
* Fix: Update Docker tag format to v1.0.2-YYYYMMDD and replace deprecated create-release action (dfd3828)
* Add GitHub Actions workflow for monthly Docker builds with automated testing and DockerHub deployment (dd4ffa7)
* Add GitHub Actions workflows for automated Docker builds and testing (0ad8f79)
* Add comprehensive test suite with safe fake API keys for validation scenarios (25a4eb7)
* Add comprehensive README with usage instructions for all platforms (9a55c71)
* Add Dockerfile with volume mounting support for external YAML files (1cff16f)
* Add Docker entrypoint script for flexible command execution (bbe4abb)
* Add core Python application and dependencies for YAML validation (94c49ab)
* Initial commit (601876a)

**Docker Image:** `pooyanazad/yaml-checker:v3.3.0-20260901`
<!-- RELEASE_NOTES_END -->

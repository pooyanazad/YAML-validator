# YAML Validator — Long-Term Improvement Plan

> **How to use this file:** Pick one task per day, complete it, mark it `[x]`, commit.
> Tasks are ordered by dependency — earlier phases unlock later ones.
> Each task is designed to be completable in **30–90 minutes**.

---

## Phase 1 — Code Quality & Foundations

These tasks clean up the existing code, fix bugs, and lay the groundwork for every future feature.

### 1.1 Remove Global State

- [x] **#1 Create `ToolAvailability` dataclass** — Replace the `CHECKOV_AVAILABLE` global ([app.py:40](file:///home/pooyan/project/YAML-validator/app.py#L40)) with a `@dataclass` that `check_dependencies()` returns. Pass it explicitly to functions that need it.
- [x] **#2 Remove `global` keyword** — `check_dependencies()` now returns `ToolAvailability`; `global` keyword is gone from `app.py`.
- [x] **#3 Update tests for new signature** — Added `TestToolAvailability` (6 tests) and 4 new `TestValidateYamlFile` tests covering `checkov=False` behaviour and mocked `check_dependencies()`. 41 → 51 tests total.

### 1.2 Fix Fragile Parsing

- [x] **#4 Fix fragile parsing with robust regex** — Note: yamllint does not natively support `-f json` output. Instead, replaced brittle string splitting with a robust regular expression in `run_yamllint` to properly parse `-f parsable` output and correctly extract rule names.
- [x] **#5 Add tests for yamllint regex parsing** — Wrote a test case with messages containing colons to verify that the robust regex successfully extracts line, column, level, message, and rule without breaking.
- [x] **#6 Handle yamllint edge cases** — Handled empty output, yamllint not installed, and malformed outputs gracefully. Added tests for each.


### 1.3 Subprocess Hardening

- [x] **#7 Add timeout to all subprocess calls** — Add `timeout=300` to `run_yamllint()` ([app.py:142](file:///home/pooyan/project/YAML-validator/app.py#L142)) and `run_checkov()` ([app.py:191](file:///home/pooyan/project/YAML-validator/app.py#L191)). Catch `subprocess.TimeoutExpired`.
- [x] **#8 Add timeout to `check_dependencies()`** — Add `timeout=30` to the version/import checks ([app.py:91](file:///home/pooyan/project/YAML-validator/app.py#L91), [app.py:97](file:///home/pooyan/project/YAML-validator/app.py#L97)).
- [x] **#9 Make timeout configurable** — Add a `--timeout` CLI flag (default 300s). Thread it through to subprocess calls.
- [x] **#10 Test timeout handling** — Write a test that mocks a hanging subprocess and verifies the timeout produces a clear error message.

### 1.4 Error Handling Improvements

- [x] **#11 Narrow exception catches** — Replaced bare `except Exception` with specific exceptions (`FileNotFoundError`, `PermissionError`, `UnicodeDecodeError`, `OSError`) in `validate_yaml_syntax`. Each gives a clear, targeted error message.
- [x] **#12 Add file permission check** — Before opening a YAML file, checks `os.path.exists()` and `os.access()`. Gives a clear error like "Permission denied: /etc/shadow" rather than a generic traceback.
- [x] **#13 Handle empty YAML files** — `yaml.safe_load_all()` on an empty file returns `[None]`. Detect this and report as INFO rather than silently passing.
- [x] **#14 Handle binary files gracefully** — If a `.yaml` file is actually binary (e.g., accidentally named), detect it early and skip with a warning instead of crashing with a decode error.

### 1.5 Code Structure

- [x] **#15 Split `app.py` into modules** — Create a `yaml_validator/` package with `__init__.py`, `models.py` (dataclasses/enums), `validators.py` (syntax, yamllint, checkov), `output.py` (print functions), `cli.py` (argparse + main).
- [x] **#16 Move models to `models.py`** — Extract `Severity`, `ValidationIssue`, `ValidationResult`, `ToolAvailability` into `yaml_validator/models.py`.
- [x] **#17 Move validators to `validators.py`** — Extract `validate_yaml_syntax()`, `run_yamllint()`, `run_checkov()`, `validate_yaml_file()`.
- [x] **#18 Move output to `output.py`** — Extract `print_colored()`, `print_issues()`, `print_summary_table()`.
- [x] **#19 Move CLI to `cli.py`** — Extract `main()`, `resolve_files()`, argparse setup.
- [x] **#20 Update `app.py` as thin entry point** — Make `app.py` simply import and call `yaml_validator.cli.main()`. Update Dockerfile and entrypoint accordingly.

---

## Phase 2 — Testing & CI

### 2.1 Test Infrastructure

- [x] **#21 Add `conftest.py`** — Create `tests/conftest.py` with shared fixtures: `clean_file`, `issues_file`, `security_file`, `tmp_yaml()` factory.
- [x] **#22 Move fixtures to `tests/fixtures/`** — Create `tests/fixtures/` directory, move all `.yaml` test files there. Update test paths.
- [x] **#23 Add `pytest.ini` / `pyproject.toml`** — Add proper pytest configuration: test discovery settings, default flags (`-v --tb=short`), markers.
- [x] **#24 Add test coverage reporting** — Add `pytest-cov` to `requirements-test.txt`. Add `--cov=app --cov-report=html` to pytest config. Add `htmlcov/` to `.gitignore`.

### 2.2 Missing Test Coverage

- [x] **#25 Test `print_colored()` output** — Use `capsys` to capture stdout and verify correct formatting for each severity level.
- [x] **#26 Test `print_issues()` grouping** — Verify issues are grouped by severity in the correct order (CRITICAL first, INFO last).
- [x] **#27 Test `print_summary_table()` formatting** — Verify the table renders correctly and counts match.
- [x] **#28 Test `check_dependencies()` with mocked tools** — Use `unittest.mock.patch` to simulate missing yamllint / checkov and verify behavior.
- [ ] **#29 Test `main()` end-to-end** — Use `subprocess.run()` to call `python app.py tests/fixtures/test3_clean.yaml` and verify exit code 0.
- [ ] **#30 Test `main()` exit code 1** — Verify `python app.py tests/fixtures/test1_issues.yaml` exits with code 1.
- [ ] **#31 Test `--help` and `--version` flags** — Verify they print expected output and exit 0.
- [ ] **#32 Test multi-file combined summary** — Run app with 2+ files and verify "Files scanned" appears in output.
- [ ] **#33 Add negative tests for `resolve_files()`** — Test symlink loops, permission-denied directories, files with no extension.
- [ ] **#34 Test large YAML files** — Create a fixture with 10,000+ lines. Verify the tool handles it without excessive memory or time.

### 2.3 CI Pipeline Improvements

- [ ] **#35 Add test coverage gate to CI** — Add `--cov-fail-under=70` to the pytest step. Fail the build if coverage drops below threshold.
- [ ] **#36 Add linting to CI (ruff or flake8)** — Add a CI step that runs `ruff check .` on every push. Fix any initial violations.
- [ ] **#37 Add type checking to CI (mypy)** — Add a CI step that runs `mypy app.py`. Fix any type errors.
- [ ] **#38 Add `black` / `ruff format` to CI** — Add a formatting check. Auto-format the codebase first, then enforce in CI.
- [ ] **#39 Pin CI action versions with SHA** — Replace `@v4`, `@v3` etc. in the workflow with exact SHA hashes for security.
- [ ] **#40 Add CI badge to README** — Add a GitHub Actions status badge at the top of `README.md`.

---

## Phase 3 — Dependency & Docker Hygiene

### 3.1 Dependency Management

- [ ] **#41 Pin dependency versions in `requirements.txt`** — Run `pip freeze` and pin exact versions: `yamllint==X.Y.Z`, `checkov==X.Y.Z`, `colorama==X.Y.Z`, `PyYAML==X.Y.Z`.
- [ ] **#42 Pin test dependency versions** — Pin `pytest` and `pytest-json-report` to exact versions.
- [ ] **#43 Add `requirements-dev.txt`** — Create a dev requirements file with `ruff`, `mypy`, `black`, `pre-commit`.
- [ ] **#44 Add Dependabot or Renovate config** — Create `.github/dependabot.yml` to get automated PR updates for pip dependencies.
- [ ] **#45 Add `pip-audit` to CI** — Add a step that runs `pip-audit` to detect known vulnerabilities in dependencies.

### 3.2 Docker Improvements

- [ ] **#46 Add `HEALTHCHECK` to Dockerfile** — Add `HEALTHCHECK CMD python3 -c "import yaml; import yamllint"` to verify the image is functional.
- [ ] **#47 Add `LABEL` metadata to Dockerfile** — Add OCI labels: `org.opencontainers.image.title`, `.description`, `.version`, `.source`, `.licenses`.
- [ ] **#48 Add non-root user to Dockerfile** — Create a `validator` user with `useradd` and switch to it with `USER validator`. Avoids running as root inside the container.
- [ ] **#49 Add `.dockerignore` entries for `__pycache__`, `.venv`, `.pytest_cache`** — Reduce build context size.
- [ ] **#50 Multi-stage Docker build** — Use a builder stage to install dependencies and a runtime stage to copy only what's needed. Reduces image size.
- [ ] **#51 Add Docker image size check to CI** — After build, print the image size. Optionally fail if it exceeds a threshold (e.g., 500MB).
- [ ] **#52 Add Trivy or Snyk container scan to CI** — Scan the Docker image for OS-level vulnerabilities before pushing.

---

## Phase 4 — New CLI Features

### 4.1 Output Formats

- [ ] **#53 Add `--format` / `-f` flag to argparse** — Choices: `text` (default), `json`. Wire it up (no implementation yet, just the flag).
- [ ] **#54 Implement JSON output** — Serialize `ValidationResult` to JSON. Print it when `--format json` is used. Suppress all colored output in JSON mode.
- [ ] **#55 Test JSON output** — Verify the JSON is valid, contains all expected fields, and round-trips correctly.
- [ ] **#56 Add SARIF output format** — Add `sarif` as a `--format` choice. Implement SARIF v2.1.0 schema output. This lights up GitHub Security tab.
- [ ] **#57 Test SARIF output** — Validate the output against the SARIF JSON Schema.
- [ ] **#58 Add JUnit XML output** — Add `junit` as a `--format` choice. CI systems can natively consume this.
- [ ] **#59 Test JUnit output** — Validate XML structure and verify it works with CI test result reporting.
- [ ] **#60 Add `--output` / `-o` flag** — Write results to a file instead of stdout. Support `-o report.json --format json`.

### 4.2 Filtering & Thresholds

- [ ] **#61 Add `--fail-level` flag** — Choices: `critical`, `high` (default), `medium`, `low`. Only exit 1 if issues at or above this severity are found.
- [ ] **#62 Test `--fail-level`** — Verify that `--fail-level critical` exits 0 when only HIGH issues exist.
- [ ] **#63 Add `--no-security` flag** — Skip Checkov entirely. Useful when Checkov is slow or irrelevant.
- [ ] **#64 Add `--no-lint` flag** — Skip yamllint. Only run syntax + security checks.
- [ ] **#65 Add `--only` flag** — `--only syntax`, `--only lint`, `--only security`. Run only one check type.
- [ ] **#66 Test all skip/only flags** — Verify each combination produces the expected subset of results.

### 4.3 Yamllint Configuration

- [ ] **#67 Add `--config` / `-c` flag** — Pass a custom `.yamllint.yml` to yamllint via its `-c` option.
- [ ] **#68 Auto-detect `.yamllint.yml`** — If `--config` is not specified, look for `.yamllint.yml`, `.yamllint.yaml`, or `.yamllint` in the current directory or parent directories.
- [ ] **#69 Test custom yamllint config** — Create a permissive config that allows long lines. Verify that the long-line warning disappears.
- [ ] **#70 Document config file support in README** — Add a section explaining how to use custom yamllint configs.

### 4.4 UX Polish Flags

- [ ] **#71 Add `--quiet` / `-q` flag** — Only show the summary table, suppress individual issue details.
- [ ] **#72 Add `--verbose` / `-v` flag** — Show tool commands being run, timing info for each check, and tool versions.

---

## Phase 5 — Advanced Validation Features

### 5.1 Duplicate Key Detection

- [ ] **#73 Create `DuplicateKeyLoader` class** — Subclass `yaml.SafeLoader` with a custom constructor that detects duplicate keys.
- [ ] **#74 Integrate duplicate key check into `validate_yaml_syntax()`** — Run the duplicate key loader as a second pass. Report duplicates as MEDIUM severity.
- [ ] **#75 Add duplicate key test fixtures** — Create YAML files with duplicate keys at various nesting levels.
- [ ] **#76 Test duplicate key detection** — Verify that duplicate keys are caught and reported with correct line numbers.

### 5.2 Schema Validation

- [ ] **#77 Add `jsonschema` dependency** — Add to `requirements.txt`. Create a `yaml_validator/schema.py` module.
- [ ] **#78 Add `--schema` flag** — Accept a path to a JSON Schema file. Validate the YAML content against it.
- [ ] **#79 Implement schema validation** — Load the schema, validate each YAML document, report violations as `ValidationIssue` with severity MEDIUM.
- [ ] **#80 Add built-in Kubernetes schema** — Bundle a basic K8s schema for Deployment, Service, ConfigMap. Use with `--schema k8s`.
- [ ] **#81 Test schema validation with valid YAML** — Verify that a conforming YAML produces no schema errors.
- [ ] **#82 Test schema validation with invalid YAML** — Verify that missing required fields, wrong types, etc. are caught.
- [ ] **#83 Add Docker Compose schema** — Bundle a Docker Compose v3 schema. Use with `--schema compose`.
- [ ] **#84 Add GitHub Actions schema** — Bundle a basic GitHub Actions workflow schema. Use with `--schema github-actions`.

### 5.3 Auto-Fix Capabilities

- [ ] **#85 Add `ruamel.yaml` dependency** — Add to `requirements.txt`. This is a round-trip YAML parser that preserves comments.
- [ ] **#86 Add `--fix` flag to argparse** — Wire up the flag, no implementation yet.
- [ ] **#87 Implement trailing whitespace removal** — Strip trailing whitespace from all lines. Write the file back using `ruamel.yaml`.
- [ ] **#88 Implement consistent indentation normalization** — Detect and normalize indentation to 2 spaces.
- [ ] **#89 Implement document start marker addition** — Add `---` at the beginning of files that lack it.
- [ ] **#90 Implement `--fix --dry-run`** — Show a diff of what would be changed without writing.
- [ ] **#91 Test auto-fix on fixture files** — Verify that fixed files pass yamllint cleanly.
- [ ] **#92 Test auto-fix preserves comments** — Verify that YAML comments survive the round-trip.

---

## Phase 6 — Reporting & Integration

### 6.1 Reporting Improvements

- [ ] **#93 Show relative paths in output** — Convert absolute paths to relative (from CWD) for cleaner output. Add `--absolute-paths` flag to override.
- [ ] **#94 Add timing info to summary** — Show how long each check took: "Syntax: 0.01s, yamllint: 0.23s, checkov: 12.4s".
- [ ] **#95 Add file count and total line count to summary** — Show "Scanned 15 files (2,340 lines total)".
- [ ] **#96 Add progress indicator for Checkov** — Show a spinner or `[1/3] Running syntax check...` progress during long-running checks.
- [issue] **#97 Warn on large files** — Print a warning if a YAML file is >1MB. Suggest `--no-security` to speed things up.
- [ ] **#98 Add `--no-color` flag** — Strip all ANSI color codes. Auto-detect when stdout is not a TTY (piped to file).
- [ ] **#99 Add exit code documentation** — Document in `--help` and README: 0 = clean or warnings only, 1 = critical/high issues, 2 = tool error.

### 6.2 GitHub Integration

- [ ] **#100 Add GitHub Actions annotations** — When running in CI (`GITHUB_ACTIONS=true`), emit `::error file=...::` annotations so issues appear inline in PRs.
- [ ] **#101 Upload SARIF to GitHub Security tab** — Add a CI step that runs with `--format sarif` and uploads via `github/codeql-action/upload-sarif`.
- [ ] **#102 Add PR comment with results** — Use `actions/github-script` to post a summary comment on PRs with the validation results table.

### 6.3 Pre-commit Hook

- [ ] **#103 Create `.pre-commit-hooks.yaml`** — Define a pre-commit hook entry so users can add yaml-validator to their `.pre-commit-config.yaml`.
- [ ] **#104 Test the pre-commit hook locally** — Install it in a test repo and verify it blocks commits with invalid YAML.
- [ ] **#105 Document pre-commit usage in README** — Add a section explaining how to install and configure the pre-commit hook.

### 6.4 VS Code Integration

- [ ] **#106 Create a Problem Matcher** — Write a `.github/problem-matcher.json` for VS Code that parses the tool's output and shows inline errors.
- [ ] **#107 Document VS Code integration** — Add a section to README explaining how to use the problem matcher with VS Code tasks.

---

## Phase 7 — Developer Experience

### 7.1 Watch Mode

- [ ] **#108 Add `watchdog` dependency** — Add to `requirements.txt`.
- [ ] **#109 Add `--watch` / `-w` flag** — Watch files/directories for changes and re-validate automatically.
- [ ] **#110 Implement file watcher** — Use `watchdog.observers.Observer` to monitor `.yaml`/`.yml` files. On change, re-run validation.
- [ ] **#111 Add debounce to watch mode** — Don't re-validate on every save event — wait 500ms for edits to settle.
- [ ] **#112 Clear screen on re-validation in watch mode** — Print a fresh report each time, not an appended one.
- [ ] **#113 Test watch mode** — Create a file, modify it, verify that validation re-runs.

### 7.2 Config File Support

- [ ] **#114 Support `.yaml-validator.yml` config file** — Allow users to set default flags (fail-level, format, timeout, etc.) in a config file.
- [ ] **#115 Config file discovery** — Look for `.yaml-validator.yml` in the current directory, then parent directories, then `~/.config/yaml-validator/`.
- [ ] **#116 Merge config file with CLI flags** — CLI flags override config file values. Document the precedence.
- [ ] **#117 Test config file loading** — Verify that a config file is discovered and its values are applied correctly.

### 7.3 Ignore Rules

- [ ] **#118 Support inline `# yaml-validator:disable` comments** — Allow users to suppress specific issues on specific lines.
- [ ] **#119 Support `--ignore-rules` flag** — Skip specific Checkov check IDs: `--ignore-rules CKV_DOCKER_2,CKV_DOCKER_3`.
- [ ] **#120 Test ignore rules** — Verify that disabled checks don't appear in the output.

---

## Phase 8 — Documentation & Community

### 8.1 README Enhancements

- [ ] **#121 Add "Contributing" section to README** — Explain how to set up the dev environment, run tests, and submit PRs.
- [ ] **#122 Add `CONTRIBUTING.md`** — Detailed contribution guidelines: code style, commit messages, PR process.
- [ ] **#123 Add `CHANGELOG.md`** — Start maintaining a changelog following [keepachangelog.com](https://keepachangelog.com/) format.
- [ ] **#124 Add architecture diagram to README** — Use a Mermaid diagram showing the validation pipeline: Input → Syntax → Lint → Security → Report.
- [ ] **#125 Add "Why This Tool?" section** — Compare with alternatives (yamllint alone, kubeval, etc.). Explain the value of combining all three checks.
- [ ] **#126 Add examples with real output screenshots** — Show before/after of clean and dirty YAML with the tool's colored output.

### 8.2 Advanced Documentation

- [ ] **#127 Add man page** — Create a man page (`yaml-validator.1`) installable via the Dockerfile.
- [ ] **#128 Add `--explain` flag** — Given a Checkov rule ID (e.g., `--explain CKV_DOCKER_2`), print a detailed explanation and fix guidance.
- [ ] **#129 Document all exit codes** — Create a table in the README: code 0, 1, 2, with explanations and examples.
- [ ] **#130 Add FAQ section to README** — Common questions: "Why is Checkov slow?", "How to suppress a specific rule?", etc.

### 8.3 Project Hygiene

- [ ] **#131 Add `CODE_OF_CONDUCT.md`** — Use the Contributor Covenant template.
- [ ] **#132 Add issue and PR templates** — Create `.github/ISSUE_TEMPLATE/bug_report.md`, `feature_request.md`, and `.github/PULL_REQUEST_TEMPLATE.md`.

---

## Phase 9 — Distribution & Packaging

### 9.1 PyPI Publishing

- [ ] **#133 Add `pyproject.toml`** — Define project metadata, dependencies, and build system for publishing to PyPI.
- [ ] **#134 Add `setup.cfg` or complete `pyproject.toml` with entry points** — Define `yaml-validator` as a console script entry point.
- [ ] **#135 Test local pip install** — Run `pip install -e .` and verify `yaml-validator` command works.
- [ ] **#136 Add PyPI publish to CI** — On release, automatically publish to PyPI using `twine` or `gh-action-pypi-publish`.
- [ ] **#137 Add PyPI badge to README** — Show the latest version from PyPI.

### 9.2 Alternative Distribution

- [ ] **#138 Add Homebrew formula** — Create a Homebrew tap so macOS users can `brew install yaml-validator`.
- [ ] **#139 Add standalone binary via PyInstaller** — Package as a single executable for users without Python.
- [ ] **#140 Add `docker-compose.yml` for development** — Make it easy to develop inside a container with live reloading.

### 9.3 Versioning

- [ ] **#141 Sync `__version__` with git tags** — Use `importlib.metadata` or `setuptools-scm` so the version is always accurate.
- [ ] **#142 Add semantic versioning policy** — Document when to bump major/minor/patch. Update README and CONTRIBUTING.

---

## Phase 10 — Performance & Polish

### 10.1 Performance

- [ ] **#143 Add `--parallel` flag** — Run validation checks (syntax, lint, security) concurrently using `concurrent.futures.ThreadPoolExecutor`.
- [ ] **#144 Parallelize multi-file scanning** — When validating multiple files, use a thread pool to validate files concurrently.
- [ ] **#145 Add caching for Checkov results** — Cache Checkov results by file hash to avoid re-scanning unchanged files.
- [ ] **#146 Benchmark and profile** — Add a `--benchmark` hidden flag that times each stage and prints a performance report.
- [ ] **#147 Optimize imports** — Lazy-import `checkov` and `yaml` modules to speed up startup time (especially for `--help`).

### 10.2 Robustness

- [ ] **#148 Handle YAML files with BOM** — Detect and strip UTF-8 BOM (`\xef\xbb\xbf`) before parsing.
- [ ] **#149 Handle YAML files with CRLF line endings** — Normalize line endings before processing.
- [issue] **#150 Handle symlinks in directory scanning** — Follow/skip symlinks based on a `--follow-symlinks` flag (default: skip).
- [ ] **#151 Add `--exclude` flag** — Exclude files/directories matching a glob pattern: `--exclude '**/vendor/**'`.
- [ ] **#152 Limit recursion depth in directory scanning** — Add `--max-depth` flag (default: unlimited).

### 10.3 Final Polish

- [ ] **#153 Add emoji-free mode** — Add `--no-emoji` for terminals that don't support Unicode. Also auto-detect when running in a minimal terminal.
- [ ] **#154 Add `--strict` mode** — Exit 1 on ANY issue (including LOW and INFO).
- [ ] **#155 Add `--count` mode** — Just print the total issue count (useful for scripting): `yaml-validator --count *.yaml` → `7`.

---

## Quick Reference: Priority Matrix

| Priority | Category | Key Outcome |
|----------|----------|-------------|
| 🔴 **P0** | Code Quality | — | Clean, testable, modular codebase |
| 🔴 **P0** | Testing & CI | — | Reliable tests, enforced quality gates |
| 🟠 **P1** | Dependency & Docker | — | Reproducible builds, secure images |
| 🟠 **P1** | CLI Features | — | JSON/SARIF output, fail-level, config |
| 🟡 **P2** | Advanced Validation | — | Duplicate keys, schema, auto-fix |
| 🟡 **P2** | Reporting & Integration | — | GitHub annotations, pre-commit |
| 🟢 **P3** | Developer Experience | — | Watch mode, config file, ignore rules |
| 🟢 **P3** | Documentation | — | Contributing guide, changelog, FAQ |
| 🔵 **P4** | Distribution | — | PyPI, Homebrew, standalone binary |
| 🔵 **P4** | Performance & Polish | — | Parallel execution, edge cases |

---

## Already Completed ✅

Based on git history, these items from the original plan are **done**:

| Item | Completed In |
|------|-------------|
| Multi-file & directory support | `124a40d` |
| `argparse` migration | `124a40d` |
| Add `.gitignore` and `.dockerignore` | `fa828af` |
| Multi-arch Docker builds (amd64/arm64) | `97679f2` |
| `--version` flag | `124a40d` |
| `--help` flag (via argparse) | `124a40d` |
| Add app tests with pytest (41 tests) | `b9e5032` |
| CI pipeline with 7 stages | `0b38079` |
| Docker integration tests | `2fcec57` |
| `workflow_dispatch` support | `1b9dcef` |

---

> **Total tasks: 155** — At 1 per day, this is roughly 5 months of daily progress.
> At 2–3 per day, you can finish in 2 months.
> Pick the pace that works for you! 🚀

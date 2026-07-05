# Contributing to YAML-validator

First off, thank you for considering contributing to YAML-validator! Contributions are highly welcome and essential for keeping this project great.

## Getting Started

1. **Find an Issue:** Look through the [Issues](../../issues) page to find a task you'd like to work on. 
2. **Claiming an Issue:** If you find an issue you'd like to tackle, drop a quick comment to let others know you're working on it.

### 🌟 A Note on "Good First Issues"
We actively use the `good first issue` tag to help new developers get involved in open source. 
* If you are picking up an issue with this tag, **please pick only one** and leave the others open for other junior developers to claim. 
* If you are an experienced developer or have already completed a `good first issue`, we'd love your help on any of the untagged issues!

## Development Setup

1. Fork the repository and clone it locally.
2. Install the necessary dependencies (we recommend using a virtual environment):
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-test.txt
   ```

## Pull Request Guidelines

* **Tests:** Ensure that your changes pass all local unit tests (`pytest tests/`) and that you have added tests for any new functionality.
* **Docker:** Ensure that the Docker build passes locally before submitting your PR.
* **PR Template:** When opening a Pull Request, please fill out the provided PR template carefully. This ensures a faster review process.
* **CI Pipeline:** All Pull Requests will automatically trigger our CI pipeline. The pipeline must pass before your PR can be merged.

Thank you for your time, energy, and contributions to YAML-validator!

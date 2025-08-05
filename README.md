# YAML Validator

A comprehensive YAML validation tool that performs syntax checking, linting, and security analysis using industry-standard tools.

## What We Check

### 🔍 **Syntax Validation**
- YAML structure and formatting
- Proper indentation and syntax rules
- Valid YAML document structure

### 📋 **Linting (yamllint)**
- Code style and formatting issues
- Indentation consistency
- Line length violations
- Trailing spaces and empty lines
- Document structure best practices

### 🔒 **Security Analysis (Checkov)**
- Security misconfigurations
- Hardcoded secrets detection
- Infrastructure security best practices
- Compliance violations
- Potential security vulnerabilities

## Usage

### Git Bash on Windows
```bash
MSYS_NO_PATHCONV=1 docker run -v "$(pwd):/data" pooyanazad/yaml-checker <yaml-file>
```

### PowerShell/CMD on Windows
```bash
docker run -v "%cd%:/data" pooyanazad/yaml-checker <yaml-file>
```

### Linux/macOS
```bash
docker run -v "$(pwd):/data" pooyanazad/yaml-checker <yaml-file>
```

## Examples

```bash
# Validate a single YAML file
MSYS_NO_PATHCONV=1 docker run -v "$(pwd):/data" pooyanazad/yaml-checker config.yaml

# Validate files in subdirectories
MSYS_NO_PATHCONV=1 docker run -v "$(pwd):/data" pooyanazad/yaml-checker tests/test.yaml
```

## Output

The validator provides detailed reports including:
- **Syntax Issues**: Parse errors and structural problems
- **Linting Issues**: Style and formatting violations with severity levels
- **Security Issues**: Security misconfigurations and vulnerabilities
- **Summary**: Total count of issues by severity (Critical, High, Medium, Low)

## Docker Image

- **Repository**: `pooyanazad/yaml-checker`
- **Latest Version**: `v1.0.2`
- **Tags**: `latest`, `v1.0.2`, `v1.0.1`

## Requirements

- Docker installed on your system
- YAML files to validate

## Features

✅ **Multi-platform support** (Windows, Linux, macOS)  
✅ **Volume mounting** for external file access  
✅ **Comprehensive validation** (syntax, style, security)  
✅ **Detailed reporting** with severity levels  
✅ **Industry-standard tools** (yamllint, checkov)  
✅ **Zero configuration** required
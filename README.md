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

## How it look like 
<img width="881" height="571" alt="image" src="https://github.com/user-attachments/assets/0a3278f9-9f86-431c-90f7-e3d122f0043b" />

## Usage

### Linux/macOS
```bash
docker run -v "$(pwd):/data" pooyanazad/yaml-checker <yaml-file>
```

### PowerShell/CMD on Windows
```bash
docker run -v "%cd%:/data" pooyanazad/yaml-checker <yaml-file>
```

### Git Bash on Windows
```bash
MSYS_NO_PATHCONV=1 docker run -v "$(pwd):/data" pooyanazad/yaml-checker <yaml-file>
```
### My personal usage
I define below command on .bashrc as an alias
```
alias ytest='docker run -v "$(pwd):/data" pooyanazad/yaml-checker'
```
I can use this anywhere simply
```
ytest ping.yaml
```

## Output

The validator provides detailed reports including:
- **Syntax Issues**: Parse errors and structural problems
- **Linting Issues**: Style and formatting violations with severity levels
- **Security Issues**: Security misconfigurations and vulnerabilities
- **Summary**: Total count of issues by severity (Critical, High, Medium, Low)

## Docker Image

- **Repository**: `pooyanazad/yaml-checker`
- **Valid tag**: Latest is updated always
- **Runtime**: Docker image is based on `python:3.12-slim`

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

## Monthly Automated Releases

- Scheduled : Every 1st of the month at 00:00 UTC with auto-incrementing versions starting from v2.0.1-YYYYMMDD, then v2.0.2-YYYYMMDD, etc.
- Includes : Fresh Docker builds, comprehensive testing, Docker Hub deployment, and GitHub releases with usage examples

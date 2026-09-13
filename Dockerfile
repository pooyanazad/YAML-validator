# Use Python slim image for smaller size
FROM python:3.12-slim

# OCI image labels for discoverability and traceability
LABEL org.opencontainers.image.title="YAML Validator" \
      org.opencontainers.image.description="Validate YAML files for syntax errors, style issues, and security misconfigurations." \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.source="https://github.com/pooyanazad/YAML-validator" \
      org.opencontainers.image.licenses="MIT"

# Set working directory
WORKDIR /app

# Create data directory for mounting external files
RUN mkdir -p /data

# Copy requirements first for better caching
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install -r requirements.txt

# Copy the application and test files
COPY app.py .
COPY yaml_validator/ ./yaml_validator/
COPY tests/ ./tests/
COPY entrypoint.sh .

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

# Set the working directory to /data for file operations
WORKDIR /data

# Verify the image is functional by checking that core libraries are importable
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import yaml; import yamllint"

# Set the entrypoint to use the shell script
ENTRYPOINT ["/app/entrypoint.sh"]

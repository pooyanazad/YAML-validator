# ─────────────────────────────────────────────
# Stage 1 — builder: install dependencies only
# ─────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Install into an isolated venv so we can copy it cleanly
RUN python3 -m venv /build/venv

COPY requirements.txt .

# Upgrade pip inside the venv and install production dependencies
RUN /build/venv/bin/pip install --upgrade pip --quiet && \
    /build/venv/bin/pip install --quiet -r requirements.txt

# ─────────────────────────────────────────────
# Stage 2 — runtime: lean production image
# ─────────────────────────────────────────────
FROM python:3.12-slim AS runtime

# OCI image labels for discoverability and traceability
LABEL org.opencontainers.image.title="YAML Validator" \
      org.opencontainers.image.description="Validate YAML files for syntax errors, style issues, and security misconfigurations." \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.source="https://github.com/pooyanazad/YAML-validator" \
      org.opencontainers.image.licenses="MIT"

# Copy the pre-built virtual environment from the builder stage
COPY --from=builder /build/venv /app/venv

# Set working directory and create mount directory
WORKDIR /app
RUN mkdir -p /data

# Copy only the application source — no test files, no dev tools
COPY app.py .
COPY yaml_validator/ ./yaml_validator/
COPY entrypoint.sh .

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

# Create a non-root user and grant ownership
RUN useradd --system --create-home --shell /bin/bash validator \
    && chown -R validator:validator /app /data

# Use the venv Python for all subsequent commands
ENV PATH="/app/venv/bin:$PATH"

# Switch to the non-root user
USER validator

# Set the working directory to /data for file operations
WORKDIR /data

# Verify the image is functional by checking that core libraries are importable
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import yaml; import yamllint"

# Set the entrypoint to use the shell script
ENTRYPOINT ["/app/entrypoint.sh"]

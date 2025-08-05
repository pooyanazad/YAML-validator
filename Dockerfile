# Use Python slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Create data directory for mounting external files
RUN mkdir -p /data

# Copy requirements first for better caching
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN python -m pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the application and test files
COPY app.py .
COPY tests/ ./tests/
COPY entrypoint.sh .

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

# Set the working directory to /data for file operations
WORKDIR /data

# Set the entrypoint to use the shell script
ENTRYPOINT ["/app/entrypoint.sh"]
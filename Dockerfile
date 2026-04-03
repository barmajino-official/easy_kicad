FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set up the application
WORKDIR /app
COPY . .

# Install requirements
RUN pip install --no-cache-dir requests pydantic

# Prepare absolute volume paths
RUN mkdir -p /app/database /app/outputFile && chmod +x /app/bulk_run.sh

# Default entrypoint for the master mirroring engine
ENTRYPOINT ["/app/bulk_run.sh"]

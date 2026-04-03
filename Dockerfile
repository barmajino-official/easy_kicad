# Use a lightweight Python base image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the project files to the container
COPY . /app/easy_kicad

# Set PYTHONPATH to identify easy_kicad as a package
ENV PYTHONPATH=/app

# Install Python dependencies
RUN pip install --no-cache-dir requests pydantic

# Make scripts executable
RUN chmod +x /app/easy_kicad/bulk_run.sh

# Default entrypoint
ENTRYPOINT ["python", "-m", "easy_kicad"]

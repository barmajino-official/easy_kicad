# Use a lightweight Python base image
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Move code to an isolated package path for robust importing
WORKDIR /opt/easy_kicad_app
COPY . easy_kicad/

# Ensure scripts are executable
RUN chmod +x easy_kicad/bulk_run.sh

# Most critical line: set PYTHONPATH to parent of 'easy_kicad' folder
ENV PYTHONPATH=/opt/easy_kicad_app

# Install requirements
# Use --no-cache-dir to minimize image size
RUN pip install --no-cache-dir requests pydantic

# Create absolute mount points for volumes
RUN mkdir -p /app/database /app/outputFile

# Set WorkDir for the script execution to be the ROOT (for relative paths)
WORKDIR /opt/easy_kicad_app

# Entry point: Run the script from the root /opt/easy_kicad_app
ENTRYPOINT ["/opt/easy_kicad_app/easy_kicad/bulk_run.sh"]

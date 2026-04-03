# Use a lightweight Python base image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy the project files to the container
# This is assuming you run docker build from the root of easy_kicad
COPY . /app/easy_kicad

# Set PYTHONPATH to identify easy_kicad as a package
ENV PYTHONPATH=/app

# Install Python dependencies
RUN pip install --no-cache-dir requests

# Define the entrypoint so you can pass arguments to the tool easily
ENTRYPOINT ["python", "-m", "easy_kicad"]

# Default command if no arguments are provided (show help)
CMD ["--help"]

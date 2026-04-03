FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set up the application build context
# (Copying everything to /tmp/build/ and then installing it)
WORKDIR /tmp/build/
COPY . .

# 🛡️ THE HOLY GRAIL: Install the project as a formal package
RUN pip install --no-cache-dir .

# Now we move to our runtime folder
RUN mkdir -p /app/database /app/outputFile
WORKDIR /app

# The package-installed 'bulk_run.sh' is also copied for utility
# OR we can just use the one from the build folder if needed
RUN cp /tmp/build/bulk_run.sh /app/bulk_run.sh && chmod +x /app/bulk_run.sh

# Default entrypoint for the master mirroring engine
ENTRYPOINT ["/app/bulk_run.sh"]

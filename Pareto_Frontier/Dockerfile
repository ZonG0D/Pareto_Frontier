FROM python:3.11-slim

# Install essential Linux utilities for observability and networking
# procps provides 'top'/'ps' logic; iproute2 facilitates network inspection
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \n    jq \
    procps \
    iproute2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install project dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Set PYTHONPATH to ensure module discovery works correctly inside the container
ENV PYTHONPATH="/app"

# Default entrypoint is the CLI tool
ENTRYPOINT ["python3", "bin/pareto_cli.py"]

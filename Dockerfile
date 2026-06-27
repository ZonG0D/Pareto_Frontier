FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set up virtualenv if preferred, but here we'll use system python for simplicity in container
ENV PATH="/app/.venv/bin:${PATH}"

ENTRYPOINT ["python3", "bin/pareto_cli.py"]

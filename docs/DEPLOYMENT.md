# Pareto Frontier Deployment Guide

This document outlines the deployment procedures for the Pareto Frontier LLM stack, focusing on energy efficiency, minimal dependencies, and high performance.

## Architecture Overview

The stack is composed of three primary layers:
1.  **Orchestration Layer:** Python-based management logic (`core/orchestrator.py`).
2.0 **Data Normalization Layer (Silas):** Lightweight Bash shims for input sanitization.
3.  **Inference Layer:** Decoupled LLM providers (Local via Ollama or Remote APIs).

## Deployment Modes

### 1. Development Mode (Direct)
Recommended for rapid development and profiling. Uses the existing virtual environment.
```bash
# Setup environment
./setup.sh

# Activate venv
source .venv/bin/activate

# Run entry point
./scripts/pareto-run "your prompt here"
```

### 2. Production Mode (Docker)
Ensures environmental parity and isolation. The project uses `docker-compose` to orchestrate the runtime components.

#### Prerequisites
- Docker & Docker Compose
- Ollama (if running local models)

#### Deployment Steps
1. **Build the stack:**
   ```bash
   docker-compose up -d --build
   ```
2. **Verify service health:**
   ```bash
   docker-compose ps
   docker-compose logs -f
   ```
3. **Run client commands:**
   Use `docker exec` to interact with the orchestration container:
   ```bash
   docker exec -it pareto_orchestrator ./scripts/pareto-run "test prompt"
   ```

## Resource Optimization (Pro-Energy Principles)

To adhere to our mission of minimizing compute costs and energy waste, implement the following configurations in production:

* **Cache Management:** Ensure the `parse_cache` directory is mapped to a high-speed persistent volume to maximize cache hits.
* **Tiered Routing:** Configure `models/config.yaml` to route simple classification tasks through lightweight models (e.g., quantized 3B models) and reserve heavy reasoning agents for complex prompts.
* **Orchestration Silos:** Use the `parse-input.sh` layer as a firewall to reject nonsensical or excessively long inputs *before* they reach expensive inference models.

## Monitoring & Observability
Metrics should be monitored via:
- **Pareto Efficiency Score:** Tracked via `evals/benchmark.py`.
- **System Load:** Monitor CPU and Memory metrics exported by the instrumentation layer during peak loads.

# Contributing to Pareto Frontier

Welcome! We build tools that prioritize people and the planet by optimizing for efficiency and accuracy.

## Our Values
- **Minimalism:** Do not add a dependency unless it's absolutely essential. Shell is our preferred language for simple logic.
- **Transparency:** Every optimization must be measurable via the `evals/` suite.
- **Integrity:** No stubs. If code isn't tested against real LLM responses, it doesn't exist.

## Development Workflow

### 1. Setting up the environment
Use our provided setup script to create a clean virtual environment:
```bash
./setup.sh
source .venv/bin/activate
```

### 2. Adding a New Intelligence Tier
If you want to add a new model tier (e.g., a ultra-fast local Llama instance):
1. Update `models/config.yaml` with the endpoint and model name.
2. Ensure it complies with our minimum latency requirements for "cheap" tiering.

### 3. Adding New Benchmark Tests
1. Add your test prompts to `data/datasets/test_inputs.jsonl`.
2. Run the full suite: `./evals/run_benchmarks.sh`.
3. Verify that no regressions were introduced in the Pareto Efficiency Score.

## Bug Reports and Feature Requests
Please use GitHub Issues to report bugs or suggest new "Pareto-optimal" optimization strategies.

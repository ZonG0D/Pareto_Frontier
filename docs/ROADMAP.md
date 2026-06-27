# 🗺️ Pareto Frontier Roadmap

A strategic plan for building the most efficient, robust, and simple cascaded LLM stack for edge environments.

## 🎯 Core Objective
Maximize Semantic Accuracy while minimizing Compute Cost and Latency (The Pareto Front).

---

## 🛠 Phase 1: Hardening & Diagnostics (CURRENT)
**Goal**: Ensure system reliability and observability before adding new features.

- [ ] **Formalize Diagnostics (`bin/pareto-doctor`)**: Stabilize error reporting for environmental issues (Ollama, VENV, Disk).
- [ ] **Standardize Benchmarking (`evals/benchmark.py`)**: Implement a rigorous "Pareto Score" calculation ($\frac{\text{Accuracy}}{\text{Cost}}$) using real execution data from `performance_audit.jsonl`.
- [ ] **Stabilize Core Cascade**: Finalize error handling and retry logic in the orchestrator to handle stochastic model failures gracefully.

## 🧠 Phase 2: Intelligence Optimization
**Goal**: Reduce the compute "floor" by preventing unnecessary reasoning tasks.

- [ ] **Zero-Cost Filtering (Input Sanitization)**: Implement a pre-orchestration check that identifies low-intent/garbage input and returns an immediate response without invoking LLMs.
- [ ] **Semantic Cache Refinement**: Enhance `core/runtime/semantic_cache.py` with support for local, fast vector similarity searches to ensure near-zero latency for repeated intent.
- [ ] **Advanced Normalization**: Integrate domain-specific cleanup rules (e.g., log parsing, code sanitization) into the "Silas" normalization engine.

## 🚀 Phase 3: Deployment & Edge Readiness
**Goal**: Make the stack a single-command solution for non-expert users on edge devices.

- [ ] **One-Command Bootstrapping (`setup_edge.sh`)**: A script to install dependencies, set up `.venv`, and configure Ollama connection in one go.
- [ ] **Edge Observability Dashboard**: A lightweight CLI/Web UI (perhaps using simple HTML files) to visualize real-time latency vs. cost metrics across the cascade tiers.
- [ ] **Automated Regression Testing**: CI-level checks that prevent updates from decreasing the overall Pareto Score of the system.

---
*Built for efficiency. Built for the edge.*

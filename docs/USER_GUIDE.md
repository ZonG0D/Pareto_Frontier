# Pareto Frontier User Guide

Welcome to **Pareto Frontier**, the high-efficiency LLM orchestration stack designed for minimal compute and maximum accuracy.

## 🚀 Quick Start

### 1. Installation
Clone this repository and run the setup script to configure your environment (creates a virtual environment and installs dependencies).
```bash
git clone https://github.com/ZonG0D/Pareto_Frontier Pareto_Frontier
cd Pareto_Frontier
./setup.sh
```

### 2. Running the Stack
Once set up, you can use the `pareto-run` command to process prompts using our cascading architecture.

#### Basic Usage (Direct Prompt)
Pass your prompt directly as an argument:
```bash
./bin/pareto-run "What is the capital of France?"
```

#### Piping Input (Batch / Stream)
You can pipe text from other commands into the stack:
```bash
echo "How to optimize LLM inference" | ./bin/pareto-run
```

## 🛠 Advanced Configuration

The behavior of the cascade is controlled via `models/config.yaml`. You can swap model endpoints for different tiers without changing code.

**Tiers:**
- **Cheap Tier**: Optimized for rapid input normalization and semantic extraction (e.g., local Ollama models).
- **Smart Tier**: High-reasoning, high-intelligence models (e.g., DeepSeek, Claude) used only when necessary.

#### Configuration Example (`models/config.yaml`)
```yaml
tiers:
  cheap:
    endpoint: "http://localhost:11434/api/chat"
    model: "llama3-8b"
  smart:
    endpoint: "https://api.openai.com/v1/chat/completions"
    model: "gpt-4o"
```

## ⚙️ Architecture Overview (The Cascade)

Pareto Frontier uses a **tiered intelligence pipeline**:

1.  **Cache Check (LRU):** A fast, local check to see if the user has asked this exact thing recently. If yes, we return the cached result instantly.
2.  **Parsing & Normalization:** The input is sent to a "Cheap" model to clean typos, expand abbreviations, and extract intent. This ensures the Smart Model receives perfect context.
3.  **Semantic Hand-off:** The normalized text is passed to the "Smart" model for high-fidelity reasoning.

## 📈 Metrics & Efficiency

We measure success via the **Pareto Score**:
$$\text{Efficiency} = \frac{\text{Semantic Accuracy}}{\text{Compute Cost (Time/Tokens)}}$$

By using cheap models for structure and smart models only for depth, we achieve massive speedups and cost reductions.

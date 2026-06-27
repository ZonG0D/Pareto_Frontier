# 🚀 Pareto Frontier

**High-Efficiency LLM Stack for the Edge.**

Pareto Frontier is an orchestration layer designed to maximize AI accuracy while minimizing compute costs and latency. By implementing a **Cascaded Intelligence Pipeline**, we ensure that expensive, high-reasoning models are only invoked when necessary, using lightweight local models to handle normalization and caching first.

## 💎 Key Features
- **Tiered Orchestration:** Uses "Cheap" (local/fast) models for preprocessing and "Smart" (heavyweight) models for deep reasoning.
- **Intelligent LRU Cache:** Sub-millisecond response times for repeated queries through an intelligent filesystem cache.
- **Semantic Normalization:** Automatically cleans noisy, typo-ridden, or fragmented user inputs before they reach the heavy model.
- **Efficiency Optimized:** Designed to run on everything from massive GPU clusters down to Raspberry Pi.

## 📦 Installation

```bash
git clone <repo_url> Pareto_Frontier
cd Pareto_Frontier
./setup.sh
```

## 🚀 Quick Start

Use the `pareto-run` CLI for an effortless experience:

```bash
# Direct prompt
./bin/pareto-run "What is the capital of France?"

# Piping input
echo "How to optimize LLM inference" | ./bin/pareto-run
```

## 📖 Documentation

For detailed configuration guides and architecture deep-dives, please refer to our [User Guide](docs/USER_GUIDE.md).

---
*Build for efficiency. Built for the edge.*


---
*Project refactored for production-grade structure.*
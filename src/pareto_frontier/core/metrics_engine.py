import time
from dataclasses import dataclass, asdict
from typing import Dict, List
from pathlib import Path


@dataclass
class ParetoMetric:
    timestamp: float
    prompt_snippet: str
    semantic_accuracy: (
        float  # 0.0 to 1.0 (assumed via LLM-based evaluation or baseline comparison)
    )
    compute_cost: float  # normalized cost metric (e.g., latency * tokens / reference)
    pareto_score: float  # accuracy / cost
    cache_hit: bool


class MetricsEngine:
    def __init__(self, audit_log_path: Path):
        self.audit_log_path = audit_log_path
        self.metrics_history: List[ParetoMetric] = []

    def log_execution(
        self, prompt: str, accuracy: float, cost: float, latency: float, cache_hit: bool
    ) -> ParetoMetric:
        """Logs a single execution and returns the computed metric."""
        # Calculate Score (Simplified: Higher is better. Lower cost/latency improves score)
        # We use 1 / cost to treat it as "value for money" or simply accuracy / cost if cost > 0
        score = accuracy / max(cost, 1e-6)

        metric = ParetoMetric(
            timestamp=time.time(),
            prompt_snippet=prompt[:50],
            semantic_accuracy=round(accuracy, 4),
            compute_cost=round(cost, 4),
            pareto_score=round(score, 4),
            cache_hit=cache_hit,
        )

        self.metrics_history.append(metric)
        self._persist_metric(metric)
        return metric

    def _persist_metric(self, metric: ParetoMetric):
        """Appends the metric to the JSONL audit log."""
        import json

        try:
            with open(self.audit_log_path, "a") as f:
                f.write(json.dumps(asdict(metric)) + "\n")
        except Exception as e:
            print(f"[ERROR] Failed to persist metric: {e}")

    def get_summary(self) -> Dict:
        """Returns an aggregate view of current session performance."""
        if not self.metrics_history:
            return {"status": "no data"}

        count = len(self.metrics_history)
        avg_accuracy = sum(m.semantic_accuracy for m in self.metrics_history) / count
        avg_cost = sum(m.compute_cost for m in self.metrics_history) / count
        avg_score = sum(m.pareto_score for m in self.metrics_history) / count
        cache_hit_rate = len([m for m in self.metrics_history if m.cache_hit]) / count

        return {
            "sample_size": count,
            "avg_accuracy": round(avg_accuracy, 4),
            "avg_cost": round(avg_cost, 4),
            "avg_pareto_score": round(avg_score, 4),
            "cache_hit_rate": f"{round(cache_hit_rate * 100, 2)}%",
        }


if __name__ == "__main__":
    # Test Mode
    import tempfile

    with tempfile.NamedTemporaryFile() as tmp:
        engine = MetricsEngine(Path(tmp.name))
        print("Logging dummy metrics...")
        engine.log_execution("Test prompt", 0.9, 1.5, 2.3, False)
        engine.log_execution("Cached prompt", 0.9, 0.1, 0.05, True)
        print(f"Summary: {engine.get_summary()}")

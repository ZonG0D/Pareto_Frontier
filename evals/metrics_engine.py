"""
Pareto Frontier Metrics Engine
Quantifies the Pareto Efficiency of the stack.
Formula: Pareto Score = Semantic Accuracy / (Compute Cost * Latency)
"""

import math

class ParetoMetrics:
    def __init__(self):
        pass

    def calculate_pareto_score(self, semantic_accuracy, compute_cost, latency):
        """
        Calculates the efficiency score. 
        Higher is better (more accuracy for less resource).
        """
        if compute_cost <= 0 or latency <= 0:
            return 0.0
        return semantic_accuracy / (compute_cost * latency)

    def evaluate_system(self, results):
        """
        Processes a batch of benchmark results to find the aggregate efficiency.
        """
        if not results:
            return None

        # Calculate mean values across the batch
        avg_accuracy = sum(r['accuracy'] for r in results) / len(results)
        avg_compute = sum(r['compute'] for r in results) / len(results)
        avg_latency = sum(r['latency'] for r in results) / len(results)

        pareto_score = self.calculate_pareto_score(avg_accuracy, avg_compute, avg_latency)

        return {
            "average_accuracy": avg_accuracy,
            "average_compute": avg_compute,
            "average_latency": avg_latency,
            "pareto_score": pareto_score
        }

if __name__ == "__main__":
    # Self-test logic
    engine = ParetoMetrics()
    sample_results = [
        {"accuracy": 0.95, "compute": 1.0, "latency": 2.0}, # Score: 0.475
        {"accuracy": 0.80, "compute": 0.2, "latency": 0.5}  # Score: 8.0 (Very efficient!)
    ]
    stats = engine.evaluate_system(sample_results)
    print(f"Test Stats - Pareto Score: {stats['pareto_score']:.4f}")

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
        if compute_cost <= 0 or latency <= 0:
            return 0.0
        return semantic_accuracy / (compute_cost * latency)

    def evaluate_system(self, results):
        if not results:
            return None
        
        avg_accuracy = sum(r['accuracy'] for r in results) / len(results)
        avg_compute = sum(r['compute'] for r in results) / len(results)
        avg_latency = sum(r['latency'] for r in results) / len(results)
        
        peak_mem = None
        if all(isinstance(r.get('peak_memory_mb'), (int, float)) for r in results if 'peak_memory_mb' in r):
             avg_mem = sum(r['peak_memory_mb'] for r in results) / len(results)
        else:
             avg_mem = None

        pareto_score = self.calculate_pareto_score(avg_accuracy, avg_compute, avg_latency)

        res = {
            "average_accuracy": avg_accuracy,
            "average_compute": avg_compute,
            "average_latency": avg_latency,
            "pareto_score": pareto_score
        }
        if avg_mem is not None:
            res["average_peak_memory_mb"] = avg_mem
            
        return res

if __name__ == "__main__":
    engine = ParetoMetrics()
    sample_results = [
        {"accuracy": 0.95, "compute": 1.0, "latency": 2.0},
        {"accuracy": 0.80, "compute": 0.2, "latency": 0.5}
    ]
    stats = engine.evaluate_system(sample_results)
    print(f"Test Stats - Pareto Score: {stats['pareto_score']:.4f}")

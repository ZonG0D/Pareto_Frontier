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
        
        # Ensure we are working with valid data points
        valid_results = [r for r in results if isinstance(r, dict) and 'accuracy' in r]
        if not valid_results:
            return None

        avg_accuracy = sum(r['accuracy'] for r in valid_results) / len(valid_results)
        
        # Safe summation to avoid division by zero or missing keys
        comp_vals = [r['compute'] for r in valid_results if 'compute' in r]
        avg_compute = sum(comp_vals) / len(comp_vals) if comp_vals else 1.0

        lat_vals = [r['latency'] for r in valid_results if 'latency' in r]
        avg_latency = sum(lat_vals) / len(lat_vals) if lat_vals else 1.0
        
        # Check peak memory (only include if present and numeric across all results to avoid skewing averages)
        mem_values = [r['peak_memory_mb'] for r in valid_results if 'peak_memory_mb' in r and isinstance(r['peak_memory_mb'], (int, float))]
        avg_mem = None
        if len(mem_values) == len(valid_results):
             avg_mem = sum(mem_values) / len(mem_values)

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

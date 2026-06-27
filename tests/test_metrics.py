from evals.metrics_engine import ParetoMetrics

def test_calculation():
    engine = ParetoMetrics()
    # Test Case 1: Perfect match
    res1 = engine.evaluate_system([{"accuracy": 1.0, "compute": 1.0, "latency": 1.0}])
    assert res1['pareto_score'] == 1.0

    # Test Case 2: Better efficiency (High accuracy, low cost)
    res2 = engine.evaluate_system([{"accuracy": 1.0, "compute": 0.5, "latency": 0.5}])
    assert res2['pareto_score'] == 4.0

    # Test Case 3: Mixed results
    sample_results = [
        {"accuracy": 0.95, "compute": 1.0, "latency": 2.0},
        {"accuracy": 0.80, "compute": 0.2, "latency": 0.5}
    ]
    # avg_acc = (0.95 + 0.8) / 2 = 0.875
    # avg_comp = (1.0 + 0.2) / 2 = 0.6
    # avg_lat  = (2.0 + 0.5) / 2  = 1.25
    # score = 0.875 / (0.6 * 1.25) = 0.875 / 0.75 = 1.1666...
    stats = engine.evaluate_system(sample_results)
    assert abs(stats['pareto_score'] - 1.1666666666666667) < 1e-6

    print("✅ Metrics Engine Verification: PASSED")

if __name__ == "__main__":
    try:
        test_calculation()
    except Exception as e:
        print(f"❌ Metrics Engine Verification: FAILED ({e})")
        exit(1)

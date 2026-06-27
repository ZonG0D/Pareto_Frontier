#!/usr/bin/env python3
import argparse
import json
import sys
import os
from pathlib import Path

# Import core logic components
try:
    from pareto_frontier.core.orchestrator import Orchestrator
except ImportError:
    # Fallback for different execution environments
    import sys as s
    s.path.append(str(Path(__file__).resolve().parent.parent))
    from pareto_frontier.core.orchestrator import Orchestrator

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[1;31m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def run_benchmarks(experiment_type: str, project_root: Path):
    print(f"{Colors.OKCYAN}{Colors.BOLD}📊 Starting Pareto Automated Benchmarking...{Colors.ENDC}")
    import subprocess
    cmd = [sys.executable, str(project_root / "evals" / "benchmark.py"), "--experiment", experiment_type]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print(f"{Colors.FAIL}Error during benchmarking:{Colors.ENDC}")
            print(result.stderr)
    except Exception as e:
        print(f"{Colors.FAIL}Failed to launch benchmark suite:{Colors.ENDC} {e}")

def process_prompt(args, project_root):
    orch = Orchestrator()

    user_input = " ".join(args.prompt) if args.prompt else ""
    if not user_input:
        try:
            import sys as s
            user_input = s.stdin.read().strip()
        except Exception:
            pass

    if not user_input:
        print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} No input detected.")
        sys.exit(1)

    print(f"\n{Colors.OKCYAN}{Colors.BOLD}🚀 Pareto Frontier Execution{Colors.ENDC}")
    print(f"{Colors.OKBLUE}----------------------------{Colors.ENDC}")
    print(f"Prompt: {user_input[:100]}{'...' if len(user_input) > 100 else ''}")

    if hasattr(orch, 'discovery_error') and orch.discovery_error:
        print(f"{Colors.FAIL}CRITICAL ERROR:{Colors.ENDC} {orch.discovery_error}")
        sys.exit(1)

    try:
        result = orch.run_cascade(user_input)

        if 'reasoning' in result and '_metrics' in result:
            metrics = result['_metrics']
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}✨ FINAL RESPONSE{Colors.ENDC}")
            print("-" * 25)
            print(result['reasoning'])
            print("-" * 25)

            if args.stats:
                print(f"\n{Colors.OKCYAN}{Colors.BOLD}📊 PERFORMANCE METRICS{Colors.ENDC}")
                print("-" * 25)
                if 'total_latency_ms' in metrics:
                    print(f"  Total Latency: {metrics['total_latency_ms']} ms")
                else:
                    print("  Latency metric unavailable.")
                if metrics.get('cache_hit'): print("  Cache Status: HIT ✨")
                else: print("  Cache Status: MISS ❄️")
                print("-" * 25)
        elif '_error_message' in result:
            print(f"\n{Colors.FAIL}RUNTIME ERROR:{Colors.ENDC}")
            print(result['_error_message'])
        else:
            print(f"Result: {result}")

    except Exception as e:
        print(f"{Colors.FAIL}RUNTIME ERROR:{Colors.ENDC} An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Pareto Frontier CLI")
    parser.add_argument("prompt", nargs='*', help="The prompt to process.")
    parser.add_argument('--stats', action='store_true', help="Show performance metrics")
    parser.add_argument('--benchmark', action='store_true', help="Run automated Pareto benchmarks")
    parser.add_argument('--experiment', choices=['standard', 'cache'], default='cache', help="Type of benchmark experiment (default: cache)")

    args = parser.parse_args()
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    if not (project_root / "pyproject.toml").exists():
        for p in [project_root, project_root.parent]:
            if (p / "pyproject.toml").exists():
                project_root = p
                break

    if args.benchmark:
        run_benchmarks(args.experiment, project_root)
    else:
        process_prompt(args, project_root)

if __name__ == "__main__":
    main()

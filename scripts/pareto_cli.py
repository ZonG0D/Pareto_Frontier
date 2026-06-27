#!/usr/bin/env python3
import argparse
import json
import sys
import os
import subprocess
from pathlib import Path
import threading

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
    cmd = [sys.executable, "evals/benchmark.py", "--experiment", experiment_type]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print(f"{Colors.FAIL}Error during benchmarking:{Colors.ENDC}")
            print(result.stderr)
    except Exception as e:
        print(f"{Colors.FAIL}Failed to launch benchmark suite:{Colors.ENDC} {e}")

def process_prompt(args, project_root):
    script_dir = Path(__file__).resolve().parent
    orchestrator_path = project_root / "core" / "orchestrator.py"

    if not orchestrator_path.exists():
        print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} Orchestrator not found at {orchestrator_path}")
        sys.exit(1)

    # Input collection (Legacy and Argument support)
    user_input = " ".join(args.prompt) if args.prompt else ""
    if not user_input:
        user_input = sys.stdin.buffer.read().decode('utf-8', errors='replace').strip().replace('\x00', ' ')

    if not user_input:
        print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} No input detected.")
        sys.exit(1)

    print(f"\n{Colors.OKCYAN}{Colors.BOLD}🚀 Pareto Frontier Execution{Colors.ENDC}")
    print(f"{Colors.OKBLUE}----------------------------{Colors.ENDC}")
    print(f"Prompt: {user_input[:100]}{'...' if len(user_input) > 100 else ''}")

    try:
        python_exe = str(project_root / ".venv" / "bin" / "python3") if (project_root / ".venv").exists() else sys.executable
        env = os.environ.copy()
        env["PYTHONPATH"] = str(project_root)

        process = subprocess.Popen(
            [python_exe, "-m", "core.orchestrator", user_input],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )

        def log_stream(stream):
            for line in stream:
                if line.strip(): print(f"  {line.strip()}")

        error_thread = threading.Thread(target=log_stream, args=(process.stderr,))
        error_thread.start()

        stdout, _ = process.communicate()
        error_thread.join()

        if process.returncode != 0:
            print(f"\n{Colors.FAIL}[FATAL ERROR]{Colors.ENDC}")
            sys.exit(1)

        data = json.loads(stdout.strip())

        if args.stats:
            metrics = data.get('_metrics', {})
            print(f"\n{Colors.OKCYAN}{Colors.BOLD}📊 PERFORMANCE METRICS{Colors.ENDC}")
            print("-" * 25)
            for stage in metrics.get('stages', []):
                name = stage.get('name', 'Unknown').capitalize()
                ms = stage.get('latency_ms', 0)
                print(f"  {name:<12}: {ms} ms")
            if metrics.get('cache_hit'): print("  Cache Status: HIT ✨")
            else: print("  Cache Status: MISS ❄️")
            print(f"Total Latency: {metrics.get('total_latency_ms', 0)} ms\n" + "-" * 25)

        print(f"\n{Colors.OKGREEN}{Colors.BOLD}✨ FINAL RESPONSE{Colors.ENDC}")
        print("-" * 25)
        if 'reasoning' in data: print(data['reasoning'])
        else: print(str(data))
        print("-" * 25)

    except json.JSONDecodeError:
        print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} Failed to parse response from the backend.")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.FAIL}[FATAL]{Colors.ENDC} An unexpected error occurred: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Pareto Frontier: High-Efficiency LLM Stack CLI")
    # Positional arguments for the prompt (optional, to allow benchmark as first arg)
    parser.add_argument("prompt", nargs='*', help="The prompt to process.")
    # Control flags
    parser.add_argument('--stats', action='store_true', help="Show performance metrics")
    parser.add_argument('--benchmark', action='store_true', help="Run automated Pareto benchmarks")
    parser.add_argument('--experiment', choices=['standard', 'cache'], default='cache', help="Type of benchmark experiment (default: cache)")

    args = parser.parse_args()
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent

    if args.benchmark:
        run_benchmarks(args.experiment, project_root)
    else:
        process_prompt(args, project_root)

if __name__ == "__main__":
    main()

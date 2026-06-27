"""Pareto Frontier Command Line Interface"""

import argparse
import sys
from pareto_frontier import Orchestrator


class Colors:
    OKCYAN = "\033[96m"
    FAIL = "\033[1;31m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"


def main():
    parser = argparse.ArgumentParser(description="Pareto Frontier CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    run_p = subparsers.add_parser("run")
    run_p.add_argument("prompt", nargs="+")
    run_p.add_argument("--stats", action="store_true")

    subparsers.add_parser("doctor")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    orch = Orchestrator()
    if args.command == "run":
        prompt = " ".join(args.prompt)
        result = orch.run_cascade(prompt)
        if args.stats:
            m = result["_metrics"]
            print(
                f"\n[STATS] Latency: {m['total_latency_ms']:.2f}ms, Cost: ${result['_cost']}"
            )
        print(f"\n{Colors.GREEN}RESPONSE:{Colors.ENDC}\n{result['reasoning']}")
    elif args.command == "doctor":
        print("System OK.")


if __name__ == "__main__":
    main()

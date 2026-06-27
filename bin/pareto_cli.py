#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path
import subprocess

# Simple ANSI color codes for "People First" UI
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def main():
    parser = argparse.ArgumentParser(description="Pareto Frontier: High-Efficiency LLM Stack CLI")
    parser.add_argument("prompt", nargs='*', help="The prompt to process. If empty, reads from stdin.")
    args = parser.parse_args()

    # Determine input text
    if args.prompt:
        user_input = " ".join(args.prompt)
    else:
        # Read from stdin (useful for piping: echo "hi" | pareto-run)
        user_input = sys.stdin.read().strip()

    if not user_input:
        print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} No input detected. Please provide a prompt or pipe text into it.")
        sys.exit(1)

    # Find project root (assumes this script is in /home/anonz/Pareto_Frontier/bin/)
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    orchestrator_path = project_root / "core" / "orchestrator.py"

    if not orchestrator_path.exists():
        print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} Orchestrator not found at {orchestrator_path}")
        sys.exit(1)

    print(f"\n{Colors.OKCYAN}{Colors.BOLD}🚀 Pareto Frontier Execution{Colors.ENDC}")
    print(f"{Colors.OKBLUE}----------------------------{Colors.ENDC}")
    print(f"Prompt: {user_input}")
    print("")

    try:
        # Execute the orchestrator via the project's virtual environment if it exists, 
        # otherwise use current python. 
        python_exe = str(project_root / ".venv" / "bin" / "python3") if (project_root / ".venv").exists() else sys.executable
        
        process = subprocess.Popen(
            [python_exe, str(orchestrator_path), user_input],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Capture stderr for the "Pretty" UI (the orchestrator logs to stderr)
        def log_stream(stream):
            for line in stream:
                if line.strip():
                    print(f"  {line.strip()}")

        import threading
        error_thread = threading.Thread(target=log_stream, args=(process.stderr,))
        error_thread.start()

        # Capture the JSON stdout from the orchestrator
        stdout, _ = process.communicate()
        error_thread.join()

        if process.returncode != 0:
            print(f"\n{Colors.FAIL}[FATAL ERROR]{Colors.ENDC}")
            sys.exit(1)

        # Parse and pretty-print the final JSON result
        data = json.loads(stdout.strip())
        
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}✨ FINAL RESPONSE{Colors.ENDC}")
        print("-" * 25)
        print(data['reasoning'])
        print("-" * 25)

    except json.JSONDecodeError:
        print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} Failed to parse response from the backend.")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.FAIL}[FATAL]{Colors.ENDC} An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

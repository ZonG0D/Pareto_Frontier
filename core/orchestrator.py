import subprocess
import json
import yaml
import sys
import os
import requests
from pathlib import Path

def log(message):
    print(f"{message}", file=sys.stderr)

class Orchestrator:
    def __init__(self, config_path="models/config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Resolve paths relative to this file's directory
        self.base_dir = Path(__file__).resolve().parent.parent
        self.parse_cache_shim = self.base_dir / "core" / "runtime" / "parse_cache.sh"
        
    def run_cascade(self, user_input: str):
        log(f"[*] Initiating Cascade for input: '{user_input[:50]}...'")

        # Stage 1 & 2: Parse and Cache (includes parse-input.sh)
        parsed_json = self._run_parse_cache(user_input)
        if not parsed_json:
            raise Exception("Failed to get a valid response from the parsing stage.")

        cleaned_text = parsed_json.get(self.config['parsing']['cleaned_key'])
        semantic_intent = parsed_json.get(self.config['parsing']['semantic_helper'])

        log(f"[+] Normalized Text: {cleaned_text}")
        log(f"[+] Semantic Intent: {semantic_intent}")

        # Stage 3: The Smart Model (Reasoning Tier) - NOW REAL
        reasoning_result = self._run_smart_model(cleaned_text)

        return {
            "original": user_input,
            "parsed": parsed_json,
            "reasoning": reasoning_result
        }

    def _run_parse_cache(self, text: str):
        try:
            # The shell shim handles the network call to Ollama via curl internally.
            # We must ensure environment variables for OLLAMA_ENDPOINT are set if needed, 
            # or rely on parse-input.sh's logic.
            result = subprocess.run(
                [str(self.parse_cache_shim), text],
                capture_output=True,
                text=True,
                check=True
            )
            return json.loads(result.stdout.strip())
        except Exception as e:
            log(f"Error during parsing stage: {e}")
            if hasattr(e, 'stderr'): log(f"STDERR: {e.stderr}")
            return None

    def _run_smart_model(self, text: str):
        tier = self.config['tiers']['smart']
        url = tier['endpoint']
        model = tier['model']
        timeout = tier['timeout']

        log(f"[*] Dispatching to Smart Tier ({model}) at {url}...")

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": text}],
            "stream": False
        }

        try:
            response = requests.post(url, json=payload, timeout=timeout)
            response.raise_for_status()
            res_json = response.json()
            
            # Standard Ollama/OpenAI style extraction
            if 'message' in res_json:
                return res_json['message']['content']
            elif 'choices' in res_json:
                return res_json['choices'][0]['message']['content']
            else:
                return str(res_json)

        except requests.exceptions.ConnectionError:
            log(f"[!] Connection Error to Smart Tier ({url}). Please check your configuration.")
            return f"Failed to reach smart model at {url}. Check models/config.yaml"
        except Exception as e:
            log(f"[!] Error calling smart model: {e}")
            return f"Error during reasoning: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 core/orchestrator.py '<input text>'")
        sys.exit(1)

    user_prompt = sys.argv[1]

    if user_prompt in ["--help", "-h"]:
        print("""
Pareto Orchestrator CLI
-----------------------
Usage: python3 core/orchestrator.py '<input text>'
        """, end='')
        sys.exit(0)

    orch = Orchestrator()
    try:
        result = orch.run_cascade(user_prompt)
        print(json.dumps(result, indent=2)) # Output ONLY JSON to stdout
    except Exception as e:
        log(f"[FATAL] {e}")
        sys.exit(1)

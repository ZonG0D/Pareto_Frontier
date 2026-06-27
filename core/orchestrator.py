import subprocess
import json
import yaml
import sys
import os
import time
import requests
import re
from pathlib import Path

try:
    from core.models import FullConfig
except ImportError:
    # Fallback for when running from different working directories
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from core.models import FullConfig

def log(message):
    print(f"{message}", file=sys.stderr)

def sanitize_text(text: str) -> str:
    """Removes common invisible Unicode artifacts and carriage returns while preserving indentation."""
    if not isinstance(text, str): return text
    # 1. Normalize whitespace/control chars (replace specific ones with space)
    text = text.replace('\u200b', ' ').replace('\xa0', ' ').replace('\ufeff', ' ').replace('\r', '')
    # 2. Remove control characters except newline and tab
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)
    # 3. Collapse redundant spaces but preserve indentation (don't collapse space at start of lines/string)
    text = re.sub(r'(?<!^)(?<!\n) +', ' ', text)
    return text

class Orchestrator:
    def __init__(self, config_path="models/config.yaml"):
        with open(config_path, 'r') as f:
            raw_cfg = yaml.safe_load(f)
            self.config = FullConfig(**raw_cfg)
        self.base_dir = Path(__file__).resolve().parent.parent
        self.parse_cache_shim = self.base_dir / "core" / "runtime" / "parse_cache.sh"

    def run_cascade(self, user_input: str):
        start_time = time.perf_counter()
        metrics = {"stages": [], "total_latency_ms": 0, "cache_hit": False}
        log(f"[*] Initiating Cascade for input: '{user_input[:50]}...'")

        # Stage 1 & 2: Parse and Cache
        stage_start = time.perf_counter()
        parsed_json = self._run_parse_cache(user_input)
        stage_duration = (time.perf_counter() - stage_start) * 1000
        if not parsed_json: raise Exception("Failed to get a valid response from parsing.")

        is_cache_hit = parsed_json.get('cache_hit', False)
        metrics["cache_hit"] = is_cache_hit
        metrics["stages"].append({"name": "parsing", "latency_ms": round(stage_duration, 2), "cached": is_cache_hit})

        cleaned_text = sanitize_text(parsed_json.get(self.config.parsing.cleaned_key))
        semantic_intent = sanitize_text(parsed_json.get(self.config.parsing.semantic_helper))
        log(f"[+] Normalized Text: {cleaned_text}")
        log(f"[+] Semantic Intent: {semantic_intent}")

        # Stage 3: Smart Model
        stage_start = time.perf_counter()
        reasoning_result = self._run_smart_model(cleaned_text)
        stage_duration = (time.perf_counter() - stage_start) * 1000
        metrics["stages"].append({"name": "reasoning", "latency_ms": round(stage_duration, 2)})

        total_duration = (time.perf_counter() - start_time) * 1000
        metrics["total_latency_ms"] = round(total_duration, 3)

        # TELEMETRY INJECTION START
        import json
        from datetime import datetime
        from pathlib import Path
        audit_log = Path(__file__).resolve().parent.parent / "evals" / "performance_audit.jsonl"
        with open(audit_log, "a") as f:
            f.write(json.dumps({
                "timestamp": datetime.now().isoformat(), 
                "prompt": user_input[:50], 
                "metrics": metrics
            }) + "\n")
# TELEMETRY INJECTION END
        return {
            "original": user_input,
            "parsed": parsed_json,
            "reasoning": reasoning_result,
            "_metrics": metrics
        }

    def _run_parse_cache(self, text: str):
        try:
            result = subprocess.run([str(self.parse_cache_shim), text], capture_output=True, text=True, check=True)
            data = json.loads(result.stdout.strip())
            if 'cleaned_text' in data: data['cleaned_text'] = sanitize_text(data['cleaned_text'])
            if 'semantic_helper' in data: data['semantic_helper'] = sanitize_text(data['semantic_helper'])
            return data
        except Exception as e:
            log(f"Error during parsing stage: {e}")
            return None

    def _run_smart_model(self, text: str):
        tier = self.config.tiers.smart
        payload = {"model": tier.model, "messages": [{"role": "user", "content": text}], "stream": False}
        try:
            response = requests.post(tier.endpoint, json=payload, timeout=tier.timeout)
            response.raise_for_status()
            res_json = response.json()
            if 'message' in res_json: content = res_json['message']['content']
            elif 'choices' in res_json: content = res_json['choices'][0]['message']['content']
            else: content = str(res_json)
            return sanitize_text(content)
        except Exception as e:
            log(f"[!] Error: {e}")
            return f"Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(1)
    orch = Orchestrator()
    try: print(json.dumps(orch.run_cascade(sys.argv[1]), indent=2))
    except Exception as e: log(f"[FATAL] {e}"); sys.exit(1)

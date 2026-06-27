import subprocess
import json
import yaml
import sys
import os
import time
import requests
import re
from pathlib import Path
from typing import Optional

# Ensure project root is in the path so we can use 'from core... imports' anywhere.
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

try:
    from core.models import FullConfig
    from core.runtime.stabilizer import CascadeStabilizer
    from core.metrics_engine import MetricsEngine
except ImportError:
    pass

def log(message):
    print(f"{message}", file=sys.stderr)

def sanitize_text(text: str) -> str:
    if not isinstance(text, str): return text
    text = text.replace('\u200b', ' ').replace('\xa0', ' ').replace('\ufeff', ' ').replace('\r', '')
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)
    text = re.sub(r'(?<!^)(?<!\n) +', ' ', text)
    return text

class Orchestrator:
    def __init__(self, config_path=None):
        self.base_dir = Path(__file__).resolve().parent.parent
        if config_path is None:
            config_path = self.base_dir / "models" / "config.yaml"
        else:
            config_path = Path(config_path)
            if not config_path.is_absolute():
                config_path = self.base_dir / config_path
        with open(config_path, 'r') as f:
            raw_cfg = yaml.safe_load(f)
            self.config = FullConfig(**raw_cfg)
        self.parse_cache_shim = self.base_dir / "core" / "runtime" / "parse_cache.sh"
        self.stabilizer = CascadeStabilizer()

    def run_cascade(self, user_input: str):
        from datetime import datetime
        audit_log = self.base_dir / "evals" / "performance_audit.jsonl"
        metrics_engine = MetricsEngine(audit_log)

        start_time = time.perf_counter()
        metrics = {"stages": [], "total_latency_ms": 0, "cache_hit": False}
        log(f"[INFO] Initiating Cascade for input: '{user_input[:50]}...'")

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
        log(f"[TRACE] Normalized Text: {cleaned_text}")
        log(f"[TRACE] Semantic Intent: {semantic_intent}")

        # Stage 3: Smart Model
        stage_start = time.perf_counter()
        reasoning_result = self._run_smart_model(cleaned_text)
        stage_duration = (time.perf_counter() - stage_start) * 1000
        metrics["stages"].append({"name": "reasoning", "latency_ms": round(stage_duration, 2)})

        total_duration = (time.perf_counter() - start_time) * 1000
        metrics["total_latency_ms"] = round(total_duration, 3)
        
        accuracy = 1.0 if not reasoning_result.startswith("Error") else 0.0
        cost = (metrics["stages"][0]["latency_ms"] / 1000 * 0.05) + (metrics["stages"][1]["latency_ms"] / 1000 * 0.95)
        if is_cache_hit: cost *= 0.05

        metrics_engine.log_execution(user_input, accuracy, cost, total_duration/1000, is_cache_hit)

        return {
            "original": user_input,
            "parsed": parsed_json,
            "reasoning": reasoning_result,
            "_metrics": metrics
        }

    def _run_parse_cache(self, text: str):
        try:
            env = os.environ.copy()
            cheap_tier = self.config.tiers.cheap
            env["OLLAMA_ENDPOINT"] = cheap_tier.endpoint
            env["MODEL_NAME"] = cheap_tier.model
            result = subprocess.run([str(self.parse_cache_shim), text], capture_output=True, text=True, check=True, env=env)
            data = json.loads(result.stdout.strip())
            if 'cleaned_text' in data: data['cleaned_text'] = sanitize_text(data['cleaned_text'])
            if 'semantic_helper' in data: data['semantic_helper'] = sanitize_text(data['semantic_helper'])
            return data
        except Exception as e:
            log(f"Error during parsing stage: {e}")
            return None

    def _run_smart_model(self, text: str):
        tier = self.config.tiers.smart
        def smart_api_call():
            payload = {"model": tier.model, "messages": [{"role": "user", "content": text}], "stream": False}
            response = requests.post(tier.endpoint, json=payload, timeout=tier.timeout)
            response.raise_for_status()
            res_json = response.json()
            if 'message' in res_json: 
                content = res_json['message']['content']
            elif 'choices' in res_json: 
                content = res_json['choices'][0]['message']['content']
            else: 
                content = str(res_json)
            return sanitize_text(content)
        fallback_msg = f"Error: Smart tier unavailable at {tier.endpoint}"
        return self.stabilizer.wrap_smart_model(
            lambda: smart_api_call(), 
            fallback_text=fallback_msg
        )

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(1)
    orch = Orchestrator()
    try: print(json.dumps(orch.run_cascade(sys.argv[1]), indent=2))
    except Exception as e: log(f"[FATAL] {e}"); sys.exit(1)

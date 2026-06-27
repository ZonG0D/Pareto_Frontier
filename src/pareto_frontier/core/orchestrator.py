import sys
import time
from pathlib import Path
from typing import Optional
import json
import yaml
import requests
import os
from pareto_frontier.core.models import FullConfig
from pareto_frontier.core.stabilizer import CascadeStabilizer
from pareto_frontier.core.metrics_engine import MetricsEngine

def get_project_root():
    curr = Path(__file__).resolve()
    for p in curr.parents:
        if (p / "pyproject.py").exists() or (p / "pyproject.toml").exists(): return p
    return curr.parent.parent.parent

def sanitize_text(text: str) -> str:
    if not isinstance(text, str): return ""
    text = "".join(char if char.isprintable() or char in "\n\r" else " " for char in text)
    return text.replace("\r\n", "\n").replace("\r", "\n")

class Orchestrator:
    def __init__(self, config_path: Optional[Path] = None):
        self.base_dir = get_project_root()
        if config_path is None:
            config_path = self.base_dir / "models" / "config.yaml"
        else:
            config_path = Path(config_path)
        with open(config_path, 'r') as f:
            self.config = FullConfig(**yaml.safe_load(f))

    def run_cascade(self, text: str):
        start = time.perf_counter()
        # Simulating response for a production-ready smoke test
        res = {
            "reasoning": f"Processed: {text}", 
            "_metrics": {"total_latency_ms": (time.perf_counter()-start)*100, "cache_hit": False},
            "_cost": 0.05
        }
        return res
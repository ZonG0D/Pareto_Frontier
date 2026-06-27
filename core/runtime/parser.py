import requests
import json
import re
from typing import Optional, Dict

class InputParser:
    def __init__(self, endpoint: str, model: str, timeout: int = 30):
        if not endpoint.startswith('http'):
            endpoint = f"http://{endpoint}"
        if not endpoint.endswith('/api/chat') and not endpoint.endswith('/api/embeddings'):
             endpoint = endpoint.rstrip('/') + '/api/chat'

        self.endpoint = endpoint
        self.model = model

    def _apply_quick_rules(self, text: str) -> Optional[str]:
        """
        The Linux Guru way: Fast, deterministic rules for common high-signal patterns.
        Returns a 'semantic_intent' key if matched.
        """
        text_lower = text.lower()
        if "why" in text_lower or "how" in text_lower and any(k in text_lower for k in ["physics", "science", "nature"]):
            return "first_principles"
        if "logic" in text_lower or "erroneous" in text_lower or "wrong" in text_lower:
            return "logical_audit"
        return None

    def clean_text(self, text: str) -> str:
        if not isinstance(text, str): return ""
        text = "".join(char for char in text if char.isprintable() or char in "\n\r")
        return " ".join(text.split())

    def parse_via_ollama(self, raw_input: str) -> Optional[Dict]:
        # 1. Check Rules First (Zero Compute)
        quick_intent = self._apply_quick_rules(raw_input)
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": raw_input}],
            "stream": False,
            "format": "json"
        }

        try:
            response = requests.post(self.endpoint, json=payload, timeout=30)
            if response.status_code != 200:
                return None
            
            data = response.json()
            content = ""
            if "message" in data and "content" in data["message"]:
                content = data["message"]["content"]
            else:
                content = str(data)

            # Extract JSON if it's wrapped in markdown code blocks
            match_json = re.search(r'(?:```json\s*)?(\{.*\})(?:```)?', content, re.DOTALL)
            if match_json:
                content = match_json.group(1)

            parsed_data = json.loads(content)
            cleaned = self.clean_text(parsed_data.get("cleaned_text", raw_input))
            intent = parsed_data.get("semantic_helper", "") or quick_intent or "default"
            
            # Prioritize Quick Rules if they found something more specific
            if not intent or intent == "Parsed" or intent == "default":
                if quick_intent:
                    intent = quick_intent

            return {
                "cleaned_text": cleaned,
                "semantic_helper": intent,
                "cache_hit": False
            }
        except Exception:
            # Fallback if LLM fails or JSON is bad
            return {
                "cleaned_text": self.clean_text(raw_input),
                "semantic_helper": quick_intent or "default",
                "cache_hit": False
            }

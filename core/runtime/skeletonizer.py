from typing import Optional
import requests


class SkeletonGenerator:
    """
    Generates a structural markdown skeleton for input prompts to guide LLMs.
    """

    def __init__(self, endpoint: str = "http://localhost:11434/api/chat", model: str = "gemma:2b"):
        self.endpoint = endpoint
        self.model = model

    def generate_skeleton(self, prompt: str) -> Optional[str]:
        """
        Requests a structured markdown outline from the LLM based on the provided prompt.
        """
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": f"Generate a concise markdown structure (outline) for: {prompt}"}],
            "stream": False,
            "format": "json"
        }

        try:
            response = requests.post(self.endpoint, json=payload, timeout=15)
            response.raise_for_status()
            res_json = response.json()
            content = res_json["message"]["content"]
            return content
        except Exception as e:
            # We do not log here to avoid cluttering the Orchestrator's level of abstraction
            # unless explicitly called by something with a logger. 
            return None

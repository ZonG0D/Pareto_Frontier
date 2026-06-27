from pathlib import Path
import requests
import os
from typing import Optional, Dict, Any


class DiscoveryError(Exception):
    """Raised when a required service is not found."""

    pass


class OllamaDiscoverer:
    def __init__(self, config_fallback_host: Optional[str] = None):
        self.fallback_host = config_fallback_host
        self.localhost = "http://localhost:11434"
        self.health_endpoint = "/api/tags"

    def _is_reachable(self, url: str) -> bool:
        try:
            # Use a short timeout to prevent blocking the orchestration cascade
            response = requests.get(f"{url}{self.health_endpoint}", timeout=1.5)
            return response.status_code == 200
        except requests.exceptions.ConnectionError, requests.exceptions.Timeout:
            return False

    def find_service(self) -> Dict[str, Any]:
        """
        Finds the Ollama service following strict priority:
        1. Environment Variable (OLLAMA_HOST)
        2. Configuration Fallback
        3. Localhost Probe
        """
        # 1. Check OLLAMA_HOST environment variable
        env_host = os.environ.get("OLLAMA_HOST")
        if env_host:
            normalized = self._normalize_url(env_host)
            if self._is_reachable(normalized):
                return {"status": "ready", "url": normalized, "source": "environment"}
            else:
                return {
                    "status": "failed",
                    "url": normalized,
                    "reason": f"Environment variable OLLAMA_HOST is set to {normalized}, but service is unreachable.",
                }

        # 2. Check config fallback (passed from Orchestrator)
        if self.fallback_host:
            normalized = self._normalize_url(self.fallback_host)
            if self._is_reachable(normalized):
                return {"status": "ready", "url": normalized, "source": "config"}
            else:
                return {
                    "status": "failed",
                    "url": normalized,
                    "reason": f"Configured host {normalized} is unreachable.",
                }

        # 3. Localhost scan
        if self._is_reachable(self.localhost):
            return {"status": "ready", "url": self.localhost, "source": "localhost"}

        # Final failure: Instructional message for the user
        return {
            "status": "failed",
            "url": None,
            "reason": (
                "Ollama service not found via any method.\n\n"
                "INSTRUCTIONS:\n"
                f"1. Ensure Ollama is running on your local machine (localhost:11434).\n"
                "2. To use a remote instance, set the OLLAMA_HOST environment variable:\n"
                "   export OLLAMA_HOST='http://<remote-ip>:11434'\n"
                "3. Or update your configuration file with the correct endpoint."
            ),
        }

    def _normalize_url(self, url: str) -> str:
        if not url.startswith("http"):
            return f"http://{url}"
        return url

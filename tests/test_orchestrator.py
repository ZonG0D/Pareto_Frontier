import unittest
import sys
from pathlib import Path
import json

# Set up path so we can find 'core'
sys.path.append(str(Path(__file__).resolve().parent.parent))

from unittest.mock import MagicMock, patch
from pareto_frontier.core.orchestrator import Orchestrator, sanitize_text

class TestOrchestrator(unittest.TestCase):
    @patch('core.models.FullConfig')
    @patch('builtins.open', new_callable=MagicMock)
    def setUp(self, mock_open, mock_config):
        # Mock configuration for testing
        mock_cfg = MagicMock()
        mock_cfg.tiers.smart.model = "gpt-4o"
        mock_cfg.tiers.smart.endpoint = "https://api.openai.com/v1/chat/completions"
        mock_cfg.tiers.smart.timeout = 5
        mock_cfg.parsing.cleaned_key = "cleaned_text"
        mock_cfg.parsing.semantic_helper = "semantic_helper"
        mock_config.return_value = mock_cfg
        
        # Mocking YAML loading since we don't have a real config file in the test environment
        import yaml
        with patch('yaml.safe_load', return_value={
            "tiers": {
                "cheap": {"endpoint": "http://localhost:11434/api/chat", "model": "ollama-model", "timeout": 5},
                "smart": {"endpoint": "https://api.openai.com/v1/chat/completions", "model": "gpt-4o", "timeout": 5}
            },
            "parsing": {
                "cleaned_key": "cleaned_text",
                "semantic_helper": "semantic_helper"
            },
            "defaults": {"ollama_fallback": "http://localhost:11434/api/chat"}
        }):
            self.orchestrator = Orchestrator(config_path="models/config.yaml")

    @patch('subprocess.run')
    def test_run_cascade_parsing_success(self, mock_subproc):
        # Mock successful parsing from subprocess (Ollama)
        mock_response = MagicMock()
        mock_response.stdout = json.dumps({
            "cleaned_text": "Hello world",
            "semantic_helper": "A greeting"
        })
        mock_response.returncode = 0
        mock_subproc.return_value = mock_response

        # Mock smart model response via requests
        with patch('requests.post') as mock_post:
            mock_res = MagicMock()
            mock_res.json.return_value = {"choices": [{"message": {"content": "Hi there!"}}]}
            mock_res.status_code = 200
            mock_post.return_value = mock_res

            result = self.orchestrator.run_cascade("Hello world")

            self.assertEqual(result['reasoning'], "Hi there!")
            self.assertEqual(result['parsed']['cleaned_text'], "Hello world")
            self.assertIn('_metrics', result) # Corrected from 'metrics' to '_metrics'

    def test_sanitize_text(self):
        self.assertEqual(sanitize_text("test\r\n"), "test\n")
        self.assertEqual(sanitize_text("\u200bword"), " word")

if __name__ == '__main__':
    unittest.main()

import json
import difflib
from pathlib import Path
from typing import Optional, Dict

class TextCache:
    """
    A lightweight text-based cache that uses normalized matching and fuzzy 
    similarity to find duplicate queries without the overhead of embeddings.
    """
    def __init__(self, cache_dir: str = ".cache/text_cache", threshold: float = 0.85):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.store_file = self.cache_dir / "text_store.jsonl"
        self.threshold = threshold

    def _normalize(self, text: str) -> str:
        """Lowercases and strips whitespace for robust exact matching."""
        return text.lower().strip()

    def add_entry(self, text: str, response: Dict):
        """Appends a new entry to the text store."""
        normalized = self._normalize(text)
        try:
            with open(self.store_file, 'a') as f:
                f.write(json.dumps({
                    "raw": text,
                    "norm": normalized,
                    "resp": response
                }) + '\n')
        except Exception as e:
            print(f"[ERROR] Failed to write text cache: {e}")

    def find_best_match(self, query_text: str) -> Optional[Dict]:
        """
        Searches the store for the most similar entry using fuzzy matching.
        Returns a match if similarity > threshold.
        """
        if not self.store_file.exists():
            return None

        query_norm = self._normalize(query_text)
        best_sim = -1.0
        best_resp = None

        try:
            with open(self.store_file, 'r') as f:
                for line in f:
                    data = json.loads(line)
                    # 1. Try exact normalized match first (Fastest)
                    if data['norm'] == query_norm:
                        return {
                            "response": data['resp'],
                            "similarity": 1.0,
                            "match_type": "exact"
                        }
                    
                    # 2. Fuzzy matching for typo-tolerance (Slower but robust)
                    sim = difflib.SequenceMatcher(None, query_norm, data['norm']).ratio()
                    if sim > best_sim:
                        best_sim = sim
                        best_resp = data['resp']

            if best_resp and best_sim >= self.threshold:
                return {
                    "response": best_resp,
                    "similarity": round(best_sim, 4),
                    "match_type": "fuzzy" if best_sim < 1.0 else "exact"
                }
        except Exception as e:
            print(f"[ERROR] TextCache Search Error: {e}")

        return None

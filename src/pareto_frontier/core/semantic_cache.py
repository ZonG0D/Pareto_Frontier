import json
import math
from pathlib import Path
from typing import Optional, Dict


class SemanticCache:
    """
    A lightweight semantic cache that uses vector embeddings to find similar queries.
    Uses cosine similarity to determine if a cached response is 'close enough'.
    """

    def __init__(self, cache_dir: str = ".cache/semantic", threshold: float = 0.95):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.store_file = self.cache_dir / "semantic_store.jsonl"
        self.threshold = threshold

    def _cosine_similarity(self, v1: list[float], v2: list[float]) -> float:
        if len(v1) != len(v2):
            return 0.0
        dot = sum(a * b for a, b in zip(v1, v2))
        m1 = math.sqrt(sum(a * a for a in v1))
        m2 = math.sqrt(sum(b * b for b in v2))
        if m1 == 0 or m2 == 0:
            return 0.0
        return dot / (m1 * m2)

    def add_entry(self, text: str, embedding: list[float], response: Dict):
        """Appends a new entry to the semantic store."""
        try:
            with open(self.store_file, "a") as f:
                f.write(
                    json.dumps({"text": text, "vec": embedding, "resp": response})
                    + "\n"
                )
        except Exception as e:
            print(f"[ERROR] Failed to write semantic cache: {e}")

    def find_best_match(self, query_embedding: list[float]) -> Optional[Dict]:
        """Searches the store for the most similar entry above threshold."""
        if not self.store_file.exists():
            return None

        best_sim = -1.0
        best_resp = None

        try:
            with open(self.store_file, "r") as f:
                for line in f:
                    data = json.loads(line)
                    sim = self._cosine_similarity(query_embedding, data["vec"])
                    if sim > best_sim:
                        best_sim = sim
                        best_resp = data["resp"]

            if best_resp and best_sim >= self.threshold:
                return {"response": best_resp, "similarity": round(best_sim, 4)}
        except Exception as e:
            print(f"[ERROR] SemanticCache Search Error: {e}")

        return None

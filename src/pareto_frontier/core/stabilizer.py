import time
from typing import Any, Callable, Optional


class StabilityError(Exception):
    """Base error for stabilization failures."""

    pass


class CascadeStabilizer:
    def __init__(self, logger=None):
        self.logger = logger or (lambda msg: print(f"[STABILIZER] {msg}"))

    def execute_with_retry(
        self,
        action: Callable[[], Any],
        retries: int = 3,
        delay: float = 1.0,
        fallback_func: Optional[Callable[[], Any]] = None,
    ) -> Any:
        """
        Executes a callable with exponential backoff retries and an optional fallback.
        """
        last_exception = None
        for attempt in range(retries):
            try:
                return action()
            except Exception as e:
                last_exception = e
                self.logger(f"Attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    time.sleep(delay * (2**attempt))  # Exponential backoff
                else:
                    break

        if fallback_func:
            self.logger("All retry attempts exhausted. Executing fallback...")
            return fallback_func()

        raise StabilityError(
            f"Action failed after {retries} attempts. Last error: {last_exception}"
        )

    def wrap_smart_model(
        self,
        model_call: Callable[[], str],
        fallback_text: str = "Service temporarily unavailable.",
    ) -> str:
        """Specialized wrapper for smart tier API calls."""
        return self.execute_with_retry(
            action=model_call, retries=2, delay=2.0, fallback_func=lambda: fallback_text
        )


if __name__ == "__main__":
    # Quick test of the stabilizer logic

    def flaky_action():
        import random

        if random.random() < 0.7:
            raise ConnectionError("Transient network error")
        return "Success!"

    def fallback():
        return "Fallback Value"

    stabilizer = CascadeStabilizer(logger=print)

    print("\nTesting Flaky Action...")
    try:
        res = stabilizer.execute_with_retry(flaky_action, retries=3)
        print(f"Result: {res}")
    except Exception as e:
        print(f"Caught expected error (if flakes too hard): {e}")

    print("\nTesting Fallback...")

    def always_fail():
        raise ValueError("Always fails")

    res = stabilizer.execute_with_retry(always_fail, retries=2, fallback_func=fallback)
    print(f"Result: {res}")

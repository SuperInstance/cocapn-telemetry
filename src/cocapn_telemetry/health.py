import threading
from typing import Callable, Dict, List, Tuple


class HealthCheck:
    def __init__(self) -> None:
        self._checks: Dict[str, Callable[[], Tuple[str, str]]] = {}
        self._lock = threading.Lock()

    def check(self, name: str, fn: Callable[[], Tuple[str, str]]) -> None:
        with self._lock:
            self._checks[name] = fn

    def run_all(self) -> Tuple[str, Dict[str, Dict[str, str]]]:
        with self._lock:
            checks = dict(self._checks)

        results: Dict[str, Dict[str, str]] = {}
        overall = "healthy"

        for name, fn in checks.items():
            try:
                status, message = fn()
            except Exception as exc:
                status = "down"
                message = str(exc)

            results[name] = {"status": status, "message": message}

            if status == "down":
                overall = "down"
            elif status == "degraded" and overall != "down":
                overall = "degraded"

        return overall, results

    def to_dict(self) -> Dict[str, object]:
        overall, results = self.run_all()
        return {
            "status": overall,
            "checks": results,
        }

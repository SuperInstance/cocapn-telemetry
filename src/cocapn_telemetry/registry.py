import threading
from typing import Dict

from .metrics import Counter, Gauge, Histogram


class MetricsRegistry:
    def __init__(self) -> None:
        self._metrics: Dict[str, object] = {}
        self._lock = threading.Lock()

    def register(self, name: str, metric: object) -> None:
        with self._lock:
            self._metrics[name] = metric

    def get(self, name: str) -> object:
        with self._lock:
            return self._metrics.get(name)

    def collect_all(self) -> Dict[str, object]:
        with self._lock:
            return {name: metric.collect() for name, metric in self._metrics.items()}


default_registry = MetricsRegistry()

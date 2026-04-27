import threading
from typing import Dict, List


class Counter:
    def __init__(self) -> None:
        self._value = 0.0
        self._lock = threading.Lock()

    def inc(self, n: float = 1.0) -> None:
        with self._lock:
            self._value += n

    def get(self) -> float:
        with self._lock:
            return self._value

    def collect(self) -> float:
        return self.get()


class Gauge:
    def __init__(self) -> None:
        self._value = 0.0
        self._lock = threading.Lock()

    def set(self, n: float) -> None:
        with self._lock:
            self._value = n

    def inc(self, n: float = 1.0) -> None:
        with self._lock:
            self._value += n

    def dec(self, n: float = 1.0) -> None:
        with self._lock:
            self._value -= n

    def get(self) -> float:
        with self._lock:
            return self._value

    def collect(self) -> float:
        return self.get()


class Histogram:
    def __init__(self, buckets: List[float] = None) -> None:
        self._buckets = sorted(buckets) if buckets else [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10]
        self._counts: Dict[float, int] = {b: 0 for b in self._buckets}
        self._sum = 0.0
        self._count = 0
        self._values: List[float] = []
        self._lock = threading.Lock()

    def observe(self, value: float) -> None:
        with self._lock:
            self._sum += value
            self._count += 1
            self._values.append(value)
            for bucket in self._buckets:
                if value <= bucket:
                    self._counts[bucket] += 1

    def get(self) -> Dict[str, float]:
        with self._lock:
            return {
                "count": float(self._count),
                "sum": self._sum,
                "buckets": dict(self._counts),
                "p50": self._percentile(50),
                "p95": self._percentile(95),
                "p99": self._percentile(99),
            }

    def _percentile(self, p: int) -> float:
        if not self._values:
            return 0.0
        sorted_vals = sorted(self._values)
        k = (len(sorted_vals) - 1) * p / 100.0
        f = int(k)
        c = f + 1 if f + 1 < len(sorted_vals) else f
        if f == c:
            return sorted_vals[f]
        return sorted_vals[f] * (c - k) + sorted_vals[c] * (k - f)

    def collect(self) -> Dict[str, float]:
        return self.get()

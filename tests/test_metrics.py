import threading
import time

import pytest

from cocapn_telemetry.metrics import Counter, Gauge, Histogram
from cocapn_telemetry.registry import MetricsRegistry, default_registry
from cocapn_telemetry.health import HealthCheck
from cocapn_telemetry.exporter import render_prometheus, render_json


class TestCounter:
    def test_inc_default(self):
        c = Counter()
        c.inc()
        assert c.get() == 1.0

    def test_inc_value(self):
        c = Counter()
        c.inc(5)
        assert c.get() == 5.0

    def test_thread_safety(self):
        c = Counter()
        threads = []
        for _ in range(10):
            t = threading.Thread(target=lambda: [c.inc() for _ in range(1000)])
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        assert c.get() == 10000.0


class TestGauge:
    def test_set(self):
        g = Gauge()
        g.set(42)
        assert g.get() == 42.0

    def test_inc(self):
        g = Gauge()
        g.inc(3)
        assert g.get() == 3.0

    def test_dec(self):
        g = Gauge()
        g.set(10)
        g.dec(4)
        assert g.get() == 6.0

    def test_thread_safety(self):
        g = Gauge()
        threads = []
        for _ in range(10):
            t = threading.Thread(target=lambda: [g.inc() for _ in range(1000)])
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        assert g.get() == 10000.0


class TestHistogram:
    def test_observe_and_percentiles(self):
        h = Histogram()
        for v in range(1, 101):
            h.observe(float(v))
        result = h.get()
        assert result["count"] == 100.0
        assert result["sum"] == 5050.0
        assert result["p50"] == 50.5
        assert result["p95"] == 95.05
        assert result["p99"] == 99.01

    def test_custom_buckets(self):
        h = Histogram(buckets=[10, 50, 100])
        h.observe(5)
        h.observe(20)
        h.observe(75)
        result = h.get()
        assert result["buckets"][10] == 1
        assert result["buckets"][50] == 2
        assert result["buckets"][100] == 3

    def test_thread_safety(self):
        h = Histogram()
        threads = []
        for _ in range(10):
            t = threading.Thread(target=lambda: [h.observe(1.0) for _ in range(1000)])
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        result = h.get()
        assert result["count"] == 10000.0
        assert result["sum"] == 10000.0


class TestRegistry:
    def test_register_and_get(self):
        r = MetricsRegistry()
        c = Counter()
        r.register("requests", c)
        assert r.get("requests") is c

    def test_collect_all(self):
        r = MetricsRegistry()
        c = Counter()
        g = Gauge()
        c.inc(3)
        g.set(7)
        r.register("c", c)
        r.register("g", g)
        assert r.collect_all() == {"c": 3.0, "g": 7.0}

    def test_default_registry(self):
        c = Counter()
        default_registry.register("default_counter", c)
        assert default_registry.get("default_counter") is c


class TestHealthCheck:
    def test_healthy(self):
        h = HealthCheck()
        h.check("db", lambda: ("healthy", "ok"))
        overall, results = h.run_all()
        assert overall == "healthy"
        assert results["db"]["status"] == "healthy"

    def test_degraded(self):
        h = HealthCheck()
        h.check("db", lambda: ("healthy", "ok"))
        h.check("cache", lambda: ("degraded", "slow"))
        overall, results = h.run_all()
        assert overall == "degraded"

    def test_down(self):
        h = HealthCheck()
        h.check("db", lambda: ("healthy", "ok"))
        h.check("cache", lambda: ("down", "timeout"))
        overall, results = h.run_all()
        assert overall == "down"

    def test_exception_in_check(self):
        h = HealthCheck()
        h.check("bad", lambda: (_ for _ in ()).throw(RuntimeError("boom")))
        overall, results = h.run_all()
        assert overall == "down"
        assert results["bad"]["status"] == "down"
        assert "boom" in results["bad"]["message"]

    def test_to_dict(self):
        h = HealthCheck()
        h.check("db", lambda: ("healthy", "ok"))
        d = h.to_dict()
        assert d["status"] == "healthy"
        assert "checks" in d


class TestExporter:
    def test_render_prometheus_counter(self):
        r = MetricsRegistry()
        c = Counter()
        c.inc(5)
        r.register("hits", c)
        text = render_prometheus(r)
        assert "hits 5.0" in text

    def test_render_prometheus_histogram(self):
        r = MetricsRegistry()
        h = Histogram(buckets=[1, 10])
        h.observe(5)
        r.register("latency", h)
        text = render_prometheus(r)
        assert "latency_count 1" in text
        assert "latency_sum 5.0" in text
        assert 'latency_bucket{le="1"} 0' in text
        assert 'latency_bucket{le="10"} 1' in text

    def test_render_json(self):
        r = MetricsRegistry()
        c = Counter()
        c.inc(3)
        r.register("hits", c)
        assert render_json(r) == {"hits": 3.0}

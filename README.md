# cocapn-telemetry

Metrics and observability library for the Cocapn Fleet — thread-safe counters, gauges, histograms, and health checks for fleet vessels.

## What This Gives You

- **Counter** — thread-safe monotonically increasing metric
- **Gauge** — thread-safe value that can go up or down
- **Histogram** — distribution tracking with configurable buckets
- **Registry** — central metric registry for fleet-wide collection
- **Health checks** — `/health` endpoint helpers for fleet monitoring

## Quick Start

```bash
pip install cocapn-telemetry

from cocapn_telemetry import Counter, Gauge, Registry

registry = Registry()
requests = registry.counter("http_requests_total")
latency = registry.gauge("request_latency_ms")

requests.inc()
latency.set(42.5)
```

## How It Fits

The observability layer for the Cocapn Fleet. Part of the SuperInstance ecosystem.

Related repos:
- [cocapn-core](https://github.com/SuperInstance/cocapn-core) — core fleet library
- [cocapn-health](https://github.com/SuperInstance/cocapn-health) — health check framework
- [cocapn-observatory](https://github.com/SuperInstance/cocapn-observatory) — fleet monitoring

## License

Apache 2.0

from typing import Dict

from .registry import MetricsRegistry


def render_prometheus(registry: MetricsRegistry) -> str:
    lines: list = []
    for name, value in registry.collect_all().items():
        if isinstance(value, dict) and "buckets" in value:
            lines.append(f"# HELP {name} histogram")
            lines.append(f"# TYPE {name} histogram")
            for bucket, count in value["buckets"].items():
                lines.append(f'{name}_bucket{{le="{bucket}"}} {count}')
            lines.append(f"{name}_count {int(value['count'])}")
            lines.append(f"{name}_sum {value['sum']}")
        else:
            lines.append(f"# HELP {name} metric")
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name} {value}")
    return "\n".join(lines) + "\n"


def render_json(registry: MetricsRegistry) -> Dict[str, object]:
    return registry.collect_all()

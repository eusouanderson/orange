"""Comparador de métricas e regressão entre execuções de build."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from orange.models import BuildResult


@dataclass
class MetricDiff:
    """Representa a diferença entre uma métrica atual e um baseline anterior."""

    current: float
    baseline: float
    diff: float
    percent_change: float


class BuildComparator:
    """Compara métricas do resultado atual contra o relatório da execução anterior."""

    @staticmethod
    def load_baseline(baseline_path: Path | str) -> dict | None:
        """Carrega dados de baseline a partir de um arquivo JSON de relatório anterior."""
        p = Path(baseline_path)
        if not p.is_file():
            return None
        try:
            return json.loads(p.read_text(encoding='utf-8'))
        except Exception:
            return None

    @classmethod
    def compare(
        cls, current: BuildResult, baseline_data: dict
    ) -> dict[str, MetricDiff]:
        """Calcula as diferenças percentuais e absolutas entre o build atual e o baseline."""
        diffs: dict[str, MetricDiff] = {}

        # Duração total
        base_dur = float(
            baseline_data.get('build', {}).get('duration_seconds', 0.0)
        )
        cur_dur = float(current.duration_seconds)
        dur_delta = cur_dur - base_dur
        dur_pct = (dur_delta / base_dur * 100.0) if base_dur > 0 else 0.0
        diffs['duration_seconds'] = MetricDiff(
            current=cur_dur,
            baseline=base_dur,
            diff=round(dur_delta, 3),
            percent_change=round(dur_pct, 2),
        )

        # Tamanho do artefato final
        base_size = float(
            baseline_data.get('build', {}).get('artifact_size_bytes', 0)
        )
        cur_size = float(current.artifact_size)
        size_delta = cur_size - base_size
        size_pct = (size_delta / base_size * 100.0) if base_size > 0 else 0.0
        diffs['artifact_size_bytes'] = MetricDiff(
            current=cur_size,
            baseline=base_size,
            diff=round(size_delta, 1),
            percent_change=round(size_pct, 2),
        )

        return diffs

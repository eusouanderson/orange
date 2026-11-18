"""Testes para o comparador de métricas e regressão de build."""

import json
import tempfile
from pathlib import Path

from orange.models import BuildResult
from orange.reports.comparator import BuildComparator


def test_build_comparator_metrics():
    with tempfile.TemporaryDirectory() as tmp:
        baseline_file = Path(tmp) / 'baseline.json'
        baseline_data = {
            'build': {
                'duration_seconds': 10.0,
                'artifact_size_bytes': 10000000,
            }
        }
        baseline_file.write_text(json.dumps(baseline_data), encoding='utf-8')

        loaded = BuildComparator.load_baseline(baseline_file)
        assert loaded is not None

        current = BuildResult(
            success=True,
            platform='linux',
            profile='production',
            compiler_used='cython',
            packager_used='pyinstaller',
            optimizer_used='upx',
            duration_seconds=8.0,  # 2.0s mais rápido (-20%)
            artifact_size=8000000,  # 2MB menor (-20%)
        )

        diffs = BuildComparator.compare(current, loaded)
        assert 'duration_seconds' in diffs
        assert 'artifact_size_bytes' in diffs

        dur_diff = diffs['duration_seconds']
        assert dur_diff.current == 8.0
        assert dur_diff.baseline == 10.0
        assert dur_diff.diff == -2.0
        assert dur_diff.percent_change == -20.0

        size_diff = diffs['artifact_size_bytes']
        assert size_diff.diff == -2000000.0
        assert size_diff.percent_change == -20.0


def test_build_comparator_missing_baseline():
    loaded = BuildComparator.load_baseline(
        '/path/to/nonexistent/baseline.json'
    )
    assert loaded is None

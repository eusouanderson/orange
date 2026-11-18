"""Testes para o gerador de relatórios e métricas."""

import json
import tempfile
from pathlib import Path

from orange.models import BuildResult, OrangeConfig, StepReport
from orange.platform.detector import PlatformManager
from orange.reports.generator import ReportGenerator


def test_generate_json_and_html_reports():
    cfg = OrangeConfig()
    cfg.project.name = 'ReportApp'
    cfg.project.version = '1.2.3'

    gen = ReportGenerator(cfg)
    plat = PlatformManager.get_info()

    result = BuildResult(
        success=True,
        platform='linux',
        profile='production',
        target_path=Path('/tmp/app'),
        duration_seconds=5.432,
        artifact_size=1048576,
        steps=[
            StepReport('compilation', 2.1, 'success', '2 binários'),
            StepReport('packaging', 3.0, 'success', 'Onefile criado'),
        ],
        compiler_used='cython',
        packager_used='pyinstaller',
        optimizer_used='upx',
    )

    with tempfile.TemporaryDirectory() as tmp:
        json_file = Path(tmp) / 'report.json'
        html_file = Path(tmp) / 'report.html'

        gen.generate_json(result, plat, json_file)
        gen.generate_html(result, plat, html_file)

        assert json_file.exists()
        data = json.loads(json_file.read_text(encoding='utf-8'))
        assert data['project'] == 'ReportApp'
        assert data['status'] == 'success'
        assert len(data['steps']) == 2

        assert html_file.exists()
        html_content = html_file.read_text(encoding='utf-8')
        assert 'ReportApp' in html_content
        assert 'SUCESSO' in html_content


def test_format_terminal_output():
    cfg = OrangeConfig()
    gen = ReportGenerator(cfg)
    result = BuildResult(
        success=True,
        platform='linux',
        profile='release',
        duration_seconds=1.2,
        steps=[StepReport('test', 1.2, 'success', 'ok')],
    )
    terminal_text = gen.format_terminal(result)
    assert 'Relatório de Build' in terminal_text
    assert 'SUCESSO' in terminal_text

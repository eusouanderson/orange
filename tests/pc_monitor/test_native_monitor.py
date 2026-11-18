"""Testes automatizados para validação do binário nativo Orange PC Monitor."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

MONITOR_DIR = Path(__file__).resolve().parent.parent.parent / 'pc-monitor'
CARGO_BIN = Path.home() / '.cargo' / 'bin' / 'cargo'


@pytest.fixture(scope='session')
def monitor_binary():
    """Garante que o binário release esteja compilado para os testes de integração."""
    release_bin = MONITOR_DIR / 'target' / 'release' / 'orange-pc-monitor'
    if not release_bin.exists():
        cargo = str(CARGO_BIN) if CARGO_BIN.exists() else shutil.which('cargo')
        if not cargo:
            pytest.skip('Cargo não encontrado no ambiente de teste.')
        subprocess.run(
            [cargo, 'build', '--release'],
            cwd=str(MONITOR_DIR),
            check=True,
            capture_output=True,
        )
    return release_bin


def test_monitor_version(monitor_binary):
    """Verifica flag de versão do monitor nativo."""
    res = subprocess.run(
        [str(monitor_binary), '--version'],
        check=True,
        capture_output=True,
        text=True,
    )
    assert 'orange-pc-monitor' in res.stdout
    assert '0.1.0' in res.stdout


def test_monitor_json_telemetry_snapshot(monitor_binary):
    """Verifica emissão de telemetria completa em formato JSON."""
    res = subprocess.run(
        [str(monitor_binary), '--once', '--json'],
        check=True,
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0

    # Localiza o payload JSON (ignora banner inicial se houver)
    json_start = res.stdout.find('{')
    assert json_start != -1, f'JSON não encontrado na saída: {res.stdout}'

    data = json.loads(res.stdout[json_start:])

    # Validação de campos essenciais
    assert 'cpu' in data
    assert 'brand' in data['cpu']
    assert data['cpu']['logical_threads'] > 0

    assert 'memory' in data
    assert data['memory']['total_bytes'] > 0
    assert 0.0 <= data['memory']['usage_percent'] <= 100.0

    assert 'energy' in data
    assert data['energy']['system_estimated_watts'] > 0.0

    assert 'health' in data
    assert 0 <= data['health']['score'] <= 100
    assert 'category' in data['health']

    assert 'disks' in data
    assert isinstance(data['disks'], list)

    assert 'network' in data


def test_monitor_memory_footprint_under_30mb(monitor_binary):
    """Valida meta estrita de engenharia: consumo de RAM inferior a 30 MB."""
    import time

    proc = subprocess.Popen(
        [str(monitor_binary)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        time.sleep(1.2)  # Aguarda estabilização da amostragem
        status_file = Path(f'/proc/{proc.pid}/status')
        if not status_file.exists():
            pytest.skip('/proc status não disponível nesta plataforma')

        rss_kb = None
        for line in status_file.read_text(encoding='utf-8').splitlines():
            if line.startswith('VmRSS:'):
                parts = line.split()
                rss_kb = int(parts[1])
                break

        assert rss_kb is not None, 'VmRSS não encontrado no status do processo'
        rss_mb = rss_kb / 1024.0

        # Meta mandatória: < 30 MB
        assert rss_mb < 30.0, (
            f'Consumo de memória ({rss_mb:.2f} MB) excedeu a meta de 30 MB!'
        )
        assert rss_mb > 0.5  # Processo ativo real
    finally:
        proc.terminate()
        proc.wait()

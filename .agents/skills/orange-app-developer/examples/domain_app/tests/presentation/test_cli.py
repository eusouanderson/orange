"""Testes de interface CLI usando CliRunner."""

import sys
from pathlib import Path

from click.testing import CliRunner

APP_ROOT = Path(__file__).resolve().parent.parent.parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from src.presentation.cli import cli  # noqa: E402


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(cli, ['--version'])
    assert result.exit_code == 0
    assert 'AwesomeApp' in result.output
    assert '1.0.0' in result.output

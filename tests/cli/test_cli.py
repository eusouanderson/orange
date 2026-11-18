"""Testes automatizados para a interface de linha de comando (CLI) do Orange."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from orange.cli.main import cli
from orange.plugins.base import BasePlugin, default_registry


class SampleTestPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return 'sample-plugin'

    @property
    def version(self) -> str:
        return '0.1.0'

    @property
    def description(self) -> str:
        return 'Plugin de teste para CLI'


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'Orange: Plataforma de Build' in result.output
    assert 'build' in result.output
    assert 'doctor' in result.output
    assert 'init' in result.output


def test_cli_version():
    runner = CliRunner()
    res_flag = runner.invoke(cli, ['--version'])
    assert res_flag.exit_code == 0
    assert 'orange v' in res_flag.output

    res1 = runner.invoke(cli, ['version'])
    assert res1.exit_code == 0
    assert 'Orange Framework' in res1.output

    res2 = runner.invoke(cli, ['version', '--json-output'])
    assert res2.exit_code == 0
    data = json.loads(res2.output)
    assert 'orange' in data
    assert 'python' in data


def test_cli_doctor():
    runner = CliRunner()
    result = runner.invoke(cli, ['doctor'])
    assert result.exit_code == 0
    assert 'Python' in result.output
    assert 'Compilador C' in result.output


def test_cli_info():
    runner = CliRunner()
    result = runner.invoke(cli, ['info'])
    assert result.exit_code == 0
    assert 'Informações do Ambiente' in result.output


def test_cli_init_command():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            ['init', '--name', 'testapp', '--version', '0.5.0'],
            input='\n',
        )
        assert result.exit_code == 0
        assert Path('orange.toml').exists()

        content = Path('orange.toml').read_text(encoding='utf-8')
        assert 'name = "testapp"' in content
        assert 'version = "0.5.0"' in content

        # Tentar recriar sem --force deve falhar/avisar
        result_duplicate = runner.invoke(cli, ['init', '--name', 'novo'])
        assert result_duplicate.exit_code != 0
        assert 'já existe' in result_duplicate.output

        # Com --force deve sobrescrever
        result_force = runner.invoke(
            cli, ['init', '--name', 'novo', '--force'], input='\n\n'
        )
        assert result_force.exit_code == 0


def test_cli_cache_commands():
    runner = CliRunner()
    with runner.isolated_filesystem():
        res_status = runner.invoke(cli, ['cache', 'status'])
        assert res_status.exit_code == 0
        assert 'Estatísticas do Cache' in res_status.output

        res_clear = runner.invoke(cli, ['cache', 'clear'])
        assert res_clear.exit_code == 0
        assert 'limpo com sucesso' in res_clear.output


def test_cli_plugins_commands():
    plugin = SampleTestPlugin()
    default_registry.register(plugin)

    runner = CliRunner()
    res_list = runner.invoke(cli, ['plugins', 'list'])
    assert res_list.exit_code == 0
    assert 'sample-plugin' in res_list.output

    res_info = runner.invoke(cli, ['plugins', 'info', 'sample-plugin'])
    assert res_info.exit_code == 0
    assert 'SampleTestPlugin' in res_info.output

    default_registry.unregister('sample-plugin')


def test_cli_build_dry_run():
    runner = CliRunner()
    result = runner.invoke(
        cli, ['build', '--dry-run', '--profile', 'development']
    )
    assert result.exit_code == 0
    assert 'Modo dry-run' in result.output
    assert 'development' in result.output


def test_cli_build_missing_config():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ['build'])
        assert result.exit_code != 0
        assert 'não encontrado' in result.output

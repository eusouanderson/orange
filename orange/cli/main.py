"""Interface de Linha de Comando (CLI) profissional do Orange Framework."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import click

import orange
from orange.builder.pipeline import BuildPipeline
from orange.cache.manager import CacheManager
from orange.config.defaults import generate_default_toml
from orange.config.manager import ConfigManager
from orange.errors import OrangeError
from orange.platform.detector import PlatformManager
from orange.plugins.base import default_registry


def format_error(msg: str) -> str:
    """Formata mensagem de erro para o terminal."""
    return click.style(f'❌ Erro: {msg}', fg='red', bold=True)


def format_success(msg: str) -> str:
    """Formata mensagem de sucesso para o terminal."""
    return click.style(f'✅ {msg}', fg='green', bold=True)


def format_info(msg: str) -> str:
    """Formata mensagem informativa para o terminal."""
    return click.style(f'ℹ️  {msg}', fg='cyan')


def format_warning(msg: str) -> str:
    """Formata mensagem de aviso para o terminal."""
    return click.style(f'⚠️  {msg}', fg='yellow')


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(
    version=orange.__version__,
    prog_name='orange',
    message='%(prog)s v%(version)s',
)
@click.option(
    '--config',
    '-c',
    type=click.Path(dir_okay=False, path_type=Path),
    default=None,
    help='Caminho alternativo para o arquivo orange.toml.',
)
@click.option(
    '--verbose',
    '-v',
    is_flag=True,
    default=False,
    help='Ativa logs detalhados de depuração.',
)
@click.option(
    '--quiet',
    '-q',
    is_flag=True,
    default=False,
    help='Modo silencioso (exibe apenas erros).',
)
@click.pass_context
def cli(
    ctx: click.Context,
    config: Path | None,
    verbose: bool,
    quiet: bool,
) -> None:
    """🍊 Orange: Plataforma de Build, Compilação e Distribuição para Python."""
    ctx.ensure_object(dict)
    ctx.obj['config_path'] = config
    ctx.obj['verbose'] = verbose
    ctx.obj['quiet'] = quiet


# =====================================================================
# COMANDO: BUILD
# =====================================================================
@cli.command()
@click.option(
    '--profile',
    '-p',
    type=str,
    default=None,
    help='Perfil de build (development, release, production ou custom).',
)
@click.option(
    '--platform',
    type=click.Choice(['linux', 'windows', 'macos'], case_sensitive=False),
    default=None,
    help='Plataforma alvo para a compilação.',
)
@click.option(
    '--compile-all',
    is_flag=True,
    default=None,
    help='Compila todos os arquivos .py do projeto para C nativo.',
)
@click.option(
    '--clean/--no-clean',
    default=None,
    help='Limpa artefatos intermediários antes de compilar.',
)
@click.option(
    '--output',
    '-o',
    type=click.Path(file_okay=False, path_type=Path),
    default=None,
    help='Diretório de saída para os artefatos compilados.',
)
@click.option(
    '--target-name',
    type=str,
    default=None,
    help='Nome personalizado para o executável gerado.',
)
@click.option(
    '--dry-run',
    is_flag=True,
    default=False,
    help='Valida a configuração e o ambiente sem executar o build.',
)
@click.pass_context
def build(
    ctx: click.Context,
    profile: str | None,
    platform: str | None,
    compile_all: bool | None,
    clean: bool | None,
    output: Path | None,
    target_name: str | None,
    dry_run: bool,
) -> None:
    """Compila e empacota a aplicação Python em binário standalone."""
    verbose = ctx.obj.get('verbose', False)
    quiet = ctx.obj.get('quiet', False)
    config_path = ctx.obj.get('config_path')

    try:
        mgr = ConfigManager(config_path)
        cfg = mgr.load()
    except OrangeError as e:
        click.echo(format_error(str(e)), err=True)
        sys.exit(1)

    # Aplica sobrescritas da CLI
    overrides: dict[str, Any] = {}
    if profile:
        overrides['profile'] = profile
    if compile_all is not None:
        overrides['compile_all'] = compile_all
    if clean is not None:
        overrides['clean'] = clean
    if output:
        overrides['output'] = str(output)
    if target_name:
        overrides['target_name'] = target_name

    try:
        ConfigManager.apply_cli_overrides(cfg, **overrides)
    except OrangeError as e:
        click.echo(format_error(str(e)), err=True)
        sys.exit(1)

    if not quiet:
        click.echo(
            click.style(
                f"\n🍊 Iniciando build de '{cfg.project.name}' (v{cfg.project.version})",
                bold=True,
                fg='yellow',
            )
        )
        click.echo(f'   • Perfil:     {cfg.build.profile}')
        click.echo(
            f'   • Cython:     {"Ativo" if cfg.compiler.cython else "Desativado"}'
        )
        click.echo(f'   • Otimização: Nível {cfg.compiler.optimization}')
        click.echo(f'   • Saída:      {cfg.build.output}\n')

    if dry_run:
        click.echo(
            format_info('Modo dry-run: configuração validada com sucesso!')
        )
        sys.exit(0)

    pipeline = BuildPipeline(cfg)
    result = pipeline.run(verbose=verbose)

    if result.success:
        if not quiet:
            summary = pipeline.report_generator.format_terminal(result)
            click.echo(summary)
            click.echo(
                format_success(
                    f'Build concluído com sucesso: {result.target_path}'
                )
            )
        sys.exit(0)
    else:
        click.echo(
            format_error(result.error_message or 'Falha no build.'), err=True
        )
        sys.exit(1)


# =====================================================================
# COMANDO: DOCTOR
# =====================================================================
@cli.command()
@click.pass_context
def doctor(ctx: click.Context) -> None:
    """Diagnóstico de saúde das ferramentas e dependências de compilação."""
    quiet = ctx.obj.get('quiet', False)

    if not quiet:
        click.echo(
            click.style(
                '\n🩺 Orange Doctor: Verificando ambiente e ferramentas...\n',
                bold=True,
                fg='cyan',
            )
        )

    checks = PlatformManager.doctor()
    has_critical_failure = False

    for name, ok, details in checks:
        if ok:
            status_mark = click.style('✅ [OK]     ', fg='green', bold=True)
        elif 'Opcional' in details:
            status_mark = click.style('⚠️  [AVISO]  ', fg='yellow', bold=True)
        else:
            status_mark = click.style('❌ [FALHA]  ', fg='red', bold=True)
            has_critical_failure = True

        click.echo(f'{status_mark} {name:<30} {details}')

    click.echo('')
    if has_critical_failure:
        click.echo(
            format_error(
                'Dependências essenciais ausentes. Instale-as antes de compilar.'
            ),
            err=True,
        )
        sys.exit(1)
    else:
        click.echo(
            format_success('Ambiente pronto e configurado para compilação!')
        )
        sys.exit(0)


# =====================================================================
# COMANDO: INIT
# =====================================================================
@cli.command()
@click.option(
    '--name',
    '-n',
    default=None,
    help='Nome identificador do projeto.',
)
@click.option(
    '--version',
    default=None,
    help='Versão semântica inicial.',
)
@click.option(
    '--entrypoint',
    '-e',
    default=None,
    help='Caminho do script Python principal.',
)
@click.option(
    '--force',
    '-f',
    is_flag=True,
    default=False,
    help='Sobrescreve orange.toml existente.',
)
@click.option(
    '--interactive',
    '-i',
    is_flag=True,
    default=False,
    help='Executa no modo interativo com prompts no terminal.',
)
def init(
    name: str | None,
    version: str | None,
    entrypoint: str | None,
    force: bool,
    interactive: bool,
) -> None:
    """Gera um arquivo de configuração orange.toml para o projeto."""
    target_path = Path('orange.toml')
    if target_path.exists() and not force:
        click.echo(
            format_warning(
                'orange.toml já existe no diretório atual. Use --force para sobrescrever.'
            )
        )
        sys.exit(1)

    if interactive and sys.stdin.isatty():
        name = name or click.prompt(
            'Nome do projeto', default='my-application'
        )
        version = version or click.prompt('Versão inicial', default='1.0.0')
        entrypoint = entrypoint or click.prompt(
            'Arquivo de entrada principal', default='./src/core/main.py'
        )
    else:
        name = name or 'my-application'
        version = version or '1.0.0'
        entrypoint = entrypoint or './src/core/main.py'

    content = generate_default_toml(
        name=name,
        version=version,
        entrypoint=entrypoint,
    )
    target_path.write_text(content, encoding='utf-8')
    click.echo(
        format_success(
            f'Arquivo orange.toml gerado com sucesso em: {target_path.resolve()}'
        )
    )


# =====================================================================
# GRUPO: CACHE
# =====================================================================
@cli.group()
def cache() -> None:
    """Gerenciamento de cache de artefatos e compilação."""
    pass


@cache.command('status')
@click.pass_context
def cache_status(ctx: click.Context) -> None:
    """Exibe estatísticas de uso do cache."""
    config_path = ctx.obj.get('config_path')
    try:
        cfg = ConfigManager(config_path).load()
        cache_dir = cfg.cache.directory
    except Exception:
        cache_dir = '.orange/cache'

    mgr = CacheManager(cache_dir=cache_dir)
    stats = mgr.get_stats()

    click.echo(
        click.style(
            '\n📦 Estatísticas do Cache Orange:\n', bold=True, fg='cyan'
        )
    )
    click.echo(f'   • Diretório:         {stats["directory"]}')
    click.echo(f'   • Entradas salvas:   {stats["cached_entries"]}')
    click.echo(
        f'   • Espaço utilizado:  {stats["total_size_mb"]} MB ({stats["total_size_bytes"]} bytes)\n'
    )


@cache.command('clear')
@click.pass_context
def cache_clear(ctx: click.Context) -> None:
    """Limpa todos os artefatos armazenados no cache."""
    config_path = ctx.obj.get('config_path')
    try:
        cfg = ConfigManager(config_path).load()
        cache_dir = cfg.cache.directory
    except Exception:
        cache_dir = '.orange/cache'

    mgr = CacheManager(cache_dir=cache_dir)
    removed = mgr.clear()
    click.echo(
        format_success(
            f'Cache limpo com sucesso! ({removed} arquivos/pastas removidos)'
        )
    )


# =====================================================================
# GRUPO: PLUGINS
# =====================================================================
@cli.group()
def plugins() -> None:
    """Gerenciamento do sistema de plugins extensível."""
    pass


@plugins.command('list')
def plugins_list() -> None:
    """Lista todos os plugins registrados no Orange."""
    registered = default_registry.list_plugins()
    click.echo(
        click.style(
            '\n🔌 Plugins Registrados no Orange:\n', bold=True, fg='cyan'
        )
    )
    if not registered:
        click.echo('   (Nenhum plugin externo carregado)\n')
        return

    for p in registered:
        click.echo(
            f'   • {click.style(p.name, bold=True)} (v{p.version}) - {p.description}'
        )
    click.echo('')


@plugins.command('info')
@click.argument('plugin_name')
def plugins_info(plugin_name: str) -> None:
    """Exibe informações detalhadas sobre um plugin."""
    p = default_registry.get(plugin_name)
    if not p:
        click.echo(
            format_error(f"Plugin '{plugin_name}' não encontrado."), err=True
        )
        sys.exit(1)

    click.echo(
        click.style(
            f'\n🔌 Informações do Plugin: {p.name}\n', bold=True, fg='cyan'
        )
    )
    click.echo(f'   • Nome:        {p.name}')
    click.echo(f'   • Versão:      {p.version}')
    click.echo(f'   • Descrição:   {p.description}')
    click.echo(f'   • Classe:      {p.__class__.__name__}\n')


@plugins.command('install')
@click.argument('plugin_name')
def plugins_install(plugin_name: str) -> None:
    """Instala um plugin via pip/poetry."""
    click.echo(format_info(f"Instalando plugin '{plugin_name}'..."))
    res = subprocess.run(
        [sys.executable, '-m', 'pip', 'install', plugin_name],
        check=False,
    )
    if res.returncode == 0:
        click.echo(
            format_success(f"Plugin '{plugin_name}' instalado com sucesso!")
        )
    else:
        click.echo(
            format_error(f"Falha ao instalar plugin '{plugin_name}'."),
            err=True,
        )
        sys.exit(res.returncode)


@plugins.command('uninstall')
@click.argument('plugin_name')
def plugins_uninstall(plugin_name: str) -> None:
    """Desinstala um plugin."""
    click.echo(format_info(f"Desinstalando plugin '{plugin_name}'..."))
    res = subprocess.run(
        [sys.executable, '-m', 'pip', 'uninstall', '-y', plugin_name],
        check=False,
    )
    if res.returncode == 0:
        click.echo(
            format_success(f"Plugin '{plugin_name}' desinstalado com sucesso!")
        )
    else:
        click.echo(
            format_error(f"Falha ao desinstalar plugin '{plugin_name}'."),
            err=True,
        )
        sys.exit(res.returncode)


# =====================================================================
# COMANDO: TEST
# =====================================================================
@cli.command(
    context_settings={
        'ignore_unknown_options': True,
        'allow_extra_args': True,
    }
)
@click.option(
    '--fast',
    is_flag=True,
    default=False,
    help='Executa apenas os testes rápidos (sem benchmarks de performance).',
)
@click.option(
    '--coverage',
    is_flag=True,
    default=False,
    help='Executa com relatório de cobertura.',
)
@click.pass_context
def test(ctx: click.Context, fast: bool, coverage: bool) -> None:
    """Executa a suíte de testes automatizados com pytest."""
    cmd = [sys.executable, '-m', 'pytest']
    if fast:
        cmd.extend(['-k', 'not test_performance'])
    if coverage:
        cmd.extend(['--cov=orange', '--cov=src', '--cov-report=term-missing'])

    # Passa quaisquer argumentos extras para o pytest
    cmd.extend(ctx.args)

    click.echo(format_info(f'Executando: {" ".join(cmd)}\n'))
    res = subprocess.run(cmd, check=False)
    sys.exit(res.returncode)


# =====================================================================
# COMANDO: VERSION & INFO
# =====================================================================
@cli.command('version')
@click.option(
    '--json-output',
    is_flag=True,
    default=False,
    help='Exibe o resultado em formato JSON.',
)
def version(json_output: bool) -> None:
    """Exibe as versões do Orange, Python e sistema operacional."""
    plat = PlatformManager.get_info()
    data = {
        'orange': orange.__version__,
        'python': plat.python_version,
        'system': plat.system,
        'architecture': plat.architecture,
    }
    if json_output:
        click.echo(json.dumps(data, indent=2))
    else:
        click.echo(f'Orange Framework v{orange.__version__}')
        click.echo(
            f'Python {plat.python_version} on {plat.system} ({plat.architecture})'
        )


@cli.command('info')
@click.pass_context
def info(ctx: click.Context) -> None:
    """Exibe informações completas sobre o ambiente, projeto e configuração."""
    plat = PlatformManager.get_info()
    config_path = ctx.obj.get('config_path')

    click.echo(
        click.style(
            '\n🍊 Orange Framework - Informações do Ambiente\n',
            bold=True,
            fg='cyan',
        )
    )
    click.echo(f'   • Versão Orange:     {orange.__version__}')
    click.echo(
        f'   • Versão Python:     {plat.python_version} ({plat.tools["python"].path})'
    )
    click.echo(f'   • Sistema:           {plat.system} ({plat.architecture})')
    click.echo(
        f'   • Compilador C:      {plat.tools["c_compiler"].version or "Não detectado"}'
    )
    click.echo(
        f'   • Cython:            {plat.tools["cython"].version or "Não detectado"}'
    )
    click.echo(
        f'   • PyInstaller:       {plat.tools["pyinstaller"].version or "Não detectado"}'
    )
    click.echo(
        f'   • UPX:               {plat.tools["upx"].version or "Não detectado"}'
    )

    try:
        cfg = ConfigManager(config_path).load()
        click.echo(
            click.style(
                '\n📄 Projeto Atual (orange.toml):\n', bold=True, fg='yellow'
            )
        )
        click.echo(f'   • Nome:              {cfg.project.name}')
        click.echo(f'   • Versão:            {cfg.project.version}')
        click.echo(f'   • Entrada:           {cfg.project.entrypoint}')
        click.echo(f'   • Perfil Padrão:     {cfg.build.profile}')
        click.echo(f'   • Diretório Saída:   {cfg.build.output}')
    except Exception:
        click.echo('\n📄 Projeto Atual: Nenhum orange.toml carregado.')

    click.echo('')

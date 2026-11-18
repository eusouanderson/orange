#!/usr/bin/env python3
"""Utilitário de geração de boilerplate para aplicações profissionais no Orange Framework.

Cria automaticamente a arquitetura em camadas (Clean Architecture) e a
estrutura de testes isolada por domínio conforme os padrões do projeto.
"""

from __future__ import annotations

import argparse
from pathlib import Path

ORANGE_TOML_TEMPLATE = """# =====================================================================
# Orange Framework - Arquivo de Configuração Central (orange.toml)
# =====================================================================

[project]
name = "{name}"
version = "0.1.0"
source = "./src"
entrypoint = "./src/core/main.py"
description = "Aplicação de alta performance construída com Orange Framework"
authors = ["{author}"]

[build]
profile = "production"
compile_all = false
clean = true
output = "./dist"
target_name = "{target_name}"

[compiler]
cython = true
optimization = 3
c_compiler = "auto"
language_level = 3
type_hints = true
extra_cflags = []

[packaging]
pyinstaller = true
onefile = true
upx = true
console = true
hidden_imports = []
add_data = []

[cache]
enabled = true
directory = ".orange/cache"

[reports]
enabled = true
format = ["terminal", "json", "html"]
output_dir = "./dist/reports"

[platforms]
linux = true
windows = true
macos = true
"""

PYPROJECT_TEMPLATE = """[tool.poetry]
name = "{name_kebab}"
version = "0.1.0"
description = "Aplicação construída com Orange Framework"
authors = ["{author}"]
readme = "README.md"

[tool.poetry.dependencies]
python = ">=3.10,<3.14"
click = ">=8.1.0"

[tool.poetry.group.dev.dependencies]
pytest = ">=8.0.0"
pytest-cov = ">=5.0.0"
ruff = ">=0.8.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.ruff]
line-length = 88
target-version = "py310"

[tool.ruff.format]
quote-style = "single"
"""

MAIN_PY = '''"""Ponto de entrada principal executável (entrypoint)."""

from __future__ import annotations

import sys


def setup_environment() -> None:
    """Configura terminal seguro contra falhas de charmap em Windows."""
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass


def main() -> None:
    """Inicialização da aplicação."""
    setup_environment()
    try:
        from src.presentation.cli import cli

        cli()
    except Exception as e:
        sys.stderr.write(f'Erro fatal na execução: {e}\\n')
        sys.exit(1)


if __name__ == '__main__':
    main()
'''

CLI_PY = '''"""Camada de Apresentação via Linha de Comando (Click)."""

from __future__ import annotations

import click


@click.group()
@click.version_option(version='0.1.0')
def cli() -> None:
    """Aplicação profissional gerada com Orange Framework."""


@cli.command('run')
@click.option('--verbose', '-v', is_flag=True, help='Ativa logs detalhados.')
def run_cmd(verbose: bool) -> None:
    """Executa a rotina principal."""
    if verbose:
        click.echo('Modo detalhado ativo.')
    click.echo('Aplicação em execução com sucesso!')
'''

GITIGNORE_CONTENT = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
*.pyd
*.c

# Distribuição e Build
dist/
build/
.orange/

# Ambientes Virtuais
.venv/
env/
venv/
"""


def scaffold(target_dir: Path, app_name: str, author: str) -> None:
    print(
        f"🍊 Criando estrutura de aplicação '{app_name}' em: {target_dir.resolve()}"
    )

    kebab_name = app_name.lower().replace(' ', '-').replace('_', '-')
    snake_name = app_name.lower().replace('-', '_').replace(' ', '_')

    # Diretórios do código-fonte
    src_dirs = [
        target_dir / 'src' / 'core',
        target_dir / 'src' / 'domain',
        target_dir / 'src' / 'application',
        target_dir / 'src' / 'infrastructure',
        target_dir / 'src' / 'presentation',
    ]

    # Diretórios de testes OBRIGATÓRIOS por domínio
    test_dirs = [
        target_dir / 'tests' / 'domain',
        target_dir / 'tests' / 'application',
        target_dir / 'tests' / 'infrastructure',
        target_dir / 'tests' / 'presentation',
    ]

    for d in src_dirs + test_dirs:
        d.mkdir(parents=True, exist_ok=True)
        init_file = d / '__init__.py'
        if not init_file.exists():
            init_file.write_text('', encoding='utf-8')

    (target_dir / 'src' / '__init__.py').write_text('', encoding='utf-8')
    (target_dir / 'tests' / '__init__.py').write_text('', encoding='utf-8')

    # Arquivos base
    (target_dir / 'orange.toml').write_text(
        ORANGE_TOML_TEMPLATE.format(
            name=app_name, author=author, target_name=snake_name
        ),
        encoding='utf-8',
    )

    (target_dir / 'pyproject.toml').write_text(
        PYPROJECT_TEMPLATE.format(name_kebab=kebab_name, author=author),
        encoding='utf-8',
    )

    (target_dir / '.gitignore').write_text(GITIGNORE_CONTENT, encoding='utf-8')
    (target_dir / 'README.md').write_text(
        f'# {app_name}\n\nAplicação profissional construída e compilada com Orange Framework.\n',
        encoding='utf-8',
    )

    (target_dir / 'src' / 'core' / 'main.py').write_text(
        MAIN_PY, encoding='utf-8'
    )
    (target_dir / 'src' / 'presentation' / 'cli.py').write_text(
        CLI_PY, encoding='utf-8'
    )

    # Testes iniciais
    (target_dir / 'tests' / 'presentation' / 'test_cli.py').write_text(
        'from click.testing import CliRunner\n'
        'from src.presentation.cli import cli\n\n'
        'def test_cli_version():\n'
        '    runner = CliRunner()\n'
        '    res = runner.invoke(cli, ["--version"])\n'
        '    assert res.exit_code == 0\n',
        encoding='utf-8',
    )

    print('✅ Projeto estruturado com sucesso seguindo todos os padrões!')
    print('Para compilar a aplicação com Orange:')
    print(f'  cd {target_dir} && orange build')


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Scaffold de aplicação Orange.'
    )
    parser.add_argument(
        '--name', '-n', default='MyOrangeApp', help='Nome da aplicação'
    )
    parser.add_argument(
        '--dest', '-d', default='.', help='Diretório de destino'
    )
    parser.add_argument(
        '--author',
        '-a',
        default='Desenvolvedor <dev@exemplo.com>',
        help='Autor da aplicação',
    )

    args = parser.parse_args()
    dest_path = Path(args.dest)
    dest_path.mkdir(parents=True, exist_ok=True)
    scaffold(dest_path, args.name, args.author)


if __name__ == '__main__':
    main()

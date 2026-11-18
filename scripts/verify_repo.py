#!/usr/bin/env python3
"""Script de verificação pré-commit / pré-push para o repositório Orange.

Valida:
1. Conformidade estrita da organização de testes por domínio (tests/<dominio>/ com __init__.py).
2. Linter de código com Ruff (ruff check).
3. Formatação de código com Ruff (ruff format --check).
4. Diagnóstico de ambiente e ferramentas com Orange Doctor.
5. Suíte de testes automatizados do core e domínios com pytest.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def print_step(title: str) -> None:
    print(
        f'\n\033[1;34m🔍 [Orange Quality Gate]\033[0m \033[1m{title}\033[0m...'
    )


def print_success(msg: str) -> None:
    print(f'   \033[32m✅ {msg}\033[0m')


def print_error(msg: str) -> None:
    print(f'   \033[31m❌ {msg}\033[0m', file=sys.stderr)


def run_command(cmd: list[str], description: str) -> bool:
    print_step(description)
    try:
        subprocess.run(cmd, check=True)
        print_success(f'{description} aprovado!')
        return True
    except subprocess.CalledProcessError as e:
        print_error(
            f'{description} falhou com código de saída {e.returncode}.'
        )
        return False
    except Exception as e:
        print_error(f'Falha ao executar {description}: {e}')
        return False


def verify_domain_testing_structure(root_dir: Path) -> bool:
    print_step('Validando regra mandatória de testes por domínio')
    tests_dir = root_dir / 'tests'
    if not tests_dir.exists():
        print_error("Diretório 'tests/' não encontrado.")
        return False

    errors: list[str] = []

    # 1. Checa se existem arquivos test_*.py soltos na raiz de tests/
    stray_files = [
        f.name
        for f in tests_dir.iterdir()
        if f.is_file()
        and f.name.startswith('test_')
        and f.name.endswith('.py')
    ]
    if stray_files:
        errors.append(
            f'Arquivos de teste soltos encontrados na raiz de tests/: {", ".join(stray_files)}.\n'
            '   -> REGRA: Todos os testes devem residir dentro de subpastas por domínio (tests/<dominio>/).'
        )

    # 2. Checa se cada subpasta de domínio possui __init__.py
    for item in tests_dir.iterdir():
        if (
            item.is_dir()
            and not item.name.startswith('.')
            and item.name != '__pycache__'
        ):
            init_file = item / '__init__.py'
            if not init_file.exists():
                errors.append(
                    f"A pasta de domínio 'tests/{item.name}' não possui arquivo '__init__.py'."
                )

            # Verifica se há pelo menos um arquivo de teste na pasta
            test_files = list(item.glob('test_*.py'))
            if not test_files:
                errors.append(
                    f"A pasta de domínio 'tests/{item.name}' não possui nenhum arquivo 'test_*.py'."
                )

    if errors:
        for err in errors:
            print_error(err)
        return False

    print_success(
        'Todos os testes estão estritamente organizados por domínio com __init__.py!'
    )
    return True


def main() -> int:
    root = Path(__file__).resolve().parent.parent

    # Flag para verificar modo rápido (apenas linter + estrutura + testes unitários rápidos)
    quick_mode = '--quick' in sys.argv or '-q' in sys.argv

    print('=' * 65)
    print(' 🍊 Orange Framework - Quality Gate & Verificação Pré-Envio')
    print('=' * 65)

    # 1. Validação da estrutura de pastas de teste
    if not verify_domain_testing_structure(root):
        print(
            '\n\033[31;1m🚨 O commit foi abortado devido a violação de padrões de teste por domínio!\033[0m\n'
        )
        return 1

    # 2. Ruff Linter
    if not run_command(
        ['poetry', 'run', 'ruff', 'check'], 'Checagem estática (Ruff Check)'
    ):
        print(
            '\n\033[31;1m🚨 O commit foi abortado devido a erros de linting! Execute `poetry run ruff check --fix`.\033[0m\n'
        )
        return 1

    # 3. Ruff Formatter
    if not run_command(
        ['poetry', 'run', 'ruff', 'format', '--check'],
        'Conformidade de formatação (Ruff Format)',
    ):
        print(
            '\n\033[31;1m🚨 O commit foi abortado devido a arquivos não formatados! Execute `poetry run ruff format`.\033[0m\n'
        )
        return 1

    # 4. Orange Doctor (Apenas em modo completo/pre-push)
    if not quick_mode:
        if not run_command(
            ['poetry', 'run', 'orange', 'doctor'],
            'Diagnóstico de Ambiente (Orange Doctor)',
        ):
            print(
                '\n\033[31;1m🚨 Falha no diagnóstico de ferramentas do Orange!\033[0m\n'
            )
            return 1

    # 5. Execução dos Testes Automatizados
    test_cmd = (
        [
            'poetry',
            'run',
            'pytest',
            'tests/builder/',
            'tests/cache/',
            'tests/cli/',
            'tests/compiler/',
            'tests/config/',
            'tests/platform/',
            'tests/plugins/',
            'tests/reports/',
            '-q',
        ]
        if quick_mode
        else ['poetry', 'run', 'pytest', '-k', 'not test_performance', '-q']
    )

    desc = (
        'Testes rápidos do Core'
        if quick_mode
        else 'Suíte completa de Testes Automatizados'
    )
    if not run_command(test_cmd, desc):
        print(
            '\n\033[31;1m🚨 Testes falharam! Corrija os erros antes de enviar ao repositório.\033[0m\n'
        )
        return 1

    print('\n' + '=' * 65)
    print(
        ' \033[32;1m✨ TUDO PRONTO! Todas as validações foram aprovadas com sucesso.\033[0m'
    )
    print('=' * 65 + '\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())

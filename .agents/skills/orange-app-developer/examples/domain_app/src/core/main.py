"""Ponto de entrada principal executável (entrypoint)."""

from __future__ import annotations

import sys


def setup_environment() -> None:
    """Configura terminal com UTF-8 seguro para Windows/Linux/macOS."""
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass


def main() -> None:
    """Função de inicialização do executável standalone."""
    setup_environment()
    try:
        from ..presentation.cli import cli

        cli()
    except Exception as e:
        sys.stderr.write(f'Erro fatal na execução: {e}\n')
        sys.exit(1)


if __name__ == '__main__':
    main()

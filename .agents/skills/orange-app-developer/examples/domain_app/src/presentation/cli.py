"""Interface de linha de comando desenvolvida com Click."""

from __future__ import annotations

from pathlib import Path

import click

from ..application.services import InventoryService
from ..infrastructure.adapters import JsonFileStorage


@click.group()
@click.version_option(version='1.0.0', prog_name='AwesomeApp')
def cli():
    """AwesomeApp - Demonstração de arquitetura profissional com Orange."""


@cli.command('add')
@click.option('--name', '-n', required=True, help='Nome do produto.')
@click.option(
    '--price', '-p', type=float, required=True, help='Preço unitário.'
)
@click.option('--qty', '-q', type=int, default=1, help='Quantidade.')
def add_item_cmd(name: str, price: float, qty: int):
    """Adiciona um item ao inventário."""
    storage = JsonFileStorage(Path('inventory.json'))
    service = InventoryService(storage)
    item = service.add_product(name, price, qty)
    click.echo(
        f"Item '{item.name}' adicionado! Subtotal: R$ {item.total():.2f}"
    )


@cli.command('total')
def total_cmd():
    """Exibe o total acumulado do inventário."""
    storage = JsonFileStorage(Path('inventory.json'))
    service = InventoryService(storage)
    total = service.get_grand_total()
    click.echo(f'Valor total em estoque: R$ {total:.2f}')

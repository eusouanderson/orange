"""Testes unitários para o domínio Item."""

import sys
from pathlib import Path

import pytest

APP_ROOT = Path(__file__).resolve().parent.parent.parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from src.domain.entities import Item  # noqa: E402


def test_item_total_calculation():
    item = Item(name='Teclado Mecânico', price=250.0, quantity=2)
    assert item.total() == 500.0


def test_item_negative_values_raise_error():
    item = Item(name='Mouse', price=-10.0, quantity=1)
    with pytest.raises(ValueError, match='não-negativos'):
        item.total()

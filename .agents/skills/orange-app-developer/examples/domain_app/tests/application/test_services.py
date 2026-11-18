"""Testes unitários para InventoryService com mock de repositório."""

import sys
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent.parent.parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from src.application.services import InventoryService  # noqa: E402
from src.domain.entities import Item  # noqa: E402


class FakeStorage:
    def __init__(self):
        self.items = []

    def save_item(self, item: Item) -> None:
        self.items.append(item)

    def list_items(self) -> list[Item]:
        return list(self.items)


def test_inventory_service_grand_total():
    storage = FakeStorage()
    service = InventoryService(storage)

    service.add_product('Item A', price=10.0, quantity=3)
    service.add_product('Item B', price=20.0, quantity=2)

    assert service.get_grand_total() == 70.0

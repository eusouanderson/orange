"""Serviços de aplicação e casos de uso."""

from __future__ import annotations

from typing import Protocol

from ..domain.entities import Item


class StoragePort(Protocol):
    """Porta de persistência do domínio."""

    def save_item(self, item: Item) -> None: ...

    def list_items(self) -> list[Item]: ...


class InventoryService:
    """Orquestrador de operações de inventário."""

    def __init__(self, storage: StoragePort) -> None:
        self.storage = storage

    def add_product(self, name: str, price: float, quantity: int) -> Item:
        item = Item(name=name, price=price, quantity=quantity)
        self.storage.save_item(item)
        return item

    def get_grand_total(self) -> float:
        items = self.storage.list_items()
        return round(sum(item.total() for item in items), 2)

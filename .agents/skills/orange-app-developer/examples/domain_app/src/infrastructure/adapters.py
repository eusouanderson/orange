"""Adaptadores concretos de infraestrutura e I/O."""

from __future__ import annotations

import json
from pathlib import Path

from ..domain.entities import Item


class JsonFileStorage:
    """Implementação em arquivo JSON da porta de armazenamento."""

    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path

    def save_item(self, item: Item) -> None:
        items = self.list_items()
        items.append(item)
        data = [
            {'name': i.name, 'price': i.price, 'quantity': i.quantity}
            for i in items
        ]
        self.file_path.write_text(json.dumps(data, indent=2), encoding='utf-8')

    def list_items(self) -> list[Item]:
        if not self.file_path.exists():
            return []
        try:
            raw = json.loads(self.file_path.read_text(encoding='utf-8'))
            return [
                Item(
                    name=x['name'],
                    price=float(x['price']),
                    quantity=int(x['quantity']),
                )
                for x in raw
            ]
        except Exception:
            return []

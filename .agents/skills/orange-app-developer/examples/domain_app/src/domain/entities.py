"""Entidades de domínio e regras de negócio puras."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    """Representa um item do catálogo."""

    name: str
    price: float
    quantity: int

    def total(self) -> float:
        """Calcula o valor total do item."""
        if self.price < 0 or self.quantity < 0:
            raise ValueError('Preço e quantidade devem ser não-negativos.')
        return round(self.price * self.quantity, 2)

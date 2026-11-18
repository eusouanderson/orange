"""Fixtures globais para a suíte de testes."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_storage_path():
    """Gera um arquivo de persistência em diretório temporário isolado."""
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        yield Path(tmp) / 'test_inventory.json'

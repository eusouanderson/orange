import os
import sys
from pathlib import Path

import pytest
from PyQt6.QtWidgets import QApplication

# Força backend offscreen para evitar dependência de display em CI/SSH
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Garante que a raiz do projeto esteja no sys.path para imports "src" e "compile"
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

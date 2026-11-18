import os
import sys
from pathlib import Path

import pytest

try:
    from PyQt6.QtWidgets import QApplication
except (ImportError, OSError):
    QApplication = None

# Força backend offscreen para evitar dependência de display em CI/SSH
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

# Garante que a raiz do projeto esteja no sys.path para imports "src" e "compile"
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(scope='session')
def qapp():
    if QApplication is None:
        pytest.skip('PyQt6 não está disponível neste ambiente.')
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

# reload.py
from PySide6.QtWidgets import QApplication

from src.core.main import MyWindow


def reload_application():
    app = QApplication([])

    window = MyWindow()
    window.show()

    app.exec()


if __name__ == '__main__':
    reload_application()

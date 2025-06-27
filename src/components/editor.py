from PySide6.QtWidgets import QPlainTextEdit


class Editor(QPlainTextEdit):
    def __init__(self, font, parent=None):
        super().__init__(parent)
        self.setFont(font)
        self.setStyleSheet('background-color: #1E1E1E; color: #D4D4D4;')
        self.setTabStopDistance(4 * font.pointSizeF())

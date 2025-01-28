import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtGui import QFontDatabase, QIcon, QFont

from src.components.editor import Editor
from src.components.file_operations import FileOperations
from src.components.ui_elements import create_buttons


class CodeEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Orange Editor")
        self.setGeometry(100, 100, 800, 600)

        # Font setup
        path_font = os.path.abspath("src/assets/font/JetBrainsMono.ttf")
        path_icon = os.path.abspath("src/assets/images/icons/orange.ico")
        print(path_font)
        print(path_icon)
        font_id = QFontDatabase.addApplicationFont(path_font)
        font_family = QFontDatabase.applicationFontFamilies(font_id)
        font_family = QFontDatabase.applicationFontFamilies(font_id)
        font = QFont(font_family, 10)
        self.setFont(font)

        
        self.setWindowIcon(QIcon(path_icon))

        # Components
        self.editor = Editor(font)
        self.file_operations = FileOperations()

        # UI Layout
        self.init_ui()

    def init_ui(self):
        buttons_layout = create_buttons(self.editor, self.file_operations)

        main_layout = QVBoxLayout()
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(self.editor)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CodeEditor()
    window.show()
    sys.exit(app.exec())

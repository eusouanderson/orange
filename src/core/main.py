import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from os import environ, path
from PySide6.QtGui import QShortcut, QKeySequence

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QPlainTextEdit,
    QFileDialog,
    QLabel,
    QColorDialog,
    QFontDialog,
    QSlider,
    
)

env = environ.get("ENV", "production")

class CodeEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        
        if env == "development":
            icon_path = path.join(
                path.dirname(__file__),
                "..",
                "assets",
                "images",
                "icons",
                "orange.ico",
            )
        else:
            icon_path = path.join(
                path.dirname(__file__), "assets", "images", "icons", "orange.ico"
            )

        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle("Orange Editor")
        self.setGeometry(100, 100, 800, 600)

        self.font = QFont("Consolas", 12)
        self.setFont(self.font)

        self.init_ui()

    def init_ui(self):
        """Inicializa os componentes da interface gráfica."""
        self.setStyleSheet("background-color: #1E1E1E; color: #D4D4D4;")
        self.create_shortcuts()
        self.editor = QPlainTextEdit(self)
        self.editor.setFont(self.font)
        self.editor.setStyleSheet("background-color: #1E1E1E; color: #D4D4D4;")
        self.editor.setTabStopDistance(4 * self.font.pointSizeF())

        self.line_number_area = QLabel(self)
        self.line_number_area.setStyleSheet("background-color: #2E2E2E; color: #888888;")
        self.line_number_area.setAlignment(Qt.AlignTop | Qt.AlignRight)
        self.line_number_area.setFont(QFont("Consolas", 10))

        self.editor.blockCountChanged.connect(self.update_line_numbers)
        self.editor.updateRequest.connect(self.update_line_area)

        self.open_button = QPushButton("Abrir", self)
        self.open_button.setStyleSheet("background-color: #333333; color: #FFFFFF;")
        self.open_button.clicked.connect(self.open_file)

        self.new_button = QPushButton("Novo", self)
        self.new_button.setStyleSheet("background-color: #333333; color: #FFFFFF;")
        self.new_button.clicked.connect(self.new_file)

        self.save_button = QPushButton("Salvar", self)
        self.save_button.setStyleSheet("background-color: #333333; color: #FFFFFF;")
        self.save_button.clicked.connect(self.save_file)

        self.format_button = QPushButton("Cor", self)
        self.format_button.setStyleSheet("background-color: #333333; color: #FFFFFF;")
        self.format_button.clicked.connect(self.open_format_dialog)

        self.transparent_button = QPushButton("Alternar Transparência", self)
        self.transparent_button.setStyleSheet("background-color: #333333; color: #FFFFFF;")
        self.transparent_button.clicked.connect(self.toggle_transparency)

        self.transparency_slider = QSlider(Qt.Horizontal, self)
        self.transparency_slider.setMinimum(0)
        self.transparency_slider.setMaximum(100)
        self.transparency_slider.setValue(100) 
        self.transparency_slider.setTickInterval(10)
        self.transparency_slider.setTickPosition(QSlider.TicksBelow)
        self.transparency_slider.valueChanged.connect(self.update_transparency)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.open_button)
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.new_button)
        buttons_layout.addWidget(self.format_button)
        buttons_layout.addWidget(self.transparent_button) 

        editor_layout = QHBoxLayout()
        editor_layout.addWidget(self.line_number_area)
        editor_layout.addWidget(self.editor)

        transparency_layout = QVBoxLayout()
        transparency_layout.addWidget(QLabel("Ajustar Transparência:"))
        transparency_layout.addWidget(self.transparency_slider)

        
        main_layout = QVBoxLayout()
        main_layout.addLayout(buttons_layout)
        main_layout.addLayout(editor_layout)
        main_layout.addLayout(transparency_layout)

        central_widget = QWidget(self)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.update_line_numbers()

        self.transparent = False
    def create_shortcuts(self):
        """Cria atalhos para os botões.""" 
        self.open_shortcut = QShortcut(QKeySequence("Ctrl+O"), self)
        self.open_shortcut.activated.connect(self.open_file)

        self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.save_shortcut.activated.connect(self.save_file)

        self.new_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        self.new_shortcut.activated.connect(self.new_file)

        self.format_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        self.format_shortcut.activated.connect(self.open_format_dialog)

        self.transparent_shortcut = QShortcut(QKeySequence("Ctrl+T"), self)
        self.transparent_shortcut.activated.connect(self.toggle_transparency)


    def update_line_numbers(self):
        """Atualiza os números de linha."""
        lines = self.editor.blockCount()
        text = "\n".join(str(i + 1) for i in range(lines))
        self.line_number_area.setText(text)

    def update_line_area(self, rect, dy):
        """Sincroniza os números de linha com o editor."""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update()

    def new_file(self):
        """Cria um novo arquivo e limpa o editor.""" 
        self.editor.setPlainText("")

    def open_file(self):
        """Abre um arquivo e carrega o conteúdo no editor.""" 
        file_path, _ = QFileDialog.getOpenFileName(self, "Abrir Arquivo", "", "Todos os Arquivos (*.*)")
        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                self.editor.setPlainText(content)

    def save_file(self):
        """Salva o conteúdo do editor em um arquivo.""" 
        file_path, _ = QFileDialog.getSaveFileName(self, "Salvar Arquivo", "", "Todos os Arquivos (*.*)")
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                content = self.editor.toPlainText()
                file.write(content)

    def open_format_dialog(self):
        """Abre um diálogo para personalizar o estilo do editor.""" 
        color = QColorDialog.getColor()
        if color.isValid():
            self.editor.setStyleSheet(
                f"background-color: #1E1E1E; color: {color.name()};"
            )

    def toggle_transparency(self):
        """Alterna a transparência da janela.""" 
        if self.transparent:
            self.setWindowOpacity(1) 
        else:
            self.setWindowOpacity(0.5)  
        
        self.transparent = not self.transparent

    def update_transparency(self):
        """Atualiza a transparência conforme o valor do slider.""" 
        opacity_value = self.transparency_slider.value() / 100  
        self.setWindowOpacity(opacity_value)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CodeEditor()
    window.show()
    sys.exit(app.exec())

import sys
import os


if not hasattr(sys, "frozen"):
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import (
        QApplication,
        QMainWindow,
        QVBoxLayout,
        QWidget,
        QPushButton,
        QLineEdit,
        QGridLayout,
        QTextEdit,
    )
else:

    from PySide6.QtCore import Qt
    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import (
        QApplication,
        QMainWindow,
        QVBoxLayout,
        QWidget,
        QPushButton,
        QLineEdit,
        QGridLayout,
        QTextEdit,
    )

env = os.environ.get("ENV", "production")


class Calculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Orange Calculator")
        self.setGeometry(300, 300, 400, 500)
        self.setFixedSize(400, 500)

        self.memory_visible = True  # Estado inicial da memória visível

        # Tela de memória
        self.memory_display = QTextEdit(self)
        self.memory_display.setReadOnly(True)
        self.memory_display.setStyleSheet("font-size: 18px; padding: 10px;")
        self.memory_display.setFixedHeight(100)

        # Botão para alternar a memória
        self.toggle_memory_button = QPushButton("Ocultar Memória")
        self.toggle_memory_button.setStyleSheet("font-size: 14px; padding: 10px;")
        self.toggle_memory_button.clicked.connect(self.toggle_memory_visibility)

        # Configuração do ícone
        if env == "development":
            icon_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "assets",
                "images",
                "icons",
                "orange.ico",
            )
        else:
            icon_path = os.path.join(
                os.path.dirname(__file__), "assets", "images", "icons", "orange.ico"
            )

        self.setWindowIcon(QIcon(icon_path))

        # Layout principal
        self.main_layout = QVBoxLayout()

        # Tela de resultados
        self.result_display = QLineEdit(self)
        self.result_display.setAlignment(Qt.AlignRight)
        self.result_display.setReadOnly(False)
        self.result_display.setStyleSheet("font-size: 24px; padding: 10px;")

        self.main_layout.addWidget(self.memory_display)
        self.main_layout.addWidget(self.toggle_memory_button)
        self.main_layout.addWidget(self.result_display)

        # Botões da calculadora
        self.button_layout = QGridLayout()
        self.create_buttons()
        self.main_layout.addLayout(self.button_layout)

        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)

    def create_buttons(self):
        buttons = [
            ("7", 0, 0),
            ("8", 0, 1),
            ("9", 0, 2),
            ("/", 0, 3, "operator"),
            ("%", 0, 4, "operator"),
            ("sin", 0, 5, "trig"),
            ("4", 1, 0),
            ("5", 1, 1),
            ("6", 1, 2),
            ("*", 1, 3, "operator"),
            ("√", 1, 4, "operator"),
            ("cos", 1, 5, "trig"),
            ("1", 2, 0),
            ("2", 2, 1),
            ("3", 2, 2),
            ("-", 2, 3, "operator"),
            ("(", 2, 4, "parenthesis"),
            ("tan", 2, 5, "trig"),
            ("0", 3, 0),
            (".", 3, 1),
            ("=", 3, 2, "operator"),
            ("+", 3, 3, "operator"),
            (")", 3, 4, "parenthesis"),
            ("log", 3, 5, "trig"),
            ("C", 4, 0, "clear"),
            ("←", 4, 1, "backspace"),
        ]

        for button in buttons:
            text, row, col = button[:3]
            style = button[3] if len(button) > 3 else ""
            self.create_button(text, row, col, style)

    def create_button(self, text, row, col, style=""):
        button = QPushButton(text)
        button.setStyleSheet("font-size: 18px; padding: 15px;")
        button.clicked.connect(self.on_button_click)

        if style == "operator":
            button.setStyleSheet(
                "font-size: 18px; padding: 15px; background-color: lightblue;"
            )
        elif style == "trig":
            button.setStyleSheet(
                "font-size: 18px; padding: 15px; background-color: lightgreen;"
            )
        elif style == "parenthesis":
            button.setStyleSheet(
                "font-size: 18px; padding: 15px; background-color: lightyellow;"
            )
        elif style == "clear":
            button.setStyleSheet(
                "font-size: 18px; padding: 15px; background-color: lightcoral;"
            )
        elif style == "backspace":
            button.setStyleSheet(
                "font-size: 18px; padding: 15px; background-color: lightgray;"
            )

        self.button_layout.addWidget(button, row, col)

    def toggle_memory_visibility(self):
        if self.memory_visible:
            self.memory_display.hide()
            self.toggle_memory_button.setText("Exibir Memória")
        else:
            self.memory_display.show()
            self.toggle_memory_button.setText("Ocultar Memória")

        self.memory_visible = not self.memory_visible

    def on_button_click(self):
        button = self.sender()
        text = button.text()
        current_text = self.result_display.text()

        if text == "=":
            self.on_equal_click()
        elif text == "C":
            self.result_display.clear()
        elif text == "←":
            self.on_backspace()
        else:
            new_text = current_text + text
            self.result_display.setText(new_text)

    def on_backspace(self):
        current_text = self.result_display.text()
        new_text = current_text[:-1]
        self.result_display.setText(new_text)

    def on_equal_click(self):

        try:
            expression = self.result_display.text()

            expression = expression.replace("√", "math.sqrt(")
            if "sqrt" in expression:
                expression = expression + ")"

            expression = expression.replace("sin", "math.sin(math.radians")
            expression = expression.replace("cos", "math.cos(math.radians")
            expression = expression.replace("tan", "math.tan(math.radians")

            if "sin" in expression or "cos" in expression or "tan" in expression:
                expression = expression + ")"

            print(expression)

            result = eval(expression)

            result_text = str(round(result, 2))

            # Atualiza o display do resultado
            self.result_display.setText(result_text)

            # Adiciona a expressão e o resultado na memória
            self.memory_display.append(
                f"{self.expression_replace(expression)} = {result_text}"
            )

        except Exception as e:
            # Tratamento de erro aprimorado
            examples = {
                "√": "√: √25",
                "%": "%: 10%2",
                "+": "+: 5+3",
                "-": "-: 10-2",
                "*": "*: 5*3",
                "/": "/: 10/2",
                "tan": "tan: tan(45)",
                "sin": "sin: sin(30)",
                "cos": "cos: cos(45)",
            }

            # Limpa e substitui a expressão para identificação
            expression_cleaned = self.expression_replace(expression)
            print(f"Erro ao processar expressão: {expression_cleaned}")

            # Gera um exemplo baseado na operação identificada
            operation = self.get_operation_from_error(expression)
            example = examples.get(operation, "Operação não reconhecida.")
            self.result_display.setText(f"Erro. Exemplo válido: {example}")
            print(f"Erro: {expression_cleaned} {e}")

    def expression_replace(self, expression):
        """Substitui elementos específicos da expressão para exibição limpa."""
        try:
            replacements = {
                "math.": "",
                "radians": "",
                ")": "",
                "(": "",
                "sqrt": "√",
            }
            for old, new in replacements.items():
                expression = expression.replace(old, new)
        except Exception as e:
            print(f"Erro ao substituir expressão: {e}")
        return expression

    def get_operation_from_error(self, expression):
        """Identifica qual operação foi mencionada no erro."""
        if "sin" in expression:
            return "sin"
        elif "cos" in expression:
            return "cos"
        elif "tan" in expression:
            return "tan"
        elif "√" in expression or "sqrt" in expression:
            return "√"
        elif "+" in expression:
            return "+"
        elif "-" in expression:
            return "-"
        elif "*" in expression:
            return "*"
        elif "/" in expression:
            return "/"

        elif "%" in expression:
            return "%"

        else:
            return None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Calculator()
    window.show()
    sys.exit(app.exec())

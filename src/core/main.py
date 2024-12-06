import sys
from os import environ, path
import math
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QKeyEvent
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QLineEdit,
    QGridLayout,
    QDialog,
    QTextEdit,
)
import cython

env = environ.get("ENV", "production")


class Calculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Orange")
        self.history = []
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
        self.setWindowTitle("Calculadora Orange")
        self.setGeometry(300, 300, 400, 500)
        self.setFixedSize(380, 400)

        self.main_layout = QVBoxLayout()

        self.result_display = QLineEdit(self)
        self.result_display.setAlignment(Qt.AlignRight)
        self.result_display.setReadOnly(False)
        self.result_display.setStyleSheet("font-size: 24px; padding: 10px;")
        self.main_layout.addWidget(self.result_display)

        self.button_layout = QGridLayout()

        self.create_button("7", 0, 0)
        self.create_button("8", 0, 1)
        self.create_button("9", 0, 2)
        self.create_button("/", 0, 3, "operator")
        self.create_button("%", 0, 4, "operator")
        self.create_button("sin", 0, 5, "trig")

        self.create_button("4", 1, 0)
        self.create_button("5", 1, 1)
        self.create_button("6", 1, 2)
        self.create_button("*", 1, 3, "operator")
        self.create_button("√", 1, 4, "operator")
        self.create_button("cos", 1, 5, "trig")

        self.create_button("1", 2, 0)
        self.create_button("2", 2, 1)
        self.create_button("3", 2, 2)
        self.create_button("-", 2, 3, "operator")
        self.create_button("(", 2, 4, "parenthesis")
        self.create_button("tan", 2, 5, "trig")

        self.create_button("0", 3, 0)
        self.create_button(".", 3, 1)
        self.create_button("=", 3, 2, "operator")
        self.create_button("+", 3, 3, "operator")
        self.create_button(")", 3, 4, "parenthesis")
        self.create_button("log", 3, 5, "trig")

        self.create_button("C", 4, 0, "clear")

        self.create_button("←", 4, 1, "backspace")

        self.create_button("Hist", 4, 2, "history")

        self.create_button("Help", 4, 3, "help")

        self.main_layout.addLayout(self.button_layout)

        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)

    def keyPressEvent(self, event: QKeyEvent):
        """
        Método para capturar a tecla pressionada no teclado e realizar a ação correspondente.
        """
        key = event.key()
        if key in [
            Qt.Key_1,
            Qt.Key_2,
            Qt.Key_3,
            Qt.Key_4,
            Qt.Key_5,
            Qt.Key_6,
            Qt.Key_7,
            Qt.Key_8,
            Qt.Key_9,
            Qt.Key_0,
        ]:

            self.result_display.setText(self.result_display.text() + event.text())

        elif key == Qt.Key_Plus:
            self.result_display.setText(self.result_display.text() + "+")
        elif key == Qt.Key_Minus:
            self.result_display.setText(self.result_display.text() + "-")
        elif key == Qt.Key_Asterisk:
            self.result_display.setText(self.result_display.text() + "*")
        elif key == Qt.Key_Slash:
            self.result_display.setText(self.result_display.text() + "/")
        elif key == Qt.Key_Percent:
            self.result_display.setText(self.result_display.text() + "%")
        elif key == Qt.Key_Period:
            self.result_display.setText(self.result_display.text() + ".")
        elif key == Qt.Key_Equal:
            self.on_equal_click()
        elif key == Qt.Key_Backspace:
            self.on_backspace()
        elif key == Qt.Key_Delete:
            self.result_display.clear()

        elif key == Qt.Key_Enter or key == Qt.Key_Return:
            self.on_equal_click()

        elif key == Qt.Key_Left:
            self.result_display.setText(self.result_display.text() + "(")
        elif key == Qt.Key_Right:
            self.result_display.setText(self.result_display.text() + ")")

        elif key == Qt.Key_L:
            self.result_display.setText(self.result_display.text() + "log")
        elif key == Qt.Key_S:
            self.result_display.setText(self.result_display.text() + "sin")
        elif key == Qt.Key_C:
            self.result_display.setText(self.result_display.text() + "cos")
        elif key == Qt.Key_T:
            self.result_display.setText(self.result_display.text() + "tan")

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
        elif style == "help":
            button.setStyleSheet(
                "font-size: 18px; padding: 15px; background-color: yellow;"
            )

        self.button_layout.addWidget(button, row, col)

    def show_help(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajuda - Atalhos do Teclado")
        dialog.setGeometry(100, 100, 400, 300)

        help_text = QTextEdit(dialog)
        help_text.setReadOnly(True)
        help_text.setText(
            """
            Atalhos do Teclado:
            1, 2, ..., 9, 0  -> Digitar números
            +, -, *, /       -> Operadores
            %                -> Módulo
            .                -> Ponto decimal
            Backspace        -> Apagar último caractere
            Delete           -> Limpar tudo
            Enter/Return     -> Calcular resultado
            (                -> Abrir parêntese
            )                -> Fechar parêntese
            Pode usar o teclado para escrever expressões matemáticas.
            e expressões trigonometricas Ex: sin(45), cos(45), tan(45)
            """
        )
        layout = QVBoxLayout()
        layout.addWidget(help_text)
        dialog.setLayout(layout)
        dialog.exec()

    def show_history(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Histórico de Operações")
        dialog.setGeometry(100, 100, 400, 300)

        text_edit = QTextEdit(dialog)
        text_edit.setReadOnly(True)
        text_edit.setText("\n".join(self.history))
        layout = QVBoxLayout()
        layout.addWidget(text_edit)
        dialog.setLayout(layout)

        dialog.exec()

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
        elif text == "Hist":
            self.show_history()
        elif text == "Help":
            self.show_help()

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

            if "sin" in expression and "(" not in expression:
                self.result_display.setText("Erro: Ex: sin(45°), Falta parênteses")
                return
            if "cos" in expression and "(" not in expression:
                self.result_display.setText("Erro: Ex: cos(45°), Falta parênteses")
                return
            if "tan" in expression and "(" not in expression:
                self.result_display.setText("Erro: Ex: tan(45°), Falta parênteses")
                return

            expression = expression.replace("sin", "math.sin(math.radians")
            expression = expression.replace("cos", "math.cos(math.radians")
            expression = expression.replace("tan", "math.tan(math.radians")
            expression = expression.replace("√", "math.sqrt(")

            if (
                "sin" in expression
                or "cos" in expression
                or "tan" in expression
                or "sqrt" in expression
            ):

                expression = expression + ")"

            else:
                expression = expression.replace(")", " ")

            print(expression)

            result = eval(expression)
            # result = round(result, 2)

            self.history.append(f"{expression} = {result}")

            self.result_display.setText(str(result))
        except Exception as e:
            self.result_display.setText("Erro")
            print(f"Erro: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Calculator()
    window.show()
    sys.exit(app.exec())

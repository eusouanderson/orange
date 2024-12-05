import sys
import os
import math
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
)

env = os.environ.get("ENV", "production")

class Calculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Orange")
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
                os.path.dirname(__file__),  "assets", "images", "icons", "orange.ico"
            )
        print(env)
        print(icon_path)

        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle("Calculadora Orange")
        self.setGeometry(300, 300, 400, 500)

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


        # Clear button
        self.create_button("C", 4, 0, "clear")

        

        # Backspace button
        self.create_button("←", 4, 1, "backspace")

        

        self.main_layout.addLayout(self.button_layout)

        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)

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
        new_text = current_text[:-1]  # Remove the last character
        self.result_display.setText(new_text)

    def on_equal_click(self):
        try:
            expression = self.result_display.text()
            print(expression)

            # Verificando se as funções trigonométricas têm parênteses
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

            if "sin" in expression or "cos" in expression or "tan" in expression:
                expression = expression.replace("√", "math.sqrt")
                expression = expression + ")"
            else:
                expression = expression.replace(")", " ")

            result = eval(expression)
            result = round(result, 2)

            self.result_display.setText(str(result))
        except Exception as e:
            self.result_display.setText("Erro")
            print(f"Erro: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Calculator()
    window.show()
    sys.exit(app.exec())

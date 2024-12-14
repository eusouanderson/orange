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
    QLabel,
)
from exchange_rate import get_exchange_rate

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
        self.setFixedSize(700, 400)

        self.main_layout = QVBoxLayout()

        self.is_result_displayed = False
        self.result_display = QLineEdit(self)
        self.result_display.setAlignment(Qt.AlignRight)
        self.result_display.setReadOnly(False)
        self.result_display.setStyleSheet("font-size: 24px; padding: 10px;")
        self.main_layout.addWidget(self.result_display)

        self.memory = {"result": ""}
        self.memory_indicator = QLineEdit(self)
        self.memory_indicator.setText("")
        self.memory_indicator.setStyleSheet(
            """
            font-size: 12px;
            padding: 5px;
            border: 1px solid #ddd;
            background-color: #f0f0f0;
            border-radius: 5px;
        """
        )
        self.memory_indicator.setGeometry(10, 10, 80, 30)
        self.memory_indicator.hide()
        self.main_layout.addWidget(self.memory_indicator)

        self.button_layout = QGridLayout()

        self.create_button("7", 0, 0)
        self.create_button("8", 0, 1)
        self.create_button("9", 0, 2)
        self.create_button("/", 0, 3, "operator")
        self.create_button("%", 0, 4, "operator")
        self.create_button("sin", 0, 5, "trig")
        self.create_button("USD:BRL", 0, 6, "exchange")
        self.create_button("MR", 0, 7, "memory")

        self.create_button("4", 1, 0)
        self.create_button("5", 1, 1)
        self.create_button("6", 1, 2)
        self.create_button("*", 1, 3, "operator")
        self.create_button("√", 1, 4, "operator")
        self.create_button("cos", 1, 5, "trig")
        self.create_button("EUR:BRL", 1, 6, "exchange")
        self.create_button("M+", 1, 7, "memory")

        self.create_button("1", 2, 0)
        self.create_button("2", 2, 1)
        self.create_button("3", 2, 2)
        self.create_button("-", 2, 3, "operator")
        self.create_button("(", 2, 4, "parenthesis")
        self.create_button("tan", 2, 5, "trig")
        self.create_button("GBP:BRL", 2, 6, "exchange")
        self.create_button("M-", 2, 7, "memory")

        self.create_button("0", 3, 0)
        self.create_button(".", 3, 1)
        self.create_button("=", 3, 2, "operator")
        self.create_button("+", 3, 3, "operator")
        self.create_button(")", 3, 4, "parenthesis")
        self.create_button("log", 3, 5, "trig")
        self.create_button("JPY:BRL", 3, 6, "exchange")

        self.create_button("C", 4, 0, "clear")
        self.create_button("←", 4, 1, "backspace")
        self.create_button("Hist", 4, 2, "history")
        self.create_button("Help", 4, 3, "help")
        self.create_button("AUD:BRL", 4, 5, "exchange")
        self.create_button("CAD:BRL", 4, 6, "exchange")

        self.main_layout.addLayout(self.button_layout)

        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)

    def handle_input(self, text):
        """
        Manipula a entrada de texto, seja do teclado ou de cliques no botão.
        """
        current_text = ""
        if text.isdigit():
            if self.is_result_displayed:
                self.result_display.setText(text)
                self.is_result_displayed = False
            else:
                current_text = self.result_display.text()
                self.result_display.setText(current_text + text)

        elif text in ["*", "/", "%", "+", "-"]:
            if self.is_result_displayed:
                current_text = self.result_display.text()
                self.result_display.setText(current_text + text)
                self.is_result_displayed = False
            else:
                current_text = self.result_display.text()
                self.result_display.setText(current_text + text)

    def on_button_click(self):
        button = self.sender()
        text = button.text()
        current_text = self.handle_input(text)

        exchange_pairs = {
            "USD:BRL": ("USD", "BRL"),
            "EUR:BRL": ("EUR", "BRL"),
            "GBP:BRL": ("GBP", "BRL"),
            "JPY:BRL": ("JPY", "BRL"),
            "AUD:BRL": ("AUD", "BRL"),
            "CAD:BRL": ("CAD", "BRL"),
            "BRL:USD": ("BRL", "USD"),
            "BRL:EUR": ("BRL", "EUR"),
            "EUR:USD": ("EUR", "USD"),
            "USD:EUR": ("USD", "EUR"),
            "BRL:GBP": ("BRL", "GBP"),
            "GBP:BRL": ("GBP", "BRL"),
            "BRL:JPY": ("BRL", "JPY"),
            "JPY:BRL": ("JPY", "BRL"),
            "USD:JPY": ("USD", "JPY"),
            "JPY:USD": ("JPY", "USD"),
            "BRL:BTC": ("BRL", "BTC"),
            "BTC:BRL": ("BTC", "BRL"),
        }

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
        elif text == "(":
            self.result_display.setText(self.result_display.text() + "(")

        elif text == ")":
            self.result_display.setText(self.result_display.text() + ")")
        
        elif text == "MR":
            if "result" in self.memory and self.memory["result"]:
                self.result_display.setText(str(self.memory["result"]))
                self.update_memory_indicator("MR")
                self.is_result_displayed = True
                self.update_memory_indicator("M " + str(self.memory["result"]))
        elif text == "M+":
            self.memory["result"] = self.result_display.text()
            self.update_memory_indicator("M " + str(self.memory["result"]))

        elif text == "M-":
            self.memory["result"] = ""
            self.memory_indicator.hide()

        elif text in exchange_pairs:
            try:
                result = self.result_display.text()
                from_currency, to_currency = exchange_pairs[text]
                rate = get_exchange_rate(
                    from_currency=from_currency, to_currency=to_currency, amount=int(result),
                )
                formatted_rate = str(rate) if to_currency != "BTC" else str(rate)
                self.result_display.setText(str(rate))
            except Exception as e:
                self.result_display.setText("Erro")

        self.current_text = self.result_display.text()

        operations = {
            "log": math.log,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "√": math.sqrt,
            "%": lambda x, y: x % y,
        }

        if text in operations:
            try:

                number = float(self.result_display.text().strip())
                if text == "log" and number <= 0:
                    self.result_display.setText(
                        "Erro  (Algoritimo indefinido para operadores negativo)"
                    )
                if text == "√" and number < 0:
                    self.result_display.setText(
                        "Erro  (Algoritimo indefinido para operadores negativo)"
                    )
                if text == "%":
                    number = str(self.result_display.text().strip().split("%")[0])
                    
                if text in ["sin", "cos", "tan"]:
                    number = math.radians(number)
                result = operations[text](number)
                self.result_display.setText(str(result))

            except ValueError as e:
                self.result_display.setText(f"Erro: {e}")
            except Exception as e:
                self.result_display.setText("Erro")

        try:
            self.result_display.setText(str(current_text + text))
        except Exception as e:
            pass

    def keyPressEvent(self, event: QKeyEvent):
        """
        Método para capturar a tecla pressionada no teclado e realizar a ação correspondente.
        """
        key = event.key()

        if Qt.Key_0 <= key <= Qt.Key_9:
            self.handle_input(chr(key))

        # Operadores matemáticos
        elif key in [
            Qt.Key_Plus,
            Qt.Key_Minus,
            Qt.Key_Asterisk,
            Qt.Key_Slash,
            Qt.Key_Percent,
        ]:
            operator_map = {
                Qt.Key_Plus: "+",
                Qt.Key_Minus: "-",
                Qt.Key_Asterisk: "*",
                Qt.Key_Slash: "/",
                Qt.Key_Percent: "%",
            }
            self.handle_input(operator_map[key])

        # Tecla ponto para decimais
        elif key == Qt.Key_Period:
            self.result_display.setText(self.result_display.text() + ".")

        # Parênteses
        elif key == Qt.Key_Left:
            self.result_display.setText(self.result_display.text() + "(")
        elif key == Qt.Key_Right:
            self.result_display.setText(self.result_display.text() + ")")

        # Funções matemáticas
        elif key == Qt.Key_L:
            self.result_display.setText(self.result_display.text() + "log")
        elif key == Qt.Key_S:
            self.result_display.setText(self.result_display.text() + "sin")
        elif key == Qt.Key_C:
            self.result_display.setText(self.result_display.text() + "cos")
        elif key == Qt.Key_T:
            self.result_display.setText(self.result_display.text() + "tan")

        # Igual
        elif key == Qt.Key_Equal or key == Qt.Key_Enter or key == Qt.Key_Return:
            self.on_equal_click()

        # Backspace para apagar o último caractere
        elif key == Qt.Key_Backspace:
            self.on_backspace()

        # Delete para limpar todo o texto
        elif key == Qt.Key_Delete:
            self.result_display.clear()

    def on_backspace(self):
        current_text = self.result_display.text()
        new_text = current_text[:-1]
        self.result_display.setText(new_text)

    def update_memory_indicator(self, action):
        """
        Atualiza o indicador de memória com base na ação realizada.
        """
        self.memory_indicator.setText(action)
        self.memory_indicator.show()

    def create_button(self, text, row, col, style=""):
        button = QPushButton(text)
        button.setStyleSheet("font-size: 15px; padding: 15px;")
        button.clicked.connect(self.on_button_click)
        if style == "history":
            button.setStyleSheet(
                "font-size: 18px; padding: 15px; background-color: lightgray;"
            )

        if style == "exchange":
            button.setStyleSheet(
                "font-size: 18px; padding: 15px; background-color: lightgreen;"
            )

        if style == "memory":
            button.setStyleSheet(
                "font-size: 18px; padding: 15px; background-color: lightblue;"
            )
        if style == "operator":
            button.setStyleSheet(
                "font-size: 18px; padding: 15px; background-color: lightblue;"
            )
        elif style == "trig":
            button.setStyleSheet(
                "font-size: 18px; padding: 15px; background-color: violet;"
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

    def on_equal_click(self):
        try:
            self.is_result_displayed = True
            expression = self.result_display.text()

            if (
                "sin" in expression
                or "cos" in expression
                or "tan" in expression
                or "sqrt" in expression
            ):

                expression = expression + ")"

            elif "%" in expression:
                expression = expression.replace(")", " ")

            result = eval(expression)

            print(f"Expressão: {expression}, Resultado: {result}")
            if not self.memory.get("result"):
                self.memory["result"] = result
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

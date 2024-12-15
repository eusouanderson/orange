import sys
from os import environ, path
import math
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon, QKeyEvent, QFont
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
    QToolTip,
    QHBoxLayout,
    QFileDialog,
)
from exchange_rate import get_exchange_rate

env = environ.get("ENV", "production")


class Calculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Orange")
        self.history = []
        self.is_dark_mode = False
        

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
        self.create_button("%", 0, 4, "operator_2")
        self.create_button("sin", 0, 5, "trig")
        self.create_button("USD:BRL", 0, 6, "exchange")
        self.create_button("MR", 0, 7, "memory")

        self.create_button("4", 1, 0)
        self.create_button("5", 1, 1)
        self.create_button("6", 1, 2)
        self.create_button("*", 1, 3, "operator")
        self.create_button("√", 1, 4, "operator_2")
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

        self.theme_button = QPushButton("🌚", self)
        self.theme_button.clicked.connect(self.toggle_theme)
        self.theme_button.setFixedHeight(20)
        self.theme_button.setFixedWidth(20)
        self.theme_button.setStyleSheet(
            """
            font-size: 12px;
            padding: 5px;
            border: 1px solid #ddd;
            border-radius: 5px;
        """
        )
        self.main_layout.addWidget(self.theme_button)

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

        elif text == "%":

            text = self.result_display.text().strip().replace("%", "")
            try:
                number = float(text)
                result = number / 100
                self.result_display.setText(str(result))
            except ValueError:
                self.result_display.setText("Erro")

        elif text in exchange_pairs:
            try:
                result = self.result_display.text()
                from_currency, to_currency = exchange_pairs[text]
                rate = get_exchange_rate(
                    from_currency=from_currency,
                    to_currency=to_currency,
                    amount=int(result),
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

        key_mappings = {
            Qt.Key_Period: lambda: self.result_display.setText(
                self.result_display.text() + "."
            ),
            Qt.Key_Left: lambda: self.result_display.setText(
                self.result_display.text() + "("
            ),
            Qt.Key_Right: lambda: self.result_display.setText(
                self.result_display.text() + ")"
            ),
            Qt.Key_L: lambda: self.result_display.setText(
                self.result_display.text() + "log"
            ),
            Qt.Key_S: lambda: self.result_display.setText(
                self.result_display.text() + "sin"
            ),
            Qt.Key_C: lambda: self.result_display.setText(
                self.result_display.text() + "cos"
            ),
            Qt.Key_T: lambda: self.result_display.setText(
                self.result_display.text() + "tan"
            ),
            Qt.Key_Equal: self.on_equal_click,
            Qt.Key_Enter: self.on_equal_click,
            Qt.Key_Return: self.on_equal_click,
            Qt.Key_Backspace: self.on_backspace,
            Qt.Key_Delete: self.result_display.clear,
        }

        if key in key_mappings:
            key_mappings[key]()

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

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()

    def apply_theme(self):
        """Aplica o tema apropriado."""
        if self.is_dark_mode:
            self.setStyleSheet(
                """
                QMainWindow {
                background-color: #1f1f1f; /* Azul escuro ou cinza com um toque mais sofisticado */
                color: white;
                }

                QLineEdit {
                    background-color: #2a2a2a; /* Tom de cinza mais escuro */
                    color: #00ff00;  /* Verde neon */
                    border: 2px solid #444; /* Borda mais grossa para destacar o input */
                    border-radius: 5px; /* Bordas arredondadas */
                    padding: 5px; /* Adicionando padding para melhorar a legibilidade */
                }

                QLineEdit:focus {
                    border: 2px solid #00ff00; /* Foco no campo com borda verde neon */
                    background-color: #3a3a3a; /* Escurece um pouco mais ao focar */
                }

                QPushButton {
                    background-color: #333; /* Cinza escuro para botões */
                    color: white;
                    border: 1px solid #555;
                    border-radius: 5px; /* Bordas arredondadas */
                    padding: 10px 20px; /* Botões com um bom tamanho */
                    
                }

                QPushButton:hover {
                    background-color: #555; /* Cor de fundo mais clara ao passar o mouse */
                    border-color: #00ff00; /* Borda verde no hover para um toque mais tecnológico */
                }

                QPushButton:pressed {
                    background-color: #444; /* Quando pressionado, fica um pouco mais escuro */
                }
            """
            )
            self.theme_button.setText("☀️")
        else:
            self.setStyleSheet(
                """
                QMainWindow {
                    background-color: #f0f0f0; /* Cor de fundo mais clara */
                    color: black;
                }

                QLineEdit {
                    background-color: #ffffff; /* Branco para campos de texto */
                    color: #333; /* Texto em cinza escuro para contraste */
                    border: 2px solid #ccc; /* Borda mais grossa para destacar o input */
                    border-radius: 5px;
                    padding: 5px;
                }

                QLineEdit:focus {
                    border: 2px solid #0077ff; /* Borda azul ao focar */
                    background-color: #e6f0ff; /* Fundo levemente azul claro ao focar */
                }

                QPushButton {
                    background-color: #e0e0e0;
                    color: black;
                    border: 1px solid #bbb;
                    border-radius: 5px;
                    padding: 10px 20px;
                    
                }

                QPushButton:hover {
                    background-color: #d0d0d0;
                    border-color: #0077ff; /* Azul no hover */
                }

                QPushButton:pressed {
                    background-color: #c0c0c0; /* Quando pressionado, fica mais escuro */
                }

            """
            )
            self.theme_button.setText("🌚")

    def create_button(self, text, row, col, style=""):
        button = QPushButton(text)

        # Estilos centralizados
        styles = {
            "history": "font-size: 18px; padding: 15px; background-color: #1E1E1E; color: #A0A0A0;",
            "exchange": "font-size: 18px; padding: 15px; background-color: #00BFAE; color: #000000;",
            "memory": "font-size: 18px; padding: 15px; background-color: #4C6A92; color: #000000;",
            "operator": "font-size: 18px; padding: 15px; background-color: #6A5ACD; color: #000000;",
            "operator_2": "font-size: 18px; padding: 15px; background-color: #9B59B6; color: #000000;",
            "trig": "font-size: 18px; padding: 15px; background-color: #8E44AD; color: #000000;",
            "parenthesis": "font-size: 18px; padding: 15px; background-color: #34495E; color: #000000;",
            "clear": "font-size: 18px; padding: 15px; background-color: #E74C3C; color: #000000;",
            "backspace": "font-size: 18px; padding: 15px; background-color: #2C3E50; color: #000000;",
            "help": "font-size: 18px; padding: 15px; background-color: #F39C12; color: #000000;",
        }

        default_style = "font-size: 15px; padding: 10px 15px; background-color: #FFFFFF; color: #000000;"; 


        # Aplicar estilo
        button.setStyleSheet(styles.get(style, default_style))

        # Adicionar ToolTip com exemplos
        QToolTip.setFont(QFont("SansSerif", 10))

        # Exemplo de Tooltip de acordo com o tipo de botão
        if style == "history":
            button.setToolTip(f"Exibe o histórico das operações.")
        elif style == "exchange":
            button.setToolTip(f"Converte o valor atual de uma moeda para outra.")
        elif style == "memory":
            button.setToolTip(f"Armazena o valor atual na memória.")
        elif style == "operator":
            button.setToolTip(f"Realiza operações (exemplo: 5 + 3 = 8).")
        elif style == "trig":
            button.setToolTip(f"Calcula funções trigonométricas (exemplo:  30 sin).")
        elif style == "parenthesis":
            button.setToolTip(f"Utilize parênteses para agrupar operações (exemplo: (3 + 5) * 2).")
        elif style == "clear":
            button.setToolTip(f"Limpa a tela da calculadora.")
        elif style == "backspace":
            button.setToolTip(f"Remove o último caractere inserido.")
        elif style == "help":
            button.setToolTip(f"Mostra informações sobre a calculadora.")
        else:
            button.setToolTip(f"Botão: {text}")  # Para botões sem estilo específico

        # Conectar animação ao clique
        button.clicked.connect(lambda: self.animate_button(button))
        button.clicked.connect(self.on_button_click)

        # Adicionar ao layout
        self.button_layout.addWidget(button, row, col)

    def animate_button(self, button):
        animation = QPropertyAnimation(button, b"geometry")
        animation.setDuration(200)
        animation.setEasingCurve(QEasingCurve.OutBounce)
        animation.setStartValue(button.geometry())
        animation.setEndValue(button.geometry().adjusted(-5, -5, 5, 5))
        animation.start()

    def show_help(self):
        # Criando a janela de ajuda
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajuda - Calculadora")
        dialog.setGeometry(100, 100, 500, 400)

        # Título principal
        title = QLabel("Guia de Uso - Calculadora")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Bold))

        # Texto informativo
        help_text = QTextEdit(dialog)
        help_text.setReadOnly(True)
        help_text.setText(
            """
            <h3>Atalhos do Teclado</h3>
            <ul>
                <li><b>1, 2, ..., 9, 0</b> -> Digitar números</li>
                <li><b>+, -, *, /</b> -> Operadores</li>
                <li><b>%</b> -> Calcula porcentagem com base no último número</li>
                <li><b>.</b> -> Adicionar ponto decimal</li>
                <li><b>Backspace</b> -> Apagar o último caractere</li>
                <li><b>Delete</b> -> Limpar tudo</li>
                <li><b>Enter/Return</b> -> Calcular resultado</li>
                <li><b>(, )</b> -> Parênteses para expressões</li>
            </ul>
            <h3>Recursos Extras</h3>
            <ul>
                <li>Suporte a expressões trigonométricas: <code>sin, cos, tan</code></li>
                <li>Suporte a <b>logaritmos</b>: <code>log</code></li>
                <li>Cálculos combinados com porcentagem: <code>200 × 10% "Ainda não funcionando" </code></li>
                <li>Conversão de moedas: <code>USD:BRL</code>, <code>EUR:BRL</code>, <code>GBP:BRL</code>, <code>JPY:BRL</code>, <code>AUD:BRL</code>, <code>CAD:BRL</code></li>
            </ul>
            <p>Use o teclado para escrever expressões matemáticas diretamente e pressione <b>Enter</b> para calcular.</p>
            """
        )
        help_text.setFont(QFont("Arial", 12))

        # Adicionar botão para fechar
        button_layout = QHBoxLayout()
        close_button = QPushButton("Fechar")
        close_button.setStyleSheet(
            "padding: 10px; background-color: #87CEEB; border-radius: 5px; font-size: 14px;"
        )
        close_button.clicked.connect(dialog.close)

        # Botão adicional para abrir um link de documentação online
        doc_button = QPushButton("Documentação Online")
        doc_button.setStyleSheet(
            "padding: 10px; background-color: #FFD700; border-radius: 5px; font-size: 14px;"
        )
        doc_button.clicked.connect(lambda: self.open_documentation())

        button_layout.addWidget(doc_button)
        button_layout.addStretch()
        button_layout.addWidget(close_button)

        # Layout principal
        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(help_text)
        layout.addLayout(button_layout)

        dialog.setLayout(layout)
        dialog.exec()

    def open_documentation(self):
        import webbrowser

        webbrowser.open("https://github.com/eusouanderson/orange_calculator")

    def show_history(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Histórico de Operações")
        dialog.setGeometry(100, 100, 400, 300)

        # Criação do QTextEdit para exibir e editar o histórico
        text_edit = QTextEdit(dialog)
        text_edit.setText("\n".join(self.history))  # Preencher o campo com o histórico

        # Botão para salvar o histórico como um arquivo TXT
        save_button = QPushButton("Salvar como TXT", dialog)
        save_button.clicked.connect(lambda: self.save_to_txt(text_edit.toPlainText()))  # Conectar à função de salvar

        # Layout para colocar o texto editável e o botão
        layout = QVBoxLayout()
        layout.addWidget(text_edit)
        layout.addWidget(save_button)
        dialog.setLayout(layout)

        dialog.exec()

    def save_to_txt(self, text):
        
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Salvar Histórico", "", "Text Files (*.txt);;All Files (*)", options=options)

        if file_path:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(text)
            

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

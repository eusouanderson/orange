import sys
from os import environ
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QTextCharFormat, QColor
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLineEdit, QTextEdit, QListWidget, QDialog
from os import path

env = environ.get("ENV", "production")

class ChatWindow(QMainWindow):
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
        self.setWindowTitle("MSN Orange")
        self.setGeometry(100, 100, 600, 500)

        # Área de chat
        self.chat_area = QTextEdit(self)
        self.chat_area.setReadOnly(True)
        self.chat_area.setTextInteractionFlags(Qt.TextEditorInteraction)

        # Lista de contatos
        self.contact_list = QListWidget(self)
        self.contact_list.addItems(["Contato 1", "Contato 2", "Contato 3"])  
        self.contact_list.setSelectionMode(QListWidget.SingleSelection)
        self.contact_list.clicked.connect(self.contact_selected)

        # Caixa de entrada de mensagem
        self.message_input = QLineEdit(self)
        self.message_input.setPlaceholderText("Digite sua mensagem...")

        # Botão de enviar
        self.send_button = QPushButton("Enviar", self)
        self.send_button.clicked.connect(self.send_message)

        # Layouts
        chat_layout = QVBoxLayout()
        chat_layout.addWidget(self.chat_area)
        chat_layout.addWidget(self.message_input)
        chat_layout.addWidget(self.send_button)

        contact_layout = QVBoxLayout()
        contact_layout.addWidget(self.contact_list)

        main_layout = QHBoxLayout()
        main_layout.addLayout(contact_layout, 1)
        main_layout.addLayout(chat_layout, 3)

        central_widget = QWidget(self)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.selected_contact = None

    def contact_selected(self):
        # Atualiza o contato selecionado
        selected_item = self.contact_list.currentItem()
        if selected_item:
            self.selected_contact = selected_item.text()
            self.chat_area.clear()
            self.chat_area.append(f"Conversando com {self.selected_contact}...")

    def send_message(self):
        message = self.message_input.text()
        if message and self.selected_contact:
            self.display_message(message, "Você")
            self.message_input.clear()
            self.save_message(message, "Você")
            

    def display_message(self, message, sender):
        
        message_format = QTextCharFormat()
        if sender == "Você":
            message_format.setForeground(QColor(0, 122, 204))
        else:
            message_format.setForeground(QColor(0, 255, 0))
        self.chat_area.setCurrentCharFormat(message_format)
        self.chat_area.append(f"{sender}: {message}")

    def save_message(self, message, sender):
        with open("chat_history.txt", "a") as file:
            file.write(f"{sender}: {message}\n")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())

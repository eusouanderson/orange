import sys
import pyaudio
import wave
from os import environ, path
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QFont
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLineEdit, QTextEdit, QListWidget
from datetime import datetime

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

        font = QFont("Arial", 10)
        self.setFont(font)

        # Área de chat
        self.chat_area = QTextEdit(self)
        self.chat_area.setReadOnly(True)
        self.chat_area.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.chat_area.setStyleSheet("background-color: #1E1E1E; color: white; border-radius: 10px; padding: 10px;")

        # Lista de contatos
        self.contact_list = QListWidget(self)
        self.contact_list.addItems(["Contato 1", "Contato 2", "Contato 3"])  
        self.contact_list.setSelectionMode(QListWidget.SingleSelection)
        self.contact_list.clicked.connect(self.contact_selected)
        self.contact_list.setStyleSheet("background-color: #2C2C2C; color: white; border-radius: 10px; padding: 10px;")

        # Caixa de entrada de mensagem
        self.message_input = QLineEdit(self)
        self.message_input.setPlaceholderText("Digite sua mensagem...")
        self.message_input.setStyleSheet("background-color: #333; color: white; border-radius: 10px; padding: 10px;")

        # Botão de enviar
        self.send_button = QPushButton("Enviar", self)
        self.send_button.setStyleSheet("background-color: #FF8C00; color: white; border-radius: 10px; padding: 10px;")
        self.send_button.clicked.connect(self.send_message)

        # Botão de enviar áudio
        self.record_button = QPushButton("Gravar Áudio", self)
        self.record_button.setStyleSheet("background-color: #FF8C00; color: white; border-radius: 10px; padding: 10px;")
        self.record_button.clicked.connect(self.toggle_recording)

        # Layouts
        chat_layout = QVBoxLayout()
        chat_layout.addWidget(self.chat_area)
        chat_layout.addWidget(self.message_input)
        chat_layout.addWidget(self.send_button)
        chat_layout.addWidget(self.record_button)

        contact_layout = QVBoxLayout()
        contact_layout.addWidget(self.contact_list)

        main_layout = QHBoxLayout()
        main_layout.addLayout(contact_layout, 1)
        main_layout.addLayout(chat_layout, 3)

        central_widget = QWidget(self)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.selected_contact = None

        # Setup do PyAudio para gravação
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.audio_file = f"recorded_audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        self.is_recording = False

    def contact_selected(self):
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
        self.chat_area.append(f"{sender}: {message}")

    def save_message(self, message, sender):
        with open("chat_history.txt", "a") as file:
            file.write(f"{sender}: {message}\n")

    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.is_recording = True
        self.record_button.setText("Parar Gravação")
        
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=16000,
                                  input=True,
                                  frames_per_buffer=1024)
        
        self.frames = []

        self.record_audio()

    def stop_recording(self):
        self.is_recording = False
        self.record_button.setText("Gravar Áudio")

        # Salva o áudio gravado
        with wave.open(self.audio_file, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(16000)
            wf.writeframes(b''.join(self.frames))

        self.stream.stop_stream()
        self.stream.close()

        self.send_audio()

    def record_audio(self):
        if self.is_recording:
            data = self.stream.read(1024)
            self.frames.append(data)
            QTimer.singleShot(100, self.record_audio)  # Continue a gravação

    def send_audio(self):
        self.chat_area.append(f"Você enviou um áudio para {self.selected_contact}")
        self.save_message(self.audio_file, "Você")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())

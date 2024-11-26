import os
import random
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget
from reload import setup_reload_signal, ReloadHandler
from watchdog.observers import Observer

# Função para trocar o fundo
def change_background(label, background_images_path):
    images = os.listdir(background_images_path)
    selected_image = random.choice(images)
    pixmap = QPixmap(os.path.join(background_images_path, selected_image))
    label.setPixmap(pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

def main():
    app = QApplication([])

    window = QWidget()
    window.setWindowTitle('Trocar Background')

    layout = QVBoxLayout()

    label = QLabel('Orange!')
    label.setAlignment(Qt.AlignCenter)
    layout.addWidget(label)

    background_images_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'images', 'background')

    button = QPushButton('Trocar Fundo')
    button.clicked.connect(lambda: change_background(label, background_images_path))
    layout.addWidget(button)

    reload_button = QPushButton('Recarregar')
    layout.addWidget(reload_button)

    window.setLayout(layout)
    window.resize(800, 600)
    window.show()

    # Configuração do sinal para recarregar a aplicação
    reload_signal = setup_reload_signal()
    reload_signal.reload_signal.connect(reload_signal.reload_app)

    # Configuração do observador para monitorar o código
    event_handler = ReloadHandler(reload_signal)
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(__file__), recursive=True)
    observer.start()

    # Executar a aplicação
    try:
        app.exec()
    finally:
        observer.stop()
        observer.join()

# Chamada para iniciar o aplicativo
if __name__ == '__main__':
    main()

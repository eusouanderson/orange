import os
import random
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget
from reload import setup_reload_signal, ReloadHandler
from watchdog.observers import Observer


# Função para trocar o fundo
def change_background(label, background_images_path):
    images = os.listdir(background_images_path)
    selected_image = random.choice(images)
    pixmap = QPixmap(os.path.join(background_images_path, selected_image))
    label.setPixmap(
        pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
    )


def main():
    app = QApplication([])

    window = QWidget()
    window.setWindowTitle("Orange")
    icon_path = os.path.join(
        os.path.dirname(__file__), "..", "assets", "images", "icons", "orange.png"
    )
    window.setWindowIcon(QIcon(icon_path))
    window.setStyleSheet("background-color: #FFA500;")  # Cor background
    # window.setStyleSheet("font: 16px Arial;") # Font
    # window.setStyleSheet("color: #FFA500;") # Cor font
    # window.setStyleSheet("border-radius: 10px;")
    # window.setStyleSheet("border: gray;") # Cor border
    # window.setStyleSheet("color: #FFA500;")

    layout = QVBoxLayout()

    label = QLabel("Orange!")
    label.setAlignment(Qt.AlignCenter)
    layout.addWidget(label)

    background_images_path = os.path.join(
        os.path.dirname(__file__), "..", "assets", "images", "background"
    )

    button = QPushButton("Trocar Background")
    button.clicked.connect(lambda: change_background(label, background_images_path))
    layout.addWidget(button)

    button1 = QPushButton("Otimizar")
    button1.clicked.connect(lambda: app.quit())
    layout.addWidget(button1)

    reload_button = QPushButton("Recarregar")
    layout.addWidget(reload_button)

    window.setLayout(layout)
    window.resize(800, 600)
    window.show()

    reload_signal = setup_reload_signal()
    reload_signal.reload_signal.connect(reload_signal.reload_app)

    event_handler = ReloadHandler(reload_signal)
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(__file__), recursive=True)
    observer.start()

    try:
        app.exec()
    finally:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    main()

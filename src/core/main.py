import os
import json
import logging
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QColor
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLineEdit,
    QSlider,
    QColorDialog,
    QDialog,
    QDialogButtonBox,
)
from watchdog.observers import Observer
from reload import setup_reload_signal, ReloadHandler
from config.clean import clean
from config.background import change_background
from config.themes import change_theme
from config.choose import choose_background_color, choose_button_color
from config.save_user_config import save_settings, load_settings

# Configuração do logger
logging.basicConfig(level=logging.DEBUG if os.getenv("ENV") == "development" else logging.WARNING)
logger = logging.getLogger(__name__)

# Layout settings window
class LayoutConfigWindow(QDialog):
    def __init__(self, window, label, button_layout):
        super().__init__(window)
        self.setWindowTitle("Layout Settings")
        self.setModal(True)

        # Layout of the settings window
        layout = QVBoxLayout()

        # Text input for background color
        self.background_input = QLineEdit(self)
        self.background_input.setPlaceholderText("Background color (e.g., #FFA500)")
        layout.addWidget(self.background_input)

        # Button to choose background color
        background_button = QPushButton("Choose Background Color", self)
        background_button.clicked.connect(
            lambda: choose_background_color(self.background_input)
        )
        layout.addWidget(background_button)

        # Text input for button color
        self.button_color_input = QLineEdit(self)
        self.button_color_input.setPlaceholderText("Button color (e.g., #ffffff)")
        layout.addWidget(self.button_color_input)

        # Button to choose button color
        button_button = QPushButton("Choose Button Color", self)
        button_button.clicked.connect(
            lambda: choose_button_color(self.button_color_input)
        )
        layout.addWidget(button_button)

        # Slider for font size
        self.font_slider = QSlider(Qt.Horizontal)
        self.font_slider.setRange(10, 40)
        self.font_slider.setValue(16)
        layout.addWidget(self.font_slider)

        # Confirmation buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Applying the layout
        self.setLayout(layout)

    def get_values(self):
        return (
            self.background_input.text(),
            self.font_slider.value(),
            self.button_color_input.text(),
        )


# Main function
def main():
    app = QApplication([])

    window = QWidget()
    window.setWindowTitle("Orange")
    icon_path = os.path.join(
        os.path.dirname(__file__), "assets", "images", "icons", "orange.ico"
    )
    window.setWindowIcon(QIcon(icon_path))

    # Load settings
    settings = load_settings()
    if settings:
        background_color = settings["background_color"]
        font_size = settings["font_size"]
        button_color = settings["button_color"]
    else:
        background_color = "#FFFFFF"  # Default background color
        font_size = 16  # Default font size
        button_color = "#000000"  # Default button color

    # Main layout
    layout = QVBoxLayout()

    # Title
    label = QLabel("Orange!")
    label.setAlignment(Qt.AlignCenter)
    layout.addWidget(label)

    # Background image path
    is_dev = os.environ.get("DEV_ENV", "false").lower() == "true"

    background_images_path = os.path.join(
        os.path.dirname(__file__),
        ".." if is_dev else "",
        "assets",
        "images",
        "background",
    )
    change_background(label, background_images_path)

    # Apply the loaded settings to the UI elements
    window.setStyleSheet(f"background-color: {background_color};")
    label.setStyleSheet(f"font-size: {font_size}px;")

    # Layout for buttons (horizontal)
    button_layout = QHBoxLayout()

    # Assuming buttons should also have color adjustments
    for button in button_layout.findChildren(QPushButton):
        button.setStyleSheet(f"background-color: {button_color};")

    # Button to change the background
    button = QPushButton("Change Background")
    button.clicked.connect(lambda: change_background(label, background_images_path))
    button_layout.addWidget(button)

    # Button to clear cache
    button1 = QPushButton("Clear Cache")
    button1.clicked.connect(lambda: clean())
    button_layout.addWidget(button1)

    # Reload button
    reload_button = QPushButton("Reload")
    button_layout.addWidget(reload_button)

    # Layout settings button
    config_button = QPushButton("Layout Settings")
    config_button.clicked.connect(lambda: show_settings(window, label, button_layout))
    button_layout.addWidget(config_button)

    # Adding the button layout to the main layout
    layout.addLayout(button_layout)

    # Setting the final layout in the window
    window.setLayout(layout)
    window.resize(800, 600)
    window.show()

    # Setting up the reload signal
    reload_signal = setup_reload_signal()
    reload_signal.reload_signal.connect(reload_signal.reload_app)

    # Observer for changes
    event_handler = ReloadHandler(reload_signal)
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(__file__), recursive=True)
    observer.start()

    try:
        app.exec()
    finally:
        observer.stop()
        observer.join()


# Function to open the settings window
def show_settings(window, label, button_layout):
    config_window = LayoutConfigWindow(window, label, button_layout)
    if config_window.exec() == QDialog.Accepted:
        background_color, font_size, button_color = config_window.get_values()
        change_theme(
            window, label, button_layout, background_color, font_size, button_color
        )
        save_settings(background_color, font_size, button_color)
        logger.debug(f"Settings saved: background_color={background_color}, font_size={font_size}, button_color={button_color}")
    else:
        logger.debug("Settings window closed without saving.")


if __name__ == "__main__":
    logger.debug("Application started")
    main()

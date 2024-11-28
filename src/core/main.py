import os
import json
import logging
from PySide6.QtCore import Qt, QTimer
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
    QSpinBox,
    QCheckBox
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


# Main application class
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Orange")
        icon_path = os.path.join(
            os.path.dirname(__file__), "..", "assets", "images", "icons", "orange.png"
        )
        self.setWindowIcon(QIcon(icon_path))

        # Load settings
        settings = load_settings()
        if settings:
            self.background_color = settings.get('background_color', '#FFFFFF')
            self.font_size = settings.get('font_size', 16)
            self.button_color = settings.get('button_color', '#000000')
        else:
            self.background_color = "#FFFFFF"  # Default background color
            self.font_size = 16  # Default font size
            self.button_color = "#000000"  # Default button color

        # Main layout
        self.layout = QVBoxLayout()

        # Title
        self.label = QLabel("Orange!")
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)

        # Background image path
        background_images_path = os.path.join(
            os.path.dirname(__file__), "..", "assets", "images", "background"
        )
        change_background(self.label, background_images_path)

        # Apply the loaded settings to the UI elements
        self.setStyleSheet(f"background-color: {self.background_color};")
        self.label.setStyleSheet(f"QLabel {{ font-size: {self.font_size}px; }}")

        # Layout for buttons (horizontal)
        self.button_layout = QHBoxLayout()

        # Button to change the background
        button = QPushButton("Change Background")
        button.setStyleSheet(f"background-color: {self.button_color}; color: #FFFFFF;")
        button.clicked.connect(lambda: change_background(self.label, background_images_path))
        self.button_layout.addWidget(button)

        # Set up timer for cache clearing
        self.timer = QTimer(self)
        self.timer.setInterval(1000)  # Default to 1 second (adjustable below)
        self.timer.timeout.connect(lambda: clean())  # Calls clean() function every interval

        # Spinbox to set interval for cache cleaning
        self.interval_spinbox = QSpinBox(self)
        self.interval_spinbox.setRange(1, 3600)  # Set range (seconds)
        self.interval_spinbox.setValue(60)  # Default 60 seconds
        self.button_layout.addWidget(self.interval_spinbox)

        # Checkbox to enable/disable infinite cleaning
        self.infinite_checkbox = QCheckBox("Infinite Loop (clear cache repeatedly)", self)
        self.button_layout.addWidget(self.infinite_checkbox)

        # Start timer button
        start_timer_button = QPushButton("Start Cache Timer", self)
        start_timer_button.setStyleSheet(f"background-color: {self.button_color}; color: #FFFFFF;")
        start_timer_button.clicked.connect(self.start_timer)
        self.button_layout.addWidget(start_timer_button)

        # Stop timer button
        stop_timer_button = QPushButton("Stop Cache Timer", self)
        stop_timer_button.setStyleSheet(f"background-color: {self.button_color}; color: #FFFFFF;")
        stop_timer_button.clicked.connect(self.stop_timer)
        self.button_layout.addWidget(stop_timer_button)

        # Reload button
        reload_button = QPushButton("Reload", self)
        reload_button.setStyleSheet(f"background-color: {self.button_color}; color: #FFFFFF;")
        self.button_layout.addWidget(reload_button)

        # Layout settings button
        config_button = QPushButton("Layout Settings", self)
        config_button.setStyleSheet(f"background-color: {self.button_color}; color: #FFFFFF;")
        config_button.clicked.connect(lambda: self.show_settings())
        self.button_layout.addWidget(config_button)

        # Adding the button layout to the main layout
        self.layout.addLayout(self.button_layout)

        # Setting the final layout in the window
        self.setLayout(self.layout)
        self.resize(800, 600)

    # Start the timer
    def start_timer(self):
        interval = self.interval_spinbox.value() * 1000  # Convert seconds to milliseconds
        print(f"Starting timer with interval: {interval} ms")
        self.timer.setInterval(interval)  # Set the new interval
        self.timer.start()  # Start the timer
        if not self.infinite_checkbox.isChecked():
            print("One-time cleaning will be triggered after the interval.")
            QTimer.singleShot(interval, self.stop_timer)  # Stop after one cycle if not infinite

    def stop_timer(self):
        print("Stopping timer.")
        self.timer.stop()  # Stop the timer

    # Function to open the settings window
    def show_settings(self):
        config_window = LayoutConfigWindow(self, self.label, self.button_layout)
        if config_window.exec() == QDialog.Accepted:
            background_color, font_size, button_color = config_window.get_values()
            change_theme(self, self.label, self.button_layout, background_color, font_size, button_color)
            save_settings(background_color, font_size, button_color)


def main():
    app = QApplication([])

    window = MainWindow()
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


if __name__ == "__main__":
    logger.debug("Application started")
    main()

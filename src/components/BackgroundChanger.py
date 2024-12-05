from PySide6.QtWidgets import QPushButton, QVBoxLayout, QLabel, QWidget


class BackgroundChanger(QWidget):
    def __init__(
        self,
        parent=None,
        label=None,
        change_background_func=None,
        background_images_path=None,
        button_color="#000000",
        background_color="#FFFFFF",
        font_size=12,
    ):
        super().__init__(parent)
        self.label = label
        self.change_background_func = change_background_func
        self.background_images_path = background_images_path
        self.button_color = button_color
        self.background_color = background_color
        self.font_size = font_size

        # Apply the loaded settings to the UI elements
        self.setStyleSheet(f"background-color: {self.background_color};")
        self.label.setStyleSheet(f"QLabel {{ font-size: {self.font_size}px; }}")

        # Layout to contain the button
        self.button_layout = QVBoxLayout(self)

        # Button to change the background
        button = QPushButton("Change Background")
        button.setStyleSheet(f"background-color: {self.button_color}; color: #FFFFFF;")
        button.clicked.connect(
            lambda: self.change_background_func(self.label, self.background_images_path)
        )
        self.button_layout.addWidget(button)

        self.setLayout(self.button_layout)  # Set the layout to the QWidget

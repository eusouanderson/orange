import os
from PySide6.QtWidgets import QPushButton
    
# Function to change the app theme in real time
def change_theme(window, label, button_layout, background_color, font_size, button_color):
    # Changing the window background color
    window.setStyleSheet(f"background-color: {background_color};")

    # Changing the font size of the label
    label.setStyleSheet(f"font-size: {font_size}px;")

    # Changing the background color of the buttons
    for button in button_layout.children():
        if isinstance(button, QPushButton):
            button.setStyleSheet(f"font-size: {font_size}px; background-color: {button_color};")

    # Updating the application styles with the passed parameters
    window.update()
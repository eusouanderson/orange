import os
import random
from PySide6.QtWidgets import QColorDialog

# Function to choose the background color
def choose_background_color(background_input):
    color = QColorDialog.getColor()
    if color.isValid():
        background_input.setText(color.name())  # Set the hex color code of the selected color

# Function to choose the button color
def choose_button_color(button_color_input):
    color = QColorDialog.getColor()
    if color.isValid():
        button_color_input.setText(color.name())  # Set the hex color code of the selected color

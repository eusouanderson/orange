import os
import random
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

def change_background(label, background_images_path):
    """Alterar o fundo da janela com uma imagem aleatória"""
    images = os.listdir(background_images_path)
    selected_image = random.choice(images)
    
    # Cria o pixmap da imagem selecionada
    pixmap = QPixmap(os.path.join(background_images_path, selected_image))
    
    # Ajusta o tamanho da imagem de acordo com o label e aplica o fundo
    label.setPixmap(
        pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
    )
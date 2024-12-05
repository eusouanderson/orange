import os
import random
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


def change_background(label, background_images_path):
    """Alterar o fundo da janela com uma imagem aleatória"""
    try:
        # Verifique se o diretório existe
        if not os.path.isdir(background_images_path):
            print(
                f"Erro: O caminho '{background_images_path}' não é um diretório válido."
            )
            return

        # Lista as imagens no diretório
        images = os.listdir(background_images_path)

        # Filtra apenas arquivos de imagem (opcional)
        images = [
            img
            for img in images
            if img.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif"))
        ]

        if not images:
            print(
                f"Erro: Nenhuma imagem encontrada no diretório '{background_images_path}'."
            )
            return

        # Seleciona uma imagem aleatória
        selected_image = random.choice(images)

        # Cria o pixmap da imagem selecionada
        pixmap = QPixmap(os.path.join(background_images_path, selected_image))

        # Ajusta o tamanho da imagem de acordo com o label e aplica o fundo
        label.setPixmap(
            pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
    except Exception as e:
        print(f"Erro ao tentar mudar o fundo: {e}")

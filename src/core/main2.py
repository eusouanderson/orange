import imageio.v3 as iio
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel, QApplication
import sys
import numpy as np

def load_dds_image(image_path):
    try:
        img = iio.imread(image_path)
        print("Imagem carregada com shape:", img.shape)

        if img.ndim == 2:
            # Tons de cinza
            img = np.stack((img,) * 3, axis=-1)

        height, width, channels = img.shape

        if channels == 4:
            fmt = QImage.Format_RGBA8888
        elif channels == 3:
            fmt = QImage.Format_RGB888
        else:
            print("Formato de cor não suportado")
            return None

        qimg = QImage(img.data, width, height, width * channels, fmt)
        return QPixmap.fromImage(qimg)
    except Exception as e:
        print("Erro ao carregar DDS:", e)
        return None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    label = QLabel()

    path = r"D:\Farming Simulator 25\data\vehicles\abi\waterTrailer550\waterTrailer550_vmask.dds"

    pixmap = load_dds_image(path)

    if pixmap and not pixmap.isNull():
        label.setPixmap(pixmap.scaledToWidth(300))
        label.show()
    else:
        print("Pixmap é nulo")

    sys.exit(app.exec())

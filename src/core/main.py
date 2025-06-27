import logging
import sys
from logging.handlers import RotatingFileHandler

from PyQt6.QtWidgets import (
    QApplication,
)

from core.whatsapp_gui import WhatsAppSenderGUI

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            'whatsapp_sender.log', maxBytes=1024 * 1024, backupCount=3
        ),
        logging.StreamHandler(),
    ],
)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    window = WhatsAppSenderGUI()
    window.show()
    sys.exit(app.exec())

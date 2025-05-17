import sys
import os
import xml.etree.ElementTree as ET

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QPushButton, QLineEdit, QTextEdit, QFileDialog,
    QMessageBox, QLabel, QScrollArea, QHBoxLayout
)
from PySide6.QtGui import QIcon, QFont, QFontDatabase, QPixmap
from PySide6.QtCore import Qt
import imageio.v3 as iio
from PySide6.QtGui import QImage

class VehicleFilesViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FS25 Vehicles Files & Materials Viewer")
        self.setGeometry(100, 100, 1000, 700)

        self.setup_font_icon()

        # Input e botões
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Cole o caminho da pasta 'vehicles' aqui...")

        self.browse_button = QPushButton("Procurar Pasta")
        self.browse_button.clicked.connect(self.browse_folder)

        self.load_button = QPushButton("Carregar Arquivos .i3d")
        self.load_button.clicked.connect(self.load_i3d_files)

        #Barra de Busca para ID ou texto
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por ID ou texto...")
        self.search_input.returnPressed.connect(self.handle_search_input)

        # Área de texto para mostrar info (Files + Materials)
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setMinimumWidth(500)


        # Barra de Busca para ID da imagem
        self.search_image_input = QLineEdit()
        self.search_image_input.setPlaceholderText("Buscar por ID da imagem...")
        self.search_image_input.returnPressed.connect(self.handle_search_image_input)
        self.search_image_input.setMinimumWidth(200)

        # Área para mostrar imagens
        self.images_area = QWidget()
        self.images_layout = QHBoxLayout()
        self.images_area.setLayout(self.images_layout)

        # Scroll area para as imagens
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.images_area)
        self.scroll_area.setMinimumHeight(150)

        # Layout geral
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.path_input)
        input_layout.addWidget(self.browse_button)
        input_layout.addWidget(self.load_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.search_input)
        main_layout.addWidget(self.search_image_input)
        main_layout.addWidget(self.output)
        main_layout.addWidget(self.scroll_area)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)


    def handle_search_input(self):
        text = self.search_input.text().strip()
        self.search_output_text(text)

    def handle_search_image_input(self):
        text = self.search_image_input.text().strip()
        self.search_output_text(text)


    def search_output_text(self, text):
        if not text:
            return

        cursor = self.output.textCursor()
        document = self.output.document()

        found = document.find(text, cursor)

        if found.isNull():
            # Se não encontrar mais ocorrências, volta ao início
            cursor.setPosition(0)
            found = document.find(text, cursor)
            if found.isNull():
                QMessageBox.information(self, "Busca", f"Nenhum resultado encontrado para: {text}")
                return

        self.output.setTextCursor(found)
        self.output.ensureCursorVisible()


    def setup_font_icon(self):
        path_font = os.path.abspath("src/assets/font/JetBrainsMono.ttf")
        path_icon = os.path.abspath("src/assets/images/icons/orange.ico")
        if os.path.exists(path_font):
            font_id = QFontDatabase.addApplicationFont(path_font)
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            font = QFont(font_family, 10)
            self.setFont(font)
        if os.path.exists(path_icon):
            self.setWindowIcon(QIcon(path_icon))

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecionar pasta vehicles")
        if folder:
            self.path_input.setText(folder)

    def load_i3d_files(self):
        self.file_id_to_type = {}
        base_path = self.path_input.text()

        if not os.path.isdir(base_path):
            QMessageBox.critical(self, "Erro", "Pasta inválida!")
            return

        self.output.clear()

        # Remove imagens antigas do layout
        for i in reversed(range(self.images_layout.count())):
            widget = self.images_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # 🧠 Detecta a pasta base do "data"
        parts = os.path.normpath(base_path).split(os.sep)
        if "data" in parts:
            data_index = parts.index("data")
            data_base_path = os.path.join(*parts[:data_index + 1])
        else:

          data_base_path = base_path

          QMessageBox.warning(self, "Aviso", "Pasta 'data' não encontrada, usando pasta base.")

        result = []

        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file.endswith(".i3d"):
                    full_path = os.path.join(root, file)
                    result.append(f"### Arquivo: {full_path}\n")

                    try:
                        tree = ET.parse(full_path)
                        root_xml = tree.getroot()

                        # --- Bloco <Files> ---
                        files_tag = root_xml.find("Files")
                        if files_tag is not None:
                            result.append(" <Files>:")
                            for file_tag in files_tag.findall("File"):
                                file_id = file_tag.attrib.get("fileId", "")
                                filename = file_tag.attrib.get("filename", "")
                                result.append(f"    [ID {file_id}] {filename}")

                                # 🔍 Resolução do caminho da imagem
                                if filename.startswith("$data/"):
                                    relative_path = filename.replace("$data/", "")
                                    image_path = os.path.join(data_base_path, relative_path)
                                elif os.path.isabs(filename):
                                    image_path = filename
                                else:
                                    image_path = os.path.join(base_path, filename)

                                # Substitui .png por .dds, se necessário
                                if image_path.endswith(".png"):
                                    image_path = image_path.replace(".png", ".dds")

                                image_path = os.path.normpath(image_path)
                                print("Caminho resolvido:", image_path)
                                self.add_image_to_layout(image_path, file_id)
                        else:
                            result.append(" <Files> não encontrado.")

                        # --- Bloco <Materials> ---
                        materials_tag = root_xml.find("Materials")
                        if materials_tag is not None:
                            result.append("\n<Materials>")
                            for material in materials_tag:
                                xml_str = ET.tostring(material, encoding="unicode")
                                result.append(xml_str.strip())

                                for texture_tag in material:
                                    tag_name = texture_tag.tag
                                    file_id = texture_tag.attrib.get("fileId")
                                    if file_id:
                                        self.file_id_to_type[file_id] = tag_name
                            result.append("</Materials>")
                        else:
                            result.append(" <Materials> não encontrado.")

                    except ET.ParseError:
                        result.append("  Erro ao analisar XML.")

                    result.append("")

        self.output.setPlainText("\n".join(result))




    def add_image_to_layout(self, image_path, file_id):
        image_container = QWidget()
        image_layout = QVBoxLayout()
        image_container.setLayout(image_layout)

        # Label do ID
        id_label = QLabel(f"ID: {file_id}")
        id_label.setAlignment(Qt.AlignCenter)
        id_label.setStyleSheet("font-weight: bold; color: #FFA500;")  # opcional para estilização

        # Imagem
        label = QLabel()
        if image_path.lower().endswith(".dds"):
            try:
                img = iio.imread(image_path)
                height, width, channels = img.shape
                fmt = QImage.Format_RGBA8888 if channels == 4 else QImage.Format_RGB888
                if channels != 3 and channels != 4:
                    img = img[:, :, :3]
                    fmt = QImage.Format_RGB888

                qimg = QImage(img.data, width, height, width * img.shape[2], fmt)
                pixmap = QPixmap.fromImage(qimg)
            except Exception as e:
                print(f"Erro ao abrir DDS {image_path}: {e}")
                return
        else:
            pixmap = QPixmap(image_path)

        if pixmap.isNull():
            return

        pixmap = pixmap.scaledToWidth(100, Qt.SmoothTransformation)
        label.setPixmap(pixmap)
        label.setToolTip(image_path)

        # Tipo abaixo da imagem
        image_type = self.file_id_to_type.get(file_id, "Desconhecido")
        type_label = QLabel(f"Tipo: {image_type}")
        type_label.setAlignment(Qt.AlignCenter)

        # Adiciona ao layout
        image_layout.addWidget(id_label)
        image_layout.addWidget(label)
        image_layout.addWidget(type_label)
        self.images_layout.addWidget(image_container)

    def handle_search_image_input(self):
      search_id = self.search_image_input.text().strip()

      for i in range(self.images_layout.count()):
          widget = self.images_layout.itemAt(i).widget()
          if widget:
              id_label = widget.layout().itemAt(0).widget()
              if not search_id or search_id in id_label.text():
                  widget.show()
              else:
                  widget.hide()




if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = VehicleFilesViewer()
    viewer.show()
    sys.exit(app.exec())

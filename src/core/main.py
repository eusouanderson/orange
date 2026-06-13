import os
import shutil
import sys

from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QImage, QPixmap, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QVBoxLayout,
    QWidget,
)


IMAGE_EXTENSIONS = {".dds", ".png", ".jpg", ".jpeg", ".bmp", ".tga", ".gif", ".tiff"}


def pil_to_pixmap(pil_img: Image.Image) -> QPixmap:
    if pil_img.mode == "RGBA":
        qimg = QImage(
            pil_img.tobytes(),
            pil_img.width,
            pil_img.height,
            QImage.Format.Format_RGBA8888,
        )
    else:
        pil_img = pil_img.convert("RGB")
        qimg = QImage(
            pil_img.tobytes(),
            pil_img.width,
            pil_img.height,
            QImage.Format.Format_RGB888,
        )
    return QPixmap.fromImage(qimg)


class TextureViewer(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Mod Texture Viewer")
        self.resize(1400, 900)

        self.mod_path: str | None = None
        self.texture_files: list[str] = []
        self.current_texture: str | None = None

        self._build_ui()
        self._aplicar_tema()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout()
        central.setLayout(root)

        toolbar = QHBoxLayout()
        btn_open = QPushButton("Abrir Mod")
        btn_open.clicked.connect(self._abrir_mod)
        btn_open.setIcon(QIcon())
        toolbar.addWidget(btn_open)

        btn_open_dir = QPushButton("Abrir Pasta")
        btn_open_dir.clicked.connect(self._abrir_pasta)
        toolbar.addWidget(btn_open_dir)

        self.label_mod_info = QLabel("Nenhum mod carregado")
        toolbar.addWidget(self.label_mod_info)
        toolbar.addStretch()
        root.addLayout(toolbar)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.texture_list = QListWidget()
        self.texture_list.setIconSize(QSize(64, 64))
        self.texture_list.setSpacing(2)
        self.texture_list.currentRowChanged.connect(self._on_texture_selected)
        left_layout.addWidget(QLabel("Texturas"))
        left_layout.addWidget(self.texture_list)
        left_panel.setLayout(left_layout)

        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.preview_label = QLabel("Selecione uma textura")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(400, 300)
        self.preview_label.setStyleSheet("background: #1b1f2a; border: 1px solid #31384a; border-radius: 4px;")

        scroll = QScrollArea()
        scroll.setWidget(self.preview_label)
        scroll.setWidgetResizable(True)
        scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(QLabel("Preview"))
        right_layout.addWidget(scroll, 1)

        self.info_label = QLabel("")
        self.info_label.setWordWrap(True)
        right_layout.addWidget(self.info_label)

        btn_swap = QPushButton("Trocar Textura...")
        btn_swap.clicked.connect(self._trocar_textura)
        right_layout.addWidget(btn_swap)

        right_panel.setLayout(right_layout)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([350, 1050])
        root.addWidget(splitter, 1)

    def _abrir_mod(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Mod (zip ou pasta)", "",
            "Mod Files (*.zip);;All Files (*)"
        )
        if not path:
            return
        self._carregar_mod(path)

    def _abrir_pasta(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Selecionar Pasta do Mod")
        if not path:
            return
        self._carregar_mod(path)

    def _carregar_mod(self, path: str) -> None:
        self.mod_path = path
        self.texture_files.clear()
        self.texture_list.clear()
        self.preview_label.clear()
        self.preview_label.setText("Carregando...")
        self.info_label.setText("")

        images = []
        if os.path.isfile(path) and path.endswith(".zip"):
            import zipfile
            with zipfile.ZipFile(path) as zf:
                for name in zf.namelist():
                    ext = os.path.splitext(name)[1].lower()
                    if ext in IMAGE_EXTENSIONS:
                        images.append(name)
            self.label_mod_info.setText(f"ZIP: {os.path.basename(path)} ({len(images)} imagens)")
        elif os.path.isdir(path):
            for root_dir, _, files in os.walk(path):
                for f in files:
                    ext = os.path.splitext(f)[1].lower()
                    if ext in IMAGE_EXTENSIONS:
                        rel = os.path.relpath(os.path.join(root_dir, f), path)
                        images.append(rel)
            self.label_mod_info.setText(f"Pasta: {os.path.basename(path)} ({len(images)} imagens)")
        else:
            QMessageBox.warning(self, "Erro", "Selecione uma pasta de mod ou arquivo .zip")
            return

        self.texture_files = sorted(images)

        if not self.texture_files:
            self.preview_label.setText("Nenhuma imagem encontrada")
            self.label_mod_info.setText(f"{os.path.basename(path)} (0 imagens)")
            return

        for img_rel in self.texture_files:
            item = QListWidgetItem(img_rel)
            thumb = self._load_thumbnail(path, img_rel)
            if thumb:
                item.setIcon(QIcon(thumb))
            self.texture_list.addItem(item)

        self.texture_list.setCurrentRow(0)

    def _load_thumbnail(self, mod_path: str, rel_path: str, size: int = 64) -> QPixmap | None:
        try:
            if os.path.isfile(mod_path) and mod_path.endswith(".zip"):
                import zipfile
                import io
                with zipfile.ZipFile(mod_path) as zf:
                    data = zf.read(rel_path)
                    pil_img = Image.open(io.BytesIO(data))
            else:
                full = os.path.join(mod_path, rel_path)
                pil_img = Image.open(full)
            pil_img.thumbnail((size, size))
            return pil_to_pixmap(pil_img)
        except Exception:
            return None

    def _load_full_image(self, mod_path: str, rel_path: str) -> Image.Image | None:
        try:
            if os.path.isfile(mod_path) and mod_path.endswith(".zip"):
                import zipfile
                import io
                with zipfile.ZipFile(mod_path) as zf:
                    data = zf.read(rel_path)
                    return Image.open(io.BytesIO(data))
            else:
                full = os.path.join(mod_path, rel_path)
                return Image.open(full)
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Não foi possível carregar:\n{rel_path}\n{e}")
            return None

    def _on_texture_selected(self, row: int) -> None:
        if row < 0 or row >= len(self.texture_files):
            return
        rel = self.texture_files[row]
        self.current_texture = rel

        pil_img = self._load_full_image(self.mod_path, rel)
        if pil_img is None:
            return

        pixmap = pil_to_pixmap(pil_img)
        size_str = f"{pil_img.width} x {pil_img.height} px"

        fmt = pil_img.format or "DDS" if rel.lower().endswith(".dds") else pil_img.format
        fsize = ""
        if os.path.isfile(self.mod_path) and self.mod_path.endswith(".zip"):
            import zipfile
            with zipfile.ZipFile(self.mod_path) as zf:
                info = zf.getinfo(rel)
                fsize = f", {info.file_size / 1024:.1f} KB"
        else:
            full = os.path.join(self.mod_path, rel)
            fsize = f", {os.path.getsize(full) / 1024:.1f} KB"

        self.info_label.setText(
            f"📄 {os.path.basename(rel)}\n"
            f"📐 {size_str}\n"
            f"💾 Formato: {fmt}{fsize}\n"
            f"📁 {os.path.dirname(rel)}"
        )

        max_w = self.preview_label.width() - 20
        max_h = self.preview_label.height() - 20
        if pil_img.width > max_w or pil_img.height > max_h:
            pil_img.thumbnail((max_w, max_h))
            pixmap = pil_to_pixmap(pil_img)

        self.preview_label.setPixmap(pixmap)

    def _trocar_textura(self) -> None:
        if not self.current_texture:
            QMessageBox.information(self, "Aviso", "Selecione uma textura primeiro")
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar nova textura", "",
            "Imagens (*.png *.jpg *.jpeg *.bmp *.tga *.dds *.gif);;All Files (*)"
        )
        if not file_path:
            return

        if isinstance(self.mod_path, str) and os.path.isfile(self.mod_path) and self.mod_path.endswith(".zip"):
            QMessageBox.information(
                self, "Aviso",
                "Para mods em ZIP, extraia o mod primeiro e use a opção 'Abrir Pasta'."
            )
            return

        try:
            dst = os.path.join(self.mod_path, self.current_texture)
            backup = dst + ".bak"
            if os.path.exists(backup):
                os.remove(backup)
            os.rename(dst, backup)
            shutil.copy2(file_path, dst)

            QMessageBox.information(
                self, "Sucesso",
                f"Textura trocada!\nOriginal renomeada para: {os.path.basename(backup)}"
            )

            row = self.texture_list.currentRow()
            thumb = self._load_thumbnail(self.mod_path, self.current_texture)
            if thumb:
                item = self.texture_list.item(row)
                if item:
                    item.setIcon(QIcon(thumb))
            self._on_texture_selected(row)

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao trocar textura:\n{e}")

    def _aplicar_tema(self) -> None:
        stylesheet = """
        QWidget { background: #0f1117; color: #e6e8f0; font-size: 13px; }
        QGroupBox { border: 1px solid #31384a; border-radius: 4px; margin-top: 10px; padding-top: 10px; }
        QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px; }
        QPushButton { background: #238636; color: #fff; border: 1px solid #2ea043; padding: 6px 12px; border-radius: 4px; font-weight: bold; }
        QPushButton:hover { background: #2ea043; }
        QPushButton:pressed { background: #1a6e1a; }
        QListWidget { background: #11141d; border: 1px solid #31384a; border-radius: 4px; padding: 4px; }
        QListWidget::item { padding: 4px; border-radius: 2px; }
        QListWidget::item:selected { background: #238636; }
        QListWidget::item:hover { background: #1b1f2a; }
        QScrollArea { border: none; }
        QLabel { color: #e6e8f0; }
        QSplitter::handle { background: #31384a; width: 2px; }
        """
        self.setStyleSheet(stylesheet)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TextureViewer()
    window.show()
    sys.exit(app.exec())

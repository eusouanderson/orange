import os
import re
import shutil
import sys

try:
    from icon_processor import run_batch
except ImportError:
    try:
        from src.core.icon_processor import run_batch
    except ImportError:
        from .icon_processor import run_batch

try:
    from src.core.calc3d import Calc3D
except ImportError:
    try:
        from calc3d import Calc3D
    except ImportError:
        Calc3D = None  # type: ignore

__all__ = ['Calc3D', 'TextureViewer', 'normalizar_path', 'run_batch']

from PIL import Image
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon, QImage, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
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

IMAGE_EXTENSIONS = {
    '.dds',
    '.png',
    '.jpg',
    '.jpeg',
    '.bmp',
    '.tga',
    '.gif',
    '.tiff',
}


def pil_to_pixmap(pil_img: Image.Image) -> QPixmap:
    if pil_img.mode == 'RGBA':
        qimg = QImage(
            pil_img.tobytes(),
            pil_img.width,
            pil_img.height,
            QImage.Format.Format_RGBA8888,
        )
    else:
        pil_img = pil_img.convert('RGB')
        qimg = QImage(
            pil_img.tobytes(),
            pil_img.width,
            pil_img.height,
            QImage.Format.Format_RGB888,
        )
    return QPixmap.fromImage(qimg)


def normalizar_path(path: str) -> str:
    if re.match(r'^[A-Za-z]:\\', path):
        drive = path[0].lower()
        rest = path[2:].replace('\\', '/')
        return f'/mnt/{drive}{rest}'
    if re.match(r'^[A-Za-z]:/', path):
        drive = path[0].lower()
        rest = path[2:]
        return f'/mnt/{drive}{rest}'
    return path


def listar_drives_wsl() -> list[str]:
    drives = []
    if os.path.isdir('/mnt'):
        for d in sorted(os.listdir('/mnt')):
            if len(d) == 1 and d.isalpha() and os.path.isdir(f'/mnt/{d}'):
                drives.append(f'/mnt/{d}')
    return drives


def fs25_mods_paths_wsl() -> list[str]:
    candidates = []
    for drive in listar_drives_wsl():
        for user_dir in ['Users', 'Usuários']:
            base = os.path.join(drive, user_dir)
            if not os.path.isdir(base):
                continue
            for username in os.listdir(base):
                doc = os.path.join(
                    drive,
                    user_dir,
                    username,
                    'Documents',
                    'My Games',
                    'FarmingSimulator2025',
                    'mods',
                )
                alt_doc = os.path.join(
                    drive,
                    user_dir,
                    username,
                    'Documentos',
                    'My Games',
                    'FarmingSimulator2025',
                    'mods',
                )
                for p in [doc, alt_doc]:
                    if os.path.isdir(p):
                        candidates.append(p)
    return candidates


class TextureViewer(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle('Mod Texture Viewer')
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
        btn_open = QPushButton('Abrir Mod ZIP')
        btn_open.clicked.connect(self._abrir_mod)
        toolbar.addWidget(btn_open)

        btn_open_dir = QPushButton('Abrir Pasta')
        btn_open_dir.clicked.connect(self._abrir_pasta)
        toolbar.addWidget(btn_open_dir)

        btn_export = QPushButton('Exportar PNG')
        btn_export.clicked.connect(self._exportar_textura)
        toolbar.addWidget(btn_export)

        toolbar.addStretch()
        root.addLayout(toolbar)

        wsl_bar = QHBoxLayout()
        self.drive_combo = QComboBox()
        self.drive_combo.setMinimumWidth(100)
        self.drive_combo.setPlaceholderText('Drive Windows...')
        wsl_bar.addWidget(QLabel('WSL:'))
        wsl_bar.addWidget(self.drive_combo)
        btn_go_drive = QPushButton('Ir')
        btn_go_drive.clicked.connect(self._ir_para_drive)
        wsl_bar.addWidget(btn_go_drive)

        fs25_dirs = fs25_mods_paths_wsl()
        if fs25_dirs:
            self.fs25_combo = QComboBox()
            self.fs25_combo.setMinimumWidth(300)
            self.fs25_combo.setPlaceholderText('FS25 mods...')
            for d in fs25_dirs:
                self.fs25_combo.addItem(d)
            wsl_bar.addWidget(QLabel('FS25:'))
            wsl_bar.addWidget(self.fs25_combo)
            btn_go_fs25 = QPushButton('Abrir Mods FS25')
            btn_go_fs25.clicked.connect(self._ir_para_fs25)
            wsl_bar.addWidget(btn_go_fs25)

        wsl_bar.addStretch()
        root.addLayout(wsl_bar)

        path_bar = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText(
            'Cole um caminho (ex: G:\\Users\\... ou /mnt/g/Users/...) e pressione Enter'
        )
        self.path_input.returnPressed.connect(self._ir_para_path)
        path_bar.addWidget(self.path_input)
        btn_go_path = QPushButton('Ir')
        btn_go_path.clicked.connect(self._ir_para_path)
        path_bar.addWidget(btn_go_path)
        root.addLayout(path_bar)

        self.label_mod_info = QLabel('Nenhum mod carregado')
        root.addWidget(self.label_mod_info)

        self._popular_drives()

        splitter = QSplitter(Qt.Orientation.Horizontal)

        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Buscar textura...')
        self.search_input.textChanged.connect(self._filtrar_texturas)
        left_layout.addWidget(self.search_input)

        self.texture_list = QListWidget()
        self.texture_list.setIconSize(QSize(64, 64))
        self.texture_list.setSpacing(2)
        self.texture_list.currentRowChanged.connect(self._on_texture_selected)
        left_layout.addWidget(QLabel('Texturas'))
        left_layout.addWidget(self.texture_list)
        left_panel.setLayout(left_layout)

        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.preview_label = QLabel('Selecione uma textura')
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(400, 300)
        self.preview_label.setStyleSheet(
            'background: #1b1f2a; border: 1px solid #31384a; border-radius: 4px;'
        )

        scroll = QScrollArea()
        scroll.setWidget(self.preview_label)
        scroll.setWidgetResizable(True)
        scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(QLabel('Preview'))
        right_layout.addWidget(scroll, 1)

        self.info_label = QLabel('')
        self.info_label.setWordWrap(True)
        right_layout.addWidget(self.info_label)

        action_row = QHBoxLayout()
        btn_swap = QPushButton('Trocar Textura...')
        btn_swap.clicked.connect(self._trocar_textura)
        action_row.addWidget(btn_swap)
        btn_export = QPushButton('Exportar como PNG')
        btn_export.clicked.connect(self._exportar_textura)
        action_row.addWidget(btn_export)
        right_layout.addLayout(action_row)

        right_panel.setLayout(right_layout)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([350, 1050])
        root.addWidget(splitter, 1)

    def _popular_drives(self) -> None:
        self.drive_combo.clear()
        for d in listar_drives_wsl():
            label = f'{d.upper()} ({d})'
            self.drive_combo.addItem(label, d)
        if self.drive_combo.count() == 0:
            self.drive_combo.addItem('Nenhum drive detectado')

    def _ir_para_drive(self) -> None:
        path = self.drive_combo.currentData()
        if path and os.path.isdir(path):
            self._abrir_pasta_com_path(path)

    def _ir_para_fs25(self) -> None:
        path = self.fs25_combo.currentText()
        if path and os.path.isdir(path):
            self._carregar_mod(path)

    def _ir_para_path(self) -> None:
        raw = self.path_input.text().strip()
        if not raw:
            return
        path = normalizar_path(raw)
        if os.path.isdir(path):
            self._carregar_mod(path)
        elif os.path.isfile(path):
            self._carregar_mod(path)
        else:
            QMessageBox.warning(
                self, 'Erro', f'Caminho não encontrado:\n{path}'
            )

    def _abrir_mod(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            'Selecionar Mod (zip ou pasta)',
            '',
            'Mod Files (*.zip);;All Files (*)',
        )
        if not path:
            return
        self._carregar_mod(path)

    def _abrir_pasta(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self, 'Selecionar Pasta do Mod'
        )
        if not path:
            return
        self._carregar_mod(path)

    def _abrir_pasta_com_path(self, path: str) -> None:
        self._carregar_mod(path)

    def _filtrar_texturas(self, text: str) -> None:
        text = text.lower()
        for i in range(self.texture_list.count()):
            item = self.texture_list.item(i)
            if item:
                item.setHidden(text not in item.text().lower())

    def _carregar_mod(self, path: str) -> None:
        self.mod_path = path
        self.texture_files.clear()
        self.texture_list.clear()
        self.search_input.clear()
        self.preview_label.clear()
        self.preview_label.setText('Carregando...')
        self.info_label.setText('')

        images = []
        if os.path.isfile(path) and path.endswith('.zip'):
            import zipfile

            with zipfile.ZipFile(path) as zf:
                for name in zf.namelist():
                    ext = os.path.splitext(name)[1].lower()
                    if ext in IMAGE_EXTENSIONS:
                        images.append(name)
                img_count = len(images)
            self.label_mod_info.setText(
                f'ZIP: {os.path.basename(path)} ({img_count} imagens)'
            )
        elif os.path.isdir(path):
            for root_dir, _, files in os.walk(path):
                for f in files:
                    ext = os.path.splitext(f)[1].lower()
                    if ext in IMAGE_EXTENSIONS:
                        rel = os.path.relpath(os.path.join(root_dir, f), path)
                        images.append(rel)
            self.label_mod_info.setText(
                f'Pasta: {os.path.basename(path)} ({len(images)} imagens)'
            )
        else:
            QMessageBox.warning(
                self, 'Erro', 'Selecione uma pasta de mod ou arquivo .zip'
            )
            return

        self.texture_files = sorted(images)

        if not self.texture_files:
            self.preview_label.setText('Nenhuma imagem encontrada')
            self.label_mod_info.setText(
                f'{os.path.basename(path)} (0 imagens)'
            )
            return

        for img_rel in self.texture_files:
            item = QListWidgetItem(img_rel)
            thumb = self._load_thumbnail(path, img_rel)
            if thumb:
                item.setIcon(QIcon(thumb))
            self.texture_list.addItem(item)

        self.texture_list.setCurrentRow(0)

    def _load_thumbnail(
        self, mod_path: str, rel_path: str, size: int = 64
    ) -> QPixmap | None:
        try:
            if os.path.isfile(mod_path) and mod_path.endswith('.zip'):
                import io
                import zipfile

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

    def _load_full_image(
        self, mod_path: str, rel_path: str
    ) -> Image.Image | None:
        try:
            if os.path.isfile(mod_path) and mod_path.endswith('.zip'):
                import io
                import zipfile

                with zipfile.ZipFile(mod_path) as zf:
                    data = zf.read(rel_path)
                    return Image.open(io.BytesIO(data))
            else:
                full = os.path.join(mod_path, rel_path)
                return Image.open(full)
        except Exception as e:
            QMessageBox.warning(
                self, 'Erro', f'Não foi possível carregar:\n{rel_path}\n{e}'
            )
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
        size_str = f'{pil_img.width} x {pil_img.height} px'

        fmt = (
            pil_img.format or 'DDS'
            if rel.lower().endswith('.dds')
            else pil_img.format
        )
        fsize = ''
        if os.path.isfile(self.mod_path) and self.mod_path.endswith('.zip'):
            import zipfile

            with zipfile.ZipFile(self.mod_path) as zf:
                info = zf.getinfo(rel)
                fsize = f', {info.file_size / 1024:.1f} KB'
        else:
            full = os.path.join(self.mod_path, rel)
            fsize = f', {os.path.getsize(full) / 1024:.1f} KB'

        self.info_label.setText(
            f'{os.path.basename(rel)}\n'
            f'{size_str}  |  {fmt}{fsize}\n'
            f'{os.path.dirname(rel)}'
        )

        max_w = self.preview_label.width() - 20
        max_h = self.preview_label.height() - 20
        if pil_img.width > max_w or pil_img.height > max_h:
            pil_img.thumbnail((max_w, max_h))
            pixmap = pil_to_pixmap(pil_img)

        self.preview_label.setPixmap(pixmap)

    def _exportar_textura(self) -> None:
        if not self.current_texture:
            QMessageBox.information(
                self, 'Aviso', 'Selecione uma textura primeiro'
            )
            return

        pil_img = self._load_full_image(self.mod_path, self.current_texture)
        if pil_img is None:
            return

        default_name = (
            os.path.splitext(os.path.basename(self.current_texture))[0]
            + '.png'
        )
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            'Salvar como PNG',
            default_name,
            'PNG Image (*.png);;All Files (*)',
        )
        if not save_path:
            return

        try:
            rgb = (
                pil_img.convert('RGB')
                if pil_img.mode not in {'RGB', 'RGBA'}
                else pil_img
            )
            rgb.save(save_path, 'PNG')
            QMessageBox.information(
                self, 'Sucesso', f'Textura exportada:\n{save_path}'
            )
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Falha ao exportar:\n{e}')

    def _trocar_textura(self) -> None:
        if not self.current_texture:
            QMessageBox.information(
                self, 'Aviso', 'Selecione uma textura primeiro'
            )
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Selecionar nova textura',
            '',
            'Imagens (*.png *.jpg *.jpeg *.bmp *.tga *.dds *.gif);;All Files (*)',
        )
        if not file_path:
            return

        if (
            isinstance(self.mod_path, str)
            and os.path.isfile(self.mod_path)
            and self.mod_path.endswith('.zip')
        ):
            QMessageBox.information(
                self,
                'Aviso',
                "Para mods em ZIP, extraia o mod primeiro e use a opção 'Abrir Pasta'.",
            )
            return

        try:
            dst = os.path.join(self.mod_path, self.current_texture)
            backup = dst + '.bak'
            if os.path.exists(backup):
                os.remove(backup)
            os.rename(dst, backup)
            shutil.copy2(file_path, dst)

            QMessageBox.information(
                self,
                'Sucesso',
                f'Textura trocada!\nOriginal renomeada para: {os.path.basename(backup)}',
            )

            row = self.texture_list.currentRow()
            thumb = self._load_thumbnail(self.mod_path, self.current_texture)
            if thumb:
                item = self.texture_list.item(row)
                if item:
                    item.setIcon(QIcon(thumb))
            self._on_texture_selected(row)

        except Exception as e:
            QMessageBox.critical(
                self, 'Erro', f'Falha ao trocar textura:\n{e}'
            )

    def _aplicar_tema(self) -> None:
        stylesheet = """
        QWidget { background: #0f1117; color: #e6e8f0; font-size: 13px; }
        QPushButton { background: #238636; color: #fff; border: 1px solid #2ea043; padding: 6px 12px; border-radius: 4px; font-weight: bold; }
        QPushButton:hover { background: #2ea043; }
        QPushButton:pressed { background: #1a6e1a; }
        QListWidget { background: #11141d; border: 1px solid #31384a; border-radius: 4px; padding: 4px; }
        QListWidget::item { padding: 4px; border-radius: 2px; }
        QListWidget::item:selected { background: #238636; }
        QListWidget::item:hover { background: #1b1f2a; }
        QLineEdit, QComboBox { background: #11141d; border: 1px solid #31384a; padding: 5px 8px; border-radius: 4px; color: #e6e8f0; }
        QComboBox::drop-down { border: none; }
        QComboBox QAbstractItemView { background: #11141d; color: #e6e8f0; selection-background-color: #238636; }
        QScrollArea { border: none; }
        QLabel { color: #e6e8f0; }
        QSplitter::handle { background: #31384a; width: 2px; }
        """
        self.setStyleSheet(stylesheet)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        run_batch(sys.argv[1])
    else:
        app = QApplication(sys.argv)
        window = TextureViewer()
        window.show()
        sys.exit(app.exec())

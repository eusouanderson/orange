from PySide6.QtWidgets import QFileDialog, QMessageBox


class FileOperations:
    @staticmethod
    def open_file(editor):
        file_path, _ = QFileDialog.getOpenFileName(
            None, 'Abrir Arquivo', '', 'Todos os Arquivos (*.*)'
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    editor.setPlainText(content)
            except Exception as e:
                QMessageBox.critical(
                    None, 'Erro', f'Não foi possível abrir o arquivo:\n{e}'
                )

from PySide6.QtWidgets import QPushButton, QHBoxLayout

def create_buttons(editor, file_operations):
    open_button = QPushButton("Abrir")
    open_button.setStyleSheet("background-color: #333333; color: #FFFFFF;")
    open_button.clicked.connect(lambda: file_operations.open_file(editor))

    save_button = QPushButton("Salvar")
    save_button.setStyleSheet("background-color: #333333; color: #FFFFFF;")
    save_button.clicked.connect(lambda: file_operations.save_file(editor))

    new_button = QPushButton("Novo")
    new_button.setStyleSheet("background-color: #333333; color: #FFFFFF;")
    new_button.clicked.connect(editor.clear)

    layout = QHBoxLayout()
    layout.addWidget(open_button)
    layout.addWidget(save_button)
    layout.addWidget(new_button)
    
    return layout

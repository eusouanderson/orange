from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget
from PySide6.QtCore import Qt

class LayoutSettingsDialog(QWidget):
    def __init__(self, parent=None, button_color="#000000", button_layout=None):
        super().__init__(parent)
        
        # Layout para os botões
        self.button_layout = button_layout

        # Armazenar a cor do botão
        self.button_color = button_color
        
        # Botão para alternar o modo de ícones apenas
        toggle_button = QPushButton("Toggle Icons Only", self)
        toggle_button.setStyleSheet(f"background-color: {self.button_color}; color: #FFFFFF;")
        toggle_button.clicked.connect(self.toggle_icon_only_mode)
        self.button_layout.addWidget(toggle_button)

        # Botão para recarregar
        reload_button = QPushButton("Reload", self)
        reload_button.setStyleSheet(f"background-color: {self.button_color}; color: #FFFFFF;")
        reload_button.clicked.connect(self.reload)
        self.button_layout.addWidget(reload_button)

        # Botão para abrir configurações de layout
        config_button = QPushButton("Layout Settings", self)
        config_button.setStyleSheet(f"background-color: {self.button_color}; color: #FFFFFF;")
        config_button.clicked.connect(self.show_settings)
        self.button_layout.addWidget(config_button)

        # Definindo o layout dos botões
        self.setLayout(self.button_layout)
    
    def toggle_icon_only_mode(self):
        # Alterna entre os modos e altera o layout da janela
        self.icon_only_mode = not getattr(self, "icon_only_mode", False)
        
        # Alterar o texto do botão para refletir o novo estado
        sender = self.sender()
        if sender:
            sender.setText("Layout" if self.icon_only_mode else "Toggle Icons Only")
        
        # Alterar o tamanho da janela
        if self.icon_only_mode:
            self.resize(200, 200)  # Tamanho menor predefinido
            logger.debug("Layout mode enabled: Window resized to 200x200.")
        else:
            self.resize(800, 600)  # Tamanho padrão
            logger.debug("Icon-only mode disabled: Window resized to 800x600.")

    def toggle_icon_only_mode(self):
        """Método para alternar entre modo ícones apenas"""
        print("Toggled Icons Only Mode")
        # Implemente a lógica para alternar o modo de ícones aqui

    def reload(self):
        """Método para recarregar as configurações"""
        print("Reloading...")
        # Implemente a lógica de recarregamento aqui

    # Function to open the settings window
    def show_settings(self):
        config_window = LayoutConfigWindow(self, self.label, self.button_layout)
        if config_window.exec() == QDialog.Accepted:
            background_color, font_size, button_color = config_window.get_values()
            change_theme(self, self.label, self.button_layout, background_color, font_size, button_color)
            save_settings(background_color, font_size, button_color)

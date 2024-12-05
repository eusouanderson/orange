from PySide6.QtWidgets import QVBoxLayout, QSpinBox, QPushButton, QCheckBox, QWidget


class CacheTimerControls(QVBoxLayout):
    def __init__(self, parent, timer, clean_function, button_color, button_layout):
        super().__init__()

        self.timer = timer
        self.clean_function = clean_function

        # Layout para os botões
        self.button_layout = button_layout  # Inicializando o button_layout
        self.addLayout(self.button_layout)

        # Spinbox para ajustar o intervalo do timer
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setRange(1, 3600)  # Intervalo em segundos
        self.interval_spinbox.setValue(60)  # Intervalo padrão
        self.addWidget(self.interval_spinbox)

        # Checkbox para definir se o timer é infinito
        self.infinite_checkbox = QCheckBox(
            "Infinite Loop (clear cache repeatedly)", parent
        )  # Passando o 'parent'
        self.button_layout.addWidget(self.infinite_checkbox)

        # Botão para iniciar o timer
        self.start_button = QPushButton("Start Timer")
        self.start_button.setStyleSheet(
            f"background-color: {button_color}; color: #FFFFFF;"
        )
        self.start_button.clicked.connect(self.start_timer)
        self.button_layout.addWidget(self.start_button)

        # Botão para parar o timer
        self.stop_button = QPushButton("Stop Timer")
        self.stop_button.setStyleSheet(
            f"background-color: {button_color}; color: #FFFFFF;"
        )
        self.stop_button.clicked.connect(self.stop_timer)
        self.button_layout.addWidget(self.stop_button)

    def start_timer(self):
        # Intervalo baseado no valor do SpinBox
        interval = (
            self.interval_spinbox.value() * 1000
        )  # Convertendo para milissegundos
        self.timer.setInterval(interval)
        self.timer.timeout.connect(self.clean_function)

        # Se a checkbox de loop infinito estiver marcada, o timer continuará
        if self.infinite_checkbox.isChecked():
            self.timer.timeout.connect(
                self.start_timer
            )  # Reconectar o timeout para loop infinito

        self.timer.start()

    def stop_timer(self):
        self.timer.stop()
        self.timer.timeout.disconnect(
            self.clean_function
        )  # Desconectar a função de limpeza quando o timer for parado

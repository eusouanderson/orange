import os
import re

import pandas as pd
from PyQt6.QtCore import QDateTime, Qt, QTime
from PyQt6.QtGui import QColor, QFont, QTextCursor
from PyQt6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressDialog,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from core.whatsapp_thread import WhatsAppSenderThread

NUMBER_MSG_SENDER = 10
NUMBER_COUNTRY_CODE = 11


class WhatsAppSenderGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('WhatsApp Message Sender - Avançado')
        self.setGeometry(100, 100, 1200, 800)
        self.thread = None
        self.setup_ui()
        self.setup_styles()

    def setup_styles(self):
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 4px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QTextEdit, QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 4px;
            }
            QGroupBox {
                border: 1px solid #ddd;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QTabBar::tab {
                padding: 8px 16px;
            }
            QProgressDialog {
                min-width: 400px;
            }
        """)

    def setup_ui(self):
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)

        # Left side - Controls
        self.controls_container = QWidget()
        self.controls_layout = QVBoxLayout()
        self.controls_container.setLayout(self.controls_layout)
        self.controls_container.setMaximumWidth(400)
        self.main_layout.addWidget(self.controls_container)

        # Right side - Results and Logs
        self.results_container = QTabWidget()
        self.main_layout.addWidget(self.results_container)

        # Setup controls
        self.setup_file_controls()
        self.setup_message_controls()
        self.setup_schedule_controls()
        self.setup_action_buttons()

        # Setup results tabs
        self.setup_results_table()
        self.setup_log_viewer()

    def setup_file_controls(self):
        group = QGroupBox('Arquivo de Contatos')
        layout = QVBoxLayout()

        self.label = QLabel('Selecione um arquivo CSV de clientes.')
        self.label.setWordWrap(True)
        layout.addWidget(self.label)

        self.botao_arquivo = QPushButton('Selecionar Arquivo')
        self.botao_arquivo.clicked.connect(self.selecionar_arquivo)
        layout.addWidget(self.botao_arquivo)

        group.setLayout(layout)
        self.controls_layout.addWidget(group)

    def setup_message_controls(self):
        group = QGroupBox('Mensagem')
        layout = QVBoxLayout()

        self.texto_mensagem = QTextEdit()
        self.texto_mensagem.setPlaceholderText(
            'Escreva aqui a mensagem que deseja enviar via WhatsApp...'
        )
        self.texto_mensagem.setMinimumHeight(150)
        layout.addWidget(self.texto_mensagem)

        group.setLayout(layout)
        self.controls_layout.addWidget(group)

    def setup_schedule_controls(self):
        group = QGroupBox('Configurações de Envio')
        layout = QVBoxLayout()

        # Scheduling options
        self.schedule_layout = QHBoxLayout()
        self.schedule_checkbox = QCheckBox('Agendar envio')
        self.schedule_checkbox.stateChanged.connect(
            self.toggle_schedule_options
        )
        self.schedule_layout.addWidget(self.schedule_checkbox)

        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat('HH:mm')
        self.time_edit.setEnabled(False)
        self.time_edit.setTime(QTime.currentTime().addSecs(300))
        self.schedule_layout.addWidget(self.time_edit)

        layout.addLayout(self.schedule_layout)

        # Delay settings
        delay_layout = QHBoxLayout()
        delay_layout.addWidget(QLabel('Delay entre envios (seg):'))

        self.delay_spinbox = QSpinBox()
        self.delay_spinbox.setRange(5, 300)
        self.delay_spinbox.setValue(30)
        delay_layout.addWidget(self.delay_spinbox)

        layout.addLayout(delay_layout)

        group.setLayout(layout)
        self.controls_layout.addWidget(group)

    def setup_action_buttons(self):
        group = QGroupBox('Ações')
        layout = QVBoxLayout()

        self.botao_formatar = QPushButton('Formatar Telefones')
        self.botao_formatar.clicked.connect(self.formatar_coluna_telefone)
        layout.addWidget(self.botao_formatar)

        self.botao_salvar = QPushButton('Salvar CSV')
        self.botao_salvar.clicked.connect(self.salvar_csv)
        layout.addWidget(self.botao_salvar)

        self.botao_whatsapp = QPushButton('Enviar Mensagens')
        self.botao_whatsapp.clicked.connect(self.enviar_whatsapp)
        self.botao_whatsapp.setStyleSheet('background-color: #2196F3;')
        layout.addWidget(self.botao_whatsapp)

        group.setLayout(layout)
        self.controls_layout.addWidget(group)

        # Add stretch to push everything up
        self.controls_layout.addStretch()

    def setup_results_table(self):
        self.table_tab = QWidget()
        self.table_layout = QVBoxLayout()
        self.table_tab.setLayout(self.table_layout)

        self.table = QTableWidget()
        self.table_layout.addWidget(self.table)

        self.results_container.addTab(self.table_tab, 'Dados')

    def setup_log_viewer(self):
        self.log_tab = QWidget()
        self.log_layout = QVBoxLayout()
        self.log_tab.setLayout(self.log_layout)

        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setFont(QFont('Courier New', NUMBER_MSG_SENDER))

        scroll = QScrollArea()
        scroll.setWidget(self.log_viewer)
        scroll.setWidgetResizable(True)
        self.log_layout.addWidget(scroll)

        self.results_container.addTab(self.log_tab, 'Logs de Envio')

    def toggle_schedule_options(self, state):
        self.time_edit.setEnabled(state == Qt.CheckState.Checked.value)

    def log(self, message, msg_type='info'):
        timestamp = QDateTime.currentDateTime().toString('hh:mm:ss')
        formatted_message = f'[{timestamp}] {message}'

        self.log_viewer.moveCursor(QTextCursor.MoveOperation.End)

        if msg_type == 'error':
            self.log_viewer.setTextColor(QColor(255, 0, 0))
        elif msg_type == 'success':
            self.log_viewer.setTextColor(QColor(0, 128, 0))
        elif msg_type == 'warning':
            self.log_viewer.setTextColor(QColor(255, 165, 0))
        else:
            self.log_viewer.setTextColor(QColor(0, 0, 0))

        self.log_viewer.insertPlainText(formatted_message + '\n')
        self.log_viewer.ensureCursorVisible()

    def selecionar_arquivo(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Selecionar Arquivo CSV', '', 'CSV Files (*.csv)'
        )
        if file_path:
            self.carregar_csv(file_path)
            self.log(f'Arquivo carregado: {file_path}', 'info')

    def carregar_csv(self, file_path):
        try:
            self.df = pd.read_csv(file_path)
            self.table.setRowCount(self.df.shape[0])
            self.table.setColumnCount(self.df.shape[1])
            self.table.setHorizontalHeaderLabels(self.df.columns)

            for i in range(self.df.shape[0]):
                for j in range(self.df.shape[1]):
                    self.table.setItem(
                        i, j, QTableWidgetItem(str(self.df.iat[i, j]))
                    )

            self.label.setText(
                f'Arquivo carregado: {os.path.basename(file_path)}'
            )
            self.log(
                f'CSV carregado com {self.df.shape[0]} registros e {
                    self.df.shape[1]
                } colunas',
                'info',
            )
        except Exception as e:
            error_msg = f'Erro ao carregar CSV: {str(e)}'
            QMessageBox.critical(self, 'Erro', error_msg)
            self.log(error_msg, 'error')

    def formatar_coluna_telefone(self):
        if not hasattr(self, 'df'):
            QMessageBox.warning(
                self, 'Erro', 'Nenhum arquivo carregado para formatar.'
            )
            return

        colunas = [
            self.table.horizontalHeaderItem(i).text().lower()
            for i in range(self.table.columnCount())
        ]
        candidatos = ['phone', 'telefone1', 'celular', 'contato']
        indice = next(
            (
                i
                for i, nome in enumerate(colunas)
                if any(c in nome for c in candidatos)
            ),
            -1,
        )

        if indice == -1:
            error_msg = 'Nenhuma coluna de telefone encontrada.'
            QMessageBox.warning(self, 'Erro', error_msg)
            self.log(error_msg, 'warning')
            return

        for linha in range(self.table.rowCount()):
            item = self.table.item(linha, indice)
            if item:
                texto = item.text()
                formatado = formatar_telefone(texto)
                self.table.setItem(linha, indice, QTableWidgetItem(formatado))

        success_msg = 'Telefones formatados com sucesso!'
        QMessageBox.information(self, 'Sucesso', success_msg)
        self.log(success_msg, 'success')

    def salvar_csv(self):
        if not hasattr(self, 'df'):
            error_msg = 'Nenhum arquivo carregado para salvar.'
            QMessageBox.warning(self, 'Erro', error_msg)
            self.log(error_msg, 'warning')
            return

        linhas = self.table.rowCount()
        colunas = self.table.columnCount()
        dados = []

        for i in range(linhas):
            linha_dados = []
            for j in range(colunas):
                item = self.table.item(i, j)
                linha_dados.append(item.text() if item else '')
            dados.append(linha_dados)

        self.df = pd.DataFrame(
            dados,
            columns=[
                self.table.horizontalHeaderItem(i).text()
                for i in range(colunas)
            ],
        )

        file_path, _ = QFileDialog.getSaveFileName(
            self, 'Salvar arquivo CSV', '', 'CSV Files (*.csv)'
        )
        if file_path:
            try:
                self.df.to_csv(file_path, index=False)
                success_msg = f'Arquivo salvo em: {file_path}'
                QMessageBox.information(self, 'Sucesso', success_msg)
                self.log(success_msg, 'success')
            except Exception as e:
                error_msg = f'Erro ao salvar CSV: {str(e)}'
                QMessageBox.critical(self, 'Erro', error_msg)
                self.log(error_msg, 'error')

    def enviar_whatsapp(self):
        mensagem = self.texto_mensagem.toPlainText().strip()
        if not mensagem:
            error_msg = 'Escreva uma mensagem antes de enviar.'
            QMessageBox.warning(self, 'Mensagem vazia', error_msg)
            self.log(error_msg, 'warning')
            return

        colunas = [
            self.table.horizontalHeaderItem(i).text().lower()
            for i in range(self.table.columnCount())
        ]
        candidatos = ['phone', 'telefone1', 'celular', 'contato']
        indice = next(
            (
                i
                for i, nome in enumerate(colunas)
                if any(c in nome for c in candidatos)
            ),
            -1,
        )

        if indice == -1:
            error_msg = 'Nenhuma coluna de telefone encontrada.'
            QMessageBox.warning(self, 'Erro', error_msg)
            self.log(error_msg, 'error')
            return

        # Get phone numbers
        phone_numbers = []
        for linha in range(self.table.rowCount()):
            item = self.table.item(linha, indice)
            if item:
                numero_raw = item.text()
                numero = re.sub(r'\D', '', numero_raw)
                if len(numero) >= NUMBER_MSG_SENDER:
                    phone_numbers.append(numero)

        if not phone_numbers:
            error_msg = 'Nenhum número de telefone válido encontrado.'
            QMessageBox.warning(self, 'Erro', error_msg)
            self.log(error_msg, 'error')
            return

        # Get scheduling options
        agendar = self.schedule_checkbox.isChecked()
        hora = self.time_edit.time().hour() if agendar else None
        minuto = self.time_edit.time().minute() if agendar else None
        delay = self.delay_spinbox.value()

        # Confirmation dialog
        confirm_msg = f'Deseja enviar a mensagem para {
            len(phone_numbers)
        } contatos?\n\nMensagem:\n{mensagem[:200]}'
        if agendar:
            confirm_msg += f'\n\nAgendado para: {hora:02d}:{minuto:02d}'
        else:
            confirm_msg += '\n\nEnvio imediato'

        confirm = QMessageBox.question(
            self,
            'Confirmar envio',
            confirm_msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            self.log('Envio cancelado pelo usuário', 'warning')
            return

        # Configurar pywhatkit para não abrir o navegador
        # pywhatkit.core.check_dependencies()
        # pywhatkit.core.close_tab(delay=0)

        # Create and start thread
        self.thread = WhatsAppSenderThread(
            phone_numbers,
            mensagem,
            delay_seconds=delay,
            agendar=agendar,
            hora=hora,
            minuto=minuto,
        )

        # Progress dialog
        self.progress = QProgressDialog(
            'Enviando mensagens...', 'Cancelar', 0, len(phone_numbers), self
        )
        self.progress.setWindowTitle('Enviando Mensagens')
        self.progress.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress.canceled.connect(self.cancel_sending)

        # Connect signals
        self.thread.update_progress.connect(self.update_progress)
        self.thread.log_message.connect(self.log)
        self.thread.finished.connect(self.sending_finished)

        self.thread.start()
        self.progress.show()
        self.log(f'Iniciando envio para {len(phone_numbers)} contatos', 'info')

    def update_progress(self, current, message, success):
        self.progress.setValue(current)
        self.progress.setLabelText(message)

    def sending_finished(self, success, error_message):
        self.progress.close()
        if success:
            QMessageBox.information(self, 'Sucesso', error_message)
            self.log(error_message, 'success')
        else:
            QMessageBox.warning(self, 'Erro', error_message)
            self.log(error_message, 'error')

    def cancel_sending(self):
        if self.thread:
            self.thread.stop()
            self.thread.wait()
        self.progress.close()
        self.log('Envio cancelado pelo usuário', 'warning')

    def closeEvent(self, event):
        if self.thread and self.thread.isRunning():
            self.thread.stop()
            self.thread.wait()
        event.accept()


def formatar_telefone(numero):
    numero = re.sub(r'\D', '', str(numero))
    if numero.startswith('55') and len(numero) > NUMBER_COUNTRY_CODE:
        numero = numero[2:]
    if len(numero) == NUMBER_COUNTRY_CODE:
        return f'({numero[:2]}) {numero[2:7]}-{numero[7:]}'
    elif len(numero) == NUMBER_MSG_SENDER:
        return f'({numero[:2]}) {numero[2:6]}-{numero[6:]}'
    else:
        return numero

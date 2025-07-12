import sys
import os
import re
import webbrowser
import urllib.parse
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
)


def formatar_telefone(numero):
    numero = re.sub(r"\D", "", str(numero))

    if numero.startswith("55") and len(numero) > 11:
        numero = numero[2:]

    if len(numero) == 11:
        return f"({numero[:2]}) {numero[2:7]}-{numero[7:]}"
    elif len(numero) == 10:
        return f"({numero[:2]}) {numero[2:6]}-{numero[6:]}"
    else:
        return numero


class ClienteCSVViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visualizador de Clientes CSV")
        self.setGeometry(100, 100, 1800, 1000)

        self.layout = QVBoxLayout()

        self.label = QLabel(
            "Selecione um diretório contendo um arquivo CSV de clientes."
        )
        self.layout.addWidget(self.label)

        self.button = QPushButton("Selecionar Arquivo")
        self.button.clicked.connect(self.selecionar_arquivo)
        self.layout.addWidget(self.button)

        self.botao_whatsapp = QPushButton("Enviar WhatsApp")
        self.botao_whatsapp.clicked.connect(self.enviar_whatsapp)
        self.layout.addWidget(self.botao_whatsapp)

        self.botao_salvar = QPushButton("Salvar CSV")
        self.botao_salvar.clicked.connect(self.salvar_csv)

        self.botao_formatar = QPushButton("Formatar Telefones")
        self.botao_formatar.clicked.connect(self.formatar_coluna_telefone)
        self.layout.addWidget(self.botao_formatar)
        self.layout.addWidget(self.botao_salvar)

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        self.setLayout(self.layout)

    def salvar_csv(self):
        if not hasattr(self, "df"):
            QMessageBox.warning(self, "Erro", "Nenhum arquivo carregado para salvar.")
            return

        linhas = self.table.rowCount()
        colunas = self.table.columnCount()

        dados = []
        for i in range(linhas):
            linha_dados = []
            for j in range(colunas):
                item = self.table.item(i, j)
                linha_dados.append(item.text() if item else "")
            dados.append(linha_dados)

        self.df = pd.DataFrame(
            dados,
            columns=[self.table.horizontalHeaderItem(i).text() for i in range(colunas)],
        )

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Salvar arquivo CSV", "", "CSV Files (*.csv)"
        )

        if file_path:
            try:
                self.df.to_csv(file_path, index=False)
                QMessageBox.information(
                    self, "Sucesso", f"Arquivo salvo em:\n{file_path}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Erro ao salvar CSV", str(e))

    def enviar_whatsapp(self):
        colunas = [
            self.table.horizontalHeaderItem(i).text().lower()
            for i in range(self.table.columnCount())
        ]
        candidatos = ["phone", "telefone1", "celular", "contato"]
        indice = next(
            (i for i, nome in enumerate(colunas) if any(c in nome for c in candidatos)),
            -1,
        )

        if indice == -1:
            QMessageBox.warning(self, "Erro", "Nenhuma coluna de telefone encontrada.")
            return

        mensagem = "Olá! Esta é uma mensagem automática."

        for linha in range(self.table.rowCount()):
            item = self.table.item(linha, indice)
            if item:
                numero_raw = item.text()
                numero = re.sub(r"\D", "", numero_raw)
                if not numero.startswith("55"):
                    numero = "55" + numero

                texto_url = urllib.parse.quote(mensagem)
                url = f"https://web.whatsapp.com/send?phone={numero}&text={texto_url}"

                webbrowser.open(url)

    def selecionar_arquivo(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Arquivo CSV", "", "CSV Files (*.csv)"
        )
        if file_path:
            self.carregar_csv(file_path)

        else:
            QMessageBox.information(
                self, "Erro", f"Nenhum arquivo encontrado em:\n{file_path}"
            )

    def carregar_csv(self, file_path):
        try:
            self.df = pd.read_csv(file_path)
            self.table.setRowCount(self.df.shape[0])
            self.table.setColumnCount(self.df.shape[1])
            self.table.setHorizontalHeaderLabels(self.df.columns)

            for i in range(self.df.shape[0]):
                for j in range(self.df.shape[1]):
                    self.table.setItem(i, j, QTableWidgetItem(str(self.df.iat[i, j])))

            self.label.setText(f"Arquivo carregado: {os.path.basename(file_path)}")
        except Exception as e:
            QMessageBox.critical(self, "Erro ao carregar CSV", str(e))

    def formatar_coluna_telefone(self):
        colunas = [
            self.table.horizontalHeaderItem(i).text().lower()
            for i in range(self.table.columnCount())
        ]
        candidatos = ["phone", "telefone1", "celular", "contato"]
        indice = next(
            (i for i, nome in enumerate(colunas) if any(c in nome for c in candidatos)),
            -1,
        )

        if indice == -1:
            QMessageBox.warning(self, "Erro", "Nenhuma coluna de telefone encontrada.")
            return

        for linha in range(self.table.rowCount()):
            item = self.table.item(linha, indice)
            if item:
                texto = item.text()
                formatado = formatar_telefone(texto)
                self.table.setItem(linha, indice, QTableWidgetItem(formatado))

        QMessageBox.information(self, "Sucesso", "Telefones formatados com sucesso!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClienteCSVViewer()
    window.show()
    sys.exit(app.exec())

import os
import re
import sys
import urllib.parse
import webbrowser

import pandas as pd
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


def formatar_telefone(numero: str) -> str:
    numero = re.sub(r"\D", "", str(numero))

    if numero.startswith("55") and len(numero) > 11:
        numero = numero[2:]

    if len(numero) == 11:
        return f"({numero[:2]}) {numero[2:7]}-{numero[7:]}"
    if len(numero) == 10:
        return f"({numero[:2]}) {numero[2:6]}-{numero[6:]}"
    return numero


class ClienteCSVViewer(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Clientes CSV • Orange")
        self.resize(1200, 780)

        self.df: pd.DataFrame | None = None
        self.df_filtrado: pd.DataFrame | None = None
        self.file_path: str | None = None

        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QVBoxLayout()
        central.setLayout(root_layout)

        self.label_caminho = QLabel("Nenhum arquivo aberto")
        root_layout.addWidget(self.label_caminho)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Filtrar por qualquer coluna...")
        self.search_bar.textChanged.connect(self.aplicar_filtro)

        self.btn_abrir = QPushButton("Abrir CSV")
        self.btn_abrir.clicked.connect(self.selecionar_arquivo)

        self.btn_recarregar = QPushButton("Recarregar")
        self.btn_recarregar.clicked.connect(self.recarregar_arquivo)
        self.btn_recarregar.setEnabled(False)

        self.btn_formatar = QPushButton("Formatar Telefones")
        self.btn_formatar.clicked.connect(self.formatar_coluna_telefone)

        self.btn_whatsapp = QPushButton("Enviar WhatsApp")
        self.btn_whatsapp.clicked.connect(self.enviar_whatsapp)

        self.btn_salvar = QPushButton("Salvar CSV")
        self.btn_salvar.clicked.connect(self.salvar_csv)

        toolbar = QHBoxLayout()
        for btn in [
            self.btn_abrir,
            self.btn_recarregar,
            self.btn_formatar,
            self.btn_whatsapp,
            self.btn_salvar,
        ]:
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            toolbar.addWidget(btn)
        toolbar.addStretch()
        toolbar.addWidget(self.search_bar)

        root_layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        root_layout.addWidget(self.table)

        status = QStatusBar()
        self.setStatusBar(status)
        self.status_rows = QLabel("0 linhas")
        self.status_cols = QLabel("0 colunas")
        status.addPermanentWidget(self.status_rows)
        status.addPermanentWidget(self.status_cols)

        self._aplicar_tema()

    def _aplicar_tema(self) -> None:
        palette = """
        QWidget { background: #0f1117; color: #e6e8f0; }
        QPushButton { background: #1f2430; color: #e6e8f0; border: 1px solid #31384a; padding: 6px 10px; border-radius: 4px; }
        QPushButton:hover { background: #2a3040; }
        QPushButton:disabled { color: #8a8fa1; border-color: #2a3040; }
        QLineEdit { background: #11141d; border: 1px solid #31384a; padding: 6px; border-radius: 4px; }
        QTableWidget { gridline-color: #2a3040; }
        QHeaderView::section { background: #1b1f2a; color: #e6e8f0; padding: 6px; border: 0px; }
        QTableWidget::item:selected { background: #2e3650; }
        QStatusBar { background: #0f1117; color: #8a8fa1; }
        """
        self.setStyleSheet(palette)

    def selecionar_arquivo(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Arquivo CSV", "", "CSV Files (*.csv)"
        )
        if not file_path:
            return
        self.carregar_csv(file_path)

    def recarregar_arquivo(self) -> None:
        if not self.file_path:
            return
        self.carregar_csv(self.file_path)

    def carregar_csv(self, file_path: str) -> None:
        try:
            df = pd.read_csv(file_path)
        except Exception as exc:  # pragma: no cover - UI
            QMessageBox.critical(self, "Erro ao carregar CSV", str(exc))
            return

        self.file_path = file_path
        self.df = df
        self.df_filtrado = df
        self.btn_recarregar.setEnabled(True)
        self.search_bar.clear()
        self.label_caminho.setText(f"Arquivo: {os.path.basename(file_path)}")
        self._preencher_tabela(df)

    def _preencher_tabela(self, df: pd.DataFrame) -> None:
        self.table.clear()
        self.table.setRowCount(len(df.index))
        self.table.setColumnCount(len(df.columns))
        self.table.setHorizontalHeaderLabels([str(c) for c in df.columns])

        for i, (_, row) in enumerate(df.iterrows()):
            for j, valor in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(valor)))

        self.status_rows.setText(f"{len(df.index)} linhas")
        self.status_cols.setText(f"{len(df.columns)} colunas")
        self.table.resizeColumnsToContents()

    def aplicar_filtro(self, texto: str) -> None:
        if self.df is None:
            return
        if not texto:
            self.df_filtrado = self.df
            self._preencher_tabela(self.df)
            return

        mask = self.df.apply(
            lambda col: col.astype(str)
            .str.contains(texto, case=False, na=False),
            axis=0,
        ).any(axis=1)

        filtrado = self.df.loc[mask]
        self.df_filtrado = filtrado
        self._preencher_tabela(filtrado)

    def salvar_csv(self) -> None:
        if self.df_filtrado is None:
            QMessageBox.warning(self, "Erro", "Nenhum dado para salvar.")
            return

        linhas = self.table.rowCount()
        colunas = self.table.columnCount()
        dados = []
        for i in range(linhas):
            linha = []
            for j in range(colunas):
                item = self.table.item(i, j)
                linha.append(item.text() if item else "")
            dados.append(linha)

        df_atual = pd.DataFrame(
            dados,
            columns=[self.table.horizontalHeaderItem(i).text() for i in range(colunas)],
        )

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Salvar arquivo CSV", self.file_path or "", "CSV Files (*.csv)"
        )
        if not file_path:
            return

        try:
            df_atual.to_csv(file_path, index=False)
            QMessageBox.information(self, "Sucesso", f"Arquivo salvo em:\n{file_path}")
        except Exception as exc:  # pragma: no cover - UI
            QMessageBox.critical(self, "Erro ao salvar CSV", str(exc))

    def _indice_coluna_telefone(self) -> int:
        if self.table.columnCount() == 0:
            return -1

        colunas = [
            self.table.horizontalHeaderItem(i).text().lower()
            for i in range(self.table.columnCount())
        ]
        candidatos = ["phone", "telefone", "telefone1", "celular", "contato"]
        return next(
            (i for i, nome in enumerate(colunas) if any(c in nome for c in candidatos)),
            -1,
        )

    def formatar_coluna_telefone(self) -> None:
        idx = self._indice_coluna_telefone()
        if idx == -1:
            QMessageBox.warning(self, "Erro", "Nenhuma coluna de telefone encontrada.")
            return

        for linha in range(self.table.rowCount()):
            item = self.table.item(linha, idx)
            if item:
                item.setText(formatar_telefone(item.text()))

        QMessageBox.information(self, "Pronto", "Telefones formatados.")

    def enviar_whatsapp(self) -> None:
        idx = self._indice_coluna_telefone()
        if idx == -1:
            QMessageBox.warning(self, "Erro", "Nenhuma coluna de telefone encontrada.")
            return

        mensagem = "Ola! Esta e uma mensagem automatica."
        for linha in range(self.table.rowCount()):
            item = self.table.item(linha, idx)
            if not item:
                continue
            numero = re.sub(r"\D", "", item.text())
            if not numero.startswith("55"):
                numero = "55" + numero

            texto_url = urllib.parse.quote(mensagem)
            url = f"https://web.whatsapp.com/send?phone={numero}&text={texto_url}"
            webbrowser.open(url)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClienteCSVViewer()
    window.show()
    sys.exit(app.exec())

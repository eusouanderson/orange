import math
import sys
from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDoubleSpinBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class Calc3D(QMainWindow):
    """Calculadora 3D para desenvolvimento em FreeCAD e engenharia."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Calc3D • FreeCAD Calculator")
        self.resize(1400, 900)

        self.historico = []
        self._build_ui()
        self._aplicar_tema()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout()
        central.setLayout(root)

        # --- Conversão de Unidades ---
        group_unidades = QGroupBox("Conversão de Unidades")
        layout_unidades = QHBoxLayout()

        self.spin_valor = QDoubleSpinBox()
        self.spin_valor.setRange(-999999, 999999)
        self.spin_valor.setDecimals(4)
        self.spin_valor.setValue(10.0)

        self.combo_de = QComboBox()
        self.combo_de.addItems(["mm", "cm", "m", "in", "ft"])
        self.combo_de.setCurrentText("mm")

        self.combo_para = QComboBox()
        self.combo_para.addItems(["mm", "cm", "m", "in", "ft"])
        self.combo_para.setCurrentText("cm")

        self.label_resultado_unidade = QLabel("0.0000")
        btn_converter = QPushButton("Converter")
        btn_converter.clicked.connect(self._converter_unidade)

        layout_unidades.addWidget(QLabel("Valor:"))
        layout_unidades.addWidget(self.spin_valor)
        layout_unidades.addWidget(self.combo_de)
        layout_unidades.addWidget(QLabel("para"))
        layout_unidades.addWidget(self.combo_para)
        layout_unidades.addWidget(btn_converter)
        layout_unidades.addWidget(self.label_resultado_unidade)
        group_unidades.setLayout(layout_unidades)
        root.addWidget(group_unidades)

        # --- Geometria 2D ---
        group_geo2d = QGroupBox("Geometria 2D")
        layout_geo2d = QVBoxLayout()

        # Linha 1: Área do retângulo/quadrado
        h1 = QHBoxLayout()
        h1.addWidget(QLabel("Área Retângulo - Largura:"))
        self.spin_rect_w = QDoubleSpinBox()
        self.spin_rect_w.setRange(0, 999999)
        self.spin_rect_w.setDecimals(4)
        self.spin_rect_w.setValue(100)
        h1.addWidget(self.spin_rect_w)
        h1.addWidget(QLabel("x Altura:"))
        self.spin_rect_h = QDoubleSpinBox()
        self.spin_rect_h.setRange(0, 999999)
        self.spin_rect_h.setDecimals(4)
        self.spin_rect_h.setValue(50)
        h1.addWidget(self.spin_rect_h)
        btn_area_rect = QPushButton("Calcular Área")
        btn_area_rect.clicked.connect(self._calcular_area_retangulo)
        h1.addWidget(btn_area_rect)
        self.label_area_rect = QLabel("0")
        h1.addWidget(self.label_area_rect)
        layout_geo2d.addLayout(h1)

        # Linha 2: Circunferência/Área Círculo
        h2 = QHBoxLayout()
        h2.addWidget(QLabel("Círculo - Raio:"))
        self.spin_raio = QDoubleSpinBox()
        self.spin_raio.setRange(0, 999999)
        self.spin_raio.setDecimals(4)
        self.spin_raio.setValue(50)
        h2.addWidget(self.spin_raio)
        btn_circ = QPushButton("Circunferência")
        btn_circ.clicked.connect(self._calcular_circunferencia)
        h2.addWidget(btn_circ)
        self.label_circ = QLabel("0")
        h2.addWidget(self.label_circ)
        btn_area_circ = QPushButton("Área")
        btn_area_circ.clicked.connect(self._calcular_area_circulo)
        h2.addWidget(btn_area_circ)
        self.label_area_circ = QLabel("0")
        h2.addWidget(self.label_area_circ)
        layout_geo2d.addLayout(h2)

        group_geo2d.setLayout(layout_geo2d)
        root.addWidget(group_geo2d)

        # --- Geometria 3D ---
        group_geo3d = QGroupBox("Geometria 3D")
        layout_geo3d = QVBoxLayout()

        # Volume cubo/paralelepípedo
        h3 = QHBoxLayout()
        h3.addWidget(QLabel("Paralelepípedo - L:"))
        self.spin_cube_l = QDoubleSpinBox()
        self.spin_cube_l.setRange(0, 999999)
        self.spin_cube_l.setDecimals(4)
        self.spin_cube_l.setValue(100)
        h3.addWidget(self.spin_cube_l)
        h3.addWidget(QLabel("x H:"))
        self.spin_cube_h = QDoubleSpinBox()
        self.spin_cube_h.setRange(0, 999999)
        self.spin_cube_h.setDecimals(4)
        self.spin_cube_h.setValue(100)
        h3.addWidget(self.spin_cube_h)
        h3.addWidget(QLabel("x P:"))
        self.spin_cube_d = QDoubleSpinBox()
        self.spin_cube_d.setRange(0, 999999)
        self.spin_cube_d.setDecimals(4)
        self.spin_cube_d.setValue(100)
        h3.addWidget(self.spin_cube_d)
        btn_vol_cube = QPushButton("Volume")
        btn_vol_cube.clicked.connect(self._calcular_volume_cubo)
        h3.addWidget(btn_vol_cube)
        self.label_vol_cube = QLabel("0")
        h3.addWidget(self.label_vol_cube)
        layout_geo3d.addLayout(h3)

        # Volume esfera
        h4 = QHBoxLayout()
        h4.addWidget(QLabel("Esfera - Raio:"))
        self.spin_esfera_r = QDoubleSpinBox()
        self.spin_esfera_r.setRange(0, 999999)
        self.spin_esfera_r.setDecimals(4)
        self.spin_esfera_r.setValue(50)
        h4.addWidget(self.spin_esfera_r)
        btn_vol_esfera = QPushButton("Volume")
        btn_vol_esfera.clicked.connect(self._calcular_volume_esfera)
        h4.addWidget(btn_vol_esfera)
        self.label_vol_esfera = QLabel("0")
        h4.addWidget(self.label_vol_esfera)
        btn_area_esfera = QPushButton("Área Superfície")
        btn_area_esfera.clicked.connect(self._calcular_area_esfera)
        h4.addWidget(btn_area_esfera)
        self.label_area_esfera = QLabel("0")
        h4.addWidget(self.label_area_esfera)
        layout_geo3d.addLayout(h4)

        # Distância 3D (entre dois pontos)
        h5 = QHBoxLayout()
        h5.addWidget(QLabel("Distância 3D: P1("))
        self.spin_x1 = QDoubleSpinBox()
        self.spin_x1.setRange(-999999, 999999)
        self.spin_x1.setDecimals(4)
        self.spin_x1.setValue(0)
        h5.addWidget(self.spin_x1)
        h5.addWidget(QLabel(","))
        self.spin_y1 = QDoubleSpinBox()
        self.spin_y1.setRange(-999999, 999999)
        self.spin_y1.setDecimals(4)
        self.spin_y1.setValue(0)
        h5.addWidget(self.spin_y1)
        h5.addWidget(QLabel(","))
        self.spin_z1 = QDoubleSpinBox()
        self.spin_z1.setRange(-999999, 999999)
        self.spin_z1.setDecimals(4)
        self.spin_z1.setValue(0)
        h5.addWidget(self.spin_z1)
        h5.addWidget(QLabel(") → P2("))
        self.spin_x2 = QDoubleSpinBox()
        self.spin_x2.setRange(-999999, 999999)
        self.spin_x2.setDecimals(4)
        self.spin_x2.setValue(100)
        h5.addWidget(self.spin_x2)
        h5.addWidget(QLabel(","))
        self.spin_y2 = QDoubleSpinBox()
        self.spin_y2.setRange(-999999, 999999)
        self.spin_y2.setDecimals(4)
        self.spin_y2.setValue(100)
        h5.addWidget(self.spin_y2)
        h5.addWidget(QLabel(","))
        self.spin_z2 = QDoubleSpinBox()
        self.spin_z2.setRange(-999999, 999999)
        self.spin_z2.setDecimals(4)
        self.spin_z2.setValue(100)
        h5.addWidget(self.spin_z2)
        h5.addWidget(QLabel(")"))
        btn_dist3d = QPushButton("Calcular")
        btn_dist3d.clicked.connect(self._calcular_distancia_3d)
        h5.addWidget(btn_dist3d)
        self.label_dist3d = QLabel("0")
        h5.addWidget(self.label_dist3d)
        layout_geo3d.addLayout(h5)

        group_geo3d.setLayout(layout_geo3d)
        root.addWidget(group_geo3d)

        # --- Ferramentas Extras ---
        group_extras = QGroupBox("Ferramentas Extras")
        layout_extras = QHBoxLayout()

        layout_extras.addWidget(QLabel("Raiz Quadrada:"))
        self.spin_sqrt = QDoubleSpinBox()
        self.spin_sqrt.setRange(0, 999999)
        self.spin_sqrt.setDecimals(4)
        self.spin_sqrt.setValue(16)
        layout_extras.addWidget(self.spin_sqrt)
        btn_sqrt = QPushButton("√")
        btn_sqrt.clicked.connect(self._calcular_sqrt)
        layout_extras.addWidget(btn_sqrt)
        self.label_sqrt = QLabel("0")
        layout_extras.addWidget(self.label_sqrt)

        layout_extras.addWidget(QLabel("Potência:"))
        self.spin_base = QDoubleSpinBox()
        self.spin_base.setRange(-999999, 999999)
        self.spin_base.setDecimals(4)
        self.spin_base.setValue(2)
        layout_extras.addWidget(self.spin_base)
        self.spin_exp = QSpinBox()
        self.spin_exp.setRange(-100, 100)
        self.spin_exp.setValue(3)
        layout_extras.addWidget(self.spin_exp)
        btn_pow = QPushButton("x^n")
        btn_pow.clicked.connect(self._calcular_potencia)
        layout_extras.addWidget(btn_pow)
        self.label_pow = QLabel("0")
        layout_extras.addWidget(self.label_pow)

        group_extras.setLayout(layout_extras)
        root.addWidget(group_extras)

        # --- Histórico ---
        group_hist = QGroupBox("Histórico de Cálculos")
        layout_hist = QVBoxLayout()
        btn_limpar = QPushButton("Limpar Histórico")
        btn_limpar.clicked.connect(self._limpar_historico)
        layout_hist.addWidget(btn_limpar)

        self.table_historico = QTableWidget()
        self.table_historico.setColumnCount(3)
        self.table_historico.setHorizontalHeaderLabels(["Hora", "Operação", "Resultado"])
        self.table_historico.setMaximumHeight(200)
        layout_hist.addWidget(self.table_historico)

        group_hist.setLayout(layout_hist)
        root.addWidget(group_hist)

    def _converter_unidade(self) -> None:
        valor = self.spin_valor.value()
        de = self.combo_de.currentText()
        para = self.combo_para.currentText()

        # Tabela de conversão: tudo para mm
        para_mm = {
            "mm": 1,
            "cm": 10,
            "m": 1000,
            "in": 25.4,  # polegada
            "ft": 304.8,  # pé
        }

        valor_mm = valor * para_mm[de]
        resultado = valor_mm / para_mm[para]

        self.label_resultado_unidade.setText(f"{resultado:.4f}")
        self._adicionar_historico(f"{valor} {de} → {para}", f"{resultado:.4f} {para}")

    def _calcular_area_retangulo(self) -> None:
        w = self.spin_rect_w.value()
        h = self.spin_rect_h.value()
        area = w * h
        self.label_area_rect.setText(f"{area:.4f}")
        self._adicionar_historico(f"Área Ret. {w}x{h}", f"{area:.4f}")

    def _calcular_circunferencia(self) -> None:
        r = self.spin_raio.value()
        circ = 2 * math.pi * r
        self.label_circ.setText(f"{circ:.4f}")
        self._adicionar_historico(f"Circunf. (r={r})", f"{circ:.4f}")

    def _calcular_area_circulo(self) -> None:
        r = self.spin_raio.value()
        area = math.pi * r * r
        self.label_area_circ.setText(f"{area:.4f}")
        self._adicionar_historico(f"Área Circ. (r={r})", f"{area:.4f}")

    def _calcular_volume_cubo(self) -> None:
        l = self.spin_cube_l.value()
        h = self.spin_cube_h.value()
        d = self.spin_cube_d.value()
        vol = l * h * d
        self.label_vol_cube.setText(f"{vol:.4f}")
        self._adicionar_historico(f"Vol. Cubo {l}×{h}×{d}", f"{vol:.4f}")

    def _calcular_volume_esfera(self) -> None:
        r = self.spin_esfera_r.value()
        vol = (4 / 3) * math.pi * (r ** 3)
        self.label_vol_esfera.setText(f"{vol:.4f}")
        self._adicionar_historico(f"Vol. Esfera (r={r})", f"{vol:.4f}")

    def _calcular_area_esfera(self) -> None:
        r = self.spin_esfera_r.value()
        area = 4 * math.pi * (r ** 2)
        self.label_area_esfera.setText(f"{area:.4f}")
        self._adicionar_historico(f"Área Esfera (r={r})", f"{area:.4f}")

    def _calcular_distancia_3d(self) -> None:
        x1, y1, z1 = self.spin_x1.value(), self.spin_y1.value(), self.spin_z1.value()
        x2, y2, z2 = self.spin_x2.value(), self.spin_y2.value(), self.spin_z2.value()
        dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)
        self.label_dist3d.setText(f"{dist:.4f}")
        self._adicionar_historico(
            f"Dist. 3D ({x1},{y1},{z1})-({x2},{y2},{z2})", f"{dist:.4f}"
        )

    def _calcular_sqrt(self) -> None:
        valor = self.spin_sqrt.value()
        resultado = math.sqrt(valor) if valor >= 0 else 0
        self.label_sqrt.setText(f"{resultado:.4f}")
        self._adicionar_historico(f"√{valor}", f"{resultado:.4f}")

    def _calcular_potencia(self) -> None:
        base = self.spin_base.value()
        exp = self.spin_exp.value()
        resultado = base ** exp
        self.label_pow.setText(f"{resultado:.4f}")
        self._adicionar_historico(f"{base}^{exp}", f"{resultado:.4f}")

    def _adicionar_historico(self, operacao: str, resultado: str) -> None:
        hora = datetime.now().strftime("%H:%M:%S")
        row = self.table_historico.rowCount()
        self.table_historico.insertRow(row)
        self.table_historico.setItem(row, 0, QTableWidgetItem(hora))
        self.table_historico.setItem(row, 1, QTableWidgetItem(operacao))
        self.table_historico.setItem(row, 2, QTableWidgetItem(resultado))
        self.table_historico.scrollToBottom()

    def _limpar_historico(self) -> None:
        self.table_historico.setRowCount(0)

    def _aplicar_tema(self) -> None:
        stylesheet = """
        QWidget { background: #0f1117; color: #e6e8f0; }
        QGroupBox { border: 1px solid #31384a; border-radius: 4px; margin-top: 10px; padding-top: 10px; color: #e6e8f0; }
        QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px; }
        QPushButton { background: #238636; color: #fff; border: 1px solid #2ea043; padding: 6px 12px; border-radius: 4px; font-weight: bold; }
        QPushButton:hover { background: #2ea043; }
        QPushButton:pressed { background: #1a6e1a; }
        QDoubleSpinBox, QSpinBox, QComboBox, QLineEdit { background: #11141d; border: 1px solid #31384a; padding: 6px; border-radius: 4px; }
        QTableWidget { gridline-color: #2a3040; }
        QHeaderView::section { background: #1b1f2a; color: #e6e8f0; padding: 6px; }
        QTableWidget::item:selected { background: #238636; }
        """
        self.setStyleSheet(stylesheet)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Calc3D()
    window.show()
    sys.exit(app.exec())


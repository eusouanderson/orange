import math

from src.core.main import Calc3D


def test_converter_unidade_mm_para_cm(qapp):
    """Testa conversão de 10mm para cm (deve ser 1cm)."""
    calc = Calc3D()
    calc.spin_valor.setValue(10)
    calc.combo_de.setCurrentText("mm")
    calc.combo_para.setCurrentText("cm")
    calc._converter_unidade()
    resultado = float(calc.label_resultado_unidade.text())
    assert abs(resultado - 1.0) < 0.0001


def test_converter_unidade_polegadas_para_mm(qapp):
    """Testa conversão de polegadas para mm."""
    calc = Calc3D()
    calc.spin_valor.setValue(1)  # 1 polegada
    calc.combo_de.setCurrentText("in")
    calc.combo_para.setCurrentText("mm")
    calc._converter_unidade()
    resultado = float(calc.label_resultado_unidade.text())
    assert abs(resultado - 25.4) < 0.0001  # 1 polegada = 25.4 mm


def test_calcular_area_retangulo(qapp):
    """Testa cálculo de área retângulo 100x50 = 5000."""
    calc = Calc3D()
    calc.spin_rect_w.setValue(100)
    calc.spin_rect_h.setValue(50)
    calc._calcular_area_retangulo()
    resultado = float(calc.label_area_rect.text())
    assert abs(resultado - 5000) < 0.0001


def test_calcular_area_circulo(qapp):
    """Testa área de círculo com raio 10 = 100π."""
    calc = Calc3D()
    calc.spin_raio.setValue(10)
    calc._calcular_area_circulo()
    resultado = float(calc.label_area_circ.text())
    esperado = math.pi * 10 * 10
    assert abs(resultado - esperado) < 0.0001


def test_calcular_circunferencia(qapp):
    """Testa circunferência com raio 10 = 2π*10."""
    calc = Calc3D()
    calc.spin_raio.setValue(10)
    calc._calcular_circunferencia()
    resultado = float(calc.label_circ.text())
    esperado = 2 * math.pi * 10
    assert abs(resultado - esperado) < 0.0001


def test_calcular_volume_cubo(qapp):
    """Testa volume cubo 10x10x10 = 1000."""
    calc = Calc3D()
    calc.spin_cube_l.setValue(10)
    calc.spin_cube_h.setValue(10)
    calc.spin_cube_d.setValue(10)
    calc._calcular_volume_cubo()
    resultado = float(calc.label_vol_cube.text())
    assert abs(resultado - 1000) < 0.0001


def test_calcular_volume_esfera(qapp):
    """Testa volume esfera com raio 1 = 4/3 * π."""
    calc = Calc3D()
    calc.spin_esfera_r.setValue(1)
    calc._calcular_volume_esfera()
    resultado = float(calc.label_vol_esfera.text())
    esperado = (4 / 3) * math.pi
    assert abs(resultado - esperado) < 0.0001


def test_calcular_area_esfera(qapp):
    """Testa área superfície esfera com raio 1 = 4π."""
    calc = Calc3D()
    calc.spin_esfera_r.setValue(1)
    calc._calcular_area_esfera()
    resultado = float(calc.label_area_esfera.text())
    esperado = 4 * math.pi
    assert abs(resultado - esperado) < 0.0001


def test_calcular_distancia_3d(qapp):
    """Testa distância 3D entre (0,0,0) e (3,4,0) = 5."""
    calc = Calc3D()
    calc.spin_x1.setValue(0)
    calc.spin_y1.setValue(0)
    calc.spin_z1.setValue(0)
    calc.spin_x2.setValue(3)
    calc.spin_y2.setValue(4)
    calc.spin_z2.setValue(0)
    calc._calcular_distancia_3d()
    resultado = float(calc.label_dist3d.text())
    assert abs(resultado - 5.0) < 0.0001


def test_calcular_distancia_3d_diagonal(qapp):
    """Testa distância 3D entre (0,0,0) e (1,1,1) = √3."""
    calc = Calc3D()
    calc.spin_x1.setValue(0)
    calc.spin_y1.setValue(0)
    calc.spin_z1.setValue(0)
    calc.spin_x2.setValue(1)
    calc.spin_y2.setValue(1)
    calc.spin_z2.setValue(1)
    calc._calcular_distancia_3d()
    resultado = float(calc.label_dist3d.text())
    esperado = math.sqrt(3)
    assert abs(resultado - esperado) < 0.0001


def test_calcular_sqrt(qapp):
    """Testa raiz quadrada de 16 = 4."""
    calc = Calc3D()
    calc.spin_sqrt.setValue(16)
    calc._calcular_sqrt()
    resultado = float(calc.label_sqrt.text())
    assert abs(resultado - 4.0) < 0.0001


def test_calcular_sqrt_negativo(qapp):
    """Testa raiz quadrada de número negativo = 0."""
    calc = Calc3D()
    calc.spin_sqrt.setValue(-5)
    calc._calcular_sqrt()
    resultado = float(calc.label_sqrt.text())
    assert resultado == 0


def test_calcular_potencia(qapp):
    """Testa 2^3 = 8."""
    calc = Calc3D()
    calc.spin_base.setValue(2)
    calc.spin_exp.setValue(3)
    calc._calcular_potencia()
    resultado = float(calc.label_pow.text())
    assert abs(resultado - 8) < 0.0001


def test_calcular_potencia_negativa(qapp):
    """Testa 2^-2 = 0.25."""
    calc = Calc3D()
    calc.spin_base.setValue(2)
    calc.spin_exp.setValue(-2)
    calc._calcular_potencia()
    resultado = float(calc.label_pow.text())
    assert abs(resultado - 0.25) < 0.0001


def test_adicionar_historico(qapp):
    """Testa adição de item ao histórico."""
    calc = Calc3D()
    initial_rows = calc.table_historico.rowCount()
    
    calc._adicionar_historico("Teste Operação", "123.45")
    
    assert calc.table_historico.rowCount() == initial_rows + 1
    # Verifica última linha
    last_row = calc.table_historico.rowCount() - 1
    assert calc.table_historico.item(last_row, 1).text() == "Teste Operação"
    assert calc.table_historico.item(last_row, 2).text() == "123.45"


def test_limpar_historico(qapp):
    """Testa limpeza do histórico."""
    calc = Calc3D()
    calc._adicionar_historico("Op 1", "100")
    calc._adicionar_historico("Op 2", "200")
    
    assert calc.table_historico.rowCount() > 0
    
    calc._limpar_historico()
    
    assert calc.table_historico.rowCount() == 0

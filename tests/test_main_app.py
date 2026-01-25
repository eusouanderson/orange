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


def test_calcular_area_retangulo(qapp):
    """Testa cálculo de área retângulo 100x50 = 5000."""
    calc = Calc3D()
    calc.spin_rect_w.setValue(100)
    calc.spin_rect_h.setValue(50)
    calc._calcular_area_retangulo()
    resultado = float(calc.label_area_rect.text())
    assert abs(resultado - 5000) < 0.0001


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


def test_calcular_potencia(qapp):
    """Testa 2^3 = 8."""
    calc = Calc3D()
    calc.spin_base.setValue(2)
    calc.spin_exp.setValue(3)
    calc._calcular_potencia()
    resultado = float(calc.label_pow.text())
    assert abs(resultado - 8) < 0.0001

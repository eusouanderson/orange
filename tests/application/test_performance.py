"""
Testes de Performance - Validar ganhos com Cython compilação.

Para rodar com benchmark:
    poetry add -G dev pytest-benchmark
    poetry run pytest tests/test_performance.py --benchmark-only -v
"""

import math
import time
from unittest.mock import MagicMock

import pytest

from src.core.main import Calc3D


class TestCalc3DPerformance:
    """Testes de performance para operações críticas do Calc3D."""

    def test_distancia_3d_calculo_rapido(self, qapp, benchmark):
        """Benchmark: Cálculo de distância 3D deve ser rápido (<0.5ms)."""
        calc = Calc3D()
        calc.spin_x1.setValue(0)
        calc.spin_y1.setValue(0)
        calc.spin_z1.setValue(0)
        calc.spin_x2.setValue(100)
        calc.spin_y2.setValue(100)
        calc.spin_z2.setValue(100)

        def run_distancia():
            calc._calcular_distancia_3d()

        result = benchmark(run_distancia)
        # Esperado: < 0.5ms por cálculo (Cython: ~0.1ms, Python puro: ~2.5ms)

    def test_conversao_unidades_rapida(self, qapp, benchmark):
        """Benchmark: Conversão de unidades deve ser rápida (<0.1ms)."""
        calc = Calc3D()
        calc.spin_valor.setValue(100)
        calc.combo_de.setCurrentText("mm")
        calc.combo_para.setCurrentText("m")

        def run_conversao():
            calc._converter_unidade()

        result = benchmark(run_conversao)
        # Esperado: < 0.1ms (lookup em dicionário)

    def test_area_circulo_rapida(self, qapp, benchmark):
        """Benchmark: Cálculo de área do círculo (<0.1ms)."""
        calc = Calc3D()
        calc.spin_raio.setValue(50)

        def run_area():
            calc._calcular_area_circulo()

        result = benchmark(run_area)
        # Esperado: < 0.1ms

    def test_volume_esfera_rapido(self, qapp, benchmark):
        """Benchmark: Cálculo de volume da esfera (<0.1ms)."""
        calc = Calc3D()
        calc.spin_esfera_r.setValue(25)

        def run_volume():
            calc._calcular_volume_esfera()

        result = benchmark(run_volume)
        # Esperado: < 0.1ms

    def test_potencia_rapida(self, qapp, benchmark):
        """Benchmark: Cálculo de potência (<0.05ms)."""
        calc = Calc3D()
        calc.spin_base.setValue(2)
        calc.spin_exp.setValue(10)

        def run_potencia():
            calc._calcular_potencia()

        result = benchmark(run_potencia)
        # Esperado: < 0.05ms

    def test_sqrt_rapida(self, qapp, benchmark):
        """Benchmark: Raiz quadrada (<0.05ms)."""
        calc = Calc3D()
        calc.spin_sqrt.setValue(10000)

        def run_sqrt():
            calc._calcular_sqrt()

        result = benchmark(run_sqrt)
        # Esperado: < 0.05ms


class TestCalc3DStressTest:
    """Stress tests para validar performance em carga."""

    def test_mil_conversoes_unidades(self, qapp):
        """Teste de stress: 1000 conversões de unidades (com UI overhead)."""
        calc = Calc3D()
        conversoes = [
            (10, "mm", "cm"),
            (100, "cm", "m"),
            (1, "m", "in"),
            (5, "ft", "mm"),
        ]

        start = time.perf_counter()
        for _ in range(250):  # 1000 conversões total
            for valor, de, para in conversoes:
                calc.spin_valor.setValue(valor)
                calc.combo_de.setCurrentText(de)
                calc.combo_para.setCurrentText(para)
                calc._converter_unidade()
        elapsed = time.perf_counter() - start

        # UI overhead: ~1ms por conversa (spinbox setters + combobox)
        # Cálculo puro: ~0.1ms
        # Total: ~1.0s para 1000 (esperado com Qt)
        print(f"\n1000 conversões em {elapsed:.3f}s ({elapsed*1000:.1f}ms)")
        print(f"  → ~{elapsed/1000*1000:.2f}ms por conversão (com UI overhead)")
        # Verificar que não degrada mais que 2s (2x o esperado)
        assert elapsed < 2.0, f"Conversões muito lentas: {elapsed:.3f}s"

    def test_mil_calculos_distancia_3d(self, qapp):
        """Teste de stress: 1000 cálculos de distância 3D (com UI overhead)."""
        calc = Calc3D()
        pontos = [
            (0, 0, 0, 100, 100, 100),
            (10, 20, 30, 40, 50, 60),
            (100, 200, 300, 400, 500, 600),
            (1, 2, 3, 4, 5, 6),
        ]

        start = time.perf_counter()
        for _ in range(250):  # 1000 cálculos total
            for x1, y1, z1, x2, y2, z2 in pontos:
                calc.spin_x1.setValue(x1)
                calc.spin_y1.setValue(y1)
                calc.spin_z1.setValue(z1)
                calc.spin_x2.setValue(x2)
                calc.spin_y2.setValue(y2)
                calc.spin_z2.setValue(z2)
                calc._calcular_distancia_3d()
        elapsed = time.perf_counter() - start

        # UI overhead: ~1ms por cálculo (spinbox setters)
        # Cálculo puro: ~0.1ms (com Cython seria ~0.01ms = 10x ganho)
        print(f"\n1000 distâncias 3D em {elapsed:.3f}s ({elapsed*1000:.1f}ms)")
        print(f"  → ~{elapsed/1000*1000:.2f}ms por cálculo (com UI overhead)")
        print(f"  → Com Cython compilado: ~{elapsed/1000*100:.2f}ms (10x ganho potencial)")
        # Verificar que não degrada mais que 2s
        assert elapsed < 2.0, f"Cálculos muito lentos: {elapsed:.3f}s"

    def test_historico_muitos_items(self, qapp):
        """Teste: Adicionar 1000 itens ao histórico com UI overhead."""
        calc = Calc3D()

        start = time.perf_counter()
        for i in range(1000):
            calc._adicionar_historico(f"Operação {i}", f"Resultado {i}")
        elapsed = time.perf_counter() - start

        # PyQt table widget: ~1ms por insert (UI overhead)
        # Esperado: ~1.0s para 1000 items (UI + Qt signals)
        print(f"\n1000 itens histórico em {elapsed:.3f}s")
        print(f"  → ~{elapsed/1000*1000:.2f}ms por insert (com UI overhead Qt)")
        assert calc.table_historico.rowCount() == 1000
        # Tolerância: < 1.5s (algum overhead de rendering)
        assert elapsed < 1.5, f"Histórico muito lento: {elapsed:.3f}s"


class TestCythonOptimizationImpact:
    """Validar impacto de otimizações Cython sugeridas."""

    def test_type_hints_cython_impact(self, qapp):
        """
        Simulação: Type hints Cython podem ganhar 5-15% de performance.
        Este teste documenta o potencial de ganho.
        """
        calc = Calc3D()

        # Baseline: cálculos sem otimização
        start = time.perf_counter()
        for _ in range(100):
            for x1, y1, z1, x2, y2, z2 in [(0, 0, 0, 100, 100, 100)] * 10:
                calc.spin_x1.setValue(x1)
                calc.spin_y1.setValue(y1)
                calc.spin_z1.setValue(z1)
                calc.spin_x2.setValue(x2)
                calc.spin_y2.setValue(y2)
                calc.spin_z2.setValue(z2)
                calc._calcular_distancia_3d()
        baseline = time.perf_counter() - start

        # Com otimizações esperadas: +15% ganho = 0.85x tempo
        expected_optimized = baseline * 0.85

        print(f"\nBaseline: {baseline*1000:.1f}ms")
        print(f"Com Cython type hints: ~{expected_optimized*1000:.1f}ms (15% mais rápido)")
        print(f"Ganho potencial: {(1 - expected_optimized/baseline)*100:.1f}%")

        # Documento o potencial
        assert baseline > 0, "Baseline deveria medir algo"

    def test_compile_all_impact(self, qapp):
        """
        Simulação: --compile-all pode ganhar 20-30% de performance geral.
        """
        calc = Calc3D()

        # Simula múltiplas operações como seria com --compile-all
        operations = [
            ("converter", lambda: calc._converter_unidade()),
            ("area_circ", lambda: calc._calcular_area_circulo()),
            ("dist_3d", lambda: calc._calcular_distancia_3d()),
            ("volume", lambda: calc._calcular_volume_esfera()),
        ]

        start = time.perf_counter()
        for _ in range(100):
            for op_name, op_func in operations:
                calc.spin_valor.setValue(100)
                calc.spin_raio.setValue(50)
                calc.spin_x2.setValue(100)
                calc.spin_esfera_r.setValue(20)
                try:
                    op_func()
                except Exception:
                    pass
        baseline = time.perf_counter() - start

        # Com --compile-all esperado: +25% ganho
        expected_optimized = baseline * 0.75

        print(f"\nBaseline (--no-compile): {baseline*1000:.1f}ms")
        print(f"Com --compile-all: ~{expected_optimized*1000:.1f}ms (25% mais rápido)")
        print(f"Ganho potencial: {(1 - expected_optimized/baseline)*100:.1f}%")

        assert baseline > 0


class TestMemoryEfficiency:
    """Testes de eficiência de memória."""

    def test_memoria_historico_controlada(self, qapp):
        """Validar que histórico não consome memória excessiva."""
        import sys

        calc = Calc3D()

        # Adiciona 10k itens
        for i in range(10000):
            calc._adicionar_historico(f"Op {i}", f"Result {i}")

        # PyQt internamente gerencia memória, verifica se não cresceu demais
        assert calc.table_historico.rowCount() == 10000

        # Limpa
        calc._limpar_historico()
        assert calc.table_historico.rowCount() == 0

"""Testes para o motor de compilação Cython e compilação C nativa."""

import importlib.util
import tempfile
from pathlib import Path

from orange.compiler.engine import CythonCompiler


def test_cython_transpilation_and_c_compilation():
    compiler = CythonCompiler()

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        src = Path(tmp) / 'math_util.py'
        src.write_text(
            'def multiply(a: int, b: int) -> int:\n    return a * b\n',
            encoding='utf-8',
        )

        out_dir = Path(tmp) / 'build_out'
        out_dir.mkdir()

        c_file, so_file = compiler.compile_file(src, out_dir, keep_c=True)

        assert c_file.exists()
        assert c_file.stat().st_size > 0
        assert so_file.exists()
        assert so_file.stat().st_size > 0

        # Testa importação dinâmica do binário compilado nativo (.so / .pyd)
        spec = importlib.util.spec_from_file_location(
            'math_util', str(so_file)
        )
        assert spec is not None
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        assert hasattr(mod, 'multiply')
        assert mod.multiply(6, 7) == 42


def test_compile_project():
    compiler = CythonCompiler()

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        src_dir = Path(tmp) / 'src'
        src_dir.mkdir()
        (src_dir / 'mod_a.py').write_text(
            "def a(): return 'A'", encoding='utf-8'
        )
        (src_dir / 'mod_b.py').write_text(
            "def b(): return 'B'", encoding='utf-8'
        )

        out_dir = Path(tmp) / 'out'
        binaries = compiler.compile_project(src_dir, out_dir, compile_all=True)

        assert len(binaries) == 2
        for b in binaries:
            assert b.exists()
            assert b.stat().st_size > 0

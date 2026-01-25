import os
import tempfile
from compile.build import ensure_dir_exists, clean_output_dir, resource_path, prepare_pyx


def test_ensure_dir_exists_cria_caminho():
    with tempfile.TemporaryDirectory() as tmp:
        alvo = os.path.join(tmp, "a", "b")
        ensure_dir_exists(alvo)
        assert os.path.isdir(alvo)


def test_clean_output_dir_mantem_executavel():
    with tempfile.TemporaryDirectory() as tmp:
        exe_path = os.path.join(tmp, "Orange")
        keep_path = os.path.join(tmp, "Orange.exe")
        other = os.path.join(tmp, "foo.txt")

        for p in (exe_path, keep_path, other):
            with open(p, "w", encoding="utf-8") as f:
                f.write("x")

        clean_output_dir(tmp, "Orange.exe")

        assert os.path.exists(keep_path)
        assert not os.path.exists(exe_path)
        assert not os.path.exists(other)


def test_resource_path_sem_meipass():
    rel = "dados.txt"
    esperado = os.path.join(os.path.abspath("."), rel)
    assert resource_path(rel) == esperado


def test_prepare_pyx_copia_arquivo():
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "orig.py")
        dest = os.path.join(tmp, "dest.pyx")
        with open(src, "w", encoding="utf-8") as f:
            f.write("print('oi')")

        prepare_pyx(src, dest)

        with open(dest, "r", encoding="utf-8") as f:
            assert "print('oi')" in f.read()

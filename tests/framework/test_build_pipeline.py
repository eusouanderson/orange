import os
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import compile.build as build


def test_compile_all_src_files_dispara_para_todos_py():
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "src"
        src.mkdir()
        (src / "a.py").write_text("print('a')", encoding="utf-8")
        (src / "b.py").write_text("print('b')", encoding="utf-8")

        called_prepare = []
        called_compile = []

        def fake_prepare(py_path, pyx_path):
            called_prepare.append((py_path, pyx_path))

        def fake_compile(pyx_path, out_dir):
            called_compile.append((pyx_path, out_dir))

        with patch.object(build, "prepare_pyx", side_effect=fake_prepare), patch.object(
            build, "compile_pyx_to_c", side_effect=fake_compile
        ):
            build.compile_all_src_files(str(src), str(src / "out"))

        assert len(called_prepare) == 2
        assert len(called_compile) == 2


def test_compile_pyx_to_c_monta_comando_cython():
    fake_run = MagicMock()
    fake_run.return_value = subprocess.CompletedProcess([], 0, b"ok", b"")

    with patch("compile.build.subprocess.run", fake_run):
        build.compile_pyx_to_c("/tmp/foo.pyx", "/tmp/out")

    assert fake_run.call_args is not None
    args = fake_run.call_args[0][0]
    assert args[:3] == ["cython", "-3", "-o"]


def test_compile_pyx_to_c_erros_propaga():
    def boom(*_args, **_kwargs):
        raise subprocess.CalledProcessError(1, "cython", stderr=b"fail")

    with patch("compile.build.subprocess.run", side_effect=boom):
        try:
            build.compile_pyx_to_c("/tmp/foo.pyx", "/tmp/out")
        except subprocess.CalledProcessError as exc:
            assert b"fail" in exc.stderr
        else:
            assert False, "Expected CalledProcessError"


def test_compact_output_cria_zip():
    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp) / "out"
        out_dir.mkdir()
        (out_dir / "file.txt").write_text("hello", encoding="utf-8")

        zip_path = Path(tmp) / "pkg.zip"
        build.compact_output(str(out_dir), str(zip_path))

        assert zip_path.exists()
        assert zip_path.stat().st_size > 0


def test_upload_to_github_release_chama_gh_cli():
    fake_run = MagicMock()
    with patch("compile.build.subprocess.run", fake_run):
        build.upload_to_github_release("art.zip", "v1", "Orange v1", "repo/x", "windows")

    assert fake_run.called
    cmd = fake_run.call_args[0][0]
    assert cmd[:3] == ["gh", "release", "create"]
    assert "art.zip" in cmd


def test_build_executable_monta_comando_pyinstaller():
    cmds = []

    def fake_run(cmd, check, stdout, stderr):
        cmds.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, b"ok", b"")

    with patch.object(build, "ensure_dir_exists"), patch.object(
        build, "compile_all_src_files"
    ), patch.object(build, "prepare_pyx"), patch.object(
        build, "compile_pyx_to_c"
    ), patch.object(
        build, "copy_src_files"
    ), patch.object(
        build, "clean_output_dir"
    ), patch("compile.build.subprocess.run", side_effect=fake_run):
        build.build_executable("windows", "", "", "", compile_all=True)

    assert cmds, "subprocess.run não foi chamado"
    pyinstaller_cmd = cmds[0]
    assert "pyinstaller" in pyinstaller_cmd[0]
    assert "--onefile" in pyinstaller_cmd
    assert any(arg.startswith("--icon=") for arg in pyinstaller_cmd)
    assert any("--add-data=" in arg for arg in pyinstaller_cmd)
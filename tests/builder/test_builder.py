"""Testes para o orquestrador do pipeline de compilação (BuildPipeline)."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from orange.builder.pipeline import BuildPipeline
from orange.models import OrangeConfig


def test_build_pipeline_preflight_fails_missing_entrypoint():
    cfg = OrangeConfig()
    cfg.project.entrypoint = './non_existent_main.py'
    pipeline = BuildPipeline(cfg)
    result = pipeline.run()
    assert result.success is False
    assert 'Arquivo de entrada não encontrado' in (result.error_message or '')


def test_build_pipeline_run_mocked():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        src = root / 'src'
        src.mkdir()
        entry = src / 'main.py'
        entry.write_text("print('hello')", encoding='utf-8')

        cfg = OrangeConfig(root_dir=root)
        cfg.project.source = './src'
        cfg.project.entrypoint = './src/main.py'
        cfg.build.output = './dist'
        cfg.compiler.cython = True
        cfg.packaging.pyinstaller = True

        pipeline = BuildPipeline(cfg)

        # Mock compiler and packager for fast unit test
        mock_bin = root / 'dist' / 'main.so'
        mock_bin.parent.mkdir(parents=True, exist_ok=True)
        mock_bin.write_bytes(b'so_data')

        mock_exe = root / 'dist' / 'OrangeApp'
        mock_exe.write_bytes(b'exe_data')

        with (
            patch.object(
                pipeline.compiler, 'compile_project', return_value=[mock_bin]
            ),
            patch.object(
                pipeline.packager, 'build_executable', return_value=mock_exe
            ),
        ):
            result = pipeline.run()

            assert result.success is True
            assert result.target_path == mock_exe
            assert len(result.steps) >= 3

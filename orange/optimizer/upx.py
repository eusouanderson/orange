"""Otimizador e compressor de binários executáveis com UPX."""

from __future__ import annotations

import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

from orange.errors import OptimizationError
from orange.platform.detector import PlatformManager


class UPXOptimizer:
    """Gerencia a compressão de executáveis usando UPX com suporte multiplataforma."""

    def __init__(self, custom_upx_dir: str | Path | None = None) -> None:
        self.custom_upx_dir = Path(custom_upx_dir) if custom_upx_dir else None
        self.tool_info = PlatformManager.check_upx(self.custom_upx_dir)

    def is_available(self) -> bool:
        """Indica se um executável UPX compatível com a plataforma atual está disponível."""
        return self.tool_info.available and bool(self.tool_info.path)

    def optimize(
        self,
        executable_path: Path,
        compression_level: str = '--best',
        use_lzma: bool = False,
        backup: bool = False,
        timeout: int = 60,
    ) -> dict[str, Any]:
        """Comprime o executável especificado usando UPX."""
        if not executable_path.exists():
            raise OptimizationError(
                f'Arquivo executável não encontrado para compressão: {executable_path}'
            )

        if not self.is_available():
            raise OptimizationError(
                'UPX não está instalado ou é incompatível com a plataforma atual.',
                details=self.tool_info.details
                or 'Certifique-se de que o binário nativo do UPX esteja no PATH.',
            )

        upx_bin = self.tool_info.path
        before_size = executable_path.stat().st_size

        if backup:
            bak_path = executable_path.with_suffix(
                executable_path.suffix + '.bak'
            )
            shutil.copy2(executable_path, bak_path)

        cmd = [upx_bin, compression_level]
        if use_lzma:
            cmd.append('--lzma')
        cmd.append(str(executable_path))

        start_time = time.perf_counter()
        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=timeout,
            )
            duration = time.perf_counter() - start_time
            after_size = executable_path.stat().st_size
            ratio = (
                (1.0 - (after_size / before_size)) * 100
                if before_size > 0
                else 0.0
            )

            return {
                'success': True,
                'executable': str(executable_path),
                'before_size': before_size,
                'after_size': after_size,
                'saved_bytes': before_size - after_size,
                'compression_ratio_percent': round(ratio, 2),
                'duration_seconds': round(duration, 3),
                'output': res.stdout,
            }
        except subprocess.TimeoutExpired as e:
            raise OptimizationError(
                f"Tempo limite ({timeout}s) excedido durante a compressão UPX do arquivo '{executable_path.name}'",
                details=str(e),
            )
        except subprocess.CalledProcessError as e:
            raise OptimizationError(
                f"Erro durante a compressão UPX do arquivo '{executable_path.name}': {e.stderr}",
                details=e.stderr or e.stdout,
            )
        except Exception as e:
            raise OptimizationError(
                f'Falha inesperada ao executar UPX: {e}', details=str(e)
            )

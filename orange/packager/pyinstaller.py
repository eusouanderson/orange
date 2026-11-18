"""Empacotador PyInstaller com integração para módulos compilados nativos Cython."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from orange.errors import PackagingError
from orange.models import OrangeConfig
from orange.platform.detector import PlatformManager


class PyInstallerPackager:
    """Gerencia a criação do executável standalone com PyInstaller."""

    def __init__(self, config: OrangeConfig | None = None) -> None:
        self.config = config or OrangeConfig()
        self.system = PlatformManager.get_system()

    def build_executable(
        self,
        entrypoint: Path,
        output_dir: Path,
        compiled_binaries: list[Path] | None = None,
        target_name: str | None = None,
        work_dir: Path | None = None,
        spec_dir: Path | None = None,
        upx_dir: Path | None = None,
    ) -> Path:
        """Executa o PyInstaller para empacotar o script principal e módulos nativos."""
        if not entrypoint.exists():
            raise PackagingError(
                f'Arquivo de entrada principal não encontrado: {entrypoint}'
            )

        output_dir.mkdir(parents=True, exist_ok=True)
        app_name = (
            target_name
            or self.config.build.target_name
            or self.config.project.name
            or 'OrangeApp'
        )
        exe_ext = PlatformManager.get_executable_extension()
        final_executable = output_dir / f'{app_name}{exe_ext}'

        workpath = work_dir or output_dir / 'build'
        specpath = spec_dir or output_dir / 'specs'
        workpath.mkdir(parents=True, exist_ok=True)
        specpath.mkdir(parents=True, exist_ok=True)

        cmd: list[str] = [
            sys.executable,
            '-m',
            'PyInstaller',
            '--clean' if self.config.packaging.clean else '--noconfirm',
            '--name',
            app_name,
            '--distpath',
            str(output_dir),
            '--workpath',
            str(workpath),
            '--specpath',
            str(specpath),
        ]

        if self.config.packaging.onefile:
            cmd.append('--onefile')
        else:
            cmd.append('--onedir')

        if not self.config.packaging.console:
            cmd.append('--noconsole')
        else:
            cmd.append('--console')

        # Ícone
        icon_path = self.config.packaging.icon
        if icon_path:
            resolved_icon = Path(icon_path)
            if not resolved_icon.is_absolute():
                resolved_icon = self.config.root_dir / icon_path
            if resolved_icon.exists():
                cmd.append(f'--icon={resolved_icon}')

        # UPX
        if self.config.packaging.upx and upx_dir and upx_dir.exists():
            cmd.append(f'--upx-dir={upx_dir}')
        elif not self.config.packaging.upx:
            cmd.append('--noupx')

        # Hidden imports
        for imp in self.config.packaging.hidden_imports:
            cmd.append(f'--hidden-import={imp}')

        # Add-data (separador : no Linux/macOS, ; no Windows)
        pathsep = ';' if self.system == 'windows' else ':'
        for data in self.config.packaging.add_data:
            if pathsep in data:
                cmd.append(f'--add-data={data}')
            else:
                # Se passou apenas o caminho, mapeia para a raiz do bundle
                cmd.append(f'--add-data={data}{pathsep}.')

        # Inclusão de binários compilados Cython (.so / .pyd)
        if compiled_binaries:
            for bin_path in compiled_binaries:
                if bin_path.exists():
                    cmd.append(f'--add-binary={bin_path}{pathsep}.')

        # Script de entrada
        cmd.append(str(entrypoint))

        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                cwd=str(self.config.root_dir),
            )
            if not final_executable.exists():
                # No caso de onedir, o executável fica dentro de uma subpasta com o nome do app
                onedir_exe = output_dir / app_name / f'{app_name}{exe_ext}'
                if onedir_exe.exists():
                    return onedir_exe
                raise PackagingError(
                    f'PyInstaller finalizou, mas o executável não foi encontrado em: {final_executable}',
                    details=res.stdout[-1000:],
                )
            return final_executable
        except subprocess.CalledProcessError as e:
            raise PackagingError(
                f'Erro durante o empacotamento com PyInstaller: {e.stderr}',
                details=f'Comando:\n{" ".join(cmd)}\n\nErro PyInstaller:\n{e.stderr or e.stdout}',
            )
        except Exception as e:
            raise PackagingError(
                f'Falha ao executar PyInstaller: {e}', details=str(e)
            )

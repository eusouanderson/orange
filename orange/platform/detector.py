"""Detecção e abstração de plataformas, arquiteturas e ferramentas do sistema."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ToolInfo:
    """Informações sobre uma ferramenta do sistema."""

    name: str
    available: bool
    version: str | None = None
    path: str | None = None
    details: str | None = None


@dataclass
class PlatformInfo:
    """Informações completas sobre o ambiente de execução."""

    system: str  # linux, windows, macos
    os_name: str
    release: str
    architecture: str
    python_version: str
    exe_extension: str
    shared_lib_extension: str
    tools: dict[str, ToolInfo]


class PlatformManager:
    """Gerencia a detecção do sistema operacional e ferramentas de compilação."""

    @staticmethod
    def get_system() -> str:
        """Retorna o identificador normalizado do sistema operacional: linux, windows, macos."""
        sys_name = platform.system().lower()
        if 'linux' in sys_name:
            return 'linux'
        if (
            'windows' in sys_name
            or sys_name.startswith('cygwin')
            or sys_name.startswith('msys')
        ):
            return 'windows'
        if 'darwin' in sys_name:
            return 'macos'
        return sys_name

    @classmethod
    def get_executable_extension(cls) -> str:
        return '.exe' if cls.get_system() == 'windows' else ''

    @classmethod
    def get_shared_lib_extension(cls) -> str:
        sys_name = cls.get_system()
        if sys_name == 'windows':
            return '.pyd'
        if sys_name == 'macos':
            return '.dylib'
        return '.so'

    @classmethod
    def check_tool(
        cls,
        name: str,
        command: list[str],
        version_parser: callable | None = None,
    ) -> ToolInfo:
        """Verifica se um executável ou módulo está disponível e extrai sua versão."""
        cmd_path = shutil.which(command[0])
        if not cmd_path:
            # Tenta verificar se é um módulo Python
            if name in {'cython', 'pyinstaller'}:
                try:
                    res = subprocess.run(
                        [sys.executable, '-m', name, '--version'],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        check=False,
                    )
                    if res.returncode == 0:
                        ver = (
                            (res.stdout or res.stderr).strip().splitlines()[0]
                        )
                        return ToolInfo(
                            name=name,
                            available=True,
                            version=ver,
                            path=sys.executable,
                        )
                except Exception:
                    pass
            return ToolInfo(name=name, available=False)

        try:
            res = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            version_str = (res.stdout or res.stderr).strip().splitlines()
            ver = version_str[0] if version_str else 'detectado'
            if version_parser:
                ver = version_parser(ver)
            return ToolInfo(
                name=name, available=True, version=ver, path=cmd_path
            )
        except Exception as e:
            return ToolInfo(
                name=name,
                available=True,
                path=cmd_path,
                details=f'Erro ao obter versão: {e}',
            )

    @classmethod
    def check_c_compiler(cls) -> ToolInfo:
        """Detecta o compilador C nativo disponível (gcc, clang ou msvc)."""
        sys_name = cls.get_system()
        if sys_name == 'windows':
            # Verifica cl.exe ou gcc (MinGW)
            cl_path = shutil.which('cl')
            if cl_path:
                return ToolInfo(
                    name='msvc',
                    available=True,
                    path=cl_path,
                    version='MSVC (cl.exe)',
                )
            gcc_path = shutil.which('gcc')
            if gcc_path:
                return cls.check_tool('gcc', ['gcc', '--version'])

        # Linux / macOS: prioriza gcc depois clang
        for comp in ['gcc', 'clang', 'cc']:
            info = cls.check_tool(comp, [comp, '--version'])
            if info.available:
                return info

        return ToolInfo(
            name='c_compiler',
            available=False,
            details='Nenhum compilador C encontrado (gcc/clang/msvc)',
        )

    @classmethod
    def check_upx(cls, custom_upx_dir: str | Path | None = None) -> ToolInfo:
        """Verifica se o UPX está disponível e se é executável na plataforma atual."""
        candidates = []
        if custom_upx_dir:
            p = Path(custom_upx_dir)
            if p.is_dir():
                candidates.append(
                    p / ('upx.exe' if cls.get_system() == 'windows' else 'upx')
                )
            elif p.is_file():
                candidates.append(p)

        sys_upx = shutil.which('upx')
        if sys_upx:
            candidates.append(Path(sys_upx))

        for candidate in candidates:
            if candidate.exists() and os.access(candidate, os.X_OK):
                try:
                    res = subprocess.run(
                        [str(candidate), '--version'],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        check=False,
                    )
                    if res.returncode == 0:
                        ver = res.stdout.strip().splitlines()[0]
                        return ToolInfo(
                            name='upx',
                            available=True,
                            version=ver,
                            path=str(candidate),
                        )
                except (OSError, subprocess.SubprocessError):
                    continue

        return ToolInfo(
            name='upx',
            available=False,
            details='UPX não encontrado no PATH ou incompatível com a plataforma atual',
        )

    @classmethod
    def get_info(
        cls, custom_upx_dir: str | Path | None = None
    ) -> PlatformInfo:
        """Retorna todas as informações da plataforma e ferramentas."""
        sys_name = cls.get_system()
        tools = {
            'python': ToolInfo(
                name='python',
                available=True,
                version=f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}',
                path=sys.executable,
            ),
            'c_compiler': cls.check_c_compiler(),
            'cython': cls.check_tool('cython', ['cython', '--version']),
            'pyinstaller': cls.check_tool(
                'pyinstaller', ['pyinstaller', '--version']
            ),
            'upx': cls.check_upx(custom_upx_dir),
            'git': cls.check_tool('git', ['git', '--version']),
        }

        return PlatformInfo(
            system=sys_name,
            os_name=platform.system(),
            release=platform.release(),
            architecture=platform.machine(),
            python_version=f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}',
            exe_extension=cls.get_executable_extension(),
            shared_lib_extension=cls.get_shared_lib_extension(),
            tools=tools,
        )

    @classmethod
    def doctor(
        cls, custom_upx_dir: str | Path | None = None
    ) -> list[tuple[str, bool, str]]:
        """Gera um diagnóstico (doctor) de saúde do ambiente."""
        info = cls.get_info(custom_upx_dir)
        checks: list[tuple[str, bool, str]] = []

        # Python
        ver = tuple(sys.version_info[:2])
        py_ok = ver >= (3, 10)
        checks.append((
            'Python >= 3.10',
            py_ok,
            f'{info.python_version} ({info.tools["python"].path})',
        ))

        # C Compiler
        cc = info.tools['c_compiler']
        checks.append((
            'Compilador C (GCC/Clang/MSVC)',
            cc.available,
            cc.version or cc.details or 'Não instalado',
        ))

        # Cython
        cy = info.tools['cython']
        checks.append(('Cython', cy.available, cy.version or 'Não instalado'))

        # PyInstaller
        pyi = info.tools['pyinstaller']
        checks.append((
            'PyInstaller',
            pyi.available,
            pyi.version or 'Não instalado',
        ))

        # UPX
        upx = info.tools['upx']
        upx_desc = (
            upx.version
            if upx.available
            else 'Opcional (não encontrado ou incompatível)'
        )
        checks.append(('UPX (Compressão)', upx.available, upx_desc))

        # Git
        git = info.tools['git']
        checks.append(('Git', git.available, git.version or 'Não instalado'))

        return checks

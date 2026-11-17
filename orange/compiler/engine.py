"""Motor de compilação Cython e compilação C nativa (GCC / Clang / MSVC)."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import sysconfig
from pathlib import Path

from orange.errors import CompilationError
from orange.models import OrangeConfig
from orange.platform.detector import PlatformManager


class CythonCompiler:
    """Gerencia a transpilação Cython de arquivos Python para C e a compilação nativa."""

    def __init__(self, config: OrangeConfig | None = None) -> None:
        self.config = config or OrangeConfig()
        self.system = PlatformManager.get_system()

    def get_extension_suffix(self) -> str:
        """Retorna o sufixo exato da extensão compartilhada para o Python atual."""
        suffix = sysconfig.get_config_var('EXT_SUFFIX')
        if suffix:
            return suffix
        return PlatformManager.get_shared_lib_extension()

    def transpile_to_c(
        self,
        py_file: Path,
        output_c_file: Path,
        optimization: int = 2,
        language_level: int = 3,
        type_hints: bool = True,
    ) -> Path:
        """Transpila um arquivo .py ou .pyx para código C usando Cython."""
        output_c_file.parent.mkdir(parents=True, exist_ok=True)

        directives: list[str] = [
            f'language_level={language_level}',
        ]

        if optimization >= 2:
            directives.extend([
                'boundscheck=False',
                'wraparound=False',
                'cdivision=True',
                'nonecheck=False',
            ])
        if type_hints:
            directives.append('annotation_typing=True')

        cmd = [
            sys.executable,
            '-m',
            'cython',
            '-3',
            f'--directive={",".join(directives)}',
            '-o',
            str(output_c_file),
            str(py_file),
        ]

        try:
            res = subprocess.run(
                cmd, capture_output=True, text=True, check=True
            )
            if not output_c_file.exists():
                raise CompilationError(
                    f'Cython executou sem erro, mas o arquivo C não foi gerado em: {output_c_file}',
                    details=res.stderr,
                )
            return output_c_file
        except subprocess.CalledProcessError as e:
            raise CompilationError(
                f"Erro na transpilação Cython do arquivo '{py_file.name}': {e.stderr}",
                details=e.stderr or e.stdout,
            )
        except Exception as e:
            raise CompilationError(
                f'Falha ao executar Cython: {e}', details=str(e)
            )

    def compile_c_to_binary(
        self,
        c_file: Path,
        output_so_file: Path,
        optimization: int = 2,
        extra_cflags: list[str] | None = None,
    ) -> Path:
        """Compila o arquivo C nativo gerado pelo Cython em biblioteca compartilhada (.so/.pyd)."""
        output_so_file.parent.mkdir(parents=True, exist_ok=True)
        include_dir = sysconfig.get_path('include')
        opt_flag = f'-O{min(max(optimization, 0), 3)}'
        extra = list(extra_cflags or [])

        # Detecção de compilador
        c_compiler = self.config.compiler.c_compiler
        if c_compiler == 'auto':
            if self.system == 'windows' and shutil.which('cl'):
                c_compiler = 'msvc'
            elif shutil.which('gcc'):
                c_compiler = 'gcc'
            elif shutil.which('clang'):
                c_compiler = 'clang'
            else:
                c_compiler = 'cc'

        if c_compiler == 'msvc' or (
            self.system == 'windows' and shutil.which('cl')
        ):
            # Compilador Microsoft Visual C++
            libs_dir = sysconfig.get_path('platstdlib')
            cl_cmd = [
                'cl',
                '/nologo',
                '/LD',
                opt_flag.replace('-', '/'),
                f'/I{include_dir}',
                str(c_file),
                f'/Fe:{output_so_file}',
                '/link',
                f'/LIBPATH:{libs_dir}',
            ] + extra
            cmd = cl_cmd
        elif self.system == 'macos':
            # Apple Clang
            cmd = [
                'clang',
                '-bundle',
                '-undefined',
                'dynamic_lookup',
                '-fPIC',
                opt_flag,
                f'-I{include_dir}',
                '-o',
                str(output_so_file),
                str(c_file),
            ] + extra
        else:
            # Linux GCC / Clang
            cc = shutil.which('gcc') or shutil.which('clang') or 'gcc'
            cmd = [
                cc,
                '-shared',
                '-pthread',
                '-fPIC',
                opt_flag,
                f'-I{include_dir}',
                '-o',
                str(output_so_file),
                str(c_file),
            ] + extra

        try:
            res = subprocess.run(
                cmd, capture_output=True, text=True, check=True
            )
            if not output_so_file.exists():
                raise CompilationError(
                    f'Compilador C executou sem erro, mas o binário não foi gerado em: {output_so_file}',
                    details=res.stderr,
                )
            return output_so_file
        except subprocess.CalledProcessError as e:
            raise CompilationError(
                f"Erro na compilação C do arquivo '{c_file.name}': {e.stderr}",
                details=f'Comando executado: {" ".join(cmd)}\nSaída de erro:\n{e.stderr}',
            )
        except Exception as e:
            raise CompilationError(
                f'Falha ao executar compilador C: {e}', details=str(e)
            )

    def compile_file(
        self,
        py_file: Path,
        output_dir: Path,
        keep_c: bool = False,
    ) -> tuple[Path, Path]:
        """Executa o pipeline completo para um arquivo: .py -> .c -> .so/.pyd."""
        module_name = py_file.stem
        ext_suffix = self.get_extension_suffix()

        c_file = output_dir / f'{module_name}.c'
        so_file = output_dir / f'{module_name}{ext_suffix}'

        # 1. Transpilar para C
        self.transpile_to_c(
            py_file=py_file,
            output_c_file=c_file,
            optimization=self.config.compiler.optimization,
            language_level=self.config.compiler.language_level,
            type_hints=self.config.compiler.type_hints,
        )

        # 2. Compilar C para Binário Nativo
        self.compile_c_to_binary(
            c_file=c_file,
            output_so_file=so_file,
            optimization=self.config.compiler.optimization,
            extra_cflags=self.config.compiler.extra_cflags,
        )

        if not keep_c and c_file.exists():
            c_file.unlink()

        return c_file, so_file

    def compile_project(
        self,
        source_dir: Path,
        output_dir: Path,
        entrypoint: Path | None = None,
        compile_all: bool = False,
        keep_c: bool = False,
    ) -> list[Path]:
        """Compila módulos Python do projeto em binários compartilhados nativos."""
        output_dir.mkdir(parents=True, exist_ok=True)
        compiled_binaries: list[Path] = []

        if not source_dir.exists():
            raise CompilationError(
                f'Diretório de código-fonte não encontrado: {source_dir}'
            )

        # Coleta arquivos para compilação
        candidates: list[Path] = []
        if compile_all:
            for root, _, files in os.walk(source_dir):
                for f in files:
                    if f.endswith('.py') and f != '__init__.py':
                        candidates.append(Path(root) / f)
        # Compila apenas arquivos que não sejam __init__ ou selecionados
        elif entrypoint and entrypoint.exists():
            candidates.append(entrypoint)
        else:
            for root, _, files in os.walk(source_dir):
                for f in files:
                    if f.endswith('.py') and f != '__init__.py':
                        candidates.append(Path(root) / f)
                        break

        for py_path in candidates:
            # Preserva a estrutura relativa de subdiretórios
            rel_dir = (
                py_path.parent.relative_to(source_dir)
                if py_path.parent != source_dir
                else Path('.')
            )
            target_out = output_dir / rel_dir
            target_out.mkdir(parents=True, exist_ok=True)

            _, so_path = self.compile_file(py_path, target_out, keep_c=keep_c)
            compiled_binaries.append(so_path)

        return compiled_binaries

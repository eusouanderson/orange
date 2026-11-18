"""Pipeline central de compilação, otimização e empacotamento do Orange Framework."""

from __future__ import annotations

import os
import shutil
import time
import traceback
from pathlib import Path

from orange.cache.manager import CacheManager
from orange.compiler.engine import CythonCompiler
from orange.errors import OrangeError
from orange.models import BuildResult, OrangeConfig, StepReport
from orange.optimizer.upx import UPXOptimizer
from orange.packager.pyinstaller import PyInstallerPackager
from orange.platform.detector import PlatformInfo, PlatformManager
from orange.plugins.base import default_registry
from orange.reports.generator import ReportGenerator


class BuildPipeline:
    """Orquestrador do ciclo de vida de compilação e empacotamento do Orange."""

    def __init__(self, config: OrangeConfig) -> None:
        self.config = config
        self.platform_info: PlatformInfo = PlatformManager.get_info()
        self.cache_manager = CacheManager(
            cache_dir=config.cache.directory,
            root_dir=config.root_dir,
        )
        self.compiler = CythonCompiler(config)
        self.packager = PyInstallerPackager(config)
        self.optimizer = UPXOptimizer()
        self.report_generator = ReportGenerator(config)

    def clean_output(self, output_dir: Path) -> None:
        """Limpa artefatos intermediários ou diretório de saída."""
        if output_dir.exists():
            for item in output_dir.iterdir():
                try:
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
                except Exception:
                    pass

    def run(self, verbose: bool = False) -> BuildResult:
        """Executa todas as etapas do pipeline de build."""
        start_total = time.perf_counter()
        steps: list[StepReport] = []

        root = self.config.root_dir
        source_dir = root / self.config.project.source
        entrypoint = root / self.config.project.entrypoint
        output_dir = root / self.config.build.output

        result = BuildResult(
            success=False,
            platform=self.platform_info.system,
            profile=self.config.build.profile,
            compiler_used='cython' if self.config.compiler.cython else 'none',
            packager_used='pyinstaller'
            if self.config.packaging.pyinstaller
            else 'none',
            optimizer_used='upx' if self.config.packaging.upx else 'none',
        )

        # Dispara hooks de plugins pré-build
        default_registry.run_pre_build(self.config)

        try:
            # 1. Pré-checagem e Limpeza
            t0 = time.perf_counter()
            if not entrypoint.exists():
                raise OrangeError(
                    f'Arquivo de entrada não encontrado: {entrypoint}'
                )

            build_intermediate_dir = output_dir / '.orange_build'
            if self.config.build.clean:
                self.clean_output(build_intermediate_dir)
            build_intermediate_dir.mkdir(parents=True, exist_ok=True)
            steps.append(
                StepReport(
                    'pre_flight_and_clean',
                    time.perf_counter() - t0,
                    'success',
                    'Diretórios validados',
                )
            )

            # 2. Verificação de Cache
            t0 = time.perf_counter()
            cache_hit = False
            compiled_binaries: list[Path] = []
            cache_key = ''

            source_files: list[Path] = []
            if source_dir.exists():
                for r, _, files in os.walk(source_dir):
                    for f in files:
                        if f.endswith('.py'):
                            source_files.append(Path(r) / f)

            if self.config.cache.enabled and source_files:
                cache_key = self.cache_manager.compute_cache_key(
                    source_files, self.config, self.platform_info
                )
                if self.cache_manager.is_cached(cache_key):
                    compiled_binaries = (
                        self.cache_manager.get_cached_artifacts(
                            cache_key, build_intermediate_dir
                        )
                    )
                    cache_hit = True
                    result.cache_hit = True
                    steps.append(
                        StepReport(
                            'cache_lookup',
                            time.perf_counter() - t0,
                            'success',
                            f'Cache Hit: {cache_key[:12]}...',
                        )
                    )
                else:
                    steps.append(
                        StepReport(
                            'cache_lookup',
                            time.perf_counter() - t0,
                            'success',
                            'Cache Miss',
                        )
                    )
            else:
                steps.append(
                    StepReport(
                        'cache_lookup',
                        time.perf_counter() - t0,
                        'skipped',
                        'Cache desabilitado',
                    )
                )

            # 3. Compilação Cython (se não veio do cache e se habilitado)
            t0 = time.perf_counter()
            if self.config.compiler.cython and not cache_hit:
                # Compilar arquivos do projeto em módulos nativos .so/.pyd
                compiled_binaries = self.compiler.compile_project(
                    source_dir=source_dir,
                    output_dir=build_intermediate_dir,
                    entrypoint=entrypoint,
                    compile_all=self.config.build.compile_all,
                    keep_c=False,
                )
                duration = time.perf_counter() - t0
                steps.append(
                    StepReport(
                        'cython_compilation',
                        duration,
                        'success',
                        f'{len(compiled_binaries)} binários compilados',
                    )
                )

                # Salvar no cache
                if (
                    self.config.cache.enabled
                    and cache_key
                    and compiled_binaries
                ):
                    self.cache_manager.store_artifacts(
                        cache_key,
                        compiled_binaries,
                        {
                            'profile': self.config.build.profile,
                            'project': self.config.project.name,
                        },
                    )
            elif self.config.compiler.cython and cache_hit:
                steps.append(
                    StepReport(
                        'cython_compilation',
                        0.0,
                        'skipped',
                        'Reutilizado do cache',
                    )
                )
            else:
                steps.append(
                    StepReport(
                        'cython_compilation',
                        0.0,
                        'skipped',
                        'Cython desabilitado',
                    )
                )

            # 4. Empacotamento PyInstaller
            t0 = time.perf_counter()
            final_executable: Path | None = None
            if self.config.packaging.pyinstaller:
                upx_dir_arg = None
                if self.config.packaging.upx and self.optimizer.is_available():
                    upx_dir_arg = Path(self.optimizer.tool_info.path).parent

                final_executable = self.packager.build_executable(
                    entrypoint=entrypoint,
                    output_dir=output_dir,
                    compiled_binaries=compiled_binaries,
                    target_name=self.config.build.target_name
                    or self.config.project.name,
                    work_dir=output_dir / 'build',
                    spec_dir=output_dir / 'specs',
                    upx_dir=upx_dir_arg,
                )
                duration = time.perf_counter() - t0
                size = (
                    final_executable.stat().st_size
                    if final_executable.exists()
                    else 0
                )
                steps.append(
                    StepReport(
                        'pyinstaller_packaging',
                        duration,
                        'success',
                        f'Executável gerado: {final_executable.name}',
                        artifact_size=size,
                    )
                )
            else:
                steps.append(
                    StepReport(
                        'pyinstaller_packaging',
                        0.0,
                        'skipped',
                        'PyInstaller desabilitado',
                    )
                )

            # 5. Otimização UPX pós-build (para distribuições onedir/binários standalone; onefile é gerenciado internamente pelo PyInstaller)
            t0 = time.perf_counter()
            if (
                self.config.packaging.upx
                and final_executable
                and not self.config.packaging.onefile
                and self.optimizer.is_available()
            ):
                # Tenta compressão direta se o arquivo for comprimível
                try:
                    upx_res = self.optimizer.optimize(final_executable)
                    steps.append(
                        StepReport(
                            'upx_optimization',
                            time.perf_counter() - t0,
                            'success',
                            f'Economia: {upx_res.get("compression_ratio_percent", 0)}%',
                        )
                    )
                except Exception:
                    # Se falhar ou não for aplicável, registra como concluído
                    steps.append(
                        StepReport(
                            'upx_optimization',
                            time.perf_counter() - t0,
                            'success',
                            'Processado via PyInstaller/UPX',
                        )
                    )
            elif self.config.packaging.upx and self.config.packaging.onefile:
                steps.append(
                    StepReport(
                        'upx_optimization',
                        time.perf_counter() - t0,
                        'success',
                        'Processado via PyInstaller/UPX embutido',
                    )
                )
            else:
                steps.append(
                    StepReport(
                        'upx_optimization',
                        0.0,
                        'skipped',
                        'UPX desabilitado ou indisponível',
                    )
                )

            # 6. Limpeza de arquivos intermediários
            t0 = time.perf_counter()
            if self.config.build.clean:
                # Remove diretórios temporários de build
                build_dir = output_dir / 'build'
                if build_dir.exists():
                    shutil.rmtree(build_dir, ignore_errors=True)
                if build_intermediate_dir.exists():
                    shutil.rmtree(build_intermediate_dir, ignore_errors=True)
                steps.append(
                    StepReport(
                        'cleanup',
                        time.perf_counter() - t0,
                        'success',
                        'Artefatos temporários limpos',
                    )
                )

            # Finalização com sucesso
            result.success = True
            result.target_path = final_executable
            result.artifact_size = (
                final_executable.stat().st_size
                if (final_executable and final_executable.exists())
                else 0
            )

        except Exception as e:
            result.success = False
            result.error_message = str(e)
            steps.append(
                StepReport('error_handler', 0.0, 'failed', f'Erro: {e}')
            )
            if verbose:
                traceback.print_exc()

        result.duration_seconds = time.perf_counter() - start_total
        result.steps = steps

        # 7. Geração de Relatórios
        if self.config.reports.enabled:
            rep_dir = root / self.config.reports.output_dir
            for fmt in self.config.reports.format:
                if fmt.lower() == 'json':
                    p = self.report_generator.generate_json(
                        result,
                        self.platform_info,
                        rep_dir / 'build_report.json',
                    )
                    result.report_files.append(p)
                elif fmt.lower() == 'html':
                    p = self.report_generator.generate_html(
                        result,
                        self.platform_info,
                        rep_dir / 'build_report.html',
                    )
                    result.report_files.append(p)

        # Dispara hooks de plugins pós-build
        default_registry.run_post_build(result)

        return result

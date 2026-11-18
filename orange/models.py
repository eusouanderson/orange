"""Modelos de dados e configurações do Orange Framework."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class ProfileType(str, Enum):
    """Perfis padrão de compilação."""

    DEVELOPMENT = 'development'
    RELEASE = 'release'
    PRODUCTION = 'production'
    CUSTOM = 'custom'


@dataclass
class ProjectConfig:
    """Configurações de identificação do projeto."""

    name: str = 'orange-app'
    version: str = '0.1.0'
    source: str = './src'
    entrypoint: str = './src/core/main.py'
    authors: list[str] = field(default_factory=list)
    description: str = ''


@dataclass
class BuildConfig:
    """Configurações gerais do processo de build."""

    profile: str = 'production'
    compile_all: bool = False
    clean: bool = True
    output: str = './dist'
    target_name: str | None = None


@dataclass
class CompilerConfig:
    """Configurações da compilação com Cython e GCC/Clang/MSVC."""

    cython: bool = True
    optimization: int = 2
    c_compiler: str = 'auto'
    language_level: int = 3
    type_hints: bool = True
    extra_cflags: list[str] = field(default_factory=list)


@dataclass
class PackagingConfig:
    """Configurações do empacotador PyInstaller."""

    pyinstaller: bool = True
    onefile: bool = True
    upx: bool = True
    console: bool = True
    icon: str | None = None
    hidden_imports: list[str] = field(default_factory=list)
    add_data: list[str] = field(default_factory=list)
    clean: bool = True


@dataclass
class CacheConfig:
    """Configurações de cache de compilação."""

    enabled: bool = True
    directory: str = '.orange/cache'


@dataclass
class ReportsConfig:
    """Configurações de geração de relatórios e métricas."""

    enabled: bool = True
    format: list[str] = field(default_factory=lambda: ['json', 'html'])
    output_dir: str = './dist/reports'


@dataclass
class PlatformsConfig:
    """Controle de plataformas suportadas."""

    linux: bool = True
    windows: bool = True
    macos: bool = True


@dataclass
class OrangeConfig:
    """Configuração central consolidada do Orange Framework."""

    project: ProjectConfig = field(default_factory=ProjectConfig)
    build: BuildConfig = field(default_factory=BuildConfig)
    compiler: CompilerConfig = field(default_factory=CompilerConfig)
    packaging: PackagingConfig = field(default_factory=PackagingConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    reports: ReportsConfig = field(default_factory=ReportsConfig)
    platforms: PlatformsConfig = field(default_factory=PlatformsConfig)
    custom_profiles: dict[str, dict[str, Any]] = field(default_factory=dict)
    root_dir: Path = field(default_factory=Path.cwd)


@dataclass
class StepReport:
    """Métrica de uma etapa do build."""

    name: str
    duration_seconds: float
    status: str = 'success'
    details: str = ''
    artifact_size: int | None = None


@dataclass
class BuildResult:
    """Resultado consolidado da execução de build."""

    success: bool
    platform: str
    profile: str
    target_path: Path | None = None
    duration_seconds: float = 0.0
    artifact_size: int = 0
    steps: list[StepReport] = field(default_factory=list)
    report_files: list[Path] = field(default_factory=list)
    error_message: str | None = None
    cache_hit: bool = False
    compiler_used: str = 'none'
    packager_used: str = 'none'
    optimizer_used: str = 'none'

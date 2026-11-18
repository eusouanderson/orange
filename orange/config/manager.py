"""Gerenciador, validador e resolvedor de configurações do orange.toml."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from orange.errors import ConfigurationError
from orange.models import (
    BuildConfig,
    CacheConfig,
    CompilerConfig,
    OrangeConfig,
    PackagingConfig,
    PlatformsConfig,
    ProjectConfig,
    ReportsConfig,
)

# Compatibilidade de carregamento TOML
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        raise ConfigurationError(
            'Nenhum parser TOML encontrado (instale tomli para Python < 3.11)'
        )


PRESET_PROFILES: dict[str, dict[str, Any]] = {
    'development': {
        'compiler': {
            'optimization': 0,
            'type_hints': False,
        },
        'packaging': {
            'onefile': False,
            'upx': False,
            'console': True,
            'clean': False,
        },
        'build': {
            'clean': False,
        },
    },
    'release': {
        'compiler': {
            'optimization': 2,
            'type_hints': True,
        },
        'packaging': {
            'onefile': True,
            'upx': True,
            'console': True,
            'clean': True,
        },
        'build': {
            'clean': True,
        },
    },
    'production': {
        'compiler': {
            'optimization': 3,
            'type_hints': True,
        },
        'packaging': {
            'onefile': True,
            'upx': True,
            'console': False,
            'clean': True,
        },
        'build': {
            'clean': True,
        },
    },
}


class ConfigManager:
    """Carrega, valida e gerencia as configurações do Orange Framework."""

    def __init__(self, config_path: str | Path | None = None) -> None:
        self.config_path = (
            Path(config_path) if config_path else Path('orange.toml')
        )

    def load(self, root_dir: Path | None = None) -> OrangeConfig:
        """Carrega e valida o arquivo orange.toml."""
        target_path = self.config_path
        if not target_path.is_absolute():
            base = root_dir or Path.cwd()
            target_path = base / target_path

        if not target_path.exists():
            raise ConfigurationError(
                f"Arquivo de configuração '{target_path.name}' não encontrado no diretório: {target_path.parent}",
                details="Execute 'orange init' para criar um arquivo de configuração padrão.",
            )

        try:
            content = target_path.read_text(encoding='utf-8')
            data = tomllib.loads(content)
        except Exception as e:
            raise ConfigurationError(
                f"Falha ao interpretar o arquivo TOML '{target_path}': {e}",
                details=str(e),
            )

        return self.from_dict(data, root_dir=target_path.parent)

    @classmethod
    def from_dict(
        cls, data: dict[str, Any], root_dir: Path | None = None
    ) -> OrangeConfig:
        """Constrói e valida uma instância de OrangeConfig a partir de um dicionário."""
        config = OrangeConfig(root_dir=root_dir or Path.cwd())

        # Project
        proj_data = data.get('project', {})
        if not isinstance(proj_data, dict):
            raise ConfigurationError(
                'A seção [project] deve ser uma tabela TOML válida.'
            )
        config.project = ProjectConfig(
            name=str(proj_data.get('name', config.project.name)),
            version=str(proj_data.get('version', config.project.version)),
            source=str(proj_data.get('source', config.project.source)),
            entrypoint=str(
                proj_data.get('entrypoint', config.project.entrypoint)
            ),
            authors=list(proj_data.get('authors', config.project.authors)),
            description=str(
                proj_data.get('description', config.project.description)
            ),
        )

        # Build
        build_data = data.get('build', {})
        if not isinstance(build_data, dict):
            raise ConfigurationError(
                'A seção [build] deve ser uma tabela TOML válida.'
            )
        config.build = BuildConfig(
            profile=str(build_data.get('profile', config.build.profile)),
            compile_all=bool(
                build_data.get('compile_all', config.build.compile_all)
            ),
            clean=bool(build_data.get('clean', config.build.clean)),
            output=str(build_data.get('output', config.build.output)),
            target_name=build_data.get('target_name'),
        )

        # Compiler
        comp_data = data.get('compiler', {})
        if not isinstance(comp_data, dict):
            raise ConfigurationError(
                'A seção [compiler] deve ser uma tabela TOML válida.'
            )
        config.compiler = CompilerConfig(
            cython=bool(comp_data.get('cython', config.compiler.cython)),
            optimization=int(
                comp_data.get('optimization', config.compiler.optimization)
            ),
            c_compiler=str(
                comp_data.get('c_compiler', config.compiler.c_compiler)
            ),
            language_level=int(
                comp_data.get('language_level', config.compiler.language_level)
            ),
            type_hints=bool(
                comp_data.get('type_hints', config.compiler.type_hints)
            ),
            extra_cflags=list(
                comp_data.get('extra_cflags', config.compiler.extra_cflags)
            ),
        )

        # Packaging
        pack_data = data.get('packaging', {})
        if not isinstance(pack_data, dict):
            raise ConfigurationError(
                'A seção [packaging] deve ser uma tabela TOML válida.'
            )
        config.packaging = PackagingConfig(
            pyinstaller=bool(
                pack_data.get('pyinstaller', config.packaging.pyinstaller)
            ),
            onefile=bool(pack_data.get('onefile', config.packaging.onefile)),
            upx=bool(pack_data.get('upx', config.packaging.upx)),
            console=bool(pack_data.get('console', config.packaging.console)),
            icon=pack_data.get('icon', config.packaging.icon),
            hidden_imports=list(
                pack_data.get(
                    'hidden_imports', config.packaging.hidden_imports
                )
            ),
            add_data=list(
                pack_data.get('add_data', config.packaging.add_data)
            ),
            clean=bool(pack_data.get('clean', config.packaging.clean)),
        )

        # Cache
        cache_data = data.get('cache', {})
        if not isinstance(cache_data, dict):
            raise ConfigurationError(
                'A seção [cache] deve ser uma tabela TOML válida.'
            )
        config.cache = CacheConfig(
            enabled=bool(cache_data.get('enabled', config.cache.enabled)),
            directory=str(cache_data.get('directory', config.cache.directory)),
        )

        # Reports
        rep_data = data.get('reports', {})
        if not isinstance(rep_data, dict):
            raise ConfigurationError(
                'A seção [reports] deve ser uma tabela TOML válida.'
            )
        config.reports = ReportsConfig(
            enabled=bool(rep_data.get('enabled', config.reports.enabled)),
            format=list(rep_data.get('format', config.reports.format)),
            output_dir=str(
                rep_data.get('output_dir', config.reports.output_dir)
            ),
        )

        # Platforms
        plat_data = data.get('platforms', {})
        if not isinstance(plat_data, dict):
            raise ConfigurationError(
                'A seção [platforms] deve ser uma tabela TOML válida.'
            )
        config.platforms = PlatformsConfig(
            linux=bool(plat_data.get('linux', config.platforms.linux)),
            windows=bool(plat_data.get('windows', config.platforms.windows)),
            macos=bool(plat_data.get('macos', config.platforms.macos)),
        )

        # Custom Profiles
        custom_profiles = data.get('profile', {})
        if isinstance(custom_profiles, dict):
            config.custom_profiles = custom_profiles

        # Aplica o perfil ativo selecionado em build.profile
        cls.apply_profile(config, config.build.profile)

        return config

    @classmethod
    def apply_profile(cls, config: OrangeConfig, profile_name: str) -> None:
        """Aplica os valores do perfil predefinido ou personalizado sobre a configuração."""
        profile_name = profile_name.lower()
        config.build.profile = profile_name

        # 1. Verifica perfis padrão
        if profile_name in PRESET_PROFILES:
            preset = PRESET_PROFILES[profile_name]
            cls._merge_profile_data(config, preset)

        # 2. Verifica perfis customizados no orange.toml
        if profile_name in config.custom_profiles:
            custom_data = config.custom_profiles[profile_name]
            cls._merge_profile_data(config, custom_data)
        elif profile_name not in PRESET_PROFILES:
            raise ConfigurationError(
                f"Perfil de build '{profile_name}' não reconhecido.",
                details=f'Perfis disponíveis: {list(PRESET_PROFILES.keys()) + list(config.custom_profiles.keys())}',
            )

    @staticmethod
    def _merge_profile_data(
        config: OrangeConfig, data: dict[str, Any]
    ) -> None:
        """Mescla dados de um perfil nas seções correspondentes da configuração."""
        if 'compiler' in data and isinstance(data['compiler'], dict):
            for k, v in data['compiler'].items():
                if hasattr(config.compiler, k):
                    setattr(config.compiler, k, v)

        if 'packaging' in data and isinstance(data['packaging'], dict):
            for k, v in data['packaging'].items():
                if hasattr(config.packaging, k):
                    setattr(config.packaging, k, v)

        if 'build' in data and isinstance(data['build'], dict):
            for k, v in data['build'].items():
                if hasattr(config.build, k):
                    setattr(config.build, k, v)

    @classmethod
    def apply_cli_overrides(
        cls, config: OrangeConfig, **overrides: Any
    ) -> None:
        """Sobrescreve opções de configuração com parâmetros passados pela CLI."""
        if overrides.get('profile'):
            cls.apply_profile(config, overrides['profile'])

        if overrides.get('compile_all') is not None:
            config.build.compile_all = bool(overrides['compile_all'])

        if overrides.get('clean') is not None:
            config.build.clean = bool(overrides['clean'])
            config.packaging.clean = bool(overrides['clean'])

        if overrides.get('output'):
            config.build.output = str(overrides['output'])

        if overrides.get('target_name'):
            config.build.target_name = str(overrides['target_name'])

        if overrides.get('entrypoint'):
            config.project.entrypoint = str(overrides['entrypoint'])

        if overrides.get('source'):
            config.project.source = str(overrides['source'])

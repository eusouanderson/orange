"""Interfaces e classes base para o sistema de plugins do Orange Framework."""

from __future__ import annotations

import abc
from pathlib import Path
from typing import Any

from orange.models import BuildResult, OrangeConfig


class BasePlugin(abc.ABC):
    """Classe base para todos os plugins do Orange."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Nome identificador do plugin."""
        pass

    @property
    @abc.abstractmethod
    def version(self) -> str:
        """Versão semântica do plugin."""
        pass

    @property
    def description(self) -> str:
        """Descrição das funcionalidades do plugin."""
        return ''

    def initialize(self, config: OrangeConfig) -> None:
        """Inicializa o plugin com a configuração atual."""
        pass


class BaseCompilerPlugin(BasePlugin):
    """Interface para plugins de compilação alternativa (ex: Nuitka, Rust, C++)."""

    @abc.abstractmethod
    def compile(
        self, source_path: Path, output_dir: Path, options: dict[str, Any]
    ) -> Path:
        """Executa a compilação de um arquivo fonte."""
        pass


class BasePackagerPlugin(BasePlugin):
    """Interface para plugins de empacotamento alternativo (ex: Briefcase, cx_Freeze)."""

    @abc.abstractmethod
    def package(
        self, entrypoint: Path, output_dir: Path, options: dict[str, Any]
    ) -> Path:
        """Executa o empacotamento da aplicação."""
        pass


class BaseOptimizerPlugin(BasePlugin):
    """Interface para plugins de otimização e pós-processamento de binários."""

    @abc.abstractmethod
    def optimize(
        self, binary_path: Path, options: dict[str, Any]
    ) -> dict[str, Any]:
        """Aplica otimizações sobre o binário compilado."""
        pass


class BaseHookPlugin(BasePlugin):
    """Interface para ganchos de ciclo de vida (pre-build e post-build)."""

    def pre_build(self, config: OrangeConfig) -> None:
        """Executado antes do início do pipeline."""
        pass

    def post_build(self, result: BuildResult) -> None:
        """Executado ao término do pipeline."""
        pass


class PluginRegistry:
    """Registro e gerenciador de plugins carregados."""

    def __init__(self) -> None:
        self._plugins: dict[str, BasePlugin] = {}

    def register(self, plugin: BasePlugin) -> None:
        """Registra um plugin no sistema."""
        self._plugins[plugin.name.lower()] = plugin

    def unregister(self, name: str) -> None:
        """Remove um plugin registrado."""
        self._plugins.pop(name.lower(), None)

    def get(self, name: str) -> BasePlugin | None:
        """Retorna o plugin pelo nome."""
        return self._plugins.get(name.lower())

    def list_plugins(self) -> list[BasePlugin]:
        """Retorna todos os plugins registrados."""
        return list(self._plugins.values())


# Instância global do registro de plugins
default_registry = PluginRegistry()

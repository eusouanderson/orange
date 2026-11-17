"""Módulo de extensibilidade e plugins do Orange Framework."""

from orange.plugins.base import (
    BaseCompilerPlugin,
    BaseHookPlugin,
    BaseOptimizerPlugin,
    BasePackagerPlugin,
    BasePlugin,
    PluginRegistry,
    default_registry,
)

__all__ = [
    'BasePlugin',
    'BaseCompilerPlugin',
    'BasePackagerPlugin',
    'BaseOptimizerPlugin',
    'BaseHookPlugin',
    'PluginRegistry',
    'default_registry',
]

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
from orange.plugins.loader import PluginLoader

__all__ = [
    'BaseCompilerPlugin',
    'BaseHookPlugin',
    'BaseOptimizerPlugin',
    'BasePackagerPlugin',
    'BasePlugin',
    'PluginLoader',
    'PluginRegistry',
    'default_registry',
]

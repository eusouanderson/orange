"""Módulo de configuração do Orange Framework."""

from orange.config.defaults import generate_default_toml
from orange.config.manager import PRESET_PROFILES, ConfigManager

__all__ = ['ConfigManager', 'PRESET_PROFILES', 'generate_default_toml']

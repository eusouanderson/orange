"""Módulo de detecção, inspeção de binários e compatibilidade multiplataforma do Orange."""

from orange.platform.detector import PlatformInfo, PlatformManager, ToolInfo
from orange.platform.linux import ElfInfo, ElfInspector, LinuxBinaryManager
from orange.platform.macos import MachOInfo, MachOInspector, MacOSBinaryManager
from orange.platform.windows import PEInfo, PEInspector, WindowsBinaryManager

__all__ = [
    'ElfInfo',
    'ElfInspector',
    'LinuxBinaryManager',
    'MachOInfo',
    'MachOInspector',
    'MacOSBinaryManager',
    'PEInfo',
    'PEInspector',
    'PlatformInfo',
    'PlatformManager',
    'ToolInfo',
    'WindowsBinaryManager',
]

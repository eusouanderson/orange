"""Descoberta dinâmica e carregador de plugins externos para o Orange Framework."""

from __future__ import annotations

import importlib.metadata
import importlib.util
import inspect
import sys
from pathlib import Path

from orange.plugins.base import BasePlugin, PluginRegistry, default_registry


class PluginLoader:
    """Carregador dinâmico de plugins a partir de entrypoints e diretórios."""

    ENTRYPOINT_GROUP = 'orange.plugins'

    def __init__(self, registry: PluginRegistry | None = None) -> None:
        self.registry = registry or default_registry

    def discover_entrypoints(self) -> int:
        """Descobre e carrega plugins registrados via entrypoints do Python (pip packages)."""
        count = 0
        try:
            eps = importlib.metadata.entry_points()
            # Compatibilidade Python 3.10 e 3.12+
            plugins_eps = (
                eps.select(group=self.ENTRYPOINT_GROUP)
                if hasattr(eps, 'select')
                else eps.get(self.ENTRYPOINT_GROUP, [])
            )
            for ep in plugins_eps:
                try:
                    plugin_cls = ep.load()
                    if inspect.isclass(plugin_cls) and issubclass(
                        plugin_cls, BasePlugin
                    ):
                        inst = plugin_cls()
                        self.registry.register(inst)
                        count += 1
                except Exception:
                    continue
        except Exception:
            pass
        return count

    def discover_directory(self, dir_path: Path | str) -> int:
        """Carrega scripts Python que definem subclasses de BasePlugin a partir de um diretório."""
        p = Path(dir_path).expanduser().resolve()
        if not p.is_dir():
            return 0

        count = 0
        for py_file in p.glob('*.py'):
            if py_file.name.startswith('_'):
                continue
            module_name = f'orange_dyn_plugin_{py_file.stem}'
            try:
                spec = importlib.util.spec_from_file_location(
                    module_name, str(py_file)
                )
                if not spec or not spec.loader:
                    continue
                mod = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = mod
                spec.loader.exec_module(mod)

                # Busca subclasses de BasePlugin instanciáveis
                for _, obj in inspect.getmembers(mod, inspect.isclass):
                    if (
                        issubclass(obj, BasePlugin)
                        and obj is not BasePlugin
                        and not inspect.isabstract(obj)
                    ):
                        inst = obj()
                        self.registry.register(inst)
                        count += 1
            except Exception:
                continue
        return count

    def discover_all(self, custom_dirs: list[Path | str] | None = None) -> int:
        """Descobre plugins em todos os locais padrão e diretórios adicionais."""
        total = self.discover_entrypoints()

        default_dirs = [
            Path.home() / '.orange' / 'plugins',
            Path('.orange') / 'plugins',
        ]
        if custom_dirs:
            default_dirs.extend([Path(d) for d in custom_dirs])

        for d in default_dirs:
            total += self.discover_directory(d)

        return total

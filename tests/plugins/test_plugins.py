"""Testes para o sistema de plugins do Orange Framework."""

from pathlib import Path
from typing import Any

from orange.models import BuildResult, OrangeConfig
from orange.plugins.base import (
    BaseCompilerPlugin,
    BaseHookPlugin,
    PluginRegistry,
)


class DummyCompilerPlugin(BaseCompilerPlugin):
    @property
    def name(self) -> str:
        return 'dummy-compiler'

    @property
    def version(self) -> str:
        return '1.0.0'

    def compile(
        self, source_path: Path, output_dir: Path, options: dict[str, Any]
    ) -> Path:
        return output_dir / 'compiled.bin'


class DummyHookPlugin(BaseHookPlugin):
    def __init__(self) -> None:
        self.pre_called = False
        self.post_called = False

    @property
    def name(self) -> str:
        return 'dummy-hook'

    @property
    def version(self) -> str:
        return '0.1.0'

    def pre_build(self, config: OrangeConfig) -> None:
        self.pre_called = True

    def post_build(self, result: BuildResult) -> None:
        self.post_called = True


def test_plugin_registry():
    registry = PluginRegistry()
    compiler_plugin = DummyCompilerPlugin()
    hook_plugin = DummyHookPlugin()

    registry.register(compiler_plugin)
    registry.register(hook_plugin)

    assert len(registry.list_plugins()) == 2
    assert registry.get('dummy-compiler') == compiler_plugin
    assert registry.get('dummy-hook') == hook_plugin

    # Executa hook
    cfg = OrangeConfig()
    res = BuildResult(success=True, platform='linux', profile='dev')
    hook_plugin.pre_build(cfg)
    hook_plugin.post_build(res)
    assert hook_plugin.pre_called is True
    assert hook_plugin.post_called is True

    registry.unregister('dummy-compiler')
    assert registry.get('dummy-compiler') is None

"""Testes para carregador dinâmico de plugins e hooks."""

import tempfile
from pathlib import Path

from orange.models import BuildResult, OrangeConfig
from orange.plugins.base import BaseHookPlugin, PluginRegistry
from orange.plugins.loader import PluginLoader


class SampleHookPlugin(BaseHookPlugin):
    def __init__(self) -> None:
        self.pre_build_called = False
        self.post_build_called = False

    @property
    def name(self) -> str:
        return 'sample-hook'

    @property
    def version(self) -> str:
        return '1.0.0'

    @property
    def description(self) -> str:
        return 'Plugin de teste para validação de hooks'

    def pre_build(self, config: OrangeConfig) -> None:
        self.pre_build_called = True

    def post_build(self, result: BuildResult) -> None:
        self.post_build_called = True


def test_plugin_registry_hooks():
    reg = PluginRegistry()
    hook = SampleHookPlugin()
    reg.register(hook)

    assert len(reg.get_hooks()) == 1
    assert reg.get_hooks()[0] is hook

    cfg = OrangeConfig()
    reg.run_pre_build(cfg)
    assert hook.pre_build_called is True

    res = BuildResult(
        success=True,
        platform='linux',
        profile='production',
        compiler_used='cython',
        packager_used='pyinstaller',
        optimizer_used='upx',
    )
    reg.run_post_build(res)
    assert hook.post_build_called is True


def test_plugin_loader_directory_discovery():
    reg = PluginRegistry()
    loader = PluginLoader(registry=reg)

    with tempfile.TemporaryDirectory() as tmp:
        plugin_file = Path(tmp) / 'my_custom_plugin.py'
        plugin_file.write_text(
            """from orange.plugins.base import BasePlugin

class DynamicCustomPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "dyn-custom"

    @property
    def version(self) -> str:
        return "0.5.0"

    @property
    def description(self) -> str:
        return "Plugin carregado dinamicamente"
""",
            encoding='utf-8',
        )

        loaded = loader.discover_directory(tmp)
        assert loaded >= 1
        p = reg.get('dyn-custom')
        assert p is not None
        assert p.name == 'dyn-custom'
        assert p.version == '0.5.0'

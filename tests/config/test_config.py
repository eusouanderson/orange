"""Testes para o módulo de configuração orange.config e validação do orange.toml."""

import tempfile
from pathlib import Path

import pytest

from orange.config.defaults import generate_default_toml
from orange.config.manager import PRESET_PROFILES, ConfigManager
from orange.errors import ConfigurationError
from orange.models import OrangeConfig


def test_generate_default_toml():
    content = generate_default_toml(name='test-app', version='2.0.0')
    assert 'name = "test-app"' in content
    assert 'version = "2.0.0"' in content
    assert '[project]' in content
    assert '[build]' in content
    assert '[compiler]' in content


def test_config_manager_load_valid():
    with tempfile.TemporaryDirectory() as tmp:
        toml_file = Path(tmp) / 'orange.toml'
        toml_file.write_text(
            generate_default_toml(name='meu-app'), encoding='utf-8'
        )

        mgr = ConfigManager(toml_file)
        cfg = mgr.load()

        assert cfg.project.name == 'meu-app'
        assert cfg.build.profile == 'production'
        assert cfg.compiler.cython is True
        assert cfg.packaging.pyinstaller is True


def test_config_manager_file_not_found():
    mgr = ConfigManager('/caminho/inexistente/orange.toml')
    with pytest.raises(ConfigurationError) as exc:
        mgr.load()
    assert 'não encontrado' in str(exc.value)


def test_config_manager_invalid_toml():
    with tempfile.TemporaryDirectory() as tmp:
        toml_file = Path(tmp) / 'orange.toml'
        toml_file.write_text('invalido [[ syntax error', encoding='utf-8')

        mgr = ConfigManager(toml_file)
        with pytest.raises(ConfigurationError) as exc:
            mgr.load()
        assert 'Falha ao interpretar o arquivo TOML' in str(exc.value)


def test_config_profiles_preset_values():
    assert 'development' in PRESET_PROFILES
    assert 'release' in PRESET_PROFILES
    assert 'production' in PRESET_PROFILES

    # Development: opt=0, upx=False
    assert PRESET_PROFILES['development']['compiler']['optimization'] == 0
    assert PRESET_PROFILES['development']['packaging']['upx'] is False

    # Production: opt=3, upx=True
    assert PRESET_PROFILES['production']['compiler']['optimization'] == 3
    assert PRESET_PROFILES['production']['packaging']['upx'] is True


def test_apply_profile_presets():
    cfg = OrangeConfig()

    ConfigManager.apply_profile(cfg, 'development')
    assert cfg.build.profile == 'development'
    assert cfg.compiler.optimization == 0
    assert cfg.packaging.upx is False

    ConfigManager.apply_profile(cfg, 'production')
    assert cfg.build.profile == 'production'
    assert cfg.compiler.optimization == 3
    assert cfg.packaging.upx is True


def test_apply_custom_profile():
    data = {
        'project': {'name': 'custom-app'},
        'build': {'profile': 'custom_opt'},
        'profile': {
            'custom_opt': {
                'compiler': {'optimization': 1},
                'packaging': {'console': True},
            }
        },
    }
    cfg = ConfigManager.from_dict(data)
    assert cfg.build.profile == 'custom_opt'
    assert cfg.compiler.optimization == 1
    assert cfg.packaging.console is True


def test_apply_profile_invalid():
    cfg = OrangeConfig()
    with pytest.raises(ConfigurationError) as exc:
        ConfigManager.apply_profile(cfg, 'perfil_inexistente')
    assert 'não reconhecido' in str(exc.value)


def test_apply_cli_overrides():
    cfg = OrangeConfig()
    ConfigManager.apply_cli_overrides(
        cfg,
        profile='development',
        compile_all=True,
        clean=False,
        output='./custom_dist',
        target_name='binary_custom',
    )
    assert cfg.build.profile == 'development'
    assert cfg.build.compile_all is True
    assert cfg.build.clean is False
    assert cfg.build.output == './custom_dist'
    assert cfg.build.target_name == 'binary_custom'

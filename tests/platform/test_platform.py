"""Testes para o módulo de plataforma e detecção de ferramentas."""

from orange.platform.detector import PlatformInfo, PlatformManager


def test_platform_manager_system_normalized():
    sys_name = PlatformManager.get_system()
    assert sys_name in {'linux', 'windows', 'macos'}


def test_platform_manager_extensions():
    exe_ext = PlatformManager.get_executable_extension()
    so_ext = PlatformManager.get_shared_lib_extension()

    sys_name = PlatformManager.get_system()
    if sys_name == 'windows':
        assert exe_ext == '.exe'
        assert so_ext == '.pyd'
    else:
        assert not exe_ext
        assert so_ext in {'.so', '.dylib'}


def test_platform_manager_get_info():
    info = PlatformManager.get_info()
    assert isinstance(info, PlatformInfo)
    assert info.system in {'linux', 'windows', 'macos'}
    assert 'python' in info.tools
    assert info.tools['python'].available is True
    assert info.python_version is not None


def test_platform_doctor_checks():
    checks = PlatformManager.doctor()
    assert len(checks) >= 5
    names = [c[0] for c in checks]
    assert any('Python' in n for n in names)
    assert any('Compilador C' in n for n in names)
    assert any('Cython' in n for n in names)
    assert any('PyInstaller' in n for n in names)

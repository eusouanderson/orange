"""Testes unitários para inspeção de binários Windows PE e UAC."""

import struct
import tempfile
from pathlib import Path

from orange.platform.windows import PEInspector, WindowsBinaryManager


def create_synthetic_pe(
    file_path: Path,
    machine: int = 0x8664,
    is_gui: bool = True,
    uac_level: str = 'asInvoker',
) -> None:
    """Cria um binário PE sintetizado para validação de cabeçalhos sem dependência de Windows."""
    pe_offset = 0x80
    dos_header = bytearray(b'\x00' * pe_offset)
    dos_header[:2] = b'MZ'
    dos_header[0x3C:0x40] = struct.pack('<I', pe_offset)

    pe_sig = b'PE\x00\x00'
    opt_size = 96
    coff_header = struct.pack('<HHIIIHH', machine, 1, 0, 0, 0, opt_size, 0x02)

    subsystem = 2 if is_gui else 3  # 2 = GUI, 3 = Console
    opt_header = bytearray(b'\x00' * opt_size)
    opt_header[:2] = struct.pack(
        '<H', 0x20B if machine in {0x8664, 0xAA64} else 0x10B
    )
    opt_header[68:70] = struct.pack('<H', subsystem)

    manifest = f'<assembly><requestedExecutionLevel level="{uac_level}" uiAccess="false"/></assembly>'.encode(
        'utf-8'
    )

    with open(file_path, 'wb') as f:
        f.write(dos_header)
        f.write(pe_sig)
        f.write(coff_header)
        f.write(opt_header)
        f.write(manifest)


def test_pe_inspector_synthetic_binary():
    with tempfile.TemporaryDirectory() as tmp:
        pe_file = Path(tmp) / 'test_app.exe'
        create_synthetic_pe(
            pe_file,
            machine=0x8664,
            is_gui=True,
            uac_level='requireAdministrator',
        )

        assert PEInspector.is_pe(pe_file) is True
        info = PEInspector.inspect(pe_file)
        assert info is not None
        assert info.machine == 'x86_64'
        assert info.is_64bit is True
        assert info.subsystem == 'gui'
        assert info.has_manifest is True
        assert info.uac_execution_level == 'requireAdministrator'


def test_pe_inspector_non_pe():
    with tempfile.TemporaryDirectory() as tmp:
        bad_file = Path(tmp) / 'corrupt.exe'
        bad_file.write_bytes(b'NOT A PE BINARY AT ALL')

        assert PEInspector.is_pe(bad_file) is False
        assert PEInspector.inspect(bad_file) is None


def test_windows_uac_manifest_generation():
    manifest = WindowsBinaryManager.generate_uac_manifest(
        'OrangeApp', execution_level='highestAvailable', ui_access=True
    )
    assert '<assembly' in manifest
    assert 'OrangeApp' in manifest
    assert 'level="highestAvailable"' in manifest
    assert 'uiAccess="true"' in manifest


def test_windows_long_path_conversion():
    short_p = 'C:\\short\\path.txt'
    assert WindowsBinaryManager.to_long_path(short_p) == short_p

    long_p = 'C:\\' + 'a' * 270 + '\\file.txt'
    converted = WindowsBinaryManager.to_long_path(long_p)
    assert converted.startswith('\\\\?\\')


def test_windows_vc_redist_check():
    redist = WindowsBinaryManager.check_vc_redist()
    assert isinstance(redist, dict)
    assert 'vcruntime140.dll' in redist

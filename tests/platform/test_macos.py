"""Testes unitários para inspeção de binários Apple Mach-O e entitlements."""

import struct
import tempfile
from pathlib import Path

from orange.platform.macos import MachOInspector, MacOSBinaryManager


def create_synthetic_macho_64(
    file_path: Path, arch_code: int = 0x0100000C
) -> None:
    """Cria um binário Mach-O 64-bit sintetizado com comando LC_RPATH."""
    magic = struct.pack('>I', 0xFEEDFACF)  # MH_MAGIC_64
    endian = '<'
    # cputype, cpusubtype, filetype (2=execute), ncmds=1, sizeofcmds=32, flags
    hdr = struct.pack(f'{endian}IIIIII', arch_code, 0, 2, 1, 32, 0)
    reserved = struct.pack(f'{endian}I', 0)

    # LC_RPATH = 0x8000001C, cmdsize = 32, offset = 12
    rpath_str = b'@executable_path/../Frameworks\x00'
    cmd = (
        struct.pack(f'{endian}III', 0x8000001C, len(rpath_str) + 12, 12)
        + rpath_str
    )

    with open(file_path, 'wb') as f:
        f.write(magic)
        f.write(hdr)
        f.write(reserved)
        f.write(cmd)


def create_synthetic_fat_macho(file_path: Path) -> None:
    """Cria um binário Mach-O Universal (Fat binary com x86_64 e arm64)."""
    magic = struct.pack('>I', 0xCAFEBABE)  # FAT_MAGIC
    narch = struct.pack('>I', 2)

    # Arch 1: x86_64 (0x01000007)
    arch1 = struct.pack('>IIIII', 0x01000007, 3, 4096, 16384, 12)
    # Arch 2: arm64 (0x0100000C)
    arch2 = struct.pack('>IIIII', 0x0100000C, 0, 20480, 16384, 14)

    with open(file_path, 'wb') as f:
        f.write(magic)
        f.write(narch)
        f.write(arch1)
        f.write(arch2)


def test_macho_inspector_64bit():
    with tempfile.TemporaryDirectory() as tmp:
        macho_file = Path(tmp) / 'orange_arm'
        create_synthetic_macho_64(macho_file, arch_code=0x0100000C)

        assert MachOInspector.is_macho(macho_file) is True
        info = MachOInspector.inspect(macho_file)
        assert info is not None
        assert info.arch == 'arm64'
        assert info.is_64bit is True
        assert info.is_fat is False
        assert '@executable_path/../Frameworks' in info.rpaths


def test_macho_inspector_universal_fat():
    with tempfile.TemporaryDirectory() as tmp:
        fat_file = Path(tmp) / 'orange_universal'
        create_synthetic_fat_macho(fat_file)

        assert MachOInspector.is_macho(fat_file) is True
        info = MachOInspector.inspect(fat_file)
        assert info is not None
        assert info.arch == 'universal'
        assert info.is_fat is True
        assert 'x86_64' in info.architectures
        assert 'arm64' in info.architectures


def test_macos_entitlements_generation():
    ent = MacOSBinaryManager.generate_entitlements(
        allow_jit=True,
        allow_unsigned_memory=True,
        disable_library_validation=True,
    )
    assert '<plist' in ent
    assert 'com.apple.security.cs.allow-jit' in ent
    assert 'com.apple.security.cs.allow-unsigned-executable-memory' in ent
    assert 'com.apple.security.cs.disable-library-validation' in ent

"""Testes unitários para abstrações de binários Linux ELF e GLIBC."""

import sys
import tempfile
from pathlib import Path

from orange.platform.linux import ElfInspector, LinuxBinaryManager


def test_elf_inspection_on_current_python_interpreter():
    python_bin = Path(sys.executable)
    if not python_bin.exists():
        return

    is_elf = ElfInspector.is_elf(python_bin)
    # No Linux o interpretador Python é um binário ELF
    if sys.platform.startswith('linux'):
        assert is_elf is True
        info = ElfInspector.inspect(python_bin)
        assert info is not None
        assert info.bitness in {32, 64}
        assert info.endianness == 'little'
        assert info.machine in {'x86_64', 'aarch64', 'i386', 'arm'}
        assert info.path == python_bin


def test_elf_non_elf_file():
    with tempfile.TemporaryDirectory() as tmp:
        txt_file = Path(tmp) / 'sample.txt'
        txt_file.write_text(
            'Hello world, not an ELF binary.', encoding='utf-8'
        )

        assert ElfInspector.is_elf(txt_file) is False
        assert ElfInspector.inspect(txt_file) is None


def test_glibc_version_detection():
    if sys.platform.startswith('linux'):
        ver = LinuxBinaryManager.get_glibc_version()
        assert ver is not None
        assert len(ver) > 0
        # GLIBC moderna deve ser compatível com baseline 2.17
        assert LinuxBinaryManager.check_glibc_compatibility('2.17') is True


def test_patchelf_availability_check():
    avail = LinuxBinaryManager.is_patchelf_available()
    assert isinstance(avail, bool)

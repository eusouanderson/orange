"""Abstrações e ferramentas para plataforma macOS (Mach-O, Universal Binaries, codesign, entitlements)."""

from __future__ import annotations

import shutil
import struct
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class MachOInfo:
    """Informações estruturais de um executável ou dylib no formato Apple Mach-O."""

    path: Path
    arch: str  # 'x86_64', 'arm64', 'universal', etc.
    is_64bit: bool
    is_fat: bool
    architectures: list[str] = field(default_factory=list)
    file_type: str = 'execute'  # 'execute', 'dylib', 'bundle', 'unknown'
    rpaths: list[str] = field(default_factory=list)
    is_signed: bool = False


class MachOInspector:
    """Inspetor puro em Python para binários Mach-O e Universal (Fat) da Apple."""

    MH_MAGIC_64 = 0xFEEDFACF
    MH_CIGAM_64 = 0xCFFAEDFE
    MH_MAGIC = 0xFEEDFACE
    MH_CIGAM = 0xCEFAEDFE
    FAT_MAGIC = 0xCAFEBABE
    FAT_CIGAM = 0xBEBAFECA

    CPU_TYPE_MAP = {
        0x01000007: 'x86_64',
        0x0100000C: 'arm64',
        0x00000007: 'i386',
        0x0000000C: 'arm',
    }

    FILE_TYPE_MAP = {
        2: 'execute',
        6: 'dylib',
        8: 'bundle',
    }

    @classmethod
    def is_macho(cls, path: Path | str) -> bool:
        """Verifica se o arquivo inicia com qualquer um dos números mágicos Mach-O."""
        p = Path(path)
        if not p.is_file() or p.stat().st_size < 4:
            return False
        try:
            with open(p, 'rb') as f:
                magic = struct.unpack('>I', f.read(4))[0]
                return magic in {
                    cls.MH_MAGIC_64,
                    cls.MH_CIGAM_64,
                    cls.MH_MAGIC,
                    cls.MH_CIGAM,
                    cls.FAT_MAGIC,
                    cls.FAT_CIGAM,
                }
        except OSError:
            return False

    @classmethod
    def inspect(cls, path: Path | str) -> MachOInfo | None:
        """Extrai detalhes arquiteturais e comandos de carga de um binário Mach-O."""
        p = Path(path)
        if not cls.is_macho(p):
            return None

        try:
            with open(p, 'rb') as f:
                raw_magic = f.read(4)
                magic = struct.unpack('>I', raw_magic)[0]

                # 1. Trata binário Universal (Fat Binary)
                if magic in {cls.FAT_MAGIC, cls.FAT_CIGAM}:
                    endian = '>' if magic == cls.FAT_MAGIC else '<'
                    nfat_arch = struct.unpack(f'{endian}I', f.read(4))[0]
                    archs: list[str] = []
                    for _ in range(min(nfat_arch, 16)):
                        cputype, _ = struct.unpack(f'{endian}II', f.read(8))
                        f.seek(12, 1)  # pula offset, size, align
                        arch_name = cls.CPU_TYPE_MAP.get(
                            cputype, f'cpu_0x{cputype:x}'
                        )
                        archs.append(arch_name)

                    return MachOInfo(
                        path=p,
                        arch='universal',
                        is_64bit=any(a in {'x86_64', 'arm64'} for a in archs),
                        is_fat=True,
                        architectures=archs,
                        file_type='execute',
                        is_signed=cls._check_is_signed(p),
                    )

                # 2. Trata binário Mach-O individual (32 ou 64-bit)
                endian = (
                    '<' if magic in {cls.MH_MAGIC, cls.MH_MAGIC_64} else '>'
                )
                is_64 = magic in {cls.MH_MAGIC_64, cls.MH_CIGAM_64}

                cputype, _, filetype, ncmds, sizeofcmds, _ = struct.unpack(
                    f'{endian}IIIIII', f.read(24)
                )
                if is_64:
                    f.seek(4, 1)  # pula campo 'reserved' no cabeçalho 64-bit

                arch_name = cls.CPU_TYPE_MAP.get(cputype, f'cpu_0x{cputype:x}')
                file_type_str = cls.FILE_TYPE_MAP.get(filetype, 'unknown')

                # Lê comandos de carga (Load Commands) em busca de LC_RPATH
                rpaths: list[str] = []
                LC_RPATH = 0x8000001C

                for _ in range(min(ncmds, 128)):
                    cmd_bytes = f.read(8)
                    if len(cmd_bytes) < 8:
                        break
                    cmd, cmdsize = struct.unpack(f'{endian}II', cmd_bytes)
                    if cmd == LC_RPATH and cmdsize > 12:
                        payload = f.read(cmdsize - 8)
                        offset = struct.unpack(f'{endian}I', payload[:4])[0]
                        # String RPATH começa no offset em relação ao início do comando
                        str_data = payload[offset - 8 :]
                        rpath_str = (
                            str_data
                            .split(b'\x00')[0]
                            .decode('utf-8', errors='ignore')
                            .strip()
                        )
                        if rpath_str:
                            rpaths.append(rpath_str)
                    else:
                        f.seek(cmdsize - 8, 1)

                return MachOInfo(
                    path=p,
                    arch=arch_name,
                    is_64bit=is_64,
                    is_fat=False,
                    architectures=[arch_name],
                    file_type=file_type_str,
                    rpaths=rpaths,
                    is_signed=cls._check_is_signed(p),
                )
        except Exception:
            return None

    @staticmethod
    def _check_is_signed(path: Path) -> bool:
        """Verifica se o binário foi assinado com codesign."""
        if not shutil.which('codesign'):
            return False
        try:
            res = subprocess.run(
                ['codesign', '-v', str(path)],
                capture_output=True,
                check=False,
                timeout=3,
            )
            return res.returncode == 0
        except Exception:
            return False


class MacOSBinaryManager:
    """Ferramentas para gerenciamento de binários macOS (codesign, entitlements, rpath)."""

    @staticmethod
    def check_codesign(binary_path: Path | str) -> tuple[bool, str]:
        """Verifica os detalhes de assinatura de um binário no macOS."""
        p = Path(binary_path)
        codesign = shutil.which('codesign')
        if not codesign or not p.exists():
            return False, 'codesign não disponível no sistema'

        try:
            res = subprocess.run(
                [codesign, '-dv', '--verbose=4', str(p)],
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
            )
            details = (res.stderr or res.stdout).strip()
            return res.returncode == 0, details
        except Exception as e:
            return False, str(e)

    @staticmethod
    def adhoc_sign(
        binary_path: Path | str, entitlements_file: Path | str | None = None
    ) -> bool:
        """Aplica assinatura ad-hoc (autoassinada) no executável."""
        p = Path(binary_path)
        codesign = shutil.which('codesign')
        if not codesign or not p.exists():
            return False

        cmd = ['codesign', '-s', '-', '--force']
        if entitlements_file and Path(entitlements_file).is_file():
            cmd.extend(['--entitlements', str(entitlements_file)])
        cmd.append(str(p))

        try:
            res = subprocess.run(
                cmd, capture_output=True, check=False, timeout=5
            )
            return res.returncode == 0
        except Exception:
            return False

    @staticmethod
    def generate_entitlements(
        allow_jit: bool = True,
        allow_unsigned_memory: bool = True,
        disable_library_validation: bool = False,
    ) -> str:
        """Gera um arquivo de entitlements XML compatível com Python e Hardened Runtime."""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.cs.allow-jit</key>
    <{'true' if allow_jit else 'false'}/>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <{'true' if allow_unsigned_memory else 'false'}/>
    <key>com.apple.security.cs.disable-library-validation</key>
    <{'true' if disable_library_validation else 'false'}/>
</dict>
</plist>
"""

    @staticmethod
    def add_rpath(binary_path: Path | str, rpath: str) -> bool:
        """Adiciona um caminho RPATH a um binário macOS usando install_name_tool."""
        p = Path(binary_path)
        tool = shutil.which('install_name_tool')
        if not tool or not p.exists():
            return False

        try:
            res = subprocess.run(
                [tool, '-add_rpath', rpath, str(p)],
                capture_output=True,
                check=False,
                timeout=5,
            )
            return res.returncode == 0
        except Exception:
            return False

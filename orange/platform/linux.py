"""Abstrações e ferramentas para plataforma Linux (ELF, RPATH, GLIBC, patchelf)."""

from __future__ import annotations

import shutil
import struct
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ElfInfo:
    """Metadados e propriedades de um binário no formato ELF."""

    path: Path
    bitness: int  # 32 ou 64
    endianness: str  # 'little' ou 'big'
    machine: str  # 'x86_64', 'aarch64', 'arm', 'i386', etc.
    os_abi: str
    is_pie: bool  # Position Independent Executable
    interpreter: str | None = None
    rpaths: list[str] = field(default_factory=list)
    needed_libs: list[str] = field(default_factory=list)


class ElfInspector:
    """Inspetor puro em Python para leitura e análise de cabeçalhos ELF."""

    ELF_MAGIC = b'\x7fELF'

    MACHINE_MAP = {
        0x03: 'i386',
        0x3E: 'x86_64',
        0x28: 'arm',
        0xB7: 'aarch64',
        0xF3: 'riscv',
    }

    @classmethod
    def is_elf(cls, path: Path | str) -> bool:
        """Verifica se o arquivo inicia com os bytes mágicos ELF."""
        p = Path(path)
        if not p.is_file() or p.stat().st_size < 16:
            return False
        try:
            with open(p, 'rb') as f:
                magic = f.read(4)
                return magic == cls.ELF_MAGIC
        except OSError:
            return False

    @classmethod
    def inspect(cls, path: Path | str) -> ElfInfo | None:
        """Inspeciona o arquivo ELF e extrai informações estruturais."""
        p = Path(path)
        if not cls.is_elf(p):
            return None

        try:
            with open(p, 'rb') as f:
                ident = f.read(16)
                ei_class = ident[4]  # 1 = 32-bit, 2 = 64-bit
                ei_data = ident[5]  # 1 = Little Endian, 2 = Big Endian
                os_abi_code = ident[7]

                bitness = 64 if ei_class == 2 else 32
                endian_prefix = '<' if ei_data == 1 else '>'
                endianness = 'little' if ei_data == 1 else 'big'

                os_abi_map = {
                    0: 'System V',
                    3: 'Linux',
                    6: 'Solaris',
                    9: 'FreeBSD',
                }
                os_abi = os_abi_map.get(os_abi_code, f'ABI({os_abi_code})')

                # Cabeçalho do arquivo ELF
                if bitness == 64:
                    hdr_fmt = f'{endian_prefix}HHIQQQIHHHHHH'
                    f.seek(16)
                    hdr_bytes = f.read(struct.calcsize(hdr_fmt))
                    if len(hdr_bytes) < struct.calcsize(hdr_fmt):
                        return None
                    (
                        e_type,
                        e_machine,
                        _,
                        _,
                        e_phoff,
                        _,
                        _,
                        _,
                        e_phentsize,
                        e_phnum,
                        _,
                        _,
                        _,
                    ) = struct.unpack(hdr_fmt, hdr_bytes)
                else:
                    hdr_fmt = f'{endian_prefix}HHIIIIIHHHHHH'
                    f.seek(16)
                    hdr_bytes = f.read(struct.calcsize(hdr_fmt))
                    if len(hdr_bytes) < struct.calcsize(hdr_fmt):
                        return None
                    (
                        e_type,
                        e_machine,
                        _,
                        _,
                        e_phoff,
                        _,
                        _,
                        _,
                        e_phentsize,
                        e_phnum,
                        _,
                        _,
                        _,
                    ) = struct.unpack(hdr_fmt, hdr_bytes)

                machine_name = cls.MACHINE_MAP.get(
                    e_machine, f'machine_0x{e_machine:x}'
                )
                is_pie = e_type == 3  # ET_DYN (Shared object / PIE)

                interpreter = None
                # Busca por PT_INTERP (segmento tipo 3)
                if e_phoff > 0 and e_phentsize > 0 and e_phnum > 0:
                    for i in range(min(e_phnum, 64)):
                        f.seek(e_phoff + i * e_phentsize)
                        if bitness == 64:
                            ph_fmt = f'{endian_prefix}IIQQQQQQ'
                            ph_bytes = f.read(struct.calcsize(ph_fmt))
                            if len(ph_bytes) == struct.calcsize(ph_fmt):
                                p_type, _, p_offset, _, _, p_filesz, _, _ = (
                                    struct.unpack(ph_fmt, ph_bytes)
                                )
                                if p_type == 3:  # PT_INTERP
                                    f.seek(p_offset)
                                    raw_interp = f.read(p_filesz)
                                    interpreter = raw_interp.split(b'\x00')[
                                        0
                                    ].decode('utf-8', errors='ignore')
                                    break

                # Tenta obter RPATH e Needed libs via patchelf ou readelf se disponível
                rpaths: list[str] = []
                needed: list[str] = []
                if shutil.which('patchelf'):
                    try:
                        res = subprocess.run(
                            ['patchelf', '--print-rpath', str(p)],
                            capture_output=True,
                            text=True,
                            check=False,
                            timeout=3,
                        )
                        if res.returncode == 0 and res.stdout.strip():
                            rpaths = [
                                r for r in res.stdout.strip().split(':') if r
                            ]
                        res_needed = subprocess.run(
                            ['patchelf', '--print-needed', str(p)],
                            capture_output=True,
                            text=True,
                            check=False,
                            timeout=3,
                        )
                        if (
                            res_needed.returncode == 0
                            and res_needed.stdout.strip()
                        ):
                            needed = res_needed.stdout.strip().splitlines()
                    except Exception:
                        pass

                return ElfInfo(
                    path=p,
                    bitness=bitness,
                    endianness=endianness,
                    machine=machine_name,
                    os_abi=os_abi,
                    is_pie=is_pie,
                    interpreter=interpreter,
                    rpaths=rpaths,
                    needed_libs=needed,
                )
        except Exception:
            return None


class LinuxBinaryManager:
    """Gerencia binários e bibliotecas compartilhadas em sistemas Linux."""

    @staticmethod
    def get_glibc_version() -> str | None:
        """Obtém a versão da GLIBC do sistema operacional."""
        try:
            import ctypes

            libc = ctypes.CDLL(None)
            gnu_get_libc_version = libc.gnu_get_libc_version
            gnu_get_libc_version.restype = ctypes.c_char_p
            return gnu_get_libc_version().decode('ascii')
        except Exception:
            pass

        # Fallback via ldd --version
        ldd = shutil.which('ldd')
        if ldd:
            try:
                res = subprocess.run(
                    [ldd, '--version'],
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=3,
                )
                first_line = (res.stdout or res.stderr).splitlines()[0]
                parts = first_line.split()
                if parts:
                    return parts[-1]
            except Exception:
                pass
        return None

    @classmethod
    def check_glibc_compatibility(cls, min_version: str = '2.17') -> bool:
        """Verifica se a GLIBC do sistema atende à versão mínima necessária."""
        cur = cls.get_glibc_version()
        if not cur:
            return True

        def parse_ver(v: str) -> tuple[int, ...]:
            clean = ''.join(c if c.isdigit() or c == '.' else '' for c in v)
            return tuple(int(x) for x in clean.split('.') if x.isdigit())

        try:
            return parse_ver(cur) >= parse_ver(min_version)
        except Exception:
            return True

    @staticmethod
    def get_rpath(binary_path: Path | str) -> list[str]:
        """Retorna a lista de RPATH/RUNPATH configurados no executável ou .so."""
        p = Path(binary_path)
        patchelf = shutil.which('patchelf')
        if not patchelf or not p.exists():
            return []

        try:
            res = subprocess.run(
                [patchelf, '--print-rpath', str(p)],
                capture_output=True,
                text=True,
                check=False,
                timeout=3,
            )
            if res.returncode == 0 and res.stdout.strip():
                return [r for r in res.stdout.strip().split(':') if r]
        except Exception:
            pass
        return []

    @staticmethod
    def set_rpath(binary_path: Path | str, rpath: str) -> bool:
        """Define o RPATH de um binário ELF usando patchelf."""
        p = Path(binary_path)
        patchelf = shutil.which('patchelf')
        if not patchelf or not p.exists():
            return False

        try:
            res = subprocess.run(
                [patchelf, '--set-rpath', rpath, str(p)],
                capture_output=True,
                check=False,
                timeout=5,
            )
            return res.returncode == 0
        except Exception:
            return False

    @classmethod
    def add_origin_rpath(
        cls, binary_path: Path | str, relative_lib_dir: str = '$ORIGIN/lib'
    ) -> bool:
        """Adiciona $ORIGIN (ou subdiretório relativo) ao RPATH para portabilidade."""
        p = Path(binary_path)
        current = cls.get_rpath(p)
        if relative_lib_dir in current or '$ORIGIN' in current:
            return True

        new_rpath = (
            ':'.join([relative_lib_dir] + current)
            if current
            else relative_lib_dir
        )
        return cls.set_rpath(p, new_rpath)

    @staticmethod
    def is_patchelf_available() -> bool:
        """Verifica se patchelf está instalado no sistema."""
        return shutil.which('patchelf') is not None

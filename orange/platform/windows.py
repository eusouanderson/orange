"""Abstrações e ferramentas para plataforma Windows (PE, Manifestos UAC, CRT, Long Paths)."""

from __future__ import annotations

import os
import shutil
import struct
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PEInfo:
    """Informações estruturais de um executável ou DLL no formato Windows PE."""

    path: Path
    machine: str  # 'x86_64', 'i386', 'arm64'
    is_64bit: bool
    subsystem: str  # 'gui', 'console', 'unknown'
    has_manifest: bool = False
    uac_execution_level: str | None = (
        None  # 'asInvoker', 'highestAvailable', 'requireAdministrator'
    )


class PEInspector:
    """Inspetor puro em Python para binários Portable Executable (PE32 / PE32+)."""

    DOS_MAGIC = b'MZ'
    PE_MAGIC = b'PE\0\0'

    MACHINE_MAP = {
        0x14C: 'i386',
        0x8664: 'x86_64',
        0xAA64: 'arm64',
    }

    SUBSYSTEM_MAP = {
        2: 'gui',  # IMAGE_SUBSYSTEM_WINDOWS_GUI
        3: 'console',  # IMAGE_SUBSYSTEM_WINDOWS_CUI
    }

    @classmethod
    def is_pe(cls, path: Path | str) -> bool:
        """Verifica se o arquivo possui as assinaturas MZ e PE."""
        p = Path(path)
        if not p.is_file() or p.stat().st_size < 64:
            return False
        try:
            with open(p, 'rb') as f:
                if f.read(2) != cls.DOS_MAGIC:
                    return False
                f.seek(0x3C)
                e_lfanew_bytes = f.read(4)
                if len(e_lfanew_bytes) < 4:
                    return False
                e_lfanew = struct.unpack('<I', e_lfanew_bytes)[0]
                if e_lfanew > p.stat().st_size - 4:
                    return False
                f.seek(e_lfanew)
                return f.read(4) == cls.PE_MAGIC
        except OSError:
            return False

    @classmethod
    def inspect(cls, path: Path | str) -> PEInfo | None:
        """Extrai metadados do cabeçalho PE (COFF e Optional Header)."""
        p = Path(path)
        if not cls.is_pe(p):
            return None

        try:
            with open(p, 'rb') as f:
                f.seek(0x3C)
                e_lfanew = struct.unpack('<I', f.read(4))[0]

                # Salta a assinatura PE\0\0
                f.seek(e_lfanew + 4)
                coff_header = f.read(20)
                if len(coff_header) < 20:
                    return None

                machine_code, _, _, _, _, opt_hdr_size, _ = struct.unpack(
                    '<HHIIIHH', coff_header
                )
                machine = cls.MACHINE_MAP.get(
                    machine_code, f'machine_0x{machine_code:x}'
                )

                subsystem = 'unknown'
                is_64bit = machine in {'x86_64', 'arm64'}

                if opt_hdr_size > 0:
                    opt_bytes = f.read(min(opt_hdr_size, 96))
                    if len(opt_bytes) >= 70:
                        opt_magic = struct.unpack('<H', opt_bytes[:2])[0]
                        is_64bit = opt_magic == 0x20B  # PE32+ (64-bit)

                        # Subsystem está no offset 68 do Optional Header
                        subsys_val = struct.unpack('<H', opt_bytes[68:70])[0]
                        subsystem = cls.SUBSYSTEM_MAP.get(
                            subsys_val, 'unknown'
                        )

                # Busca rápida por manifesto XML embutido
                f.seek(0)
                # Lê até 1MB do executável em busca de manifest
                content_sample = f.read(1024 * 1024)
                has_manifest = (
                    b'<assembly' in content_sample
                    or b'requestedExecutionLevel' in content_sample
                )
                uac_level = None
                if has_manifest:
                    for level in [
                        'asInvoker',
                        'highestAvailable',
                        'requireAdministrator',
                    ]:
                        if (
                            f'level="{level}"'.encode('utf-8')
                            in content_sample
                        ):
                            uac_level = level
                            break

                return PEInfo(
                    path=p,
                    machine=machine,
                    is_64bit=is_64bit,
                    subsystem=subsystem,
                    has_manifest=has_manifest,
                    uac_execution_level=uac_level,
                )
        except Exception:
            return None


class WindowsBinaryManager:
    """Utilitários para gestão de binários Windows (Manifestos, CRT, Long Paths)."""

    CRT_LIBRARIES = ['msvcp140.dll', 'vcruntime140.dll', 'vcruntime140_1.dll']

    @classmethod
    def check_vc_redist(cls) -> dict[str, bool]:
        """Verifica a presença das principais DLLs do Microsoft Visual C++ Runtime."""
        status = {}
        for dll in cls.CRT_LIBRARIES:
            found = shutil.which(dll) is not None
            if not found:
                sys_root = os.environ.get('SystemRoot', 'C:\\Windows')
                for sub in ['System32', 'SysWOW64']:
                    if (Path(sys_root) / sub / dll).exists():
                        found = True
                        break
            status[dll] = found
        return status

    @staticmethod
    def generate_uac_manifest(
        app_name: str,
        execution_level: str = 'asInvoker',
        ui_access: bool = False,
    ) -> str:
        """Gera um manifesto XML de aplicação compatível com UAC do Windows."""
        return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity
    version="1.0.0.0"
    processorArchitecture="*"
    name="{app_name}"
    type="win32"
  />
  <description>{app_name}</description>
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel
          level="{execution_level}"
          uiAccess="{'true' if ui_access else 'false'}"
        />
      </requestedPrivileges>
    </security>
  </trustInfo>
  <compatibility xmlns="urn:schemas-microsoft-com:compatibility.v1">
    <application>
      <!-- Windows 10 e Windows 11 -->
      <supportedOS Id="{{8e0f7a12-bfb3-4fe8-b9a5-48fd50a15a9a}}"/>
    </application>
  </compatibility>
</assembly>
"""

    @staticmethod
    def is_long_paths_enabled() -> bool:
        """Verifica se o Windows suporta Long Paths (> 260 caracteres)."""
        try:
            import winreg

            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r'SYSTEM\CurrentControlSet\Control\FileSystem',
            )
            val, _ = winreg.QueryValueEx(key, 'LongPathsEnabled')
            return bool(val)
        except Exception:
            return False

    @staticmethod
    def to_long_path(path: str | Path) -> str:
        """Adiciona o prefixo '\\\\?\\' se o caminho ultrapassar 260 caracteres no Windows."""
        p_str = str(path)
        if len(p_str) >= 260 and not p_str.startswith('\\\\?\\'):
            abs_path = os.path.abspath(p_str)
            return f'\\\\?\\{abs_path}'
        return p_str

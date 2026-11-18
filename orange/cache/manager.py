"""Gerenciamento de cache inteligente para artefatos e compilação do Orange."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Any

from orange.errors import CacheError
from orange.models import OrangeConfig
from orange.platform.detector import PlatformInfo


class CacheManager:
    """Gerencia o cache de compilação, hashes de código e reutilização de artefatos."""

    def __init__(
        self,
        cache_dir: str | Path = '.orange/cache',
        root_dir: Path | None = None,
    ) -> None:
        self.root_dir = root_dir or Path.cwd()
        self.cache_dir = (
            Path(cache_dir)
            if Path(cache_dir).is_absolute()
            else self.root_dir / cache_dir
        )
        self.metadata_dir = self.cache_dir / 'meta'
        self.artifacts_dir = self.cache_dir / 'artifacts'

    def ensure_dirs(self) -> None:
        """Cria os diretórios de cache se não existirem."""
        try:
            self.metadata_dir.mkdir(parents=True, exist_ok=True)
            self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise CacheError(
                f"Falha ao criar diretórios de cache em '{self.cache_dir}': {e}"
            )

    def compute_file_hash(self, file_path: Path) -> str:
        """Calcula o SHA256 de um arquivo."""
        hasher = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            raise CacheError(f'Erro ao calcular hash de {file_path}: {e}')

    def compute_cache_key(
        self,
        files: list[Path],
        config: OrangeConfig,
        platform_info: PlatformInfo,
    ) -> str:
        """Gera uma chave única e determinística de cache baseada nas fontes e configurações."""
        hasher = hashlib.sha256()

        # 1. Informações do ambiente e compiladores
        env_meta = {
            'python_version': platform_info.python_version,
            'system': platform_info.system,
            'architecture': platform_info.architecture,
            'cython_version': platform_info.tools.get('cython', {}).version
            or 'none',
            'c_compiler': platform_info.tools.get('c_compiler', {}).name
            or 'none',
        }
        hasher.update(json.dumps(env_meta, sort_keys=True).encode('utf-8'))

        # 2. Configurações de build e compiler
        conf_meta = {
            'profile': config.build.profile,
            'compile_all': config.build.compile_all,
            'optimization': config.compiler.optimization,
            'language_level': config.compiler.language_level,
            'type_hints': config.compiler.type_hints,
            'extra_cflags': config.compiler.extra_cflags,
        }
        hasher.update(json.dumps(conf_meta, sort_keys=True).encode('utf-8'))

        # 3. Hash do conteúdo de cada arquivo fonte (ordenado)
        for f in sorted(files, key=str):
            if f.exists() and f.is_file():
                rel_path = str(
                    f.relative_to(self.root_dir)
                    if f.is_relative_to(self.root_dir)
                    else f.name
                )
                hasher.update(rel_path.encode('utf-8'))
                hasher.update(self.compute_file_hash(f).encode('utf-8'))

        return hasher.hexdigest()

    def is_cached(self, cache_key: str) -> bool:
        """Verifica se há artefatos válidos para a chave especificada."""
        meta_file = self.metadata_dir / f'{cache_key}.json'
        artifact_entry = self.artifacts_dir / cache_key
        return (
            meta_file.exists()
            and artifact_entry.exists()
            and any(artifact_entry.iterdir())
        )

    def get_cached_artifacts(
        self, cache_key: str, destination_dir: Path
    ) -> list[Path]:
        """Restaura artefatos do cache para o diretório de destino."""
        if not self.is_cached(cache_key):
            return []

        source_entry = self.artifacts_dir / cache_key
        restored: list[Path] = []
        destination_dir.mkdir(parents=True, exist_ok=True)

        for item in source_entry.iterdir():
            target = destination_dir / item.name
            if item.is_dir():
                shutil.copytree(item, target, dirs_exist_ok=True)
            else:
                shutil.copy2(item, target)
            restored.append(target)

        return restored

    def store_artifacts(
        self,
        cache_key: str,
        artifacts: list[Path],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Salva artefatos gerados no cache."""
        self.ensure_dirs()
        target_entry = self.artifacts_dir / cache_key
        target_entry.mkdir(parents=True, exist_ok=True)

        for art in artifacts:
            if art.exists():
                dst = target_entry / art.name
                if art.is_dir():
                    shutil.copytree(art, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(art, dst)

        meta = metadata or {}
        meta['cache_key'] = cache_key
        meta['artifacts_count'] = len(artifacts)
        meta_file = self.metadata_dir / f'{cache_key}.json'
        meta_file.write_text(json.dumps(meta, indent=2), encoding='utf-8')

    def clear(self) -> int:
        """Limpa o cache completamente e retorna a quantidade de itens removidos."""
        count = 0
        if self.cache_dir.exists():
            for item in self.cache_dir.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
                count += 1
        return count

    def get_stats(self) -> dict[str, Any]:
        """Retorna estatísticas de uso do cache."""
        total_size = 0
        entries_count = 0

        if self.cache_dir.exists():
            for root, _, files in os.walk(self.cache_dir):
                for f in files:
                    fp = os.path.join(root, f)
                    total_size += os.path.getsize(fp)

        if self.artifacts_dir.exists():
            entries_count = len([
                d for d in self.artifacts_dir.iterdir() if d.is_dir()
            ])

        return {
            'directory': str(self.cache_dir),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'cached_entries': entries_count,
        }

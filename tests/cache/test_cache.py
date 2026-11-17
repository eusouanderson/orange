"""Testes para o gerenciador de cache inteligente do Orange."""

import tempfile
from pathlib import Path

from orange.cache.manager import CacheManager
from orange.models import OrangeConfig
from orange.platform.detector import PlatformManager


def test_cache_compute_file_hash():
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / 'sample.py'
        f.write_text("print('test')", encoding='utf-8')

        mgr = CacheManager(cache_dir=Path(tmp) / '.cache')
        h1 = mgr.compute_file_hash(f)
        assert len(h1) == 64

        # Modifica conteúdo
        f.write_text("print('test modificado')", encoding='utf-8')
        h2 = mgr.compute_file_hash(f)
        assert h1 != h2


def test_cache_compute_cache_key():
    with tempfile.TemporaryDirectory() as tmp:
        f1 = Path(tmp) / 'a.py'
        f1.write_text('def a(): pass', encoding='utf-8')

        mgr = CacheManager(cache_dir=Path(tmp) / '.cache', root_dir=Path(tmp))
        cfg = OrangeConfig()
        plat = PlatformManager.get_info()

        key1 = mgr.compute_cache_key([f1], cfg, plat)
        key2 = mgr.compute_cache_key([f1], cfg, plat)
        assert key1 == key2

        # Modifica configuração
        cfg.compiler.optimization = 0
        key3 = mgr.compute_cache_key([f1], cfg, plat)
        assert key1 != key3


def test_cache_store_and_restore():
    with tempfile.TemporaryDirectory() as tmp:
        mgr = CacheManager(cache_dir=Path(tmp) / '.cache', root_dir=Path(tmp))
        art = Path(tmp) / 'module.so'
        art.write_bytes(b'\x7fELFfakebinary')

        key = 'test_key_123'
        mgr.store_artifacts(key, [art], {'info': 'test'})
        assert mgr.is_cached(key)

        # Restaura em outro diretório
        dest = Path(tmp) / 'restored'
        restored = mgr.get_cached_artifacts(key, dest)
        assert len(restored) == 1
        assert (dest / 'module.so').exists()
        assert (dest / 'module.so').read_bytes() == b'\x7fELFfakebinary'


def test_cache_clear_and_stats():
    with tempfile.TemporaryDirectory() as tmp:
        mgr = CacheManager(cache_dir=Path(tmp) / '.cache', root_dir=Path(tmp))
        art = Path(tmp) / 'test.bin'
        art.write_bytes(b'data' * 100)

        mgr.store_artifacts('key1', [art])
        stats = mgr.get_stats()
        assert stats['cached_entries'] == 1
        assert stats['total_size_bytes'] > 0

        cleared = mgr.clear()
        assert cleared > 0
        assert not mgr.is_cached('key1')

"""Orange Framework - Plataforma de Build, Compilação e Distribuição para Python."""

__version__ = '0.2.0'
__author__ = 'Anderson Rodrigues'
__license__ = 'MIT'

from orange.errors import (
    CacheError,
    CompilationError,
    ConfigurationError,
    OptimizationError,
    OrangeError,
    PackagingError,
    PlatformError,
)

__all__ = [
    '__version__',
    'OrangeError',
    'ConfigurationError',
    'CompilationError',
    'PackagingError',
    'OptimizationError',
    'PlatformError',
    'CacheError',
]

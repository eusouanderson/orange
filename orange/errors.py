"""Definição de exceções especializadas do Orange Framework."""


class OrangeError(Exception):
    """Exceção base para todos os erros do Orange Framework."""

    def __init__(self, message: str, details: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details

    def __str__(self) -> str:
        if self.details:
            return f'{self.message}\nDetalhes: {self.details}'
        return self.message


class ConfigurationError(OrangeError):
    """Erro em arquivo de configuração (orange.toml) ou validação de parâmetros."""

    pass


class PlatformError(OrangeError):
    """Erro de incompatibilidade ou falta de ferramentas no sistema operacional."""

    pass


class CompilationError(OrangeError):
    """Erro durante a transpilação Cython ou compilação C nativa."""

    pass


class PackagingError(OrangeError):
    """Erro durante o empacotamento com PyInstaller."""

    pass


class OptimizationError(OrangeError):
    """Erro durante a otimização ou compressão (UPX, stripping)."""

    pass


class CacheError(OrangeError):
    """Erro no gerenciamento do cache de compilação."""

    pass


class PluginError(OrangeError):
    """Erro de carregamento ou execução de plugins."""

    pass

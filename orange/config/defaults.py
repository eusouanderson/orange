"""Modelos e templates padrão para arquivos de configuração orange.toml."""

DEFAULT_ORANGE_TOML = """# =====================================================================
# Orange Framework - Arquivo de Configuração Central (orange.toml)
# Documentação: https://github.com/eusouanderson/orange
# =====================================================================

[project]
name = "{name}"
version = "{version}"
source = "./src"
entrypoint = "{entrypoint}"
description = "{description}"
authors = ["{author}"]

[build]
profile = "production"
compile_all = false
clean = true
output = "./dist"

[compiler]
cython = true
optimization = 2
c_compiler = "auto"
language_level = 3
type_hints = true
extra_cflags = []

[packaging]
pyinstaller = true
onefile = true
upx = true
console = true
hidden_imports = []
add_data = []

[cache]
enabled = true
directory = ".orange/cache"

[reports]
enabled = true
format = ["json", "html"]
output_dir = "./dist/reports"

[platforms]
linux = true
windows = true
macos = true

# =====================================================================
# Perfis Personalizados (Opcional)
# =====================================================================
# [profile.custom_debug]
# compiler.optimization = 0
# packaging.upx = false
# packaging.console = true
# build.clean = false
"""


def generate_default_toml(
    name: str = 'my-application',
    version: str = '1.0.0',
    entrypoint: str = './src/core/main.py',
    description: str = 'Aplicação compilada com Orange Framework',
    author: str = 'Anderson Rodrigues <eusouanderson@outlook.com>',
) -> str:
    """Gera o conteúdo de um orange.toml padrão configurado."""
    return DEFAULT_ORANGE_TOML.format(
        name=name,
        version=version,
        entrypoint=entrypoint,
        description=description,
        author=author,
    )

# Guia Completo de Configuração: orange.toml

O arquivo `orange.toml` é o manifesto central declarativo de qualquer aplicação gerenciada pelo **Orange Framework**. Ele controla o comportamento dos compiladores Cython, empacotador PyInstaller, otimizador UPX, cache e relatórios.

---

## 1. Esquema Completo Anotado

```toml
# =====================================================================
# Orange Framework - Arquivo de Configuração Central (orange.toml)
# =====================================================================

[project]
name = "my-application"                     # Nome oficial da aplicação
version = "1.0.0"                           # Versão SemVer
source = "./src"                            # Diretório com o código-fonte Python
entrypoint = "./src/core/main.py"           # Ponto de entrada executável principal
description = "Descrição detalhada do aplicativo"
authors = ["Nome do Desenvolvedor <dev@exemplo.com>"]

[build]
profile = "production"                      # Perfil padrão: development, release ou production
compile_all = false                         # Se true, transpila todos os .py do source para C
clean = true                                # Se true, limpa artefatos temporários após o build
output = "./dist"                           # Diretório de destino do binário compilado
target_name = "MyApp"                       # Nome do binário final gerado (opcional)

[compiler]
cython = true                               # Habilita compilação C via Cython
optimization = 3                            # Nível de otimização C do GCC/Clang (0, 1, 2 ou 3)
c_compiler = "auto"                         # auto, gcc, clang ou msvc
language_level = 3                          # Python 3
type_hints = true                           # Utiliza type hints do Python para otimizar tipos C
extra_cflags = ["-O3", "-fPIC"]             # Flags adicionais passadas ao compilador C

[packaging]
pyinstaller = true                          # Habilita empacotamento standalone via PyInstaller
onefile = true                              # true: arquivo único autossuficiente; false: pasta onedir
upx = true                                  # Habilita compressão de binários com UPX
console = true                              # true: exibe terminal (CLI); false: oculta console (GUI)
icon = "./src/assets/images/icons/app.ico"  # Ícone do executável (Windows/macOS)
hidden_imports = [                          # Módulos importados dinamicamente que devem ser embutidos
    "my_app.plugins",
    "sqlite3"
]
add_data = [                                # Arquivos ou pastas adicionais a incluir no bundle
    "src/assets:assets"                     # Formato origem:destino_no_bundle
]

[cache]
enabled = true                              # Habilita cache inteligente incremental
directory = ".orange/cache"                 # Pasta de armazenamento dos hashes e binários

[reports]
enabled = true                              # Habilita geração de métricas de compilação
format = ["json", "html"]                   # Formatos: terminal, json, html
output_dir = "./dist/reports"               # Pasta para os relatórios de compilação

[platforms]
linux = true                                # Habilita compilação para Linux
windows = true                              # Habilita compilação para Windows
macos = true                                # Habilita compilação para macOS
```

---

## 2. Perfis de Compilação (*Build Profiles*)

O Orange suporta três perfis pré-configurados que podem ser alternados facilmente via CLI (`orange build --profile <nome>`):

| Característica | `development` | `release` | `production` |
| :--- | :--- | :--- | :--- |
| **Cython** | Opcional | Ativo | Ativo |
| **Otimização C** | Nível 0 (`-O0`) | Nível 2 (`-O2`) | Nível 3 (`-O3`) |
| **UPX** | Desabilitado | Habilitado | Habilitado |
| **Onefile** | Desabilitado (`onedir`) | Opcional | Habilitado |
| **Clean Intermediários** | `false` (incremental rápido) | `true` | `true` |
| **Foco** | Velocidade de iteração | Teste pré-lançamento | Distribuição final compacta |

---

## 3. Sobrescrita de Configurações via CLI

Qualquer valor definido no `orange.toml` pode ser sobrescrito em tempo de execução pelos parâmetros da linha de comando:

```bash
# Compila forçando o perfil production e limpando saída
orange build --profile production --clean

# Compila sobrescrevendo o diretório de saída
orange build --output ./bin_releases

# Força a compilação de todos os arquivos .py do projeto para C nativo
orange build --compile-all
```

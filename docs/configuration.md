# Guia de Configuração (`orange.toml`)

O Orange Framework adota uma abordagem de configuração centralizada e declarativa via **TOML** através do arquivo `orange.toml`.

---

## 1. Exemplo Completo de `orange.toml`

```toml
[project]
name = "my-application"
version = "1.0.0"
source = "./src"
entrypoint = "./src/main.py"
icon = "./src/assets/icon.png"

[build]
profile = "production"
compile_all = true
clean = true
output = "./dist"
target_name = "my-app"

[compiler]
cython = true
optimization = 3
c_compiler = "auto"
annotate = false
keep_c = false

[packaging]
pyinstaller = true
onefile = true
noconsole = true
upx = true
clean = true

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
```

---

## 2. Seções e Parâmetros

### `[project]`
Metadados essenciais da aplicação:
- `name` *(string)*: Nome oficial do projeto.
- `version` *(string)*: Versão semântica (ex: `1.0.0`).
- `source` *(string)*: Diretório onde residem os módulos Python.
- `entrypoint` *(string)*: Arquivo de entrada principal a ser executado.
- `icon` *(string, opcional)*: Caminho para o ícone da aplicação (`.ico` ou `.png`).

### `[build]`
Parâmetros gerais do processo de build:
- `profile` *(string)*: Perfil de compilação padrão (`development`, `release`, `production`).
- `compile_all` *(bool)*: Se `true`, todos os arquivos `.py` em `source` serão compilados para C.
- `clean` *(bool)*: Se `true`, limpa artefatos temporários após o término do build.
- `output` *(string)*: Diretório de destino final dos executáveis gerados.
- `target_name` *(string, opcional)*: Nome do binário final gerado.

### `[compiler]`
Configurações do compilador Cython e GCC/Clang/MSVC:
- `cython` *(bool)*: Habilita ou desabilita a transpilação para C nativo.
- `optimization` *(int, 0 a 3)*: Nível de otimização das flags do compilador C (`-O0` a `-O3`).
- `c_compiler` *(string)*: Compilador C a utilizar (`auto`, `gcc`, `clang`, `msvc`).
- `annotate` *(bool)*: Gera relatórios HTML de anotação de tipos do Cython.
- `keep_c` *(bool)*: Mantém os arquivos intermediários `.c` após a compilação.

### `[packaging]`
Configurações do empacotador PyInstaller:
- `pyinstaller` *(bool)*: Habilita empacotamento com PyInstaller.
- `onefile` *(bool)*: Gera um único arquivo executável autônomo.
- `noconsole` *(bool)*: Oculta a janela de terminal no Windows/macOS (modo GUI).
- `upx` *(bool)*: Aplica compressão de executável via UPX.

### `[cache]`
Gerenciamento de cache incremental:
- `enabled` *(bool)*: Ativa cache inteligente baseado em hashes SHA-256.
- `directory` *(string)*: Diretório onde os hashes e binários são cacheados.

### `[reports]`
Geração de métricas e relatórios:
- `enabled` *(bool)*: Ativa a emissão de relatórios ao final do build.
- `format` *(lista de strings)*: Formatos desejados (`["json", "html"]`).
- `output_dir` *(string)*: Diretório onde os relatórios serão gravados.

---

## 3. Perfis de Compilação Pré-definidos

O Orange inclui três perfis otimizados nativamente:

| Propriedade | `development` | `release` | `production` |
|---|---|---|---|
| **Otimização C** | Nível 0 (`-O0`) | Nível 2 (`-O2`) | Nível 3 (`-O3`) |
| **Transpilação Cython** | Desativada | Ativa (módulos críticos) | Ativa (`--compile-all`) |
| **Limpeza de Temporários** | Não | Sim | Sim |
| **Compressão UPX** | Desativada | Ativa | Ativa |
| **Relatórios de Métricas** | Sim (Terminal) | Sim (Terminal + JSON) | Sim (Terminal, JSON, HTML) |

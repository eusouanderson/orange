# 🍊 Orange Framework

[![CI (Lint & Tests)](https://github.com/eusouanderson/orange/actions/workflows/ci.yml/badge.svg)](https://github.com/eusouanderson/orange/actions/workflows/ci.yml)
[![CodeQL Analysis](https://github.com/eusouanderson/orange/actions/workflows/codeql.yml/badge.svg)](https://github.com/eusouanderson/orange/actions/workflows/codeql.yml)
[![Multi-Platform Test Suite](https://github.com/eusouanderson/orange/actions/workflows/tests.yml/badge.svg)](https://github.com/eusouanderson/orange/actions/workflows/tests.yml)
[![Cross-Platform Build](https://github.com/eusouanderson/orange/actions/workflows/build.yml/badge.svg)](https://github.com/eusouanderson/orange/actions/workflows/build.yml)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

> **Plataforma profissional de compilação, otimização, empacotamento e distribuição de aplicações Python em binários standalone de alta performance para Linux, Windows e macOS.**

O **Orange** automatiza e moderniza o ciclo de compilação de aplicações Python, combinando transpilação em C via **Cython**, compilação nativa com **GCC / Clang / MSVC**, empacotamento standalone com **PyInstaller**, compressão com **UPX**, cache inteligente baseado em **SHA-256** e integração nativa com **GitHub Actions**.

---

## ✨ Principais Funcionalidades

- **CLI Profissional (`orange`)**: Interface de terminal ergonômica com diagnósticos (`orange doctor`), geração de configurações (`orange init`), compilação (`orange build`), cache e plugins.
- **Configuração Declarativa (`orange.toml`)**: Centralização de metadados, perfis, opções de compilador, empacotamento e métricas em um único arquivo de configuração validado.
- **Perfis de Compilação Pré-configurados**:
  - `development`: Compilação rápida para depuração sem overhead de otimização.
  - `release`: Compilação balanceada com empacotamento e verificações de integridade.
  - `production`: Transpilação C completa (`--compile-all`), otimizações máximas do compilador C (`-O3`), limpeza de temporários e compressão UPX.
- **Cache Inteligente**: Hashing criptográfico SHA-256 de código-fonte e opções de compilação para evitar recompilação de módulos inalterados.
- **Abstração Multiplataforma Avançada**:
  - **Linux**: Inspeção de binários ELF, injeção de `$ORIGIN` no RPATH via `patchelf`, verificação de compatibilidade com baseline GLIBC.
  - **Windows**: Inspeção de cabeçalhos PE32/PE32+, geração de manifestos de privilégios UAC (`asInvoker`, `requireAdministrator`), suporte a Windows Long Paths (`\\?\`) e verificação de VC++ CRT.
  - **macOS**: Inspeção de binários Mach-O individuais e **Universal (Fat Binaries)** (`x86_64` + `arm64`), assinatura ad-hoc com `codesign` e geração de `entitlements.plist` para Hardened Runtime.
- **GitHub Action Oficial (`action.yml`)**: Ação composta nativa para compilação multiplataforma e publicação de executáveis em releases com uma única linha de configuração.
- **Suporte a Docker Multi-Stage**: Imagens otimizadas com estágios separados de `builder` (compilação completa) e `runtime` (distroless/slim mínima).
- **Sistema de Plugins Extensível**: Descoberta automática de plugins externos via Python entrypoints (`orange.plugins`) e hooks de ciclo de vida do build (`pre_build`, `post_build`).
- **Relatórios de Métricas**: Emissão de relatórios em JSON, HTML e Terminal com histórico de métricas e comparador de regressão de tamanho e tempo de build.

---

## 🚀 Instalação Rápida

```bash
# Via pip
pip install orange-micro-framework

# Via Poetry
poetry add orange-micro-framework
```

---

## ⚡ Início Rápido (Quickstart)

### 1. Inicialize a Configuração
No diretório do seu projeto Python, gere o arquivo `orange.toml`:

```bash
orange init
```

### 2. Valide o Ambiente de Compilação
Verifique se os compiladores C, Python e ferramentas auxiliares estão prontos:

```bash
orange doctor
```

### 3. Compile a sua Aplicação
Execute o build do executável standalone:

```bash
# Compilação padrão
orange build

# Compilação otimizada para produção
orange build --profile production

# Teste prévio da configuração
orange build --dry-run
```

O binário final compilado e autônomo será gerado em `./dist/` pronto para distribuição!

---

## 📄 Exemplo de Configuração: `orange.toml`

```toml
[project]
name = "minha-aplicacao"
version = "1.0.0"
source = "./src"
entrypoint = "./src/main.py"
icon = "./src/assets/icon.png"

[build]
profile = "production"
compile_all = true
clean = true
output = "./dist"

[compiler]
cython = true
optimization = 3
c_compiler = "auto"

[packaging]
pyinstaller = true
onefile = true
upx = true

[cache]
enabled = true
directory = ".orange/cache"

[reports]
enabled = true
format = ["json", "html"]
```

---

## 🤖 Integração com GitHub Actions

Compile seu executável automaticamente em matriz multiplataforma (Linux, Windows e macOS) adicionando a action ao seu workflow:

```yaml
name: Multiplatform Build Pipeline

on:
  push:
    branches: [main]

jobs:
  build:
    name: Build on ${{ matrix.os }}
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]

    steps:
      - uses: actions/checkout@v4

      - name: Build Executável com Orange
        uses: eusouanderson/orange@main
        with:
          source: ./src
          output: ./dist
          profile: production
          compile-all: true
          python-version: '3.12'
          cache: true
          upload-artifact: true
```

---

## 🐳 Uso com Docker

Compile sem instalar dependências nativas no seu sistema operacional:

```bash
# Compila o executável gerando o binário no host em ./dist
docker compose run --rm orange-build

# Executa o aplicativo conteinerizado na imagem de runtime mínima
docker compose up orange-app
```

---

## 📚 Documentação Detalhada

- [Referência Completa da Linha de Comando (CLI)](docs/cli.md)
- [Guia de Configuração e Esquema do `orange.toml`](docs/configuration.md)
- [Arquitetura Modular e Componentes](docs/architecture.md)
- [Integração e Workflows no GitHub Actions](docs/github-actions.md)
- [Guia de Docker e Conteinerização](docs/docker.md)

---

## 🧪 Testes Automatizados

O Orange Framework conta com suíte de testes com cobertura em todos os domínios:

```bash
# Executa todos os testes unitários rápidos
poetry run orange test --fast

# Executa testes com relatório de cobertura de código
poetry run orange test --coverage

# Executa checagem de código com o linter Ruff
poetry run ruff check
```

---

## 📄 Licença

Este projeto é distribuído sob a licença **MIT**. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.

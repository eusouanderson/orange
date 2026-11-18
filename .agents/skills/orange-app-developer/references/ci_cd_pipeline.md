# Integração com GitHub Actions e CI/CD

O **Orange Framework** possui uma **Composite Action oficial** (`eusouanderson/orange@main`) pronta para ser integrada em qualquer repositório de aplicações Python.

---

## 1. Utilizando a Orange Action em Qualquer Repositório

Para compilar e gerar executáveis da sua aplicação em CI/CD sem precisar instalar manualmente compiladores C, UPX ou PyInstaller, adicione a step em seu workflow:

```yaml
- name: Compilar com Orange Framework
  uses: eusouanderson/orange@main
  with:
    source: ./src
    output: ./dist
    profile: production
    compile-all: false
    python-version: '3.12'
    config-file: orange.toml
    cache: true
    upload-artifact: true
    artifact-name: my-app-binary
```

---

## 2. Pipeline Multiplataforma Completo (Linux, macOS, Windows)

Crie o arquivo `.github/workflows/build-and-release.yml` na sua aplicação:

```yaml
name: Cross-Platform Build & Release

on:
  push:
    branches: [main]
    tags: ['v*']
  pull_request:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: write

jobs:
  # 1. Qualidade de Código e Testes Unitários Isolados por Domínio
  test:
    name: Lint & Testes por Domínio
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Código
        uses: actions/checkout@v4

      - name: Configurar Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Instalar Poetry
        run: pip install poetry

      - name: Instalar Dependências
        run: poetry install --with dev

      - name: Linter com Ruff
        run: poetry run ruff check && poetry run ruff format --check

      - name: Executar Testes por Domínio
        run: poetry run pytest tests/ --cov=src

  # 2. Matriz Multiplataforma de Compilação de Binários
  build:
    name: Build em ${{ matrix.os }}
    needs: test
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]

    steps:
      - name: Checkout Código
        uses: actions/checkout@v4

      - name: Compilar Binário com Orange Action
        id: orange-build
        uses: eusouanderson/orange@main
        with:
          source: ./src
          output: ./dist
          profile: production
          config-file: orange.toml
          cache: true
          upload-artifact: true
          artifact-name: my-app-${{ matrix.os }}

  # 3. Publicação Automática de Releases no GitHub
  release:
    name: Criar GitHub Release
    if: startsWith(github.ref, 'refs/tags/v')
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Download de Todos os Artefatos
        uses: actions/download-artifact@v4
        with:
          path: release-artifacts

      - name: Publicar Release com Binários Nativos
        uses: softprops/action-gh-release@v2
        with:
          files: release-artifacts/**/*
          generate_release_notes: true
```

---

## 3. Benefícios do Cache Inteligente no CI/CD

Quando o parâmetro `cache: true` está ativo na Orange Action:
- O Orange calcula o hash SHA-256 de todo o código-fonte (`.py`), do `orange.toml` e do ambiente Python.
- Se o código não sofreu alterações que afetem a compilação C, os binários já gerados são reutilizados instantaneamente, reduzindo o tempo de CI de minutos para poucos segundos.

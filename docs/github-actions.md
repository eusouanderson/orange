# Integração com GitHub Actions

O Orange Framework fornece suporte oficial de primeira classe para pipelines de CI/CD do GitHub Actions através de uma **Composite Action** oficial e **Reusable Workflows**.

---

## 1. Utilizando a Orange Action (`action.yml`)

Para integrar o Orange em qualquer repositório de aplicação Python no GitHub Actions, basta adicionar a seguinte etapa ao seu workflow:

```yaml
name: Build & Release Application

on:
  push:
    branches: [main]
  pull_request:
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
      - name: Checkout Código
        uses: actions/checkout@v4

      - name: Build com Orange Action
        uses: eusouanderson/orange@main
        with:
          source: ./src
          output: ./dist
          profile: production
          compile-all: true
          python-version: '3.12'
          cache: true
          upload-artifact: true
          artifact-name: my-app-binary
```

---

## 2. Entradas da Action (`inputs`)

| Entrada | Tipo | Padrão | Descrição |
|---|---|---|---|
| `source` | string | `./src` | Diretório contendo os arquivos fonte Python da aplicação. |
| `output` | string | `./dist` | Diretório de destino do executável standalone. |
| `profile` | string | `production` | Perfil de compilação (`development`, `release`, `production`). |
| `compile-all` | boolean | `false` | Se `true`, todos os arquivos Python serão compilados para C. |
| `python-version` | string | `3.12` | Versão do Python utilizada no build. |
| `config-file` | string | `orange.toml` | Caminho do arquivo de configuração do Orange. |
| `cache` | boolean | `true` | Ativa cache inteligente de dependências e artefatos compilados. |
| `upload-artifact` | boolean | `true` | Se `true`, realiza o upload automático do executável gerado como artefato do GitHub Actions. |
| `artifact-name` | string | `application-binary` | Prefixo do nome do artefato enviado ao GitHub. |

---

## 3. Saídas da Action (`outputs`)

- `executable-path`: Caminho relativo ou absoluto para o binário executável compilado.
- `build-status`: Status final da compilação (`success` ou `failed`).

---

## 4. Reusable Workflow (`reusable-build.yml`)

O repositório também disponibiliza um fluxo reutilizável completo que orquestra setup, compilação e upload de artefatos:

```yaml
jobs:
  call-orange-build:
    uses: eusouanderson/orange/.github/workflows/reusable-build.yml@main
    with:
      source: ./src
      output: ./dist
      profile: production
      compile-all: true
      python-version: '3.12'
      os: ubuntu-latest
```

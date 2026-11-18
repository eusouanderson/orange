# Referência da Linha de Comando (Orange CLI)

A **Orange CLI** é a interface oficial de terminal para gerenciamento de compilação, diagnóstico, perfis, cache e plugins do Orange Framework.

---

## 1. Comandos Disponíveis

```bash
orange [OPÇÕES_GLOBAIS] COMANDO [OPÇÕES_DO_COMANDO]
```

### Opções Globais

- `-c, --config CAMINHO`: Especifica o caminho alternativo para o arquivo `orange.toml` (padrão: `./orange.toml`).
- `-v, --verbose`: Exibe logs detalhados e stack traces de depuração.
- `-q, --quiet`: Modo silencioso, suprime saídas não essenciais para automações e CI/CD.
- `-h, --help`: Exibe a ajuda da CLI.
- `--version`: Exibe a versão do Orange.

---

## 2. Comandos Detalhados

### `orange build`
Compila e empacota a aplicação Python em um binário nativo autônomo (*standalone*).

```bash
orange build [OPÇÕES]
```

#### Opções:
- `-c, --config CAMINHO`: Caminho alternativo para o `orange.toml`.
- `-p, --profile [development|release|production|custom]`: Seleciona o perfil de compilação.
- `--platform [linux|windows|macos]`: Define a plataforma alvo.
- `--compile-all`: Força a transpilação e compilação em C de todos os módulos `.py`.
- `--clean / --no-clean`: Executa ou ignora a limpeza de artefatos temporários antes do build.
- `-o, --output DIRETÓRIO`: Sobrescreve o diretório de destino dos binários.
- `--target-name NOME`: Define o nome do executável final gerado.
- `--dry-run`: Valida as dependências e a configuração sem executar a compilação.

#### Exemplos:
```bash
# Build padrão usando configurações do orange.toml
orange build

# Build otimizado para produção
orange build --profile production

# Validação pré-build em pipeline de CI
orange build --dry-run
```

---

### `orange doctor`
Executa o diagnóstico completo de saúde do ambiente de compilação, validando compiladores, bibliotecas e utilitários instalados.

```bash
orange doctor
```

#### Verificações Realizadas:
- Versão do Python (`>= 3.10`).
- Compilador C nativo (`GCC`, `Clang` ou `MSVC`).
- Transpilador `Cython`.
- Empacotador `PyInstaller`.
- Compressor de binários `UPX` (opcional).
- Controle de versão `Git`.

---

### `orange init`
Gera um arquivo de configuração `orange.toml` interativo ou com valores padrão para o projeto.

```bash
orange init [OPÇÕES]
```

#### Opções:
- `--force`: Sobrescreve um arquivo `orange.toml` existente no diretório atual.

---

### `orange cache`
Gerencia o cache inteligente de dependências e hashes SHA-256 de módulos compilados.

```bash
# Exibe tamanho e quantidade de entradas em cache
orange cache status

# Limpa todos os artefatos armazenados em cache
orange cache clear
```

---

### `orange plugins`
Gerencia o ecossistema de extensibilidade e plugins do Orange.

```bash
# Lista todos os plugins carregados e ativos
orange plugins list

# Exibe detalhes de um plugin específico
orange plugins info <NOME_DO_PLUGIN>

# Instala um plugin externo via pip
orange plugins install <PACOTE_DO_PLUGIN>

# Remove um plugin instalado
orange plugins uninstall <PACOTE_DO_PLUGIN>
```

---

### `orange test`
Executa a suíte de testes automatizados com `pytest`, com suporte a argumentos adicionais.

```bash
# Executa todos os testes
orange test

# Executa apenas testes rápidos (ignora benchmarks)
orange test --fast

# Executa testes com relatório de cobertura de código
orange test --coverage
```

---

### `orange version` & `orange info`
Exibe informações de diagnóstico da versão e do ambiente operacional.

```bash
# Versão rápida em formato legível ou JSON
orange version
orange version --json-output

# Relatório completo do ambiente, compilador, projeto e orange.toml
orange info
```

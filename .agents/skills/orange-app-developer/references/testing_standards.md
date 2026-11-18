# Padrões Obrigatórios de Testes Automatizados no Orange

Este documento define as diretrizes rigorosas para a suíte de testes de qualquer aplicação construída com o Orange Framework.

---

## 1. Regra Fundamental: Organização Estrita por Domínio

> [!IMPORTANT]
> **REGRA MANDATÓRIA DO PROJETO:**
> Na pasta `tests/`, **todo e qualquer domínio da aplicação deve obrigatoriamente possuir um diretório próprio com o nome do domínio**, contendo um arquivo `__init__.py` e seus respectivos arquivos de teste `test_*.py`.
>
> **É estritamente proibido** colocar arquivos de teste soltos na raiz de `tests/`.

### Estrutura Obrigatória de Pastas de Teste:

```text
tests/
├── __init__.py
├── conftest.py                     # Fixtures compartilhadas e configuração de ambiente
├── domain/                         # Domínio de regras de negócio
│   ├── __init__.py
│   ├── test_entities.py
│   └── test_rules.py
├── application/                    # Casos de uso e serviços
│   ├── __init__.py
│   ├── test_services.py
│   └── test_dtos.py
├── infrastructure/                 # Adaptadores de banco de dados, arquivos e APIs
│   ├── __init__.py
│   ├── test_storage.py
│   └── test_adapters.py
└── presentation/                   # Interfaces de CLI, controladores e GUI
    ├── __init__.py
    ├── test_cli.py
    └── test_controllers.py
```

---

## 2. Padrões de Implementação de Testes

### A. Isolamento e Mocking
1. **Sem I/O Real nos Testes Unitários**:
   - Utilize a fixture padrão `tmp_path` do pytest ou mocks para chamadas de sistema.
2. **Ambientes Headless (Sem Interface Gráfica)**:
   - Em testes de componentes visuais (ex: PyQt6), utilize `pytest.skip` ou instancie `QApplication` com flag `-platform offscreen`:
   ```python
   import pytest


   @pytest.fixture(scope='session')
   def qapp():
       try:
           from PyQt6.QtWidgets import QApplication

           app = QApplication.instance()
           if app is None:
               app = QApplication(['app', '-platform', 'offscreen'])
           return app
       except Exception:
           pytest.skip('PyQt6 não disponível para testes gráficos headless')
   ```

### B. Manipulação Segura de Binários no Windows (Prevenção de WinError 5)
Ao testar rotinas de compilação ou carregamento dinâmico de extensões C (`.pyd` no Windows), o sistema operacional bloqueia a remoção do arquivo enquanto a biblioteca estiver mapeada na memória do processo.

> [!WARNING]
> Sempre utilize `tempfile.TemporaryDirectory(ignore_cleanup_errors=True)` ao criar pastas temporárias que receberão binários `.pyd`:

```python
import tempfile
from pathlib import Path


def test_compiled_native_module():
    # ignore_cleanup_errors=True evita PermissionError: [WinError 5] Access is denied no Windows
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        build_dir = Path(tmp)
        # Executa compilação e teste do módulo
        assert build_dir.exists()
```

---

## 3. Qualidade de Código e Linting

Toda a suíte de código e testes deve manter **zero erros** no Ruff:

1. **Checagem estática**:
   ```bash
   poetry run ruff check
   ```
2. **Formatação de código**:
   ```bash
   poetry run ruff format --check
   ```
3. **Execução de Testes com Cobertura**:
   ```bash
   poetry run pytest --cov=src tests/
   ```

---

## 4. Testes do CLI Orange

Ao testar comandos de CLI desenvolvidos com Click, utilize `CliRunner` do Click para isolar `stdout`, `stderr` e códigos de retorno:

```python
from click.testing import CliRunner
from src.presentation.cli import cli


def test_cli_version_command():
    runner = CliRunner()
    result = runner.invoke(cli, ['--version'])
    assert result.exit_code == 0
    assert '1.0.0' in result.output
```

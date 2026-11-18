# Otimização e Performance de Aplicações com Orange Framework

O **Orange Framework** combina **Cython**, **GCC/Clang/MSVC**, **PyInstaller** e **UPX** para gerar executáveis nativos ultrarrápidos e compactos. Este documento detalha como escrever código Python que extrai o máximo desempenho do pipeline do Orange.

---

## 1. Otimização com Cython em Modo Python Puro

Para manter o código 100% executável tanto no interpretador Python comum (durante desenvolvimento e testes) quanto compilado para C nativo (em produção), utilize o **Modo Python Puro do Cython** (`import cython`):

```python
from __future__ import annotations
import cython


# Diretivas de compilação aplicadas no topo do arquivo ou em funções críticas
@cython.cfunc
@cython.exceptval(check=False)
def fast_matrix_dot(
    a: cython.p_double, b: cython.p_double, size: cython.int
) -> cython.double:
    """Função com compilação direta para C sem sobrecarga do interpretador."""
    total: cython.double = 0.0
    i: cython.int
    for i in range(size):
        total += a[i] * b[i]
    return total


def calculate_analytics(data: list[float]) -> float:
    """Ponto de entrada Python público com checagem de tipos estática."""
    if not data:
        return 0.0

    n: cython.int = len(data)
    acc: cython.double = 0.0
    val: cython.double

    for val in data:
        acc += val

    return acc / n
```

### Regras de Otimização Cython no Orange:
1. **Tipagem Estática Explícita**: Sempre use anotações de tipo primitivo (`int`, `float`, `cython.int`, `cython.double`) nos loops internos.
2. **Desabilite Bounds Checking em Funções Críticas**:
   ```python
   @cython.boundscheck(False)
   @cython.wraparound(False)
   def vector_sum(arr: cython.double[:]) -> cython.double: ...
   ```
3. **Liberação do GIL para Concorrência Real**:
   Tarefas puramente matemáticas em arrays de memória podem liberar o Python Global Interpreter Lock (GIL), escalando em múltiplos núcleos de CPU reais:
   ```python
   with cython.nogil:
       # Processamento numérico puro em C
       pass
   ```
4. **Configuração no `orange.toml`**:
   ```toml
   [compiler]
   cython = true
   optimization = 3       # Nível 3 (-O3) para vetorização e unrolling de loops
   language_level = 3     # Python 3
   type_hints = true      # Compilador infere tipos das anotações Python padrão
   ```

---

## 2. Inicialização Rápida (*Fast Startup*) e Lazy Imports

O tempo de carregamento de um executável standalone empacotado com PyInstaller é sensível ao número de módulos importados na inicialização (`entrypoint`).

### Padrão de Importação Preguiçosa (*Lazy Import*):
Nunca importe dependências pesadas no topo de arquivos da camada de domínio ou no ponto de entrada global.

```python
# ❌ INCORRETO: Carrega bibliotecas pesadas no boot antes mesmo do usuário escolher a ação
import numpy as np
import pandas as pd
from PyQt6.QtWidgets import QApplication, QMainWindow


def run_cli_command():
    print('Executando comando simples...')
```

```python
# ✅ CORRETO: Carrega sob demanda apenas quando a rotina específica for invocada
def generate_report(data: list[dict]) -> None:
    # Importação diferida
    import pandas as pd

    df = pd.DataFrame(data)
    df.to_csv('report.csv')
```

---

## 3. Otimização de Empacotamento com PyInstaller

### A. Escolha de Modo: `onefile` vs `onedir`
- **`onefile = true`**: Ideal para utilitários de linha de comando (CLI) ou ferramentas distribuídas como arquivo único.
  - *Comportamento*: No boot, extrai as bibliotecas para uma pasta temporária do sistema operacional (`_MEIxxxx`).
- **`onefile = false` (`onedir`)**: Ideal para softwares de grande porte ou com interfaces gráficas pesadas (GUI com Qt/WebEngine).
  - *Vantagem*: Inicialização instantânea, pois os arquivos já residem no disco sem necessidade de descompactação prévia.

### B. Otimização de Imports Ocultos (`hidden_imports`):
Adicione apenas os módulos que o PyInstaller não consegue detectar estaticamente através de análise de AST:
```toml
[packaging]
pyinstaller = true
hidden_imports = ["orange.plugins", "my_app.adapters.sqlite"]
```

---

## 4. Otimização e Compressão com UPX

O **UPX (Ultimate Packer for eXecutables)** comprime binários nativos executáveis e bibliotecas compartilhadas (.so, .pyd, .dll).

### Melhores Práticas de UPX no Orange:
1. **Onefile Bundles**:
   - Em pacotes `onefile = true`, o Orange e o PyInstaller aplicam o UPX nas bibliotecas compartilhadas internas (.so/.dll) durante o empacotamento.
   - **Nunca** execute UPX manualmente sobre o arquivo `.exe` ou ELF final de um `onefile`, pois isso pode corromper o cabeçalho CArchive ou congelar o processo de inicialização. O Orange gerencia essa regra automaticamente.
2. **Onedir e Binários Nativos Standalone**:
   - Em modos `onedir` ou compilações de bibliotecas C, o UPX comprime o executável final com reduções de até 50% a 70% no tamanho em disco.
3. **Exclusões de Arquivos Delicados**:
   - Bibliotecas com proteção contra alteração de assinatura digital ou packers internos (como alguns runtimes do Windows CRT ou bibliotecas criptográficas) devem ser preservadas sem UPX se causarem falso positivo em antivírus.

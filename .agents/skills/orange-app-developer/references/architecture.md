# Arquitetura Limpa e Organização de Código no Orange Framework

Este guia estabelece os padrões arquiteturais obrigatórios para o desenvolvimento de aplicações Python de alta performance, manuteníveis e prontas para compilação nativa com o **Orange Framework**.

---

## 1. Princípios Arquiteturais Fundamentais

Ao construir uma aplicação destinada ao ecossistema Orange, o código deve seguir os princípios de **Clean Architecture** e **Domain-Driven Design (DDD)** simplificado:

1. **Independência de Frameworks**: O núcleo da regra de negócio não depende de bibliotecas externas de UI, bancos de dados ou empacotadores.
2. **Testabilidade Total**: Regras de negócio podem ser testadas sem UI, sem banco de dados, sem rede e sem compilação prévia.
3. **Direção Única de Dependência**: As camadas externas conhecem as internas; as internas **nunca** conhecem as camadas externas.
4. **Isolamento de Hotspots de Performance**: Módulos que exigem processamento intensivo em CPU ou proteção de propriedade intelectual devem ser explicitamente isolados para compilação estática com **Cython**.

```
    ┌──────────────────────────────────────────────┐
    │       Presentation (CLI / GUI / API)         │
    │  ┌────────────────────────────────────────┐  │
    │  │       Application (Use Cases / DTOs)   │  │
    │  │  ┌──────────────────────────────────┐  │  │
    │  │  │   Domain (Entities / Rules)      │  │  │
    │  │  └──────────────────────────────────┘  │  │
    │  │       Infrastructure (Adapters/IO)     │  │
    │  └────────────────────────────────────────┘  │
    └──────────────────────────────────────────────┘
```

---

## 2. Estrutura Padrão de Diretórios

Toda aplicação profissional desenvolvida com o Orange deve seguir a seguinte topologia de pastas:

```text
my-orange-app/
├── orange.toml                 # Configuração central de build, perfis e compiladores
├── pyproject.toml              # Metadados do projeto, dependências Poetry e linter
├── README.md                   # Documentação do projeto
├── src/
│   ├── __init__.py
│   ├── core/                   # Inicialização, container DI e ciclo de vida
│   │   ├── __init__.py
│   │   ├── container.py        # Injeção de dependências e composição de instâncias
│   │   └── main.py             # Entrypoint executável do PyInstaller
│   ├── domain/                 # Regras de negócio puras (Sem dependências I/O)
│   │   ├── __init__.py
│   │   ├── entities.py         # Modelos de dados e validações puras
│   │   ├── exceptions.py       # Exceções de domínio específicas
│   │   └── interfaces.py       # Protocolos / Contratos Abstratos (ABC)
│   ├── application/            # Casos de uso e orquestração
│   │   ├── __init__.py
│   │   ├── dtos.py             # Data Transfer Objects com validação de tipos
│   │   └── services.py         # Orquestradores de regras de negócio
│   ├── infrastructure/         # I/O, Sistema de Arquivos, Banco e Hardware
│   │   ├── __init__.py
│   │   ├── adapters.py         # Implementação concreta das interfaces do domínio
│   │   └── storage.py          # Persistência local ou remota
│   └── presentation/           # Interfaces de usuário (CLI / GUI)
│       ├── __init__.py
│       ├── cli.py              # Interface de linha de comando (Click / Rich)
│       └── gui/                # Interface gráfica (PyQt6 / PySide6 / Tkinter)
│           ├── __init__.py
│           └── views.py
└── tests/                      # TESTES OBRIGATORIAMENTE ORGANIZADOS POR DOMÍNIO
    ├── __init__.py
    ├── conftest.py             # Fixtures globais do pytest
    ├── domain/                 # Testes unitários do domínio
    │   ├── __init__.py
    │   └── test_entities.py
    ├── application/            # Testes unitários de use cases
    │   ├── __init__.py
    │   └── test_services.py
    ├── infrastructure/         # Testes de integração/mocks de I/O
    │   ├── __init__.py
    │   └── test_adapters.py
    └── presentation/           # Testes de CLI / Controllers
        ├── __init__.py
        └── test_cli.py
```

---

## 3. Diretrizes de Camadas

### A. Domínio (`src/domain/`)
- Contém apenas código Python puro.
- **Proibido**: importar `requests`, `PyQt6`, `sqlalchemy`, `sys.argv`, etc.
- Todas as operações externas devem ser abstraídas via `typing.Protocol` ou `abc.ABC`.
- Funções matemáticas e algorítmicas de alta intensidade devem residir aqui para receber otimização Cython nível 3 (`-O3`).

### B. Aplicação (`src/application/`)
- Orquestra o fluxo de dados entre entidades de domínio e os adaptadores de infraestrutura.
- Define `DTOs` imutáveis utilizando `dataclasses` com `frozen=True` ou `pydantic`.
- Converte exceções de infraestrutura em exceções compreensíveis de domínio.

### C. Infraestrutura (`src/infrastructure/`)
- Implementa as portas/interfaces do domínio (acesso a arquivos, rede, hardware).
- Trata timeouts, reconexões e erros de I/O de maneira resiliente.
- Carrega de forma preguiçosa (*lazy import*) bibliotecas externas pesadas que não são necessárias no boot.

### D. Apresentação (`src/presentation/`)
- CLI profissional com mensagens amigáveis, opções de verbose (`--verbose`) e silent (`--quiet`).
- Fallbacks automáticos de codificação UTF-8 para terminais Windows (cp1252/cp850).
- GUI opcional isolada: a aplicação deve ser completamente funcional sem interface gráfica.

### E. Ponto de Entrada (`src/core/main.py`)
- O arquivo apontado em `orange.toml` (`[project.entrypoint]`).
- Responsável por:
  1. Configurar encoding do terminal (`sys.stdout.reconfigure(encoding='utf-8')`).
  2. Inicializar tratamento global de exceções e sinais (`SIGINT`, `SIGTERM`).
  3. Fazer o bootstrap do container de dependências.
  4. Executar a camada de apresentação apropriada (CLI ou GUI).

---

## 4. Tratamento de Exceções e Resiliência

- Crie uma hierarquia explícita de exceções derivada de uma classe base do projeto:
  ```python
  class AppError(Exception):
      """Classe base de erros da aplicação."""

      def __init__(self, message: str, details: str | None = None) -> None:
          super().__init__(message)
          self.message = message
          self.details = details


  class ValidationError(AppError):
      """Falha de validação de dados de entrada."""


  class ProcessingError(AppError):
      """Falha no processamento algorítmico."""
  ```
- Nunca capture exceções genéricas (`except:`) sem logging ou relançamento.
- Registre rastros de erro detalhados apenas quando `verbose=True` ou em modo debug.

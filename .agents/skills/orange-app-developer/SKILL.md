---
name: orange-app-developer
description: >-
  Instrui agentes de IA e LLMs a arquitetar, desenvolver, otimizar, testar e compilar
  aplicações Python completas de alto nível profissional utilizando o Orange Framework.
  Ensina Clean Architecture, separação estrita de domínios, otimização C com Cython,
  empacotamento PyInstaller, compressão UPX, integração de CI/CD com GitHub Actions e a
  regra obrigatória de organização de testes por domínio em tests/<dominio>/.
---

# Orange Framework: Desenvolvimento Profissional de Aplicações

Esta skill é o guia definitivo para desenvolver softwares profissionais, ultra-otimizados e prontos para distribuição multiplataforma utilizando o **Orange Framework**.

---

## 🍊 As 5 Leis de Ouro do Desenvolvimento com Orange

Qualquer aplicação construída ou mantida com o Orange Framework deve obedecer rigorosamente às seguintes diretrizes:

### 1. Arquitetura Limpa e Isolamento de Domínios
- Estruture o código em camadas concêntricas: `src/domain/`, `src/application/`, `src/infrastructure/`, `src/presentation/` e `src/core/main.py`.
- O domínio é sagrado: **nenhuma regra de negócio deve depender de frameworks externos, GUI ou I/O**.
- O ponto de entrada (`entrypoint`) em `src/core/main.py` gerencia o ciclo de vida, encoding UTF-8 seguro e injeção de dependências.
- 📖 Consulte o guia detalhado em: [Clean Architecture](./references/architecture.md).

### 2. Organização Obrigatória de Testes por Domínio
> [!IMPORTANT]
> **REGRA MANDATÓRIA:**
> Na pasta `tests/`, cada domínio do sistema **deve obrigatoriamente possuir um diretório próprio com o nome do domínio**, contendo um arquivo `__init__.py` e seus respectivos arquivos de teste (`tests/<dominio>/test_<modulo>.py`).
>
> Arquivos soltos na raiz de `tests/` são expressamente proibidos.
- No Windows, sempre use `tempfile.TemporaryDirectory(ignore_cleanup_errors=True)` ao testar módulos nativos para evitar `WinError 5 (Access is Denied)`.
- 📖 Consulte os padrões completos em: [Padrões de Testes](./references/testing_standards.md).

### 3. Otimização Máxima com Cython (Modo Python Puro)
- Escreva código Python padrão enriquecido com anotações de tipo estático (`int`, `float`, `cython.int`, `cython.double`).
- Ative o nível 3 de otimização C no `orange.toml` (`[compiler.optimization = 3]`) para vetorização automática de loops e compilação nativa com GCC/Clang/MSVC.
- 📖 Consulte as técnicas em: [Guia de Otimização](./references/optimization.md).

### 4. Empacotamento Inteligente e Regras de UPX
- Para executáveis do tipo `--onefile`, o PyInstaller comprime os binários internos com UPX de maneira segura. **Nunca** tente re-executar UPX sobre o arquivo único final `.exe` ou ELF.
- Para distribuições `--onedir`, utilize UPX com timeout controlado para reduzir o tamanho dos binários em até 70%.
- 📖 Consulte as diretrizes de empacotamento em: [Guia de Configuração](./references/configuration.md).

### 5. Multiplataforma e CI/CD Nativo
- Garanta suporte transparente para Linux, macOS (Universal 2 / Mach-O 64-bit) e Windows (PE/Manifesto UAC).
- Utilize a GitHub Action oficial em seus pipelines: `uses: eusouanderson/orange@main`.
- 📖 Consulte o modelo de CI/CD em: [Pipeline GitHub Actions](./references/ci_cd_pipeline.md).

---

## 🛠️ Passo a Passo para Criar uma Nova Aplicação

### Passo 1: Inicializar a Estrutura do Projeto
Para criar a estrutura de diretórios, use o script de scaffold automático da skill:
```bash
python .agents/skills/orange-app-developer/scripts/scaffold_app.py --name "MinhaAplicacao" --dest "."
```
Ou crie manualmente o arquivo `orange.toml` na raiz utilizando o modelo em [examples/orange.toml](./examples/orange.toml).

### Passo 2: Implementar a Regra de Negócio
No diretório `src/domain/`, crie as entidades e serviços puros. Veja a implementação de referência em [examples/domain_app/src/domain/entities.py](./examples/domain_app/src/domain/entities.py).

### Passo 3: Implementar os Testes por Domínio
Crie a pasta de testes correspondente ao domínio:
```bash
mkdir -p tests/domain tests/application tests/presentation
touch tests/domain/__init__.py tests/application/__init__.py tests/presentation/__init__.py
```
Implemente os testes unitários. Veja exemplos funcionais em [examples/domain_app/tests/](./examples/domain_app/tests/).

### Passo 4: Validar Qualidade e Sintaxe
Execute o linter estático e garanta 0 erros e 100% de conformidade:
```bash
poetry run ruff check
poetry run ruff format --check
```

### Passo 5: Diagnóstico e Execução de Testes
Valide o ambiente local com o comando doctor do Orange:
```bash
orange doctor
orange test
```

### Passo 6: Compilação e Distribuição
Gere o executável final standalone:
```bash
# Para build de produção ultra-otimizado com Cython e UPX
orange build --profile production

# Para verificar as métricas e relatórios gerados
ls -lh dist/
cat dist/reports/build_metrics.json
```

---

## 📚 Mapa de Referências e Recursos

- 🏛️ **Arquitetura & Clean Code**: [architecture.md](./references/architecture.md)
- ⚡ **Otimização & Cython C-Speed**: [optimization.md](./references/optimization.md)
- 🧪 **Padrões de Testes por Domínio**: [testing_standards.md](./references/testing_standards.md)
- ⚙️ **Manual Completo do orange.toml**: [configuration.md](./references/configuration.md)
- 🚀 **Automação de CI/CD com GitHub Actions**: [ci_cd_pipeline.md](./references/ci_cd_pipeline.md)
- 💻 **Projeto Exemplo Completo**: [examples/domain_app/](./examples/domain_app/)
- 📜 **Gerador Automático de Boilerplate**: [scripts/scaffold_app.py](./scripts/scaffold_app.py)

# 🗺️ Orange Framework - Roadmap & Próximos Passos

**Status:** v0.1.148 | **Atualizado:** Janeiro 2026

---

## 🎯 Visão Geral

Este documento detalha o plano de desenvolvimento para Orange Framework, dividido em **4 fases temporais** com ações específicas, métricas de sucesso e dependências.

---

## 📋 Próximas Ações Recomendadas

### ⏱️ **IMEDIATO** (Esta Semana - Ações Bloqueantes)

**Objetivo:** Validar ambiente de build e customizar interface base

#### [ ] Testar `--compile-all` Flag Localmente
- **Ação:** Execute build com todas as funcionalidades
  ```bash
  make build FLAGS="--compile-all"
  ```
- **Resultado esperado:** 
  - Executável compilado (~120MB antes de compressão)
  - Gain de performance 20-30% vs Python puro
  - Arquivo ZIP pronto em `dist/`
- **Tempo estimado:** 30-45 minutos
- **Bloqueador?** Não, mas recomendado antes de otimizações

#### [ ] Customizar `src/core/main.py` com Sua Interface
- **Ação:** Editar classe `Calc3D` para sua aplicação
  ```python
  # Modifique:
  # - initUI() para seu layout
  # - Adicione novos métodos de cálculo
  # - Customize tema/cores em _aplicar_tema()
  ```
- **Checklist:**
  - [ ] Layout finalizado
  - [ ] Todos os inputs funcionando
  - [ ] Testes locais passando (`make test`)
  - [ ] Theme aplicado (cores, fontes)
- **Tempo estimado:** 2-4 horas
- **Bloqueador?** SIM - não compile sem isso!

#### [ ] Rodar Suite de Testes (`make test`)
- **Ação:** Validar que ambiente está OK
  ```bash
  make test  # Deve retornar: 43/43 PASSED
  ```
- **Resultado esperado:**
  ```
  ======================== 43 passed in ~2.8s ========================
  ```
- **Se falhar:**
  - Verifique Poetry install: `poetry install`
  - Limpe cache: `make clean`
  - Reporte issue no GitHub
- **Tempo estimado:** 5 minutos

---

### 📅 **CURTO PRAZO** (Este Mês - Otimizações Básicas)

**Objetivo:** Ganhar performance inicial + documentar uso

#### [ ] Adicionar Type Hints Cython para Geometria 3D
- **Ação:** Editar `src/core/main.py` com type hints estáticos
- **Ganho:** +5-15% de performance
- **Implementação:**
  ```python
  # Adicione no topo do arquivo:
  # cython: language_level=3, optimize.unpack_method_calls=True
  
  def _calcular_distancia_3d(self,
                             double x1, double y1, double z1,
                             double x2, double y2, double z2) -> double:
      """Tipos C estáticos = sem overhead"""
      return sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)
  ```
- **Validação:**
  - [ ] Código compila sem erros
  - [ ] Testes passam
  - [ ] Benchmark mostra melhoria
- **Tempo estimado:** 2-3 horas
- **Documentação:** [BUILD_OPTIMIZATION_GUIDE.md](BUILD_OPTIMIZATION_GUIDE.md) Nível 2

#### [ ] Benchmarking Antes/Depois com pytest-benchmark
- **Ação:** Medir performance real com e sem otimizações
- **Comando:**
  ```bash
  poetry run pytest tests/test_performance.py --benchmark-only -v
  ```
- **Métricas para coletar:**
  - Tempo médio de cálculo (antes/depois)
  - OPS (operations per second)
  - Desvio padrão
- **Documentar:** Criar arquivo `PERFORMANCE_BASELINE.md`
  ```markdown
  ## Baseline (v0.1.148 sem otimizações)
  - Distância 3D: 1.1 ms ± 0.2 ms
  - CPU: Intel Core i7-12700H
  
  ## Com Type Hints Cython
  - Distância 3D: 0.9 ms ± 0.15 ms (18% ganho)
  ```
- **Tempo estimado:** 1 hora
- **Bloqueador?** Não, informativo

#### [ ] Documentar Performance para Usuários
- **Ação:** Criar `docs/PERFORMANCE_GUIDE.md`
- **Conteúdo:**
  - Explicar por que Orange é mais rápido
  - Mostrar benchmarks reais
  - Instruções para otimizar código do usuário
  - Dicas de Cython para iniciantes
- **Tempo estimado:** 2-3 horas
- **Resultado:** Usuários entendem valor da ferramenta

---

### 🔄 **MÉDIO PRAZO** (Próximo Trimestre - Funcionalidades Novas)

**Objetivo:** Performance avançada + estabilidade produção

#### [ ] Implementar Multiprocessing para Batch Calcs
- **Ação:** Permitir cálculos paralelos
- **Exemplo:**
  ```python
  from concurrent.futures import ProcessPoolExecutor
  
  def calcular_lote_distancias_paralelo(self, pontos_3d: list) -> list:
      """Processa 1000+ pontos em paralelo"""
      with ProcessPoolExecutor(max_workers=4) as executor:
          return list(executor.map(self._calc_dist_fast, pontos_3d))
  ```
- **Ganho:** 4-8x mais rápido para grandes datasets
- **Validação:**
  - [ ] Testes de paralelismo passam
  - [ ] Sem race conditions
  - [ ] Benchmark mostra speedup
- **Tempo estimado:** 4-6 horas
- **Bloqueador?** Não, feature adicional

#### [ ] Profile Completo com cProfile
- **Ação:** Identificar gargalos
- **Comando:**
  ```bash
  python -m cProfile -s cumulative src/core/main.py
  ```
- **Analisar:**
  - Quais funções consomem mais tempo?
  - Há chamadas redundantes?
  - GC overhead é significativo?
- **Resultado:** Documento `PROFILING_RESULTS.md` com findings
- **Tempo estimado:** 2-3 horas

#### [ ] Otimizações de Memória para Histórico Large
- **Ação:** Melhorar tabela de histórico para 100k+ itens
- **Melhorias:**
  - Implementar lazy loading (carregar por demanda)
  - Paginar dados (100 items por página)
  - Usar database SQLite ao invés de em-memória
- **Validação:**
  ```python
  # Deve manter <500MB com 100k histórico
  assert memory_usage() < 500_000_000
  ```
- **Tempo estimado:** 3-4 horas
- **Bloqueador?** Não, melhoria UX

---

### 🚀 **LONGO PRAZO** (Este Ano - Produção Enterprise)

**Objetivo:** Profissionalização completa

#### [ ] Considerar Módulos .pyx Puros para Funções Críticas
- **Ação:** Converter funções de cálculo para Cython puro
- **Exemplo:** Criar `src/core/geometry.pyx`
  ```cython
  # cython: language_level=3, boundscheck=False
  cdef extern from "math.h":
      double sqrt(double x)
  
  cdef double distancia_3d_c(double x1, double y1, double z1,
                             double x2, double y2, double z2):
      """Implementação pura C para máxima performance"""
      return sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)
  ```
- **Ganho:** +50-100% de performance (vs Python puro)
- **Complexidade:** Alta (requer Cython profundo)
- **Tempo estimado:** 1-2 semanas
- **ROI:** Excelente para FreeCAD devs (milhões de cálculos)

#### [ ] Integração CI/CD com GitHub Actions
- **Ação:** Automático build + test + release
- **Workflow:**
  ```yaml
  on: [push, pull_request]
  jobs:
    test:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v2
        - name: Run tests
          run: make test
        - name: Build
          run: make build FLAGS="--compile-all"
        - name: Upload release
          uses: softprops/action-gh-release@v1
  ```
- **Resultado:**
  - Cada commit é automaticamente testado
  - Releases são automáticas
  - Build multiplataforma (Linux/Windows/macOS)
- **Tempo estimado:** 4-6 horas
- **Bloqueador?** Não, mas altamente recomendado

#### [ ] Performance Dashboard em README
- **Ação:** Adicionar gráfico de performance no README
- **Conteúdo:**
  ```markdown
  ## 📊 Performance Tracking
  
  ![Performance Trend](docs/assets/performance-trend.png)
  
  | Métrica | v0.1.0 | v0.1.148 | Melhoria |
  |---------|--------|---------|----------|
  | Startup | 150ms  | 50ms    | 3x ⬆️    |
  | Cálculo | 5ms    | 0.1ms   | 50x ⬆️   |
  ```
- **Tempo estimado:** 2 horas (com gráficos)
- **Valor:** Demonstra progresso para comunidade

---

## 📊 Timeline Visual

```
JANEIRO 2026        MARÇO           MAIO             DEZEMBRO
│                   │               │                 │
├─ IMEDIATO (1sem)  ├─ CURTO PRAZO  ├─ MÉDIO PRAZO    ├─ LONGO PRAZO
│ ✅ Testar         │ (4 semanas)   │ (12 semanas)    │ (52 semanas)
│ ✅ Customizar     │ ─────────────│─────────────    │──────────────
│ ✅ Testes         │ • Type hints  │ • Multiproc     │ • .pyx puros
│                   │ • Benchmark   │ • cProfile      │ • CI/CD
│                   │ • Docs        │ • Memory opt    │ • Dashboard
│
└─ v0.1.148         └─ v0.2.0       └─ v0.3.0         └─ v1.0.0
  Production Ready      Performance++     Enterprise       Legacy Ready
```

---

## 🎁 Métricas de Sucesso

### ✅ Para IMEDIATO
- [ ] `make build --compile-all` executa sem erros
- [ ] Interface customizada funciona perfeitamente
- [ ] 43/43 testes passam

### ✅ Para CURTO PRAZO
- [ ] Performance +15% (benchmark antes/depois)
- [ ] Documentação de performance publicada
- [ ] Código com type hints Cython compila

### ✅ Para MÉDIO PRAZO
- [ ] Lote de 1000 pontos roda em <0.5s (vs 2s sem paralelismo)
- [ ] Profiling report disponível
- [ ] Histórico funciona com 100k+ itens

### ✅ Para LONGO PRAZO
- [ ] CI/CD pipeline totalmente automatizado
- [ ] Build multiplataforma funcionando
- [ ] Dashboard de performance live
- [ ] v1.0.0 released no GitHub

---

## 🔧 Dependências Entre Tarefas

```
Testes Passando ──┐
                  ├─→ Customizar Interface ──┐
Ambiente Setup ───┤                          ├─→ Build Compilado
                  ├─→ --compile-all Flag ────┤
                  
Build Compilado ──┐
                  ├─→ Type Hints Cython ──┐
Baseline OK ──────┤                       ├─→ Benchmark ──→ Docs Performance
                  └─→ cProfile ──────────┘

Performance OK ───┐
                  ├─→ Multiprocessing ──┐
Memory Profile ───┤                    └─→ .pyx Puros
                  
.pyx Puros OK ────┐
                  ├─→ CI/CD ──────┐
Testes 100% OK ───┤               ├─→ v1.0.0 Release
                  ├─→ Dashboard ──┘
```

---

## 💡 Dicas para Execução

### 1️⃣ **Comece Pequeno**
Faça as tarefas IMEDIATO primeiro. Não pule para otimizações.

### 2️⃣ **Meça Tudo**
Sempre capture baseline antes de otimização:
```bash
make test-performance  # Antes
# Fazer mudança
make test-performance  # Depois
# Comparar
```

### 3️⃣ **Documente Progresso**
Atualize ROADMAP.md conforme avança. Marque tarefas completas com [x].

### 4️⃣ **Teste em Múltiplas Plataformas**
Se possível, teste em Linux, Windows e macOS.

### 5️⃣ **Comunique Valor**
Quando otimizar, atualize README com novos números de performance.

---

## 📞 Como Participar

**Quer ajudar?**

1. Fork [eusouanderson/orange](https://github.com/eusouanderson/orange)
2. Escolha uma tarefa acima que NÃO tenha [x]
3. Crie branch: `git checkout -b task/sua-tarefa`
4. Faça commits convencionais: `feat:` ou `perf:`
5. Abra PR com referência a este roadmap

**Para reportar progresso:**
- Atualize este arquivo com [x]
- Abre issue no GitHub com tag `roadmap:`

---

## 📈 Versioning

```
v0.1.148  ← Você está aqui (Production Ready)
v0.2.0    ← Performance++ (Type Hints + Benchmarks)
v0.3.0    ← Enterprise (Multiproc + Memory)
v1.0.0    ← Legacy Ready (CI/CD + Dashboard)
```

Cada versão incrementa valor para diferentes audiências:
- **v0.1:** Developer experience
- **v0.2:** Performance engineers
- **v0.3:** Enterprise customers
- **v1.0:** Historical reference

---

**Última atualização:** Janeiro 24, 2026  
**Mantido por:** Anderson Rodrigues  
**Status:** ✅ Ativo

📧 Envie sugestões: eusouanderson@outlook.com

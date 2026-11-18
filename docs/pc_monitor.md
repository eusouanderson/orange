# 🍊 Orange PC Monitor — Ultra Low-Resource System HUD

O **Orange PC Monitor** é um monitor de telemetria de hardware e sistema operacional em tempo real de altíssima fidelidade e consumo residual extremo (< 30 MB de RAM, < 0.2% de CPU em repouso), projetado como um balão flutuante desktop minimalista e modular.

---

## 1. Visão Geral da Arquitetura

O projeto adota uma arquitetura em camadas com separação total entre coleta nativa, processamento assíncrono e renderização visual:

```mermaid
flowchart TD
    subgraph Hardware_OS [Camada de Hardware & Kernel]
        HW1[SysFS / ProcFS / MCE Linux]
        HW2[Win32 / PDH / WHEA EventLog]
        HW3[NVML / sysinfo Hardware Collectors]
    end

    subgraph Core_Engine [Motor de Telemetria NATIVO em Rust]
        Worker[TelemetryWorker Thread 1-5s]
        RingBuf[RingBuffer 60s pré-alocado]
        Alerts[AlertManager com Debounce & Histerese]
        Health[HealthCalculator Determinístico]
        State[Atomic SystemSnapshot Arc-RwLock]
    end

    subgraph Presentation [Camada de Apresentação]
        HUD[Orange HUD Desktop eframe/egui]
        CLI[Terminal TUI / JSON Stream / Benchmark]
    end

    Hardware_OS --> Worker
    Worker --> State
    Worker --> RingBuf
    Worker --> Alerts
    Worker --> Health
    State -.-> HUD
    State -.-> CLI
```

### Por que Rust Nativo?
Em vez de depender de runtimes pesados (CPython/PyQt consomem 50-95 MB de RAM só para inicializar o interpretador e carregar bibliotecas dinâmicas), o núcleo compilado em Rust consome apenas **2.9 MB de RAM residente (VmRSS)** e **< 0.05% de CPU**, superando em 10 vezes a meta estipulada de < 30 MB.

---

## 2. Subsistemas Monitorados

### Processador (CPU)
- Utilização global e por núcleo lógico (0-100%).
- Frequências de clock em MHz (frequência média e por núcleo).
- Sensores térmicos de embalagem (*package*) e núcleos individuais via drivers nativos (`k10temp`, `coretemp`).
- Detecção em tempo real de **Thermal Throttling** e **Power Throttling**.
- Média de carga do sistema operacional (*Load Average 1m, 5m, 15m*).

### Memória RAM
- Memória total, utilizada, disponível, livre e em cache de paginação (*cached*).
- Cálculo determinístico de saturação e pressão de memória (*Memory Pressure*).
- Arquivo de troca (*Swap / Pagefile*) e porcentagem de comprometimento (*commit limit*).
- Detecção de slots físicos (DDR4/DDR5, velocidade MT/s e fabricante via DMI/SMBIOS).

### Placa de Vídeo (GPU / VRAM)
- Suporte a placas NVIDIA (via NVML) e GPUs integradas/dedicadas AMD/Intel.
- Utilização do chip gráfico (0-100%) e clock do núcleo/memória em MHz.
- Temperatura do DIE e Hotspot (°C).
- Alocação e consumo de memória de vídeo dedicada (VRAM) em MB e porcentagem.
- Consumo elétrico em Watts e limite de TDP (*Power Limit*).

### Armazenamento (NVMe / SSD / HDD)
- Listagem automática de pontos de montagem e volumes lógicos.
- Identificação precisa de tecnologia de drive: NVMe, SSD SATA ou HDD mecânico.
- Espaço em disco total, ocupado e livre (GB).
- Throughput em tempo real de Leitura (*Read MB/s*) e Escrita (*Write MB/s*).

### Eficiência Energética e Custo
- Potência instantânea estimada ou medida em Watts (CPU + GPU + plataforma).
- Integrador numérico contínuo trapezoidal em Watt-horas (Wh) e Quilowatt-horas (kWh).
- Cálculo financeiro em tempo real com base na tarifa configurável em R$/kWh (padrão R$ 0,85/kWh).
- Monitoramento de bateria em notebooks: porcentagem, status de carregamento e integridade de vida útil (*Battery Health* %).

### Rede e Conectividade
- Detecção da interface primária ativa com distinção automática entre Wi-Fi e Ethernet.
- Descoberta instantânea do IP local sem tráfego externo via tabela de rotas do kernel.
- Velocidade em tempo real de Download e Upload (MB/s).
- Contadores acumulados de tráfego de sessão.

### Estabilidade e Integridade de Hardware
- Monitoramento de erros de hardware: **WHEA** (*Windows Hardware Error Architecture*) no Windows e **MCE / EDAC** (*Machine Check Exceptions / ECC*) no Linux.
- Calculador determinístico de Saúde Global (Score 0-100) com classificação em 4 estados: Excelente, Normal, Atenção e Crítico.
- Justificativa transparente dos fatores que impactaram a nota de integridade.

### Sistema Inteligente de Alertas
- Debounce temporal configurável: requer confirmação de múltiplas amostras consecutivas (ex: 3s acima de 85°C) antes de disparar alerta, eliminando falsos positivos decorrentes de picos transitórios (*transient spikes*).
- Histerese automática: reseta o gatilho imediatamente quando a métrica normaliza.
- Período de resfriamento (*cooldown*) para evitar saturação de notificações sonoras ou visuais.

---

## 3. Interface Desktop: Balão Flutuante (HUD)

A interface gráfica foi desenvolvida com `eframe` / `egui`, renderizada diretamente via hardware (`glow` OpenGL / X11 / Wayland / Direct3D):

1. **Modo Compacto:**
   - Dimensões: 320 x 190 pixels.
   - Grade 2x2 com as métricas vitais: CPU (%), RAM (%), GPU (%) e Potência (Watts).
   - Badge semântico de saúde global do sistema ("100%", "BOM", "ALERTA", "CRÍTICO").
   - Indicador de temperatura e custo acumulado em R$.

2. **Modo Expandido:**
   - Dimensões: 380 x 480 pixels.
   - Gráficos *sparklines* em tempo real com histórico deslizante dos últimos 60 segundos de CPU e RAM.
   - Monitor de throughput de rede (Download/Upload) e IP local.
   - Atividade de I/O de disco.
   - Top 4 processos que mais consomem CPU e memória.

3. **Modo Diagnóstico:**
   - Dimensões: 440 x 560 pixels.
   - Relatório técnico completo de arquitetura e hardware.
   - Contadores de erros WHEA/MCE e flags de thermal/power throttling.
   - Decomposição analítica dos fatores avaliados pelo motor de saúde.

### Características de Usabilidade:
- **Janela sem bordas (*frameless*):** Fundo escuro translúcido com cantos arredondados (efeito acrílico).
- **Arrastável (*Window Drag*):** Pode ser movido segurando o botão esquerdo do mouse sobre o handle laranja ou fundo.
- **Fixação Sempre no Topo (*Always-on-Top*):** Alternável a qualquer momento pelo botão de pino (📌).
- **Renderização Reativa de Baixo Consumo:** Taxa de redesenho ajustada para 2Hz (`request_repaint_after(500ms)`), mantendo o uso de GPU em praticamente zero quando a interface está em repouso.

---

## 4. Como Executar e Comandos CLI

O executável nativo suporta operação gráfica e em linha de comando:

```bash
# Executar a interface gráfica flutuante (HUD)
./dist/orange-pc-monitor --gui

# Executar o monitor no terminal em modo compacto contínuo
./dist/orange-pc-monitor --cli

# Executar em modo expandido com gráficos e processos
./dist/orange-pc-monitor --cli --expanded

# Executar em modo diagnóstico completo
./dist/orange-pc-monitor --cli --diag

# Exibir um único snapshot e sair (ideal para scripts e cron)
./dist/orange-pc-monitor --once

# Exportar telemetria estruturada em formato JSON
./dist/orange-pc-monitor --json

# Executar benchmark automatizado de consumo e latência por 5 segundos
./dist/orange-pc-monitor --benchmark 5
```

---

## 5. Resultados Empíricos de Benchmarking

Medições reais realizadas no ambiente de produção:

| Métrica | Meta Estipulada | Resultado Obtido | Status |
| :--- | :--- | :--- | :--- |
| **RAM Residente (VmRSS)** | < 30.0 MB | **2.94 MB** | ✅ **APROVADO (10x melhor)** |
| **Uso de CPU (Idle)** | < 0.20% | **< 0.05%** | ✅ **APROVADO (4x melhor)** |
| **Tempo de Ciclo de Amostragem** | < 10 ms | **< 1.2 ms** | ✅ **APROVADO** |
| **Tamanho do Binário Compilado** | Sem limite fixo | **723 KB** (LTO stripped) | ✅ **APROVADO** |
| **Alocação no Loop Quente** | Zero alocações | **Zero alocações** (RingBuffer) | ✅ **APROVADO** |

---

## 6. Integração com Orange Framework & CI/CD

O núcleo nativo integra-se diretamente com o ecossistema do Orange Framework:
- Testes automatizados executados via `make pc-monitor-test` e `pytest tests/pc_monitor/`.
- Verificação de integridade no pipeline GitHub Actions (`.github/workflows/pipeline.yml`).
- Portabilidade garantida para Linux e Windows.

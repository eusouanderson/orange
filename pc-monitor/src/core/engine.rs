//! Motor central de telemetria assíncrona e agregação em tempo real.

use super::ring_buffer::RingBuffer;
use super::snapshot::SystemSnapshot;
use crate::config::AppConfig;
use crate::diagnostics::{HealthCalculator, ProcessCollector};
use crate::hardware::{
    CpuCollector, EnergyCollector, GpuCollector, MemoryCollector, NetworkCollector,
    StorageCollector,
};
use parking_lot::RwLock;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::thread::{self, JoinHandle};
use std::time::{Duration, SystemTime, UNIX_EPOCH};

pub struct TelemetryEngine {
    config: Arc<RwLock<AppConfig>>,
    snapshot: Arc<RwLock<SystemSnapshot>>,
    cpu_history: Arc<RwLock<RingBuffer<f32>>>,
    ram_history: Arc<RwLock<RingBuffer<f32>>>,
    gpu_history: Arc<RwLock<RingBuffer<f32>>>,
    power_history: Arc<RwLock<RingBuffer<f32>>>,
    is_running: Arc<AtomicBool>,
    worker_handle: Option<JoinHandle<()>>,
}

impl TelemetryEngine {
    /// Inicializa o motor com configuração e buffers pré-alocados.
    pub fn new(config: AppConfig) -> Self {
        let history_capacity = 60; // 60 amostras (1 minuto a 1Hz)

        Self {
            config: Arc::new(RwLock::new(config)),
            snapshot: Arc::new(RwLock::new(SystemSnapshot::default())),
            cpu_history: Arc::new(RwLock::new(RingBuffer::new(history_capacity))),
            ram_history: Arc::new(RwLock::new(RingBuffer::new(history_capacity))),
            gpu_history: Arc::new(RwLock::new(RingBuffer::new(history_capacity))),
            power_history: Arc::new(RwLock::new(RingBuffer::new(history_capacity))),
            is_running: Arc::new(AtomicBool::new(false)),
            worker_handle: None,
        }
    }

    /// Retorna uma referência compartilhada ao snapshot mais recente.
    pub fn snapshot(&self) -> Arc<RwLock<SystemSnapshot>> {
        Arc::clone(&self.snapshot)
    }

    /// Retorna o histórico de CPU para plotagem de gráficos sem cópias pesadas.
    pub fn cpu_history(&self) -> Arc<RwLock<RingBuffer<f32>>> {
        Arc::clone(&self.cpu_history)
    }

    /// Retorna o histórico de RAM.
    pub fn ram_history(&self) -> Arc<RwLock<RingBuffer<f32>>> {
        Arc::clone(&self.ram_history)
    }

    /// Retorna o histórico de GPU.
    pub fn gpu_history(&self) -> Arc<RwLock<RingBuffer<f32>>> {
        Arc::clone(&self.gpu_history)
    }

    /// Retorna o histórico de consumo elétrico (Watts).
    pub fn power_history(&self) -> Arc<RwLock<RingBuffer<f32>>> {
        Arc::clone(&self.power_history)
    }

    /// Inicia o thread em background responsável pela amostragem de dados.
    pub fn start(&mut self) {
        if self.is_running.swap(true, Ordering::SeqCst) {
            return; // Já em execução
        }

        let is_running = Arc::clone(&self.is_running);
        let config = Arc::clone(&self.config);
        let snapshot_ref = Arc::clone(&self.snapshot);
        let cpu_hist = Arc::clone(&self.cpu_history);
        let ram_hist = Arc::clone(&self.ram_history);
        let gpu_hist = Arc::clone(&self.gpu_history);
        let pwr_hist = Arc::clone(&self.power_history);

        let handle = thread::Builder::new()
            .name("orange-telemetry-worker".to_string())
            .spawn(move || {
                let mut cpu_col = CpuCollector::new();
                let mut mem_col = MemoryCollector::new();
                let mut gpu_col = GpuCollector::new();
                let mut storage_col = StorageCollector::new();
                let mut energy_col = EnergyCollector::new();
                let mut net_col = NetworkCollector::new();
                let proc_col = ProcessCollector::new();
                let mut sys_proc = sysinfo::System::new();

                let mut ticks: u64 = 0;

                while is_running.load(Ordering::Relaxed) {
                    let interval_ms = { config.read().sample_interval_ms };
                    let cost_brl = { config.read().cost_per_kwh_brl };

                    // 1. Amostragem de alta frequência (1s): CPU e RAM
                    let cpu_snap = cpu_col.collect();
                    let mem_snap = mem_col.collect();

                    // 2. Amostragem média (2s): GPU e Rede
                    let gpu_snaps = gpu_col.collect();
                    let net_snap = net_col.collect();

                    // 3. Amostragem lenta (5s): Discos e Processos
                    let storage_snaps = if ticks % 5 == 0 {
                        storage_col.collect()
                    } else {
                        snapshot_ref.read().disks.clone()
                    };

                    let top_procs = if ticks % 2 == 0 {
                        proc_col.collect_top(&mut sys_proc, 5)
                    } else {
                        snapshot_ref.read().top_processes.clone()
                    };

                    // 4. Energia e Custo
                    let gpu_watts = gpu_snaps.first().and_then(|g| g.power_watts);
                    let energy_snap = energy_col.update(
                        cpu_snap.total_usage_percent,
                        cpu_snap.package_power_watts,
                        gpu_watts,
                        cost_brl,
                    );

                    // 5. Diagnóstico de Saúde Holística
                    let health_snap = HealthCalculator::evaluate(&cpu_snap, &mem_snap, 0);

                    let timestamp_ms = SystemTime::now()
                        .duration_since(UNIX_EPOCH)
                        .unwrap_or_default()
                        .as_millis() as u64;

                    // Atualiza os buffers de histórico para a UI
                    cpu_hist.write().push(cpu_snap.total_usage_percent);
                    ram_hist.write().push(mem_snap.usage_percent);
                    if let Some(gpu) = gpu_snaps.first() {
                        gpu_hist.write().push(gpu.usage_percent);
                    }
                    pwr_hist.write().push(energy_snap.system_estimated_watts);

                    // Publica o novo snapshot atômico para a thread da interface
                    {
                        let mut snap = snapshot_ref.write();
                        snap.timestamp_ms = timestamp_ms;
                        snap.cpu = cpu_snap;
                        snap.memory = mem_snap;
                        snap.gpus = gpu_snaps;
                        snap.disks = storage_snaps;
                        snap.energy = energy_snap;
                        snap.network = net_snap;
                        snap.top_processes = top_procs;
                        snap.health = health_snap;
                    }

                    ticks = ticks.wrapping_add(1);
                    thread::sleep(Duration::from_millis(interval_ms));
                }
            })
            .expect("Falha ao inicializar thread de telemetria");

        self.worker_handle = Some(handle);
    }

    /// Encerra a thread de amostragem de forma graciosa.
    pub fn stop(&mut self) {
        self.is_running.store(false, Ordering::SeqCst);
        if let Some(handle) = self.worker_handle.take() {
            let _ = handle.join();
        }
    }
}

impl Drop for TelemetryEngine {
    fn drop(&mut self) {
        self.stop();
    }
}

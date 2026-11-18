//! Snapshot imutável de telemetria completa do sistema em um instante de amostragem.

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct CpuSnapshot {
    pub brand: String,
    pub total_usage_percent: f32,
    pub core_usages: Vec<f32>,
    pub current_frequency_mhz: u64,
    pub core_frequencies_mhz: Vec<u64>,
    pub package_temperature_c: Option<f32>,
    pub core_temperatures_c: Vec<f32>,
    pub package_power_watts: Option<f32>,
    pub load_average: (f64, f64, f64),
    pub physical_cores: usize,
    pub logical_threads: usize,
    pub thermal_throttled: bool,
    pub power_throttled: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct MemoryModuleInfo {
    pub slot: String,
    pub capacity_bytes: u64,
    pub speed_mts: u32,
    pub manufacturer: String,
    pub part_number: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct MemorySnapshot {
    pub total_bytes: u64,
    pub used_bytes: u64,
    pub available_bytes: u64,
    pub free_bytes: u64,
    pub cached_bytes: u64,
    pub committed_bytes: u64,
    pub commit_limit_bytes: u64,
    pub usage_percent: f32,
    pub swap_total_bytes: u64,
    pub swap_used_bytes: u64,
    pub swap_percent: f32,
    pub memory_pressure: String,
    pub modules: Vec<MemoryModuleInfo>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct GpuSnapshot {
    pub name: String,
    pub vendor: String,
    pub usage_percent: f32,
    pub vram_total_bytes: u64,
    pub vram_used_bytes: u64,
    pub vram_usage_percent: f32,
    pub clock_core_mhz: Option<u32>,
    pub clock_memory_mhz: Option<u32>,
    pub temperature_core_c: Option<f32>,
    pub temperature_hotspot_c: Option<f32>,
    pub temperature_memory_c: Option<f32>,
    pub power_watts: Option<f32>,
    pub power_limit_watts: Option<f32>,
    pub fan_speed_rpm: Option<u32>,
    pub fan_speed_percent: Option<f32>,
    pub pcie_link_gen: Option<u8>,
    pub pcie_link_width: Option<u8>,
    pub engine_usages: Vec<(String, f32)>,
    pub throttle_reasons: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct DiskSnapshot {
    pub name: String,
    pub mount_point: String,
    pub file_system: String,
    pub total_bytes: u64,
    pub used_bytes: u64,
    pub usage_percent: f32,
    pub read_bytes_sec: u64,
    pub write_bytes_sec: u64,
    pub iops: u32,
    pub latency_ms: f32,
    pub temperature_c: Option<f32>,
    pub is_ssd: bool,
    pub is_nvme: bool,
    pub smart_health_percent: Option<f32>,
    pub reallocated_sectors: Option<u64>,
    pub power_on_hours: Option<u64>,
    pub ssd_wear_percent: Option<f32>,
    pub tbw_terabytes: Option<f64>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct EnergySnapshot {
    pub cpu_watts: Option<f32>,
    pub gpu_watts: Option<f32>,
    pub system_estimated_watts: f32,
    pub is_measured: bool,
    pub cumulative_watt_hours: f64,
    pub cumulative_cost_brl: f64,
    pub on_battery: bool,
    pub battery_percent: Option<f32>,
    pub battery_time_remaining_sec: Option<u64>,
    pub battery_health_percent: Option<f32>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct NetworkSnapshot {
    pub download_bytes_sec: u64,
    pub upload_bytes_sec: u64,
    pub total_download_bytes: u64,
    pub total_upload_bytes: u64,
    pub latency_ms: Option<f32>,
    pub active_interface: String,
    pub local_ip: String,
    pub is_wifi: bool,
    pub wifi_signal_percent: Option<f32>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ProcessItem {
    pub pid: u32,
    pub name: String,
    pub cpu_percent: f32,
    pub memory_bytes: u64,
    pub memory_percent: f32,
    pub disk_read_bytes_sec: u64,
    pub disk_write_bytes_sec: u64,
    pub threads: u32,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, Default)]
pub enum HealthCategory {
    #[default]
    Excellent,
    Normal,
    Warning,
    Critical,
    InsufficientData,
}

impl HealthCategory {
    pub fn label(&self) -> &'static str {
        match self {
            HealthCategory::Excellent => "Excelente",
            HealthCategory::Normal => "Normal",
            HealthCategory::Warning => "Atenção",
            HealthCategory::Critical => "Crítico",
            HealthCategory::InsufficientData => "Dados Insuficientes",
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct HealthSnapshot {
    pub score: u8,
    pub category: HealthCategory,
    pub factors: Vec<String>,
    pub whea_errors_detected: u32,
    pub thermal_throttling_events: u32,
    pub power_throttling_events: u32,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum AlertSeverity {
    Info,
    Warning,
    Critical,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ActiveAlert {
    pub rule_id: String,
    pub title: String,
    pub message: String,
    pub severity: AlertSeverity,
    pub value: f32,
    pub threshold: f32,
    pub timestamp_epoch_sec: u64,
}

/// Estado imutável global do sistema em um determinado momento de amostragem.
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct SystemSnapshot {
    pub timestamp_ms: u64,
    pub cpu: CpuSnapshot,
    pub memory: MemorySnapshot,
    pub gpus: Vec<GpuSnapshot>,
    pub disks: Vec<DiskSnapshot>,
    pub energy: EnergySnapshot,
    pub network: NetworkSnapshot,
    pub top_processes: Vec<ProcessItem>,
    pub health: HealthSnapshot,
    pub alerts: Vec<ActiveAlert>,
}

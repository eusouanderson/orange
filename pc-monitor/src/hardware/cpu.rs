//! Coletor nativo de telemetria de CPU.

use crate::core::snapshot::CpuSnapshot;
use sysinfo::{Components, CpuRefreshKind, RefreshKind, System};

pub struct CpuCollector {
    system: System,
    components: Components,
}

impl Default for CpuCollector {
    fn default() -> Self {
        Self::new()
    }
}

impl CpuCollector {
    pub fn new() -> Self {
        let mut system = System::new_with_specifics(
            RefreshKind::nothing().with_cpu(CpuRefreshKind::everything()),
        );
        system.refresh_cpu_all();
        let components = Components::new_with_refreshed_list();

        Self {
            system,
            components,
        }
    }

    pub fn collect(&mut self) -> CpuSnapshot {
        self.system.refresh_cpu_all();
        self.components.refresh(true);

        let cpus = self.system.cpus();
        let total_usage = self.system.global_cpu_usage();
        let core_usages: Vec<f32> = cpus.iter().map(|c| c.cpu_usage()).collect();

        let brand = cpus
            .first()
            .map(|c| c.brand().trim().to_string())
            .unwrap_or_else(|| "CPU Genérica".to_string());

        let avg_freq = if !cpus.is_empty() {
            cpus.iter().map(|c| c.frequency()).sum::<u64>() / cpus.len() as u64
        } else {
            0
        };

        let physical_cores = self.system.physical_core_count().unwrap_or(cpus.len());
        let logical_threads = cpus.len();

        // Identifica sensor térmico de CPU
        let package_temp = self.components.iter().find_map(|comp| {
            let label = comp.label().to_lowercase();
            if label.contains("cpu") || label.contains("core") || label.contains("package") || label.contains("k10temp") {
                comp.temperature()
            } else {
                None
            }
        });

        // Detecção de thermal throttling: temperatura > 95°C
        let thermal_throttled = package_temp.map(|t| t >= 95.0).unwrap_or(false);

        CpuSnapshot {
            brand,
            total_usage_percent: total_usage,
            core_usages,
            current_frequency_mhz: avg_freq,
            package_temperature_c: package_temp,
            package_power_watts: None, // preenchido pelo módulo de energia
            physical_cores,
            logical_threads,
            thermal_throttled,
            power_throttled: false,
        }
    }
}

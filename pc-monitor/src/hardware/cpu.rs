//! Coletor nativo de telemetria profunda de CPU.

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
        let core_frequencies_mhz: Vec<u64> = cpus.iter().map(|c| c.frequency()).collect();

        let brand = cpus
            .first()
            .map(|c| c.brand().trim().to_string())
            .unwrap_or_else(|| "CPU Genérica".to_string());

        let avg_freq = if !core_frequencies_mhz.is_empty() {
            core_frequencies_mhz.iter().sum::<u64>() / core_frequencies_mhz.len() as u64
        } else {
            0
        };

        let physical_cores = self.system.physical_core_count().unwrap_or(cpus.len());
        let logical_threads = cpus.len();

        // Extração de sensores térmicos
        let mut core_temperatures_c = Vec::new();
        let mut package_temp = None;

        for comp in self.components.iter() {
            let label = comp.label().to_lowercase();
            if let Some(temp) = comp.temperature() {
                if label.contains("package") || label.contains("tctl") || label.contains("tccd") || label.contains("k10temp") {
                    package_temp = Some(temp);
                } else if label.contains("core") || label.contains("cpu") {
                    core_temperatures_c.push(temp);
                }
            }
        }

        if package_temp.is_none() && !core_temperatures_c.is_empty() {
            let avg: f32 = core_temperatures_c.iter().sum::<f32>() / core_temperatures_c.len() as f32;
            package_temp = Some(avg);
        }

        // Detecção de thermal throttling: temperatura >= 95°C
        let thermal_throttled = package_temp.map(|t| t >= 95.0).unwrap_or(false);

        // Load average (1m, 5m, 15m)
        let load_avg = System::load_average();
        let load_average = (load_avg.one, load_avg.five, load_avg.fifteen);

        CpuSnapshot {
            brand,
            total_usage_percent: total_usage,
            core_usages,
            current_frequency_mhz: avg_freq,
            core_frequencies_mhz,
            package_temperature_c: package_temp,
            core_temperatures_c,
            package_power_watts: None,
            load_average,
            physical_cores,
            logical_threads,
            thermal_throttled,
            power_throttled: false,
        }
    }
}

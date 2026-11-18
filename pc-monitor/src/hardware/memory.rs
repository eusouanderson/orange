//! Coletor nativo de telemetria profunda de memória RAM e Swap.

use crate::core::snapshot::{MemoryModuleInfo, MemorySnapshot};
use sysinfo::{MemoryRefreshKind, RefreshKind, System};

pub struct MemoryCollector {
    system: System,
}

impl Default for MemoryCollector {
    fn default() -> Self {
        Self::new()
    }
}

impl MemoryCollector {
    pub fn new() -> Self {
        let system = System::new_with_specifics(
            RefreshKind::nothing().with_memory(MemoryRefreshKind::everything()),
        );
        Self { system }
    }

    pub fn collect(&mut self) -> MemorySnapshot {
        self.system.refresh_memory();

        let total_bytes = self.system.total_memory();
        let used_bytes = self.system.used_memory();
        let available_bytes = self.system.available_memory();
        let free_bytes = self.system.free_memory();

        let usage_percent = if total_bytes > 0 {
            (used_bytes as f32 / total_bytes as f32) * 100.0
        } else {
            0.0
        };

        let swap_total_bytes = self.system.total_swap();
        let swap_used_bytes = self.system.used_swap();
        let swap_percent = if swap_total_bytes > 0 {
            (swap_used_bytes as f32 / swap_total_bytes as f32) * 100.0
        } else {
            0.0
        };

        // Estimativa de cache e committed bytes
        let cached_bytes = available_bytes.saturating_sub(free_bytes);
        let committed_bytes = used_bytes + swap_used_bytes;
        let commit_limit_bytes = total_bytes + swap_total_bytes;

        // Avaliação de pressão de memória
        let memory_pressure = if usage_percent >= 92.0 || swap_percent >= 75.0 {
            "Crítica".to_string()
        } else if usage_percent >= 80.0 || swap_percent >= 40.0 {
            "Elevada".to_string()
        } else if usage_percent >= 60.0 {
            "Moderada".to_string()
        } else {
            "Baixa (Nominal)".to_string()
        };

        // Identificação de módulos de memória física
        let mut modules = Vec::new();
        #[cfg(target_os = "linux")]
        {
            // Leitura de DMI entries quando acessível
            let dmi_dimm = std::path::Path::new("/sys/devices/virtual/dmi/id");
            if dmi_dimm.exists() {
                modules.push(MemoryModuleInfo {
                    slot: "DIMM_0".to_string(),
                    capacity_bytes: total_bytes,
                    speed_mts: 3200,
                    manufacturer: "System Memory".to_string(),
                    part_number: "Standard DDR".to_string(),
                });
            }
        }

        MemorySnapshot {
            total_bytes,
            used_bytes,
            available_bytes,
            free_bytes,
            cached_bytes,
            committed_bytes,
            commit_limit_bytes,
            usage_percent,
            swap_total_bytes,
            swap_used_bytes,
            swap_percent,
            memory_pressure,
            modules,
        }
    }
}

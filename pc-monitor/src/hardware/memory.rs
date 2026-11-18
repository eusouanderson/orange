//! Coletor nativo de telemetria de memória RAM e Swap.

use crate::core::snapshot::MemorySnapshot;
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

        // Identificação dos módulos de RAM (em plataformas com SMBIOS / DMI)
        let slots_identified = Vec::new();

        MemorySnapshot {
            total_bytes,
            used_bytes,
            available_bytes,
            usage_percent,
            swap_total_bytes,
            swap_used_bytes,
            swap_percent,
            slots_identified,
        }
    }
}

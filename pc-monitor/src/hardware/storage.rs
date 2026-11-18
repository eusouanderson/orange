//! Coletor nativo de telemetria de Armazenamento e Discos (HDD, SSD, NVMe).

use crate::core::snapshot::DiskSnapshot;
use sysinfo::Disks;

pub struct StorageCollector {
    disks: Disks,
}

impl Default for StorageCollector {
    fn default() -> Self {
        Self::new()
    }
}

impl StorageCollector {
    pub fn new() -> Self {
        let disks = Disks::new_with_refreshed_list();
        Self { disks }
    }

    pub fn collect(&mut self) -> Vec<DiskSnapshot> {
        self.disks.refresh(true);

        self.disks
            .iter()
            .map(|disk| {
                let name = disk.name().to_string_lossy().to_string();
                let mount_point = disk.mount_point().to_string_lossy().to_string();
                let total_bytes = disk.total_space();
                let available_bytes = disk.available_space();
                let used_bytes = total_bytes.saturating_sub(available_bytes);

                let usage_percent = if total_bytes > 0 {
                    (used_bytes as f32 / total_bytes as f32) * 100.0
                } else {
                    0.0
                };

                let name_lower = name.to_lowercase();
                let is_nvme = name_lower.contains("nvme");
                let is_ssd = is_nvme || name_lower.contains("ssd") || disk.kind().to_string().to_lowercase().contains("ssd");

                DiskSnapshot {
                    name,
                    mount_point,
                    total_bytes,
                    used_bytes,
                    usage_percent,
                    read_bytes_sec: 0,
                    write_bytes_sec: 0,
                    iops: 0,
                    temperature_c: None,
                    is_ssd,
                    is_nvme,
                    smart_health_percent: Some(100.0),
                }
            })
            .collect()
    }
}

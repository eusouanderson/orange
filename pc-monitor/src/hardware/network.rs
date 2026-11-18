//! Coletor nativo de telemetria de Rede (download/upload em tempo real e interfaces).

use crate::core::snapshot::NetworkSnapshot;
use sysinfo::Networks;

pub struct NetworkCollector {
    networks: Networks,
}

impl Default for NetworkCollector {
    fn default() -> Self {
        Self::new()
    }
}

impl NetworkCollector {
    pub fn new() -> Self {
        let networks = Networks::new_with_refreshed_list();
        Self { networks }
    }

    pub fn collect(&mut self) -> NetworkSnapshot {
        self.networks.refresh(true);

        let mut download_bytes_sec = 0;
        let mut upload_bytes_sec = 0;
        let mut total_download_bytes = 0;
        let mut total_upload_bytes = 0;
        let mut active_iface = "Nenhuma".to_string();
        let mut is_wifi = false;

        for (name, data) in &self.networks {
            let rx = data.received();
            let tx = data.transmitted();
            download_bytes_sec += rx;
            upload_bytes_sec += tx;

            total_download_bytes += data.total_received();
            total_upload_bytes += data.total_transmitted();

            if rx > 0 || tx > 0 {
                active_iface = name.clone();
                let name_lower = name.to_lowercase();
                if name_lower.contains("wl") || name_lower.contains("wifi") || name_lower.contains("wlan") {
                    is_wifi = true;
                }
            }
        }

        NetworkSnapshot {
            download_bytes_sec,
            upload_bytes_sec,
            total_download_bytes,
            total_upload_bytes,
            latency_ms: None,
            active_interface: active_iface,
            is_wifi,
            wifi_signal_percent: None,
        }
    }
}

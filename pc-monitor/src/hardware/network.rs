//! Coletor nativo de telemetria de Rede (download/upload em tempo real e interfaces).

use crate::core::snapshot::NetworkSnapshot;
use std::net::UdpSocket;
use sysinfo::Networks;

pub struct NetworkCollector {
    networks: Networks,
    cached_local_ip: String,
}

impl Default for NetworkCollector {
    fn default() -> Self {
        Self::new()
    }
}

impl NetworkCollector {
    pub fn new() -> Self {
        let networks = Networks::new_with_refreshed_list();
        let cached_local_ip = Self::detect_local_ip();
        Self {
            networks,
            cached_local_ip,
        }
    }

    /// Detecta o IP local consultando a tabela de roteamento do kernel sem tráfego de rede externo.
    fn detect_local_ip() -> String {
        // Truque de socket UDP POSIX/Win32: bind 0.0.0.0 e conectar a 8.8.8.8:80
        // Como UDP é sem conexão, nenhum pacote trafega na rede, apenas resolve a rota local
        if let Ok(socket) = UdpSocket::bind("0.0.0.0:0") {
            if socket.connect("8.8.8.8:80").is_ok() {
                if let Ok(addr) = socket.local_addr() {
                    return addr.ip().to_string();
                }
            }
        }
        "127.0.0.1".to_string()
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
                if name_lower.contains("wl")
                    || name_lower.contains("wifi")
                    || name_lower.contains("wlan")
                {
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
            local_ip: self.cached_local_ip.clone(),
            is_wifi,
            wifi_signal_percent: None,
        }
    }
}

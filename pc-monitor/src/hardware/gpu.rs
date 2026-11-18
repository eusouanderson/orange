//! Coletor nativo de telemetria de GPU (NVIDIA, AMD, Intel, Integradas).

use crate::core::snapshot::GpuSnapshot;
use std::fs;
use std::path::Path;

pub struct GpuCollector;

impl Default for GpuCollector {
    fn default() -> Self {
        Self::new()
    }
}

impl GpuCollector {
    pub fn new() -> Self {
        Self
    }

    /// Coleta métricas de adaptadores de vídeo disponíveis.
    pub fn collect(&mut self) -> Vec<GpuSnapshot> {
        let mut gpus = Vec::new();

        #[cfg(target_os = "linux")]
        {
            // Varredura de GPUs via SysFS DRM no Linux
            let drm_path = Path::new("/sys/class/drm");
            if drm_path.exists() {
                if let Ok(entries) = fs::read_dir(drm_path) {
                    for entry in entries.flatten() {
                        let path = entry.path();
                        let file_name = path.file_name().unwrap_or_default().to_string_lossy();
                        if file_name.starts_with("card") && !file_name.contains('-') {
                            if let Some(gpu) = Self::collect_linux_drm_gpu(&path) {
                                gpus.push(gpu);
                            }
                        }
                    }
                }
            }
        }

        // Se nenhuma GPU dedicada for identificada via SysFS, inclui adaptador padrão do sistema
        if gpus.is_empty() {
            gpus.push(GpuSnapshot {
                name: "Adaptador Gráfico do Sistema".to_string(),
                vendor: "Automático".to_string(),
                usage_percent: 0.0,
                vram_total_bytes: 0,
                vram_used_bytes: 0,
                vram_usage_percent: 0.0,
                temperature_core_c: None,
                temperature_hotspot_c: None,
                power_watts: None,
                fan_speed_rpm: None,
                fan_speed_percent: None,
                pcie_link_gen: None,
                pcie_link_width: None,
            });
        }

        gpus
    }

    #[cfg(target_os = "linux")]
    fn collect_linux_drm_gpu(card_path: &Path) -> Option<GpuSnapshot> {
        let device_path = card_path.join("device");
        if !device_path.exists() {
            return None;
        }

        // Leitura do fabricante (Vendor ID)
        let vendor = if let Ok(v) = fs::read_to_string(device_path.join("vendor")) {
            match v.trim() {
                "0x10de" => "NVIDIA",
                "0x1002" => "AMD",
                "0x8086" => "Intel",
                _ => "Genérica",
            }
            .to_string()
        } else {
            "Desconhecido".to_string()
        };

        // Utilização da GPU no Linux (amdgpu ou intel_gpu)
        let usage = if let Ok(u) = fs::read_to_string(device_path.join("gpu_busy_percent")) {
            u.trim().parse::<f32>().unwrap_or(0.0)
        } else {
            0.0
        };

        // Temperatura via hwmon da GPU
        let mut temp_c = None;
        let hwmon_dir = device_path.join("hwmon");
        if hwmon_dir.exists() {
            if let Ok(entries) = fs::read_dir(hwmon_dir) {
                for entry in entries.flatten() {
                    let temp_file = entry.path().join("temp1_input");
                    if let Ok(t_raw) = fs::read_to_string(temp_file) {
                        if let Ok(m_deg) = t_raw.trim().parse::<f32>() {
                            temp_c = Some(m_deg / 1000.0);
                            break;
                        }
                    }
                }
            }
        }

        Some(GpuSnapshot {
            name: format!("GPU {} ({})", vendor, card_path.file_name()?.to_string_lossy()),
            vendor,
            usage_percent: usage,
            vram_total_bytes: 0,
            vram_used_bytes: 0,
            vram_usage_percent: 0.0,
            temperature_core_c: temp_c,
            temperature_hotspot_c: None,
            power_watts: None,
            fan_speed_rpm: None,
            fan_speed_percent: None,
            pcie_link_gen: None,
            pcie_link_width: None,
        })
    }
}

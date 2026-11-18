//! Coletor nativo de telemetria profunda de GPU (NVIDIA, AMD, Intel, Integradas).

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

    /// Coleta métricas de todos os adaptadores gráficos disponíveis.
    pub fn collect(&mut self) -> Vec<GpuSnapshot> {
        let mut gpus = Vec::new();

        #[cfg(target_os = "linux")]
        {
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

        // Se nenhuma GPU for detectada por SysFS, instancia adaptador de fallback
        if gpus.is_empty() {
            gpus.push(GpuSnapshot {
                name: "Adaptador Gráfico do Sistema".to_string(),
                vendor: "Sistema Operacional".to_string(),
                usage_percent: 0.0,
                vram_total_bytes: 0,
                vram_used_bytes: 0,
                vram_usage_percent: 0.0,
                clock_core_mhz: None,
                clock_memory_mhz: None,
                temperature_core_c: None,
                temperature_hotspot_c: None,
                temperature_memory_c: None,
                power_watts: None,
                power_limit_watts: None,
                fan_speed_rpm: None,
                fan_speed_percent: None,
                pcie_link_gen: None,
                pcie_link_width: None,
                engine_usages: vec![("3D Graphics".to_string(), 0.0)],
                throttle_reasons: Vec::new(),
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

        // Leitura de Vendor
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

        // Utilização da GPU
        let usage = if let Ok(u) = fs::read_to_string(device_path.join("gpu_busy_percent")) {
            u.trim().parse::<f32>().unwrap_or(0.0)
        } else {
            0.0
        };

        // Clocks atuais
        let mut clock_core_mhz = None;
        let mut clock_mem_mhz = None;

        if let Ok(c) = fs::read_to_string(device_path.join("pp_dpm_sclk")) {
            // AMD sclk
            for line in c.lines() {
                if line.contains('*') {
                    if let Some(mhz_str) = line.split_whitespace().nth(1) {
                        clock_core_mhz = mhz_str.trim_end_matches("Mhz").parse::<u32>().ok();
                    }
                }
            }
        }

        if let Ok(m) = fs::read_to_string(device_path.join("pp_dpm_mclk")) {
            // AMD mclk
            for line in m.lines() {
                if line.contains('*') {
                    if let Some(mhz_str) = line.split_whitespace().nth(1) {
                        clock_mem_mhz = mhz_str.trim_end_matches("Mhz").parse::<u32>().ok();
                    }
                }
            }
        }

        // Temperaturas (Core e Hotspot)
        let mut temp_core_c = None;
        let mut temp_hotspot_c = None;

        let hwmon_dir = device_path.join("hwmon");
        if hwmon_dir.exists() {
            if let Ok(entries) = fs::read_dir(hwmon_dir) {
                for entry in entries.flatten() {
                    let p = entry.path();
                    if let Ok(t1) = fs::read_to_string(p.join("temp1_input")) {
                        if let Ok(m) = t1.trim().parse::<f32>() {
                            temp_core_c = Some(m / 1000.0);
                        }
                    }
                    if let Ok(t2) = fs::read_to_string(p.join("temp2_input")) {
                        if let Ok(m) = t2.trim().parse::<f32>() {
                            temp_hotspot_c = Some(m / 1000.0);
                        }
                    }
                }
            }
        }

        // VRAM
        let mut vram_total_bytes = 0;
        let mut vram_used_bytes = 0;

        if let Ok(v_tot) = fs::read_to_string(device_path.join("mem_info_vram_total")) {
            vram_total_bytes = v_tot.trim().parse::<u64>().unwrap_or(0);
        }
        if let Ok(v_used) = fs::read_to_string(device_path.join("mem_info_vram_used")) {
            vram_used_bytes = v_used.trim().parse::<u64>().unwrap_or(0);
        }

        let vram_usage_percent = if vram_total_bytes > 0 {
            (vram_used_bytes as f32 / vram_total_bytes as f32) * 100.0
        } else {
            0.0
        };

        // PCIe Link Speed / Width
        let pcie_link_gen = fs::read_to_string(device_path.join("current_link_speed"))
            .ok()
            .and_then(|s| {
                if s.contains("16.0") {
                    Some(4)
                } else if s.contains("8.0") {
                    Some(3)
                } else if s.contains("5.0") {
                    Some(2)
                } else {
                    Some(1)
                }
            });

        let pcie_link_width = fs::read_to_string(device_path.join("current_link_width"))
            .ok()
            .and_then(|s| s.trim().parse::<u8>().ok());

        Some(GpuSnapshot {
            name: format!("GPU {} ({})", vendor, card_path.file_name()?.to_string_lossy()),
            vendor,
            usage_percent: usage,
            vram_total_bytes,
            vram_used_bytes,
            vram_usage_percent,
            clock_core_mhz,
            clock_memory_mhz: clock_mem_mhz,
            temperature_core_c: temp_core_c,
            temperature_hotspot_c: temp_hotspot_c,
            temperature_memory_c: None,
            power_watts: None,
            power_limit_watts: None,
            fan_speed_rpm: None,
            fan_speed_percent: None,
            pcie_link_gen,
            pcie_link_width,
            engine_usages: vec![
                ("3D Graphics".to_string(), usage),
                ("Compute".to_string(), 0.0),
            ],
            throttle_reasons: Vec::new(),
        })
    }
}

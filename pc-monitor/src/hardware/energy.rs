//! Coletor e calculador de energia, consumo em Watts, acumulador Wh/kWh e custo financeiro.

use crate::core::snapshot::EnergySnapshot;
use std::time::Instant;

pub struct EnergyCollector {
    last_sample_instant: Instant,
    cumulative_watt_hours: f64,
}

impl Default for EnergyCollector {
    fn default() -> Self {
        Self::new()
    }
}

impl EnergyCollector {
    pub fn new() -> Self {
        Self {
            last_sample_instant: Instant::now(),
            cumulative_watt_hours: 0.0,
        }
    }

    /// Atualiza o consumo e integra numericamente a energia acumulada em Wh e custo em R$.
    pub fn update(
        &mut self,
        cpu_usage_percent: f32,
        cpu_watts_measured: Option<f32>,
        gpu_watts_measured: Option<f32>,
        cost_per_kwh_brl: f64,
    ) -> EnergySnapshot {
        let now = Instant::now();
        let delta_seconds = now.duration_since(self.last_sample_instant).as_secs_f64();
        self.last_sample_instant = now;

        // Determinação do consumo em Watts:
        let is_measured = cpu_watts_measured.is_some() || gpu_watts_measured.is_some();

        // Se CPU não tiver sensor de hardware, estima com base na carga e TDP base de 65W
        let estimated_cpu_w = cpu_watts_measured.unwrap_or_else(|| {
            let base_idle = 15.0;
            let dynamic = (cpu_usage_percent / 100.0) * 50.0;
            base_idle + dynamic
        });

        let estimated_gpu_w = gpu_watts_measured.unwrap_or(20.0);
        let platform_base_w = 25.0; // Placa-mãe, ventoinhas, SSDs, RAM

        let total_system_watts = estimated_cpu_w + estimated_gpu_w + platform_base_w;

        // Integração numérica contínua em Watt-horas: E = P * (t / 3600)
        let added_wh = (total_system_watts as f64 * delta_seconds) / 3600.0;
        self.cumulative_watt_hours += added_wh;

        let cumulative_kwh = self.cumulative_watt_hours / 1000.0;
        let cumulative_cost_brl = cumulative_kwh * cost_per_kwh_brl;

        // Telemetria de bateria via SysFS (Linux) ou Win32
        let (on_battery, battery_percent, battery_time) = Self::read_battery_telemetry();

        EnergySnapshot {
            cpu_watts: cpu_watts_measured.or(Some(estimated_cpu_w)),
            gpu_watts: gpu_watts_measured.or(Some(estimated_gpu_w)),
            system_estimated_watts: total_system_watts,
            is_measured,
            cumulative_watt_hours: self.cumulative_watt_hours,
            cumulative_cost_brl,
            on_battery,
            battery_percent,
            battery_time_remaining_sec: battery_time,
        }
    }

    fn read_battery_telemetry() -> (bool, Option<f32>, Option<u64>) {
        #[cfg(target_os = "linux")]
        {
            use std::fs;
            use std::path::Path;

            let bat_dir = Path::new("/sys/class/power_supply/BAT0");
            if bat_dir.exists() {
                let capacity = fs::read_to_string(bat_dir.join("capacity"))
                    .ok()
                    .and_then(|s| s.trim().parse::<f32>().ok());

                let status = fs::read_to_string(bat_dir.join("status"))
                    .unwrap_or_default();
                let on_battery = status.trim().to_lowercase() == "discharging";

                return (on_battery, capacity, None);
            }
        }

        (false, None, None)
    }
}

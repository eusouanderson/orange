//! Calculador determinístico de integridade e estabilidade do computador.

use crate::core::snapshot::{CpuSnapshot, HealthCategory, HealthSnapshot, MemorySnapshot};

pub struct HealthCalculator;

impl HealthCalculator {
    /// Avalia a saúde global do sistema com base em regras determinísticas e transparentes.
    pub fn evaluate(
        cpu: &CpuSnapshot,
        memory: &MemorySnapshot,
        whea_errors: u32,
    ) -> HealthSnapshot {
        let mut score: i32 = 100;
        let mut factors = Vec::new();

        // 1. Eixo Térmico
        if let Some(temp) = cpu.package_temperature_c {
            if temp >= 95.0 {
                score -= 30;
                factors.push(format!("CPU em temperatura crítica ({:.1}°C)", temp));
            } else if temp >= 85.0 {
                score -= 15;
                factors.push(format!("CPU em temperatura elevada ({:.1}°C)", temp));
            }
        }

        if cpu.thermal_throttled {
            score -= 20;
            factors.push("Thermal Throttling ativo na CPU".to_string());
        }

        // 2. Eixo de Memória
        if memory.usage_percent >= 95.0 {
            score -= 25;
            factors.push(format!("Memória RAM em saturação crítica ({:.1}%)", memory.usage_percent));
        } else if memory.usage_percent >= 85.0 {
            score -= 10;
            factors.push(format!("Alta pressão de memória RAM ({:.1}%)", memory.usage_percent));
        }

        if memory.swap_percent >= 80.0 {
            score -= 15;
            factors.push("Utilização severa do arquivo de paginação (Swap)".to_string());
        }

        // 3. Eixo de Estabilidade (WHEA)
        if whea_errors > 0 {
            let penalty = (whea_errors * 20).min(50) as i32;
            score -= penalty;
            factors.push(format!("{} erro(s) de hardware WHEA detectados", whea_errors));
        }

        // Normalização do score entre 0 e 100
        let final_score = score.clamp(0, 100) as u8;

        let category = match final_score {
            90..=100 => HealthCategory::Excellent,
            75..=89 => HealthCategory::Normal,
            50..=74 => HealthCategory::Warning,
            _ => HealthCategory::Critical,
        };

        if factors.is_empty() {
            factors.push("Todos os componentes operando em condições nominais ideais.".to_string());
        }

        HealthSnapshot {
            score: final_score,
            category,
            factors,
            whea_errors_detected: whea_errors,
            thermal_throttling_events: if cpu.thermal_throttled { 1 } else { 0 },
            power_throttling_events: 0,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_health_evaluation_nominal() {
        let cpu = CpuSnapshot {
            package_temperature_c: Some(55.0),
            thermal_throttled: false,
            ..Default::default()
        };
        let mem = MemorySnapshot {
            usage_percent: 40.0,
            swap_percent: 0.0,
            ..Default::default()
        };

        let health = HealthCalculator::evaluate(&cpu, &mem, 0);
        assert_eq!(health.score, 100);
        assert_eq!(health.category, HealthCategory::Excellent);
    }

    #[test]
    fn test_health_evaluation_critical() {
        let cpu = CpuSnapshot {
            package_temperature_c: Some(98.0),
            thermal_throttled: true,
            ..Default::default()
        };
        let mem = MemorySnapshot {
            usage_percent: 96.0,
            swap_percent: 85.0,
            ..Default::default()
        };

        let health = HealthCalculator::evaluate(&cpu, &mem, 1);
        assert!(health.score < 50);
        assert_eq!(health.category, HealthCategory::Critical);
        assert!(health.factors.len() >= 3);
    }
}

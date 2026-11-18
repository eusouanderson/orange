//! Sistema inteligente de alertas com debounce temporal e histerese.
//! Evita alarmes falsos causados por picos transitórios de hardware.

use crate::core::snapshot::{ActiveAlert, AlertSeverity};
use std::time::{Duration, Instant};

pub struct AlertRule {
    pub id: &'static str,
    pub title: &'static str,
    pub severity: AlertSeverity,
    pub threshold: f32,
    pub required_consecutive_hits: u32,
    pub cooldown: Duration,
    // Estado interno
    current_consecutive_hits: u32,
    last_triggered: Option<Instant>,
    pub is_active: bool,
}

impl AlertRule {
    pub fn new(
        id: &'static str,
        title: &'static str,
        severity: AlertSeverity,
        threshold: f32,
        required_consecutive_hits: u32,
        cooldown: Duration,
    ) -> Self {
        Self {
            id,
            title,
            severity,
            threshold,
            required_consecutive_hits,
            cooldown,
            current_consecutive_hits: 0,
            last_triggered: None,
            is_active: false,
        }
    }

    /// Avalia a regra contra um valor amostrado.
    /// Retorna Some(ActiveAlert) se o alerta acabou de ser disparado após o debounce.
    pub fn evaluate(&mut self, current_value: f32, message: &str) -> Option<ActiveAlert> {
        let now = Instant::now();
        let exceeds = current_value >= self.threshold;

        if exceeds {
            self.current_consecutive_hits += 1;
            if self.current_consecutive_hits >= self.required_consecutive_hits {
                self.is_active = true;
                let should_fire = match self.last_triggered {
                    None => true,
                    Some(last) => now.duration_since(last) >= self.cooldown,
                };

                if should_fire {
                    self.last_triggered = Some(now);
                    let epoch = std::time::SystemTime::now()
                        .duration_since(std::time::UNIX_EPOCH)
                        .unwrap_or_default()
                        .as_secs();

                    return Some(ActiveAlert {
                        rule_id: self.id.to_string(),
                        title: self.title.to_string(),
                        message: message.to_string(),
                        severity: self.severity,
                        value: current_value,
                        threshold: self.threshold,
                        timestamp_epoch_sec: epoch,
                    });
                }
            }
        } else {
            // Histerese: reseta a contagem de debounce se cair abaixo do threshold
            self.current_consecutive_hits = 0;
            self.is_active = false;
        }

        None
    }
}

pub struct AlertManager {
    rules: Vec<AlertRule>,
    active_alerts: Vec<ActiveAlert>,
}

impl Default for AlertManager {
    fn default() -> Self {
        Self::new()
    }
}

impl AlertManager {
    pub fn new() -> Self {
        let rules = vec![
            AlertRule::new(
                "cpu_temp_high",
                "Temperatura Alta na CPU",
                AlertSeverity::Warning,
                85.0,
                3, // Requer 3 segundos consecutivos
                Duration::from_secs(60),
            ),
            AlertRule::new(
                "cpu_temp_crit",
                "Temperatura Crítica na CPU",
                AlertSeverity::Critical,
                95.0,
                2, // Requer 2 segundos consecutivos
                Duration::from_secs(30),
            ),
            AlertRule::new(
                "ram_pressure",
                "Saturação de Memória RAM",
                AlertSeverity::Warning,
                90.0,
                5,
                Duration::from_secs(120),
            ),
            AlertRule::new(
                "whea_error",
                "Instabilidade de Hardware (WHEA/MCE)",
                AlertSeverity::Critical,
                1.0,
                1,
                Duration::from_secs(300),
            ),
        ];

        Self {
            rules,
            active_alerts: Vec::with_capacity(8),
        }
    }

    pub fn evaluate_all(
        &mut self,
        cpu_temp: Option<f32>,
        ram_percent: f32,
        whea_errors: u32,
    ) -> &[ActiveAlert] {
        self.active_alerts.clear();

        for rule in &mut self.rules {
            let fired = match rule.id {
                "cpu_temp_high" => cpu_temp.and_then(|t| {
                    rule.evaluate(t, &format!("CPU atingiu {:.1}°C sustentados.", t))
                }),
                "cpu_temp_crit" => cpu_temp.and_then(|t| {
                    rule.evaluate(t, &format!("PERIGO: CPU a {:.1}°C! Risco de shutdown.", t))
                }),
                "ram_percent" | "ram_pressure" => {
                    rule.evaluate(ram_percent, &format!("RAM a {:.1}% de uso.", ram_percent))
                }
                "whea_error" => {
                    rule.evaluate(whea_errors as f32, &format!("{} erro(s) de hardware detectados.", whea_errors))
                }
                _ => None,
            };

            if let Some(alert) = fired {
                self.active_alerts.push(alert);
            }
        }

        &self.active_alerts
    }

    pub fn get_active_alerts(&self) -> &[ActiveAlert] {
        &self.active_alerts
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_alert_debounce() {
        let mut rule = AlertRule::new(
            "test_rule",
            "Teste",
            AlertSeverity::Warning,
            80.0,
            3,
            Duration::from_secs(10),
        );

        // Amostra 1: Acima do threshold, mas ainda não atingiu 3 hits
        let a1 = rule.evaluate(85.0, "pico");
        assert!(a1.is_none());
        assert!(!rule.is_active);

        // Amostra 2: Continua acima
        let a2 = rule.evaluate(86.0, "pico 2");
        assert!(a2.is_none());

        // Amostra 3: 3º hit consecutivo -> Dispara alerta!
        let a3 = rule.evaluate(87.0, "sustentado");
        assert!(a3.is_some());
        assert!(rule.is_active);

        // Amostra 4: Cooldown ainda ativo -> Não dispara novo alerta
        let a4 = rule.evaluate(88.0, "sustentado");
        assert!(a4.is_none());
    }

    #[test]
    fn test_alert_hysteresis_reset() {
        let mut rule = AlertRule::new(
            "test_rule",
            "Teste",
            AlertSeverity::Warning,
            80.0,
            3,
            Duration::from_secs(10),
        );

        // Amostra 1 e 2 altas
        rule.evaluate(85.0, "pico");
        rule.evaluate(85.0, "pico");

        // Amostra 3 normaliza -> Reseta debounce
        rule.evaluate(70.0, "normal");
        assert_eq!(rule.current_consecutive_hits, 0);

        // Próxima amostra alta conta como 1, não 3
        let a = rule.evaluate(85.0, "novo pico");
        assert!(a.is_none());
    }
}

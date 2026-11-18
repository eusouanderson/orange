//! Configurações persistentes da aplicação e HUD.

use serde::{Deserialize, Serialize};
use std::fs;
use std::path::PathBuf;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, Default)]
pub enum ViewMode {
    #[default]
    Compact,
    Expanded,
    Diagnostic,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AppConfig {
    pub view_mode: ViewMode,
    pub window_x: f32,
    pub window_y: f32,
    pub window_width: f32,
    pub window_height: f32,
    pub always_on_top: bool,
    pub click_through: bool,
    pub opacity: f32,
    pub sample_interval_ms: u64,
    pub cost_per_kwh_brl: f64,
    pub start_with_windows: bool,
    pub minimize_to_tray: bool,
    pub use_fahrenheit: bool,
}

impl Default for AppConfig {
    fn default() -> Self {
        Self {
            view_mode: ViewMode::Compact,
            window_x: 100.0,
            window_y: 100.0,
            window_width: 240.0,
            window_height: 220.0,
            always_on_top: true,
            click_through: false,
            opacity: 0.92,
            sample_interval_ms: 1000,
            cost_per_kwh_brl: 0.90,
            start_with_windows: false,
            minimize_to_tray: true,
            use_fahrenheit: false,
        }
    }
}

impl AppConfig {
    /// Determina o caminho padrão do arquivo de configuração persistente.
    pub fn config_path() -> PathBuf {
        let mut path = std::env::current_dir().unwrap_or_else(|_| PathBuf::from("."));
        path.push("orange_hud_config.json");
        path
    }

    /// Carrega as configurações persistidas ou retorna o valor padrão caso não existam.
    pub fn load_or_default() -> Self {
        let path = Self::config_path();
        if path.exists() {
            if let Ok(content) = fs::read_to_string(&path) {
                if let Ok(cfg) = serde_json::from_str::<Self>(&content) {
                    return cfg;
                }
            }
        }
        Self::default()
    }

    /// Salva as configurações em arquivo JSON no disco.
    pub fn save(&self) -> Result<(), std::io::Error> {
        let path = Self::config_path();
        let content = serde_json::to_string_pretty(self)
            .map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e))?;
        fs::write(path, content)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_config_serialization() {
        let cfg = AppConfig::default();
        let json = serde_json::to_string(&cfg).expect("Serialization failed");
        let decoded: AppConfig = serde_json::from_str(&json).expect("Deserialization failed");
        assert_eq!(cfg.view_mode, decoded.view_mode);
        assert_eq!(cfg.sample_interval_ms, decoded.sample_interval_ms);
    }
}

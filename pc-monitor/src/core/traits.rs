//! Trait padronizado para provedores de sensores e telemetria de hardware.

use super::types::{MetricSample, SensorCategory};
use std::error::Error;

/// Contrato padronizado que qualquer fonte de telemetria deve implementar.
pub trait SensorProvider: Send + Sync {
    /// Identificador único da fonte de telemetria (ex: "cpu.sysinfo", "gpu.nvml").
    fn id(&self) -> &str;

    /// Nome amigável de exibição (ex: "Intel RAPL Telemetry").
    fn name(&self) -> &str;

    /// Categoria principal de hardware coberta por este provedor.
    fn category(&self) -> SensorCategory;

    /// Verifica se a telemetria é suportada e acessível na máquina atual.
    fn is_available(&self) -> bool;

    /// Inicializa canais de comunicação, drivers ou bibliotecas de baixo nível.
    fn init(&mut self) -> Result<(), Box<dyn Error>>;

    /// Executa uma leitura instantânea dos sensores.
    fn sample(&mut self) -> Result<Vec<MetricSample>, Box<dyn Error>>;

    /// Libera recursos alocados, handles de drivers ou conexões.
    fn shutdown(&mut self) {}
}

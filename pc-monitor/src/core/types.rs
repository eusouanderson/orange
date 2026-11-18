//! Tipos e estruturas de dados fundamentais para o sistema de sensores e telemetria.

use serde::{Deserialize, Serialize};

/// Categorias principais de hardware e subsistemas monitorados.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum SensorCategory {
    Cpu,
    Memory,
    Gpu,
    Storage,
    Energy,
    Motherboard,
    Network,
    OperatingSystem,
}

/// Nível de confiabilidade e origem da telemetria coletada.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum SensorQuality {
    /// Leitura direta de registrador de hardware (MSR, SMBus, EC).
    HardwareDirect,
    /// Leitura através do driver oficial do fabricante (ex: NVML, ADL).
    DriverTelemetry,
    /// Métrica calculada ou estimada por modelo matemático (ex: consumo total somado).
    Estimated,
    /// Telemetria genérica via contadores do sistema operacional (ex: PDH, SysFS).
    Fallback,
    /// Sensor físico não presente ou sem permissão de acesso.
    Unavailable,
}

/// Unidades de medida das métricas de monitoramento.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum Unit {
    Percent,
    Megabytes,
    Gigabytes,
    MegaHertz,
    Celsius,
    Watts,
    WattHours,
    KiloWattHours,
    MegabytesPerSec,
    Iops,
    Milliseconds,
    Rpm,
    Volts,
    Amperes,
    CurrencyBrl,
    Count,
    None,
}

impl Unit {
    pub fn symbol(&self) -> &'static str {
        match self {
            Unit::Percent => "%",
            Unit::Megabytes => "MB",
            Unit::Gigabytes => "GB",
            Unit::MegaHertz => "MHz",
            Unit::Celsius => "°C",
            Unit::Watts => "W",
            Unit::WattHours => "Wh",
            Unit::KiloWattHours => "kWh",
            Unit::MegabytesPerSec => "MB/s",
            Unit::Iops => "IOPS",
            Unit::Milliseconds => "ms",
            Unit::Rpm => "RPM",
            Unit::Volts => "V",
            Unit::Amperes => "A",
            Unit::CurrencyBrl => "R$",
            Unit::Count => "un",
            Unit::None => "",
        }
    }
}

/// Representação polimórfica de valor métrico sem overhead de alocação dinâmica.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum MetricValue {
    Float(f64),
    Integer(i64),
    Text(String),
    Boolean(bool),
}

impl MetricValue {
    pub fn as_f64(&self) -> f64 {
        match self {
            MetricValue::Float(v) => *v,
            MetricValue::Integer(v) => *v as f64,
            MetricValue::Boolean(b) => if *b { 1.0 } else { 0.0 },
            MetricValue::Text(_) => 0.0,
        }
    }
}

/// Amostra individual de um sensor coletada em um instante no tempo.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct MetricSample {
    pub id: String,
    pub name: String,
    pub category: SensorCategory,
    pub value: MetricValue,
    pub unit: Unit,
    pub quality: SensorQuality,
    pub timestamp_ms: u64,
}

impl MetricSample {
    pub fn new(
        id: impl Into<String>,
        name: impl Into<String>,
        category: SensorCategory,
        value: MetricValue,
        unit: Unit,
        quality: SensorQuality,
        timestamp_ms: u64,
    ) -> Self {
        Self {
            id: id.into(),
            name: name.into(),
            category,
            value,
            unit,
            quality,
            timestamp_ms,
        }
    }
}

/// Estado operacional de um sensor.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum SensorStatus {
    Normal,
    Warning,
    Critical,
    Throttling,
    Disabled,
}

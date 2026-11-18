//! # Orange PC Monitor
//!
//! Ultra Low-Resource System Hardware & OS HUD by Orange Framework.
//! Projetado para consumo inferior a 30 MB de RAM e 0,2% de CPU em repouso.

pub mod config;
pub mod core;
pub mod diagnostics;
pub mod hardware;
pub mod ui;

pub use config::{AppConfig, ViewMode};
pub use core::{
    MetricSample, MetricValue, RingBuffer, SensorCategory, SensorProvider, SensorQuality,
    SensorStatus, SystemSnapshot, TelemetryEngine, Unit,
};
pub use diagnostics::{AlertManager, HealthCalculator, ProcessCollector, StabilityCollector};
pub use ui::{HudViewMode, OrangeHudApp, Theme};

//! Janela flutuante desktop minimalista (HUD) usando eframe/egui.

use super::components::{badge, metric_tile, sparkline, stat_row};
use super::theme::Theme;
use crate::config::AppConfig;
use crate::core::engine::TelemetryEngine;
use crate::core::snapshot::{ActiveAlert, AlertSeverity, SystemSnapshot};
use eframe::egui::{self, Color32, Frame, Margin, Rounding, Vec2};
use std::sync::Arc;
use std::time::Duration;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum HudViewMode {
    Compact,
    Expanded,
    Diagnostic,
}

pub struct OrangeHudApp {
    engine: Arc<TelemetryEngine>,
    current_mode: HudViewMode,
    is_always_on_top: bool,
    #[allow(dead_code)]
    pub click_through: bool,
    #[allow(dead_code)]
    pub config: AppConfig,
}

impl OrangeHudApp {
    pub fn new(engine: Arc<TelemetryEngine>, config: AppConfig) -> Self {
        Self {
            engine,
            current_mode: HudViewMode::Compact,
            is_always_on_top: config.always_on_top,
            click_through: config.click_through,
            config,
        }
    }

    pub fn set_mode(&mut self, mode: HudViewMode, ctx: &egui::Context) {
        self.current_mode = mode;
        let new_size = match mode {
            HudViewMode::Compact => Vec2::new(320.0, 190.0),
            HudViewMode::Expanded => Vec2::new(380.0, 480.0),
            HudViewMode::Diagnostic => Vec2::new(440.0, 560.0),
        };
        ctx.send_viewport_cmd(egui::ViewportCommand::InnerSize(new_size));
    }
}

impl eframe::App for OrangeHudApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        // Redesenho reativo de baixa frequência (2Hz) para consumo residual de GPU (< 0.05%)
        ctx.request_repaint_after(Duration::from_millis(500));

        let snapshot = self.engine.snapshot().read().clone();

        // Janela frameless translúcida
        let frame = Frame::none()
            .fill(Theme::BG_WINDOW)
            .rounding(Rounding::same(10.0))
            .stroke(Theme::BORDER_STROKE)
            .inner_margin(Margin::same(12.0));

        egui::CentralPanel::default().frame(frame).show(ctx, |ui| {
            // Permite arrastar a janela clicando no cabeçalho ou fundo
            self.render_header(ui, ctx, &snapshot);

            ui.add_space(8.0);

            // Alertas ativos destacados caso existam
            if !snapshot.alerts.is_empty() {
                self.render_alert_banner(ui, &snapshot.alerts);
                ui.add_space(6.0);
            }

            match self.current_mode {
                HudViewMode::Compact => self.render_compact_view(ui, &snapshot),
                HudViewMode::Expanded => self.render_expanded_view(ui, &snapshot),
                HudViewMode::Diagnostic => self.render_diagnostic_view(ui, &snapshot),
            }
        });
    }
}

impl OrangeHudApp {
    fn render_header(&mut self, ui: &mut egui::Ui, ctx: &egui::Context, snap: &SystemSnapshot) {
        ui.horizontal(|ui| {
            // Drag handle sutil
            let drag_response = ui.allocate_response(Vec2::new(14.0, 14.0), egui::Sense::drag());
            ui.painter().circle_filled(
                drag_response.rect.center(),
                4.5,
                Theme::ORANGE_ACCENT,
            );
            if drag_response.dragged() {
                ctx.send_viewport_cmd(egui::ViewportCommand::StartDrag);
            }

            ui.add_space(2.0);

            // Título do app
            ui.label(
                egui::RichText::new("ORANGE HUD")
                    .size(11.0)
                    .color(Theme::TEXT_PRIMARY)
                    .strong(),
            );

            // Badge de Saúde
            let (h_text, h_col) = match snap.health.score {
                90..=100 => ("100%", Theme::STATUS_EXCELLENT),
                75..=89 => ("BOM", Theme::STATUS_NORMAL),
                50..=74 => ("ALERTA", Theme::STATUS_WARNING),
                _ => ("CRÍTICO", Theme::STATUS_CRITICAL),
            };
            badge(ui, h_text, h_col, Color32::WHITE);

            // Botões de modo à direita
            ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                // Fechar
                if ui
                    .button(egui::RichText::new("✕").size(10.0).color(Theme::TEXT_MUTED))
                    .clicked()
                {
                    ctx.send_viewport_cmd(egui::ViewportCommand::Close);
                }

                // Alternar Pin (Always on top)
                let pin_col = if self.is_always_on_top {
                    Theme::ORANGE_ACCENT
                } else {
                    Theme::TEXT_MUTED
                };
                if ui
                    .button(egui::RichText::new("📌").size(10.0).color(pin_col))
                    .clicked()
                {
                    self.is_always_on_top = !self.is_always_on_top;
                    let level = if self.is_always_on_top {
                        egui::viewport::WindowLevel::AlwaysOnTop
                    } else {
                        egui::viewport::WindowLevel::Normal
                    };
                    ctx.send_viewport_cmd(egui::ViewportCommand::WindowLevel(level));
                }

                // Modo Diagnóstico
                let diag_col = if self.current_mode == HudViewMode::Diagnostic {
                    Theme::ORANGE_ACCENT
                } else {
                    Theme::TEXT_MUTED
                };
                if ui
                    .button(egui::RichText::new("DIAG").size(9.0).color(diag_col))
                    .clicked()
                {
                    self.set_mode(HudViewMode::Diagnostic, ctx);
                }

                // Modo Expandido
                let exp_col = if self.current_mode == HudViewMode::Expanded {
                    Theme::ORANGE_ACCENT
                } else {
                    Theme::TEXT_MUTED
                };
                if ui
                    .button(egui::RichText::new("EXP").size(9.0).color(exp_col))
                    .clicked()
                {
                    self.set_mode(HudViewMode::Expanded, ctx);
                }

                // Modo Compacto
                let comp_col = if self.current_mode == HudViewMode::Compact {
                    Theme::ORANGE_ACCENT
                } else {
                    Theme::TEXT_MUTED
                };
                if ui
                    .button(egui::RichText::new("MIN").size(9.0).color(comp_col))
                    .clicked()
                {
                    self.set_mode(HudViewMode::Compact, ctx);
                }
            });
        });
    }

    fn render_alert_banner(&self, ui: &mut egui::Ui, alerts: &[ActiveAlert]) {
        for alert in alerts {
            let bg_col = match alert.severity {
                AlertSeverity::Critical => Theme::STATUS_CRITICAL,
                AlertSeverity::Warning => Theme::STATUS_WARNING,
                AlertSeverity::Info => Theme::STATUS_NORMAL,
            };

            ui.horizontal(|ui| {
                badge(ui, "ALERTA", bg_col, Color32::WHITE);
                ui.label(
                    egui::RichText::new(&alert.message)
                        .size(10.5)
                        .color(Theme::TEXT_PRIMARY),
                );
            });
        }
    }

    fn render_compact_view(&self, ui: &mut egui::Ui, snap: &SystemSnapshot) {
        // Grade 2x2 com as métricas vitais
        egui::Grid::new("compact_metrics_grid")
            .num_columns(2)
            .spacing(Vec2::new(14.0, 10.0))
            .show(ui, |ui| {
                // 1. CPU
                let cpu_temp_txt = snap
                    .cpu
                    .package_temperature_c
                    .map(|t| format!("{:.0}°C", t))
                    .unwrap_or_else(|| "--".to_string());
                metric_tile(
                    ui,
                    "CPU",
                    &format!("{:.1}%", snap.cpu.total_usage_percent),
                    &cpu_temp_txt,
                    snap.cpu.total_usage_percent,
                    Theme::usage_color(snap.cpu.total_usage_percent),
                );

                // 2. RAM
                let ram_used_gb = snap.memory.used_bytes as f32 / (1024.0 * 1024.0 * 1024.0);
                let ram_total_gb = snap.memory.total_bytes as f32 / (1024.0 * 1024.0 * 1024.0);
                metric_tile(
                    ui,
                    "MEMÓRIA",
                    &format!("{:.1}%", snap.memory.usage_percent),
                    &format!("{:.1}/{:.0} GB", ram_used_gb, ram_total_gb),
                    snap.memory.usage_percent,
                    Theme::usage_color(snap.memory.usage_percent),
                );
                ui.end_row();

                // 3. GPU
                if let Some(gpu) = snap.gpus.first() {
                    let gpu_temp_txt = gpu
                        .temperature_core_c
                        .map(|t| format!("{:.0}°C", t))
                        .unwrap_or_else(|| "--".to_string());
                    metric_tile(
                        ui,
                        "GPU",
                        &format!("{:.1}%", gpu.usage_percent),
                        &gpu_temp_txt,
                        gpu.usage_percent,
                        Theme::usage_color(gpu.usage_percent),
                    );
                } else {
                    metric_tile(ui, "GPU", "N/A", "--", 0.0, Theme::TEXT_MUTED);
                }

                // 4. Energia / Watts
                let watts_txt = format!("{:.0} W", snap.energy.system_estimated_watts);
                let cost_txt = format!("R$ {:.2}", snap.energy.cumulative_cost_brl);
                let watts_percent = (snap.energy.system_estimated_watts / 250.0) * 100.0;
                metric_tile(
                    ui,
                    "POTÊNCIA",
                    &watts_txt,
                    &cost_txt,
                    watts_percent,
                    Theme::ORANGE_ACCENT,
                );
                ui.end_row();
            });
    }

    fn render_expanded_view(&self, ui: &mut egui::Ui, snap: &SystemSnapshot) {
        egui::ScrollArea::vertical().show(ui, |ui| {
            self.render_compact_view(ui, snap);

            ui.add_space(8.0);
            ui.separator();
            ui.add_space(4.0);

            // Gráficos de Histórico em Tempo Real
            ui.label(
                egui::RichText::new("HISTÓRICO RECENTE (60s)")
                    .size(10.0)
                    .color(Theme::TEXT_SECONDARY)
                    .strong(),
            );
            ui.add_space(4.0);

            let cpu_history = self.engine.cpu_history().read().to_chronological_vec();
            ui.label(egui::RichText::new("Carga da CPU").size(10.0).color(Theme::TEXT_MUTED));
            sparkline(ui, &cpu_history, 100.0, 36.0, Theme::ORANGE_ACCENT);

            ui.add_space(6.0);
            let ram_history = self.engine.ram_history().read().to_chronological_vec();
            ui.label(egui::RichText::new("Uso de RAM").size(10.0).color(Theme::TEXT_MUTED));
            sparkline(ui, &ram_history, 100.0, 36.0, Theme::STATUS_NORMAL);

            ui.add_space(8.0);
            ui.separator();
            ui.add_space(4.0);

            // Subsistema de Armazenamento e Rede
            ui.label(
                egui::RichText::new("SUBSISTEMAS & REDE")
                    .size(10.0)
                    .color(Theme::TEXT_SECONDARY)
                    .strong(),
            );
            ui.add_space(4.0);

            let rx_mb = snap.network.download_bytes_sec as f32 / (1024.0 * 1024.0);
            let tx_mb = snap.network.upload_bytes_sec as f32 / (1024.0 * 1024.0);
            stat_row(
                ui,
                "Rede (Down / Up)",
                &format!("{:.2} MB/s  ↓ /  {:.2} MB/s  ↑", rx_mb, tx_mb),
            );
            stat_row(ui, "Interface Ativa", &snap.network.active_interface);
            stat_row(ui, "IP Local", &snap.network.local_ip);

            if let Some(disk) = snap.disks.first() {
                let r_mb = disk.read_bytes_sec as f32 / (1024.0 * 1024.0);
                let w_mb = disk.write_bytes_sec as f32 / (1024.0 * 1024.0);
                stat_row(
                    ui,
                    &format!("Disco ({})", disk.mount_point),
                    &format!("{:.1} MB/s R / {:.1} MB/s W", r_mb, w_mb),
                );
            }

            ui.add_space(8.0);
            ui.separator();
            ui.add_space(4.0);

            // Top Processos
            ui.label(
                egui::RichText::new("TOP PROCESSOS (CPU / RAM)")
                    .size(10.0)
                    .color(Theme::TEXT_SECONDARY)
                    .strong(),
            );
            ui.add_space(4.0);

            for proc in snap.top_processes.iter().take(4) {
                let mem_mb = proc.memory_bytes as f32 / (1024.0 * 1024.0);
                ui.horizontal(|ui| {
                    ui.label(
                        egui::RichText::new(&proc.name)
                            .size(10.5)
                            .color(Theme::TEXT_PRIMARY),
                    );
                    ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                        ui.label(
                            egui::RichText::new(format!("{:.1}% | {:.0} MB", proc.cpu_percent, mem_mb))
                                .size(10.0)
                                .color(Theme::TEXT_MUTED),
                        );
                    });
                });
            }
        });
    }

    fn render_diagnostic_view(&self, ui: &mut egui::Ui, snap: &SystemSnapshot) {
        egui::ScrollArea::vertical().show(ui, |ui| {
            ui.label(
                egui::RichText::new("DIAGNÓSTICO TÉCNICO & INTEGRIDADE")
                    .size(11.0)
                    .color(Theme::ORANGE_ACCENT)
                    .strong(),
            );
            ui.add_space(6.0);

            // 1. Integridade de Hardware
            stat_row(ui, "Índice de Saúde Global", &format!("{}/100 ({})", snap.health.score, snap.health.category.label()));
            stat_row(ui, "Erros de Hardware (WHEA/MCE)", &format!("{}", snap.health.whea_errors_detected));
            stat_row(
                ui,
                "Thermal Throttling CPU",
                if snap.cpu.thermal_throttled { "ATIVO (PERIGO)" } else { "Inativo (Nominal)" },
            );
            stat_row(
                ui,
                "Power Throttling CPU",
                if snap.cpu.power_throttled { "ATIVO" } else { "Inativo" },
            );

            ui.add_space(6.0);
            ui.separator();
            ui.add_space(4.0);

            // 2. Detalhes de Processador e Arquitetura
            ui.label(egui::RichText::new("PROCESSADOR").size(10.0).color(Theme::TEXT_SECONDARY).strong());
            stat_row(ui, "Modelo", &snap.cpu.brand);
            stat_row(ui, "Núcleos Físicos / Threads", &format!("{} / {}", snap.cpu.physical_cores, snap.cpu.logical_threads));
            stat_row(ui, "Clock Atual", &format!("{} MHz", snap.cpu.current_frequency_mhz));
            stat_row(ui, "Load Average (1, 5, 15m)", &format!("{:.2}, {:.2}, {:.2}", snap.cpu.load_average.0, snap.cpu.load_average.1, snap.cpu.load_average.2));

            ui.add_space(6.0);
            ui.separator();
            ui.add_space(4.0);

            // 3. Eficiência Energética e Bateria
            ui.label(egui::RichText::new("ENERGIA & CUSTO").size(10.0).color(Theme::TEXT_SECONDARY).strong());
            stat_row(ui, "Consumo Instantâneo", &format!("{:.1} Watts", snap.energy.system_estimated_watts));
            stat_row(ui, "Origem da Leitura", if snap.energy.is_measured { "Sensor Físico (Medido)" } else { "Modelo Matemático Estimado" });
            stat_row(ui, "Energia Acumulada", &format!("{:.3} kWh ({:.1} Wh)", snap.energy.cumulative_watt_hours / 1000.0, snap.energy.cumulative_watt_hours));
            stat_row(ui, "Custo Financeiro Estimado", &format!("R$ {:.3}", snap.energy.cumulative_cost_brl));

            if let Some(bat_pct) = snap.energy.battery_percent {
                stat_row(ui, "Bateria", &format!("{:.0}% ({})", bat_pct, if snap.energy.on_battery { "Descarregando" } else { "Conectado à Tomada" }));
            }

            ui.add_space(6.0);
            ui.separator();
            ui.add_space(4.0);

            // 4. Fatores Avaliados pelo Motor
            ui.label(egui::RichText::new("FATORES DE INTEGRIDADE").size(10.0).color(Theme::TEXT_SECONDARY).strong());
            for factor in &snap.health.factors {
                ui.horizontal(|ui| {
                    ui.label(egui::RichText::new("•").size(10.0).color(Theme::ORANGE_ACCENT));
                    ui.label(egui::RichText::new(factor).size(10.0).color(Theme::TEXT_PRIMARY));
                });
            }
        });
    }
}

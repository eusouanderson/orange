//! Componentes visuais ultra leves para o HUD minimalista.

use super::theme::Theme;
use eframe::egui::{self, Color32, Pos2, Rect, Response, Sense, Stroke, Ui, Vec2};

/// Desenha uma barra de progresso horizontal ultra compacta.
pub fn mini_progress_bar(ui: &mut Ui, percent: f32, color: Color32, height: f32) {
    let desired_size = Vec2::new(ui.available_width(), height);
    let (rect, _response) = ui.allocate_exact_size(desired_size, Sense::hover());

    let painter = ui.painter();
    // Fundo da barra
    painter.rect_filled(rect, 2.0, Theme::BG_PROGRESS_BAR);

    // Preenchimento proporcional
    let fill_width = (rect.width() * (percent.clamp(0.0, 100.0) / 100.0)).max(0.0);
    if fill_width > 0.0 {
        let fill_rect = Rect::from_min_size(rect.min, Vec2::new(fill_width, rect.height()));
        painter.rect_filled(fill_rect, 2.0, color);
    }
}

/// Cartão compacto de métrica com valor numérico e barra de progresso.
pub fn metric_tile(
    ui: &mut Ui,
    title: &str,
    value_text: &str,
    sub_text: &str,
    percent: f32,
    color: Color32,
) {
    ui.vertical(|ui| {
        ui.horizontal(|ui| {
            ui.label(
                egui::RichText::new(title)
                    .size(10.5)
                    .color(Theme::TEXT_SECONDARY)
                    .strong(),
            );
            ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                ui.label(
                    egui::RichText::new(sub_text)
                        .size(10.0)
                        .color(Theme::TEXT_MUTED),
                );
            });
        });

        ui.add_space(1.0);

        ui.horizontal(|ui| {
            ui.label(
                egui::RichText::new(value_text)
                    .size(15.0)
                    .color(Theme::TEXT_PRIMARY)
                    .strong(),
            );
        });

        ui.add_space(2.0);
        mini_progress_bar(ui, percent, color, 3.5);
    });
}

/// Desenha um gráfico sparkline em tempo real no painter sem alocação dinâmica.
pub fn sparkline(ui: &mut Ui, samples: &[f32], max_val: f32, height: f32, stroke_color: Color32) {
    let desired_size = Vec2::new(ui.available_width(), height);
    let (rect, _response) = ui.allocate_exact_size(desired_size, Sense::hover());
    let painter = ui.painter();

    // Fundo do gráfico
    painter.rect_filled(
        rect,
        3.0,
        Color32::from_rgba_premultiplied(10, 12, 16, 160),
    );

    if samples.len() < 2 {
        return;
    }

    let n = samples.len();
    let step_x = rect.width() / (n - 1) as f32;
    let safe_max = if max_val <= 0.0 { 100.0 } else { max_val };

    let mut points = Vec::with_capacity(n);
    for (i, &val) in samples.iter().enumerate() {
        let x = rect.min.x + i as f32 * step_x;
        let norm_y = (val / safe_max).clamp(0.0, 1.0);
        let y = rect.max.y - (norm_y * (rect.height() - 4.0)) - 2.0;
        points.push(Pos2::new(x, y));
    }

    // Linha do gráfico
    for i in 0..points.len() - 1 {
        painter.line_segment(
            [points[i], points[i + 1]],
            Stroke::new(1.2_f32, stroke_color),
        );
    }
}

/// Linha de estatística Chave - Valor.
pub fn stat_row(ui: &mut Ui, label: &str, value: &str) {
    ui.horizontal(|ui| {
        ui.label(
            egui::RichText::new(label)
                .size(11.0)
                .color(Theme::TEXT_SECONDARY),
        );
        ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
            ui.label(
                egui::RichText::new(value)
                    .size(11.0)
                    .color(Theme::TEXT_PRIMARY)
                    .strong(),
            );
        });
    });
}

/// Badge de status arredondado.
pub fn badge(ui: &mut Ui, text: &str, bg_color: Color32, text_color: Color32) -> Response {
    let padding = Vec2::new(6.0, 2.0);
    let galley = ui.painter().layout_no_wrap(
        text.to_string(),
        egui::FontId::proportional(10.0),
        text_color,
    );
    let size = galley.size() + padding * 2.0;
    let (rect, response) = ui.allocate_exact_size(size, Sense::click());

    if ui.is_rect_visible(rect) {
        let painter = ui.painter();
        painter.rect_filled(rect, 4.0, bg_color);
        painter.galley(rect.min + padding, galley, text_color);
    }

    response
}

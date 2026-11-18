//! Tema visual minimalista e futurista para o Orange PC Monitor HUD.

use eframe::egui::{Color32, Stroke};

pub struct Theme;

impl Theme {
    // Cores de fundo com transparência acrílica
    pub const BG_WINDOW: Color32 = Color32::from_rgba_premultiplied(18, 20, 24, 225);
    pub const BG_CARD: Color32 = Color32::from_rgba_premultiplied(28, 32, 40, 210);
    pub const BG_CARD_HOVER: Color32 = Color32::from_rgba_premultiplied(40, 46, 58, 230);
    pub const BG_PROGRESS_BAR: Color32 = Color32::from_rgba_premultiplied(40, 44, 52, 180);

    // Borda sutil de vidro
    pub const BORDER_COLOR: Color32 = Color32::from_rgba_premultiplied(255, 140, 0, 70); // Orange glow sutil
    pub const BORDER_STROKE: Stroke = Stroke {
        width: 1.0,
        color: Self::BORDER_COLOR,
    };

    // Cores de destaque (Branding Orange)
    pub const ORANGE_ACCENT: Color32 = Color32::from_rgb(255, 120, 20);
    pub const ORANGE_HOVER: Color32 = Color32::from_rgb(255, 145, 60);

    // Cores de texto
    pub const TEXT_PRIMARY: Color32 = Color32::from_rgb(240, 243, 246);
    pub const TEXT_SECONDARY: Color32 = Color32::from_rgb(145, 155, 168);
    pub const TEXT_MUTED: Color32 = Color32::from_rgb(100, 110, 122);

    // Cores de status de telemetria
    pub const STATUS_EXCELLENT: Color32 = Color32::from_rgb(34, 197, 94); // Emerald 500
    pub const STATUS_NORMAL: Color32 = Color32::from_rgb(59, 130, 246);    // Blue 500
    pub const STATUS_WARNING: Color32 = Color32::from_rgb(245, 158, 11);   // Amber 500
    pub const STATUS_CRITICAL: Color32 = Color32::from_rgb(239, 68, 68);   // Red 500

    /// Retorna cor semântica com base na porcentagem de uso (0.0 - 100.0).
    pub fn usage_color(percent: f32) -> Color32 {
        if percent < 60.0 {
            Self::STATUS_EXCELLENT
        } else if percent < 85.0 {
            Self::STATUS_WARNING
        } else {
            Self::STATUS_CRITICAL
        }
    }

    /// Retorna cor semântica para temperatura (°C).
    pub fn temp_color(temp_c: f32) -> Color32 {
        if temp_c < 65.0 {
            Self::STATUS_EXCELLENT
        } else if temp_c < 80.0 {
            Self::STATUS_WARNING
        } else {
            Self::STATUS_CRITICAL
        }
    }
}

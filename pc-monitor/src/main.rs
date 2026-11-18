//! Ponto de entrada do Orange PC Monitor (CLI / HUD Daemon).

use orange_pc_monitor::config::AppConfig;
use orange_pc_monitor::core::TelemetryEngine;
use std::env;
use std::thread;
use std::time::Duration;

fn print_banner() {
    println!("\x1b[1;38;5;208m");
    println!("   🍊 ORANGE PC MONITOR — ULTRA LOW RESOURCE SYSTEM HUD");
    println!("   Status: Ativo | Alvo de Consumo: < 30 MB RAM | < 0.2% CPU");
    println!("\x1b[0m");
}

fn print_snapshot_cli(engine: &TelemetryEngine, mode: &str) {
    let snap = engine.snapshot().read().clone();

    // Limpa terminal para exibição de HUD em tempo real
    print!("\x1b[2J\x1b[H");

    println!("=================================================================");
    println!(" 🍊 ORANGE PC MONITOR — HUD COMPACTO");
    println!("=================================================================");

    let cpu = &snap.cpu;
    let mem = &snap.memory;
    let energy = &snap.energy;
    let net = &snap.network;
    let health = &snap.health;

    let total_gb = mem.total_bytes as f64 / 1_073_741_824.0;
    let used_gb = mem.used_bytes as f64 / 1_073_741_824.0;

    println!(
        " ⚡ CPU:   {:>5.1}% | {:>4} MHz | Temp: {:>5} | {}",
        cpu.total_usage_percent,
        cpu.current_frequency_mhz,
        cpu.package_temperature_c
            .map(|t| format!("{:.1}°C", t))
            .unwrap_or_else(|| "N/D".to_string()),
        cpu.brand
    );

    println!(
        " 🧠 RAM:   {:>5.1}% | {:.2} / {:.2} GB | Swap: {:.1}%",
        mem.usage_percent, used_gb, total_gb, mem.swap_percent
    );

    for (i, gpu) in snap.gpus.iter().enumerate() {
        let vram_used_mb = gpu.vram_used_bytes / 1_048_576;
        let vram_total_mb = gpu.vram_total_bytes / 1_048_576;
        println!(
            " 🎮 GPU{}:  {:>5.1}% | Temp: {:>5} | VRAM: {}/{} MB | {}",
            i,
            gpu.usage_percent,
            gpu.temperature_core_c
                .map(|t| format!("{:.1}°C", t))
                .unwrap_or_else(|| "N/D".to_string()),
            vram_used_mb,
            vram_total_mb,
            gpu.name
        );
    }

    let rx_mb = net.download_bytes_sec as f64 / 1_048_576.0;
    let tx_mb = net.upload_bytes_sec as f64 / 1_048_576.0;
    println!(
        " 🌐 REDE:  ↓ {:.2} MB/s | ↑ {:.2} MB/s ({})",
        rx_mb, tx_mb, net.active_interface
    );

    println!(
        " 🔋 ENERGIA: {:.1} W (Est.) | Acumulado: {:.3} Wh | Custo: R$ {:.4}",
        energy.system_estimated_watts,
        energy.cumulative_watt_hours,
        energy.cumulative_cost_brl
    );

    println!(
        " 🩺 SAÚDE:  {} (Score: {}/100)",
        health.category.label(),
        health.score
    );

    if mode == "expanded" || mode == "diag" {
        println!("\n------------------ DISCOS & ARMAZENAMENTO -----------------------");
        for d in &snap.disks {
            let total_gb = d.total_bytes as f64 / 1_073_741_824.0;
            let used_gb = d.used_bytes as f64 / 1_073_741_824.0;
            let disk_type = if d.is_nvme {
                "NVMe"
            } else if d.is_ssd {
                "SSD"
            } else {
                "HDD"
            };
            println!(
                " • [{}] {} ({:.1} GB / {:.1} GB - {:.1}%)",
                disk_type, d.mount_point, used_gb, total_gb, d.usage_percent
            );
        }

        println!("\n------------------ TOP CONSUMO DE PROCESSOS ---------------------");
        for (idx, p) in snap.top_processes.iter().take(5).enumerate() {
            let mem_mb = p.memory_bytes / 1_048_576;
            println!(
                " {}. [PID {:>5}] {:<22} | CPU: {:>5.1}% | RAM: {:>4} MB",
                idx + 1,
                p.pid,
                p.name,
                p.cpu_percent,
                mem_mb
            );
        }

        println!("\n------------------ FATORES DE DIAGNÓSTICO -----------------------");
        for factor in &health.factors {
            println!(" • {}", factor);
        }
    }

    println!("=================================================================");
    println!(" [Pressione Ctrl+C para encerrar o monitor nativo]");
}

fn main() {
    let args: Vec<String> = env::args().collect();

    if args.iter().any(|a| a == "--version" || a == "-v") {
        println!("orange-pc-monitor 0.1.0 (Orange Framework Native Core)");
        return;
    }

    print_banner();

    let config = AppConfig::load_or_default();
    let mut engine = TelemetryEngine::new(config);
    engine.start();

    // Aguarda primeiro ciclo de amostragem
    thread::sleep(Duration::from_millis(600));

    if args.iter().any(|a| a == "--json") {
        let snap = engine.snapshot().read().clone();
        println!(
            "{}",
            serde_json::to_string_pretty(&snap).unwrap_or_default()
        );
        return;
    }

    let mode = if args.iter().any(|a| a == "--diag") {
        "diag"
    } else if args.iter().any(|a| a == "--expanded") {
        "expanded"
    } else {
        "compact"
    };

    // Loop de exibição em tempo real do HUD no terminal
    let is_interactive = !args.iter().any(|a| a == "--once");
    if !is_interactive {
        print_snapshot_cli(&engine, mode);
        return;
    }

    loop {
        print_snapshot_cli(&engine, mode);
        thread::sleep(Duration::from_millis(1000));
    }
}

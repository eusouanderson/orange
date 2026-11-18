//! Monitoramento assíncrono dos processos com maior consumo de recursos.

use crate::core::snapshot::ProcessItem;
use sysinfo::{ProcessesToUpdate, System};

pub struct ProcessCollector;

impl Default for ProcessCollector {
    fn default() -> Self {
        Self::new()
    }
}

impl ProcessCollector {
    pub fn new() -> Self {
        Self
    }

    /// Amostra e retorna os principais processos ordenados por consumo de CPU e RAM.
    pub fn collect_top(&self, system: &mut System, limit: usize) -> Vec<ProcessItem> {
        system.refresh_processes(ProcessesToUpdate::All, true);

        let total_mem = system.total_memory();
        let mut processes: Vec<ProcessItem> = system
            .processes()
            .iter()
            .map(|(pid, proc)| {
                let mem = proc.memory();
                let mem_percent = if total_mem > 0 {
                    (mem as f32 / total_mem as f32) * 100.0
                } else {
                    0.0
                };

                ProcessItem {
                    pid: pid.as_u32(),
                    name: proc.name().to_string_lossy().to_string(),
                    cpu_percent: proc.cpu_usage(),
                    memory_bytes: mem,
                    memory_percent: mem_percent,
                    disk_read_bytes_sec: 0,
                    disk_write_bytes_sec: 0,
                    threads: 1,
                }
            })
            .collect();

        // Ordena pelos maiores consumidores de CPU + RAM
        processes.sort_by(|a, b| {
            let score_a = a.cpu_percent + (a.memory_percent * 2.0);
            let score_b = b.cpu_percent + (b.memory_percent * 2.0);
            score_b.partial_cmp(&score_a).unwrap_or(std::cmp::Ordering::Equal)
        });

        processes.truncate(limit);
        processes
    }
}

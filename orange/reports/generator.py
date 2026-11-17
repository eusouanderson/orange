"""Gerador de relatórios e métricas de build (JSON, HTML e Terminal)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from orange.models import BuildResult, OrangeConfig
from orange.platform.detector import PlatformInfo


class ReportGenerator:
    """Gera relatórios detalhados de compilação em formatos JSON, HTML e texto."""

    def __init__(self, config: OrangeConfig) -> None:
        self.config = config

    def to_dict(
        self, result: BuildResult, platform_info: PlatformInfo
    ) -> dict[str, Any]:
        """Converte o resultado do build em dicionário estruturado para serialização."""
        return {
            'project': self.config.project.name,
            'version': self.config.project.version,
            'status': 'success' if result.success else 'failed',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'platform': result.platform,
            'architecture': platform_info.architecture,
            'profile': result.profile,
            'build_time_seconds': round(result.duration_seconds, 3),
            'artifact': {
                'path': str(result.target_path)
                if result.target_path
                else None,
                'size_bytes': result.artifact_size,
                'size_mb': round(result.artifact_size / (1024 * 1024), 2)
                if result.artifact_size
                else 0.0,
            },
            'tools': {
                'compiler': result.compiler_used,
                'packager': result.packager_used,
                'optimizer': result.optimizer_used,
                'python_version': platform_info.python_version,
            },
            'cache': {
                'hit': result.cache_hit,
                'enabled': self.config.cache.enabled,
            },
            'steps': [
                {
                    'name': step.name,
                    'status': step.status,
                    'duration_seconds': round(step.duration_seconds, 3),
                    'details': step.details,
                    'artifact_size': step.artifact_size,
                }
                for step in result.steps
            ],
            'error': result.error_message,
        }

    def generate_json(
        self,
        result: BuildResult,
        platform_info: PlatformInfo,
        output_path: Path,
    ) -> Path:
        """Gera o arquivo de relatório em JSON."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        data = self.to_dict(result, platform_info)
        output_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8'
        )
        return output_path

    def generate_html(
        self,
        result: BuildResult,
        platform_info: PlatformInfo,
        output_path: Path,
    ) -> Path:
        """Gera o arquivo de relatório em HTML visual com dashboard e timeline."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        data = self.to_dict(result, platform_info)

        status_color = '#238636' if result.success else '#da3633'
        status_text = 'SUCESSO' if result.success else 'FALHA'

        steps_rows = ''
        for s in data['steps']:
            badge = (
                '✅'
                if s['status'] == 'success'
                else ('⏭️' if s['status'] == 'skipped' else '❌')
            )
            steps_rows += f"""
            <tr>
                <td>{badge} {s['name']}</td>
                <td>{s['status'].upper()}</td>
                <td>{s['duration_seconds']}s</td>
                <td><code>{s['details'] or '-'}</code></td>
            </tr>
            """

        html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Orange Build Report - {data['project']}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #0d1117; color: #c9d1d9; margin: 0; padding: 24px; }}
        .container {{ max-width: 900px; margin: 0 auto; background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 24px; }}
        h1 {{ margin-top: 0; display: flex; align-items: center; justify-content: space-between; color: #f0883e; }}
        .badge {{ background: {status_color}; color: #fff; padding: 4px 12px; border-radius: 12px; font-size: 14px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin: 20px 0; }}
        .card {{ background: #21262d; border: 1px solid #30363d; border-radius: 6px; padding: 12px 16px; }}
        .card-label {{ font-size: 12px; color: #8b949e; text-transform: uppercase; }}
        .card-value {{ font-size: 18px; font-weight: bold; margin-top: 4px; color: #f0f6fc; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 16px; }}
        th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid #30363d; font-size: 14px; }}
        th {{ background: #21262d; color: #8b949e; }}
        code {{ background: #0d1117; padding: 2px 6px; border-radius: 4px; font-size: 13px; color: #79c0ff; }}
        .footer {{ margin-top: 24px; font-size: 12px; color: #8b949e; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>
            <span>🍊 Orange Build Report: {data['project']} v{data['version']}</span>
            <span class="badge">{status_text}</span>
        </h1>
        <div class="grid">
            <div class="card">
                <div class="card-label">Tempo Total</div>
                <div class="card-value">{data['build_time_seconds']}s</div>
            </div>
            <div class="card">
                <div class="card-label">Tamanho do Artefato</div>
                <div class="card-value">{data['artifact']['size_mb']} MB</div>
            </div>
            <div class="card">
                <div class="card-label">Plataforma / Perfil</div>
                <div class="card-value">{data['platform']} ({data['profile']})</div>
            </div>
            <div class="card">
                <div class="card-label">Cache Hit</div>
                <div class="card-value">{'SIM' if data['cache']['hit'] else 'NÃO'}</div>
            </div>
        </div>

        <h3>Etapas da Compilação</h3>
        <table>
            <thead>
                <tr>
                    <th>Etapa</th>
                    <th>Status</th>
                    <th>Duração</th>
                    <th>Detalhes</th>
                </tr>
            </thead>
            <tbody>
                {steps_rows}
            </tbody>
        </table>

        <h3>Ferramentas Utilizadas</h3>
        <p>
            <b>Python:</b> {data['tools']['python_version']} |
            <b>Compilador C:</b> {data['tools']['compiler']} |
            <b>Empacotador:</b> {data['tools']['packager']} |
            <b>Otimizador:</b> {data['tools']['optimizer']}
        </p>

        {f'<div style="color: #ff7b72; margin-top: 16px;"><b>Erro:</b> {data["error"]}</div>' if data['error'] else ''}

        <div class="footer">Gerado automaticamente pelo Orange Framework em {data['timestamp']}</div>
    </div>
</body>
</html>
"""
        output_path.write_text(html_content, encoding='utf-8')
        return output_path

    def format_terminal(self, result: BuildResult) -> str:
        """Formata resumo amigável para exibição no terminal."""
        lines = [
            '\n' + '=' * 60,
            f' 🍊 Relatório de Build: {self.config.project.name} (v{self.config.project.version})',
            '=' * 60,
            f' Status:         {"✅ SUCESSO" if result.success else "❌ FALHA"}',
            f' Perfil:         {result.profile}',
            f' Plataforma:     {result.platform}',
            f' Tempo Total:    {round(result.duration_seconds, 2)}s',
        ]
        if result.target_path:
            lines.append(f' Executável:     {result.target_path}')
            lines.append(
                f' Tamanho:        {round(result.artifact_size / (1024 * 1024), 2)} MB ({result.artifact_size} bytes)'
            )
        if result.cache_hit:
            lines.append(' Cache:          ✅ Reutilizado (Hit)')

        lines.append('-' * 60)
        lines.append(' Etapas executadas:')
        for s in result.steps:
            icon = (
                '✅'
                if s.status == 'success'
                else ('⏭️' if s.status == 'skipped' else '❌')
            )
            lines.append(
                f'   {icon} {s.name:<25} {round(s.duration_seconds, 3):>7.3f}s   {s.details}'
            )
        lines.append('=' * 60 + '\n')
        return '\n'.join(lines)

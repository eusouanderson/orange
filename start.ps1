# Detectar sistema operacional (Windows)
Write-Host "🟦 Windows detectado"

# Caminhos do projeto
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectPath = Join-Path $ScriptDir "src"
$AppPath = Join-Path $ProjectPath "core\main.py"

# Variáveis de ambiente
$env:PYTHONPATH = "$ProjectPath;$env:PYTHONPATH"
$env:ENV = "development"
$env:DEV_ENV = "true"

Write-Host "PYTHONPATH: $env:PYTHONPATH"

# Verificar se o arquivo existe
if (!(Test-Path $AppPath)) {
    Write-Host "❌ Arquivo não encontrado: $AppPath"
    exit 1
}

# Função para executar o app
function Executar-App {
    Write-Host "🚀 Executando o aplicativo..."
    poetry run python "$AppPath"
    return $LASTEXITCODE
}

# Executar
Executar-App
$Status = $LASTEXITCODE

# Final
if ($Status -ne 0) {
    Write-Host "💥 Falha na execução. Código de saída: $Status"
    exit $Status
}

exit 0

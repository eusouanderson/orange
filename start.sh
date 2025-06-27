#!/bin/bash

# Detectar o sistema operacional
OS=$(uname -s)

# Caminhos do projeto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_PATH="$SCRIPT_DIR/src"
APP_PATH="$PROJECT_PATH/core/main.py"

# PYTHONPATH comum
export PYTHONPATH="$PYTHONPATH:$PROJECT_PATH"

# Configurações específicas por OS
if [[ "$OS" == "Linux" ]]; then
    echo "🟢 Linux detectado"
    export QT_QPA_PLATFORM=xcb
elif [[ "$OS" == MINGW* || "$OS" == CYGWIN* || "$OS" == "Darwin" ]]; then
    echo "🟦 Windows (Git Bash/Cygwin) detectado"
    export ENV=development
    export DEV_ENV=true
else
    echo "⚠️ Sistema desconhecido: $OS"
fi

echo "PYTHONPATH: $PYTHONPATH"

# Função principal
executar_app() {
    echo "🚀 Executando o aplicativo..."
    poetry run python "$APP_PATH"
    return $?
}

# Verificação do arquivo
if [ ! -f "$APP_PATH" ]; then
    echo "❌ Arquivo não encontrado: $APP_PATH"
    exit 1
fi

executar_app
STATUS=$?

# Tratamento para Linux (Qt)
if [ "$STATUS" -ne 0 ] && [ "$OS" == "Linux" ]; then
    echo "⚠️ Execução falhou. Verificando libxcb-cursor0..."

    if ! dpkg -s libxcb-cursor0 >/dev/null 2>&1; then
        echo "📦 Instalando libxcb-cursor0..."
        sudo apt update && sudo apt install -y libxcb-cursor0
    else
        echo "✅ libxcb-cursor0 já instalado."
    fi

    echo "🔁 Tentando novamente..."
    executar_app
    STATUS=$?
fi

# Final
if [ "$STATUS" -ne 0 ]; then
    echo "💥 Falha na execução. Código de saída: $STATUS"
    exit $STATUS
fi

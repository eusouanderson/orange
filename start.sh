#!/bin/bash

# Detectar o sistema operacional
OS=$(uname -s)

# Obter o diretório absoluto do script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_PATH="$SCRIPT_DIR/src"
APP_PATH="$PROJECT_PATH/core/main.py"

# Configuração comum
export PYTHONPATH="$PYTHONPATH:$PROJECT_PATH"

# Configurações específicas para Linux
if [ "$OS" == "Linux" ]; then
    echo "Detectado: Linux"
    export QT_QPA_PLATFORM=xcb
    echo "PYTHONPATH configurado para: $PYTHONPATH"
    echo "Variáveis de ambiente configuradas para Linux."
fi

# Configurações específicas para Windows
if [[ "$OS" == MINGW* || "$OS" == CYGWIN* || "$OS" == "Darwin" ]]; then
    echo "Detectado: Windows"
    export ENV=development
    export DEV_ENV=true
    echo "PYTHONPATH configurado para: $PYTHONPATH"
    echo "Variáveis de ambiente configuradas para Windows."
fi

# Função para executar o app
executar_app() {
    echo "Executando o aplicativo..."
    poetry run python "$APP_PATH"
    return $?
}

# Verificar se o arquivo main.py existe antes de executar
if [ ! -f "$APP_PATH" ]; then
    echo "Erro: O arquivo main.py não foi encontrado no caminho especificado: $APP_PATH"
    exit 1
fi

# Primeira tentativa de execução
executar_app
STATUS=$?

# Se falhou e estamos no Linux, tentar instalar dependência e executar novamente
if [ "$STATUS" -ne 0 ] && [ "$OS" == "Linux" ]; then
    echo "A execução falhou. Verificando dependência 'libxcb-cursor0'..."

    if ! dpkg -s libxcb-cursor0 >/dev/null 2>&1; then
        echo "Tentando instalar libxcb-cursor0..."
        if command -v sudo >/dev/null 2>&1; then
            sudo apt update && sudo apt install -y libxcb-cursor0
        else
            echo "Erro: 'sudo' não disponível. Instale manualmente o pacote: libxcb-cursor0"
            exit 1
        fi
    else
        echo "'libxcb-cursor0' já está instalado. Pode haver outro problema com o Qt."
    fi

    echo "Tentando executar novamente..."
    executar_app
    STATUS=$?
fi

# Verifica se a execução ainda falha
if [ "$STATUS" -ne 0 ]; then
    echo "Erro: A aplicação falhou mesmo após tentativa de correção."
    exit $STATUS
fi

#!/bin/bash

# Detectar o sistema operacional
OS=$(uname -s)

# Configurações específicas para Linux
if [ "$OS" == "Linux" ]; then
    echo "Detectado: Linux"
    export PYTHONPATH=$PYTHONPATH:/home/anderson/orange/src  # Corrigir o caminho
    export QT_QPA_PLATFORM=xcb
    echo "Variáveis de ambiente configuradas para Linux."
fi

# Configurações específicas para Windows
if [[ "$OS" == "MINGW"* || "$OS" == "CYGWIN"* || "$OS" == "Darwin" ]]; then
    echo "Detectado: Windows"
    
    # Definir o caminho absoluto do projeto no Windows, corrigindo para barras invertidas
    PROJECT_PATH="C:\\Users\\Anderson\\Documents\\orange\\src"
    
    # Adicionar o caminho do projeto ao PYTHONPATH (sem o : inicial)
    export PYTHONPATH=$PROJECT_PATH
    
    # Definir o ambiente de desenvolvimento    
    export ENV=development
    
    # Definir o ambiente de desenvolvimento
    export DEV_ENV=true
    # Exibir PYTHONPATH para garantir que o caminho foi configurado corretamente
    echo "PYTHONPATH configurado para: $PYTHONPATH"

    echo "Variáveis de ambiente configuradas para Windows."
fi

# Corrigir caminho do script para execução em ambas plataformas
if [ "$OS" == "Linux" ]; then
    # No Linux, o script deve procurar no caminho correto
    APP_PATH="/home/anderson/orange/src/core/main.py"
elif [[ "$OS" == "MINGW"* || "$OS" == "CYGWIN"* || "$OS" == "Darwin" ]]; then
    # No Windows, o script deve procurar no caminho correto
    APP_PATH="C:\\Users\\Anderson\\Documents\\orange\\src\\core\\main.py"
fi

# Verificar se o arquivo main.py existe antes de executar
if [ -f "$APP_PATH" ]; then
    echo "Executando o aplicativo..."
    poetry run python "$APP_PATH"
else
    echo "Erro: O arquivo main.py não foi encontrado no caminho especificado: $APP_PATH"
    exit 1
fi

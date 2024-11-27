#!/bin/bash

# Detectar o sistema operacional
OS=$(uname -s)

# Configurações específicas para Linux
if [ "$OS" == "Linux" ]; then
    echo "Detectado: Linux"
    export PYTHONPATH=$PYTHONPATH:/home/anderson/projects/orange/src
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
    export DEV_ENV=true
    # Exibir PYTHONPATH para garantir que o caminho foi configurado corretamente
    echo "PYTHONPATH configurado para: $PYTHONPATH"

    echo "Variáveis de ambiente configuradas para Windows."
fi

# Executar o aplicativo com Poetry
echo "Executando o aplicativo..."
poetry run python src/core/main.py

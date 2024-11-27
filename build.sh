#!/bin/bash

# Verifica o sistema operacional
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM="linux"
elif [[ "$OSTYPE" == "cygwin" ]]; then
    PLATFORM="windows"
elif [[ "$OSTYPE" == "msys" ]]; then
    PLATFORM="windows"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="mac"
else
    echo "Unsupported OS type"
    exit 1
fi

# Definir variáveis de ambiente dependendo do sistema operacional
if [[ "$PLATFORM" == "windows" ]]; then
    export PROJECT_PATH="C:\\Users\\Anderson\\Documents\\orange\\src"
elif [[ "$PLATFORM" == "linux" ]]; then
    export PROJECT_PATH="/home/anderson/projects/orange/src"
fi

# Executa o script de build com a plataforma e a versão do release
echo "Executando o build para a plataforma $PLATFORM..."
poetry run python compile/build.py $PLATFORM v0.1.1

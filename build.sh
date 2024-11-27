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

# Executa o script Python com a plataforma como argumento
poetry run python src/build/build.py $PLATFORM v0.1.1
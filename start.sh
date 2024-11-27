#!/bin/bash

# Defina a variável de ambiente necessária para o Qt
export PYTHONPATH=$PYTHONPATH:/home/anderson/projects/orange/src
export QT_QPA_PLATFORM=xcb

# Execute o aplicativo com o Poetry
poetry run python src/core/main.py

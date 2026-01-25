#!/bin/bash

export ENV=production

show_help() {
    echo "Uso: ./build.sh [opções]"
    echo "Opções:"
    echo "  --compile-all      Compila todos os arquivos Python para Cython"
    echo "  --help             Exibe esta mensagem de ajuda"
}

# Detecta plataforma e define comando Python
case "$OSTYPE" in
  linux*)   PLATFORM="linux"; PYTHON_CMD="python3" ;;
  darwin*)  PLATFORM="mac"; PYTHON_CMD="python3" ;;
  cygwin*|msys*) PLATFORM="windows"; PYTHON_CMD="python" ;;
  *)        echo "Unsupported OS type"; exit 1 ;;
esac

# Caminho do projeto automaticamente com base no local do script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_PATH="$SCRIPT_DIR/src"
export PROJECT_PATH

# Extrai repositório e flags
REPO=""
COMPILE_ALL=""

for arg in "$@"
do
    case $arg in
        --compile-all)
            COMPILE_ALL="--compile-all"
            ;;
        --help)
            show_help
            exit 0
            ;;
        --no-upload)
            # ignorado, suportado para compatibilidade
            ;;
        *)
            # Assume que é o repositório (ex: eusouanderson/orange)
            if [[ "$arg" =~ ^[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$ ]]; then
                REPO="$arg"
            else
                echo "Opção desconhecida: $arg"
                echo "Use --help para mais informações."
                exit 1
            fi
            ;;
    esac
done

# Usa repositório padrão se não fornecido
REPO="${REPO:-eusouanderson/orange}"

# Usa o Poetry para extrair a versão corretamente
VERSION=$(poetry run python -c "from pathlib import Path; import tomllib if hasattr(__import__('builtins'), '__tomllib') else __import__('tomli'); import sys; data = tomllib.loads(Path('pyproject.toml').read_text()) if hasattr(__import__('builtins'), '__tomllib') else __import__('tomli').loads(Path('pyproject.toml').read_text()); print(data['tool']['poetry']['version'])" 2>/dev/null || poetry version -s)


if [ -z "$VERSION" ]; then
    echo "Erro: Não foi possível obter a versão do pyproject.toml"
    exit 1
fi

echo "Versão atual: $VERSION"

# Incrementa versão (patch)
IFS='.' read -r major minor patch <<< "$VERSION"
patch=$((patch + 1))
NEW_VERSION="$major.$minor.$patch"

# Atualiza o pyproject.toml com nova versão
python3 -c "
from pathlib import Path
import tomllib if hasattr(__import__('builtins'), '__tomllib') else __import__('tomli')
try:
    data = tomllib.loads(Path('pyproject.toml').read_text())
except:
    data = __import__('tomli').loads(Path('pyproject.toml').read_text())
data['tool']['poetry']['version'] = '$NEW_VERSION'
import toml
with open('pyproject.toml', 'w') as f:
    toml.dump(data, f)
" 2>/dev/null || poetry version $NEW_VERSION


echo "Nova versão: $NEW_VERSION"

# Build do projeto
echo "Executando o build para a plataforma $PLATFORM com versão $NEW_VERSION..."
if [ -n "$COMPILE_ALL" ]; then
    poetry run $PYTHON_CMD compile/build.py $PLATFORM v$NEW_VERSION $REPO $COMPILE_ALL
else
    poetry run $PYTHON_CMD compile/build.py $PLATFORM v$NEW_VERSION $REPO
fi

# Criar release no GitHub
EXE_NAME="Orange"
if [ "$PLATFORM" = "windows" ]; then
    EXE_NAME="Orange.exe"
fi

echo "Criando a release no GitHub com a versão $NEW_VERSION..."
gh release create v$NEW_VERSION dist/Orange-v$NEW_VERSION.zip --repo $REPO --title "Orange $NEW_VERSION" --notes "Release Orange $NEW_VERSION Platform: $PLATFORM"

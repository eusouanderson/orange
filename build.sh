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

# Lida com argumentos
for arg in "$@"
do
    case $arg in
        --compile-all)
            echo "Compilando todos os arquivos Python para Cython..."
            poetry run $PYTHON_CMD compile/build.py $PLATFORM v0.1.1 eusouanderson/orange_calculator --compile-all
            exit 0
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo "Opção desconhecida: $arg"
            echo "Use --help para mais informações."
            exit 1
            ;;
    esac
done

# Usa o Poetry para extrair a versão corretamente
VERSION='3.0.0' || $(poetry run $PYTHON_CMD -c "import toml; print(toml.load('pyproject.toml')['tool']['poetry']['version'])")

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
poetry run $PYTHON_CMD -c "
import toml
with open('pyproject.toml', 'r') as f:
    data = toml.load(f)
data['tool']['poetry']['version'] = '$NEW_VERSION'
with open('pyproject.toml', 'w') as f:
    toml.dump(data, f)
"

echo "Nova versão: $NEW_VERSION"

# Build do projeto
echo "Executando o build para a plataforma $PLATFORM com versão $NEW_VERSION..."
poetry run $PYTHON_CMD compile/build.py $PLATFORM v$NEW_VERSION

# Criar release no GitHub
echo "Criando a release no GitHub com a versão $NEW_VERSION..."
gh release create v$NEW_VERSION dist/Orange.exe --repo eusouanderson/orange_calculator --title "Orange $NEW_VERSION" --notes "Release Orange $NEW_VERSION Platform: $PLATFORM"

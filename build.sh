#!/bin/bash

# Exporta o ambiente
export ENV=production

# Função para exibir ajuda
show_help() {
    echo "Uso: ./build.sh [opções]"
    echo "Opções:"
    echo "  --compile-all      Compila todos os arquivos Python para Cython"
    echo "  --help             Exibe esta mensagem de ajuda"
}

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

# Processa argumentos
for arg in "$@"
do
    case $arg in
        --compile-all)
            echo "Compilando todos os arquivos Python para Cython..."
            poetry run python compile/build.py $PLATFORM v0.1.1 eusouanderson/orange_calculatore --compile-all
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

# Define o caminho do projeto com base no sistema operacional
if [[ "$PLATFORM" == "windows" ]]; then
    export PROJECT_PATH="C:\\Users\\Anderson\\Documents\\orange\\src"
elif [[ "$PLATFORM" == "linux" ]]; then
    export PROJECT_PATH="/home/anderson/projects/orange/src"
fi

# Instala a biblioteca toml
pip install toml

# Obtém a versão atual do pyproject.toml
VERSION=$(python -c "import toml; version = toml.load('pyproject.toml')['tool']['poetry']['version']; print(version)")

if [ -z "$VERSION" ]; then
    echo "Erro: Não foi possível obter a versão do pyproject.toml"
    exit 1
fi

# Incrementa o número da versão
IFS='.' read -r major minor patch <<< "$VERSION"
patch=$((patch + 1))
NEW_VERSION="$major.$minor.$patch"

python -c "import toml; data = toml.load('pyproject.toml'); data['tool']['poetry']['version'] = '$NEW_VERSION'; toml.dump(data, open('pyproject.toml', 'w'))"

echo "Nova versão: $NEW_VERSION"

# Executa o build
echo "Executando o build para a plataforma $PLATFORM com versão $NEW_VERSION..."
poetry run python compile/build.py $PLATFORM v$NEW_VERSION

# Cria a release no GitHub
echo "Criando a release no GitHub com a versão $NEW_VERSION..."
gh release create v$NEW_VERSION dist/Orange.exe --repo eusouanderson/orange_calculator --title "Orange $NEW_VERSION" --notes "Release Orange $NEW_VERSION Platform: $PLATFORM"

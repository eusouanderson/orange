#!/bin/bash


export ENV=production


show_help() {
    echo "Uso: ./build.sh [opções]"
    echo "Opções:"
    echo "  --compile-all      Compila todos os arquivos Python para Cython"
    echo "  --help             Exibe esta mensagem de ajuda"
}


if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM="linux"
    PYTHON_CMD="python3" 
elif [[ "$OSTYPE" == "cygwin" || "$OSTYPE" == "msys" ]]; then
    PLATFORM="windows"
    PYTHON_CMD="python" 
elif [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="mac"
    PYTHON_CMD="python3"  
else
    echo "Unsupported OS type"
    exit 1
fi


for arg in "$@"
do
    case $arg in
        --compile-all)
            echo "Compilando todos os arquivos Python para Cython..."
            poetry run $PYTHON_CMD compile/build.py $PLATFORM v0.1.1 eusouanderson/orange_calculatore --compile-all
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


if [[ "$PLATFORM" == "windows" ]]; then
    export PROJECT_PATH="C:\\Users\\Anderson\\Documents\\orange\\src"
elif [[ "$PLATFORM" == "linux" || "$PLATFORM" == "mac" ]]; then
    export PROJECT_PATH="/home/anderson/projects/orange/src"
fi


VERSION=$($PYTHON_CMD -c "import toml; print(toml.load('pyproject.toml')['tool']['poetry']['version'])")


if [ -z "$VERSION" ]; then
    echo "Erro: Não foi possível obter a versão do pyproject.toml"
    exit 1
fi

echo "Versão: $VERSION"


IFS='.' read -r major minor patch <<< "$VERSION"
patch=$((patch + 1))
NEW_VERSION="$major.$minor.$patch"


$PYTHON_CMD -c "import toml; data = toml.load('pyproject.toml'); data['tool']['poetry']['version'] = '$NEW_VERSION'; toml.dump(data, open('pyproject.toml', 'w'))"

echo "Nova versão: $NEW_VERSION"


echo "Executando o build para a plataforma $PLATFORM com versão $NEW_VERSION..."
poetry run $PYTHON_CMD compile/build.py $PLATFORM v$NEW_VERSION


echo "Criando a release no GitHub com a versão $NEW_VERSION..."
gh release create v$NEW_VERSION dist/Orange.exe --repo eusouanderson/orange_calculator --title "Orange $NEW_VERSION" --notes "Release Orange $NEW_VERSION Platform: $PLATFORM"

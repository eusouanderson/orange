#!/bin/bash


export ENV=production



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

poetry run python src/compile/build.py $PLATFORM v0.1.1 eusouanderson/orange_calculatore

# REPOSITORIO CALCULADORA /eusouanderson/orange_calculator




if [[ "$PLATFORM" == "windows" ]]; then
    export PROJECT_PATH="C:\\Users\\Anderson\\Documents\\orange\\src"
elif [[ "$PLATFORM" == "linux" ]]; then
    export PROJECT_PATH="/home/anderson/projects/orange/src"
fi


pip install toml


VERSION=$(python -c "import toml; version = toml.load('pyproject.toml')['tool']['poetry']['version']; print(version)")


if [ -z "$VERSION" ]; then
    echo "Erro: Não foi possível obter a versão do pyproject.toml"
    exit 1
fi


IFS='.' read -r major minor patch <<< "$VERSION"
patch=$((patch + 1))
NEW_VERSION="$major.$minor.$patch"


python -c "import toml; data = toml.load('pyproject.toml'); data['tool']['poetry']['version'] = '$NEW_VERSION'; toml.dump(data, open('pyproject.toml', 'w'))"

echo "Nova versão: $NEW_VERSION"


echo "Executando o build para a plataforma $PLATFORM com versão $NEW_VERSION..."
poetry run python compile/build.py $PLATFORM v$NEW_VERSION


echo "Criando a release no GitHub com a versão $NEW_VERSION..."
gh release create v$NEW_VERSION dist/Orange.exe --repo eusouanderson/orange --title "Orange $NEW_VERSION" --notes "Release Orange $NEW_VERSION Platform: $PLATFORM"

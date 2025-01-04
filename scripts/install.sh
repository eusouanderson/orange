#!/bin/bash

show_help() {
    echo "Uso: ./install.sh [opções]"
    echo "Opções:"
    echo "  --help                Exibe esta mensagem de ajuda"
    echo "  --install-essentials  Instala as dependências build-essential, python3-dev e portaudio19-dev"
    echo "  --install-gh          Instala o GitHub CLI (gh)"
    echo "  --create-dist         Cria o diretório dist, se não existir"
    echo "  --install-poetry      Instala o Poetry, se não estiver instalado"
}

install_gh() {
    echo "Instalando o GitHub CLI..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt update
        sudo apt install -y gh
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install gh
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        echo "Instalação do GitHub CLI no Windows não suportada diretamente. Instale manualmente ou use o WSL."
        exit 1
    fi

    if ! command -v gh &> /dev/null
    then
        echo "Erro: O GitHub CLI não foi instalado corretamente."
        exit 1
    fi
    echo "GitHub CLI instalado com sucesso!"
}

install_essentials() {
    echo "Instalando as dependências essenciais..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt update
        sudo apt install -y build-essential python3-dev portaudio19-dev
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install portaudio
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        echo "Instalação das dependências essenciais no Windows não suportada diretamente. Instale manualmente ou use o WSL."
        exit 1
    fi

    echo "Dependências instaladas com sucesso!"
}

create_dist() {
    echo "Verificando se o diretório dist existe..."
    mkdir -p ../dist
    echo "Diretório dist criado (se não existia)."
}

install_poetry() {
    echo "Verificando se o Poetry está instalado..."
    if ! command -v poetry &> /dev/null
    then
        echo "Poetry não encontrado. Instalando o Poetry..."
        if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* ]]; then
            curl -sSL https://install.python-poetry.org | python3 -
        elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
            echo "Instale o Poetry manualmente ou use o WSL."
            exit 1
        fi
        if ! command -v poetry &> /dev/null
        then
            echo "Erro: O Poetry não foi instalado corretamente."
            exit 1
        fi
        echo "Poetry instalado com sucesso!"
    else
        echo "Poetry já está instalado."
    fi
}

install_project() {
    if command -v poetry &> /dev/null; then
        echo "Poetry detectado. Instalando dependências com Poetry..."
        poetry install  
    elif command -v pip &> /dev/null; then
        echo "pip detectado. Instalando dependências com pip..."
        pip install -r requirements.txt  
    else
        echo "Nem Poetry nem pip encontrados. Instalando o Poetry..."
        install_poetry
        poetry install  
    fi
}

activate_poetry_env() {
    echo "Ativando o ambiente virtual do Poetry..."
    poetry shell
}

for arg in "$@"
do
    case $arg in
        --help)
            show_help
            exit 0
            ;;
        --install-essentials)
            install_essentials
            exit 0
            ;;
        --install-gh)
            install_gh
            exit 0
            ;;
        --create-dist)
            create_dist
            exit 0
            ;;
        --install-poetry)
            install_poetry
            exit 0
            ;;
        *)
            echo "Opção desconhecida: $arg"
            echo "Use --help para mais informações."
            exit 1
            ;;
    esac
done

echo "Verificando se o diretório dist existe..."
create_dist

echo "Verificando se o GitHub CLI (gh) está instalado..."
if ! command -v gh &> /dev/null
then
    echo "GitHub CLI não encontrado. Instalando..."
    install_gh
else
    echo "GitHub CLI já está instalado."
fi

echo "Verificando se o Poetry está instalado..."
install_poetry

echo "Instalando o projeto..."
install_project 

echo "Verificando se o ambiente virtual do Poetry está ativo..."
activate_poetry_env

echo "Instalando as dependências essenciais..."
install_essentials

echo "Todos os pré-requisitos estão configurados. Agora você pode ir até a raiz e executar o ./start.sh."

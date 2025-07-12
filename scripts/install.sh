#!/bin/bash

# Flags para execução condicional
INSTALL_GH=false
INSTALL_ESSENTIALS=false
CREATE_DIST=false
INSTALL_POETRY=false
SHOW_HELP=false

show_help() {
    echo "Uso: ./install.sh [opções]"
    echo "Opções:"
    echo "  --help                Exibe esta mensagem de ajuda"
    echo "  --install-essentials  Instala build-essential, python3-dev e portaudio19-dev"
    echo "  --install-gh          Instala o GitHub CLI (gh)"
    echo "  --create-dist         Cria o diretório dist, se não existir"
    echo "  --install-poetry      Instala o Poetry, se necessário"
}

install_gh() {
    echo "Instalando o GitHub CLI..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt update
        sudo apt install -y gh
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install gh
    else
        echo "Instalação do GitHub CLI no seu sistema requer instalação manual."
        return 1
    fi
    command -v gh >/dev/null && echo "GitHub CLI instalado com sucesso!"
}

install_essentials() {
    echo "Instalando as dependências essenciais..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt update
        sudo apt install -y build-essential python3-dev portaudio19-dev
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install portaudio
    else
        echo "Instalação automática não suportada neste sistema."
        return 1
    fi
}

create_dist() {
    echo "Criando diretório dist (se necessário)..."
    mkdir -p ../dist
}

install_poetry() {
    echo "Verificando o Poetry..."
    if ! command -v poetry &> /dev/null; then
        echo "Poetry não encontrado. Instalando..."
        curl -sSL https://install.python-poetry.org | python3 -
        export PATH="$HOME/.local/bin:$PATH"
    fi
    command -v poetry >/dev/null && echo "Poetry instalado com sucesso!"
}

install_project() {
    echo "Instalando dependências do projeto com Poetry..."
    poetry install
}

activate_poetry_env() {
    echo "Ativando ambiente virtual do Poetry..."
    poetry shell
}

# Parse dos argumentos
for arg in "$@"; do
    case $arg in
        --help) SHOW_HELP=true ;;
        --install-essentials) INSTALL_ESSENTIALS=true ;;
        --install-gh) INSTALL_GH=true ;;
        --create-dist) CREATE_DIST=true ;;
        --install-poetry) INSTALL_POETRY=true ;;
        *) echo "Opção desconhecida: $arg"; SHOW_HELP=true ;;
    esac
done

# Execução baseada nos argumentos
if [ "$SHOW_HELP" = true ]; then
    show_help
    exit 0
fi

# Execução condicional
[ "$CREATE_DIST" = true ] && create_dist
[ "$INSTALL_GH" = true ] && install_gh
[ "$INSTALL_POETRY" = true ] && install_poetry
[ "$INSTALL_ESSENTIALS" = true ] && install_essentials

# Execução padrão se nenhum argumento for passado
if [ "$#" -eq 0 ]; then
    create_dist
    install_gh
    install_poetry
    install_project
    install_essentials
    activate_poetry_env
    echo "Tudo pronto. Você pode agora executar: ./start.sh"
fi

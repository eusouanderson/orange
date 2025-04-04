# Makefile para configurar e rodar a aplicação

OS := $(shell uname -s)

# Caminho do projeto
PROJECT_PATH := $(if $(findstring Linux,$(OS)), /home/anderson/projects/orange/src, C:\\Users\\Anderson\\Documents\\orange\\src)

start:
	# Configurações de variáveis de ambiente específicas
	ifeq ($(OS),Linux)
		@echo "Configurando ambiente para Linux..."
		export PYTHONPATH := $(PYTHONPATH):/home/anderson/projects/orange/src
		export QT_QPA_PLATFORM := xcb
		@echo "Variáveis de ambiente configuradas para Linux."
	endif

	ifeq ($(findstring MINGW,$(OS)),MINGW)
		@echo "Configurando ambiente para Windows..."
		export PYTHONPATH := $(PROJECT_PATH)
		export ENV := development
		export DEV_ENV := true
		@echo "Variáveis de ambiente configuradas para Windows."
	endif

	# Executa o aplicativo
	@echo "Executando o aplicativo..."
	poetry run python src/core/main.py

build:
	#!/bin/bash

	# Definir variável de ambiente
	export ENV=production

	# Verificar o sistema operacional
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
	poetry run python src/compile/build.py $PLATFORM v0.1.1

	# Definir variáveis de ambiente dependendo do sistema operacional
	if [[ "$PLATFORM" == "windows" ]]; then
		export PROJECT_PATH="C:\\Users\\Anderson\\Documents\\orange\\src"
	elif [[ "$PLATFORM" == "linux" ]]; then
		export PROJECT_PATH="/home/anderson/projects/orange/src"
	fi

	# Instalar o módulo toml (se não estiver instalado)
	pip install toml

	# Pega a versão do pyproject.toml
	VERSION=$(python -c "import toml; version = toml.load('pyproject.toml')['tool']['poetry']['version']; print(version)")

	# Verifica se a versão foi encontrada
	if [ -z "$VERSION" ]; then
		echo "Erro: Não foi possível obter a versão do pyproject.toml"
		exit 1
	fi

	# Incrementar o número de patch da versão
	IFS='.' read -r major minor patch <<< "$VERSION"
	patch=$((patch + 1))
	NEW_VERSION="$major.$minor.$patch"

	# Atualiza o pyproject.toml com a nova versão
	python -c "import toml; data = toml.load('pyproject.toml'); data['tool']['poetry']['version'] = '$NEW_VERSION'; toml.dump(data, open('pyproject.toml', 'w'))"

	@echo "Nova versão: $NEW_VERSION"

	# Executa o script de build com a plataforma e a nova versão
	@echo "Executando o build para a plataforma $PLATFORM com versão $NEW_VERSION..."
	poetry run python compile/build.py $PLATFORM v$NEW_VERSION

	# Subir a release no GitHub com a nova tag
	@echo "Criando a release no GitHub com a versão $NEW_VERSION..."
	gh release create v$NEW_VERSION dist/Orange.exe --repo eusouanderson/orange --title "Orange $NEW_VERSION" --notes "Release Orange $NEW_VERSION Platform: $PLATFORM"

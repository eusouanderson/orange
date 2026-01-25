# Makefile para configurar e rodar a aplicação

OS := $(shell uname -s)

.PHONY: build build-local start test watch

# Valores padrão podem ser sobrescritos na linha de comando, ex:
# make build TAG=v1.2.3 FLAGS="--compile-all"
TAG ?= v$(shell poetry version -s)
PLATFORM ?= linux
FLAGS ?= --compile-all --no-upload
REPO ?= eusouanderson/orange

build:
	@echo "Construindo $(TAG) para $(PLATFORM) (flags: $(FLAGS))..."
	poetry run python compile/build.py $(PLATFORM) $(TAG) $(REPO) $(FLAGS)

build-local: build

start:
	@echo "Executando o aplicativo..."
	QT_QPA_PLATFORM=xcb PYTHONPATH=$(PWD)/src poetry run python src/core/main.py

watch:
	@echo "Iniciando watch mode (recarrega ao salvar arquivos Python)..."
	PYTHONPATH=$(PWD)/src poetry run python scripts/watch.py


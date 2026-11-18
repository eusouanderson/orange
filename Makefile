# Makefile para configurar e rodar a aplicação

OS := $(shell uname -s)

.DEFAULT_GOAL := help
.PHONY: help build build-local start test test-framework test-app test-cov test-performance test-fast test-core watch hooks verify lint format pc-monitor-build pc-monitor-test pc-monitor-benchmark pc-monitor-run

help:
	@echo "Orange Framework - Comandos disponíveis:"
	@echo "  make help                 Exibe esta mensagem de ajuda"
	@echo "  make hooks                Configura e ativa os hooks do Husky no Git"
	@echo "  make verify               Executa a verificação completa de pré-envio"
	@echo "  make lint                 Executa linter e formatação com Ruff"
	@echo "  make pc-monitor-build     Compila o binário nativo do Orange PC Monitor (Rust)"
	@echo "  make pc-monitor-test      Executa os testes nativos do PC Monitor"
	@echo "  make pc-monitor-benchmark Executa o benchmark de consumo extremo de RAM/CPU"
	@echo "  make pc-monitor-run       Executa o HUD desktop flutuante"
	@echo "  make start                Executa o aplicativo em modo dev"
	@echo "  make build                Compila e gera executável"
	@echo "  make test                 Executa todos os testes"
	@echo "  make test-core            Executa testes dos módulos do Orange Core"
	@echo "  make test-fast            Executa testes rápidos"
	@echo "  make watch                Inicia watch mode"

CARGO ?= $(shell which cargo 2>/dev/null || echo $(HOME)/.cargo/bin/cargo)

pc-monitor-build:
	@echo "Compilando Orange PC Monitor em modo release..."
	@cd pc-monitor && $(CARGO) build --release
	@mkdir -p dist
	@cp pc-monitor/target/release/orange-pc-monitor dist/
	@echo "✅ Binário pronto em dist/orange-pc-monitor"

pc-monitor-test:
	@echo "Executando testes unitários nativos do PC Monitor..."
	@cd pc-monitor && $(CARGO) test
	@poetry run pytest tests/pc_monitor/
	@echo "✅ Todos os testes do PC Monitor passaram!"

pc-monitor-benchmark:
	@cd pc-monitor && $(CARGO) run --release -- --benchmark 5

pc-monitor-run:
	@./dist/orange-pc-monitor

hooks:
	@echo "Configurando hooks do Husky no Git..."
	git config core.hooksPath .husky
	chmod +x .husky/pre-commit .husky/pre-push .husky/_/husky.sh
	@echo "✅ Hooks do Husky ativados com sucesso!"

verify:
	@python3 scripts/verify_repo.py

lint:
	@poetry run ruff check --fix
	@poetry run ruff format

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

test:
	@echo "Rodando TODOS os testes (framework + application)..."
	poetry run pytest

test-fast:
	@echo "Rodando testes rápidos (sem benchmarks longos)..."
	poetry run pytest -k "not test_performance"

test-core:
	@echo "Rodando testes dos módulos do Orange Core (config, compiler, builder, cache, cli)..."
	poetry run pytest tests/builder/ tests/cache/ tests/cli/ tests/compiler/ tests/config/ tests/platform/ tests/plugins/ tests/reports/

test-framework:
	@echo "Rodando testes do Framework (build, watch, compilação)..."
	poetry run pytest tests/framework/

test-app:
	@echo "Rodando testes da Aplicação (Calc3D)..."
	poetry run pytest tests/application/

test-cov:
	@echo "Rodando testes com cobertura detalhada..."
	poetry run pytest --cov=src --cov=scripts --cov-report=term-missing

test-performance:
	@echo "Rodando benchmarks de performance..."
	poetry run pytest tests/application/test_performance.py --benchmark-only

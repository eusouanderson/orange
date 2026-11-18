# ==============================================================================
# Multi-stage Dockerfile para Orange Framework
# ==============================================================================
# Estágio 1: Builder - Ambiente completo com compiladores C, Cython, PyInstaller e UPX
FROM python:3.12-slim-bookworm AS builder

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Instala dependências de compilação de sistema para Linux
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        patchelf \
        libegl1 \
        libgl1 \
        upx-ucl \
        git && \
    rm -rf /var/lib/apt/lists/*

# Instala ferramentas Python
RUN pip install --upgrade pip setuptools wheel poetry

# Copia metadados e dependências do projeto
COPY pyproject.toml poetry.lock ./

# Instala dependências do Orange no ambiente do builder
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Copia o código-fonte do Orange e o projeto
COPY orange/ ./orange/
COPY src/ ./src/
COPY orange.toml ./

# Instala o Orange em modo editável e executa o build de produção
RUN pip install -e . && \
    orange doctor && \
    orange build --profile production --clean

# ==============================================================================
# Estágio 2: Runtime - Imagem mínima final contendo apenas o binário compilado
FROM debian:bookworm-slim AS runtime

WORKDIR /app

# Instala bibliotecas mínimas de execução (OpenGL/EGL para UI)
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
        libegl1 \
        libgl1 \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Cria usuário não-root por segurança
RUN useradd -m -u 1000 -s /bin/bash appuser
USER appuser

# Copia o executável final compilado a partir do estágio de build
COPY --from=builder /app/dist/ /app/dist/

# Ponto de entrada padrão
ENTRYPOINT ["/app/dist/Orange"]

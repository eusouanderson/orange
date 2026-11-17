# Uso com Docker & Docker Compose

O Orange Framework oferece suporte nativo e otimizado a ambientes conteinerizados através de um **Dockerfile Multi-Stage** de alta performance e configuração do **Docker Compose**.

---

## 1. Compilação Local com Docker Compose

Para compilar uma aplicação sem a necessidade de instalar compiladores C, Cython ou dependências nativas na sua máquina hospedeira:

```bash
# Executa a compilação de produção e gera o binário no host em ./dist
docker compose run --rm orange-build
```

O container compila o código-fonte Python utilizando Cython, GCC e PyInstaller, e grava o executável standalone resultante diretamente na pasta `./dist` da sua máquina local.

---

## 2. Executando a Imagem de Runtime

Após a compilação, você pode executar o executável compilado dentro de uma imagem mínima baseada em Debian:

```bash
# Executa a aplicação conteinerizada
docker compose up orange-app
```

---

## 3. Construindo Manualmente via Dockerfile

```bash
# Constrói apenas o executável final em container
docker build --target runtime -t my-orange-app:latest .

# Executa o container
docker run --rm my-orange-app:latest
```

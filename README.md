# Orange Framework: Python Micro Framework for Cython Compilation

## Overview

Orange Framework é um micro framework projetado para facilitar o processo de compilação de Python para Cython, além de automatizar a criação de diretórios em ambientes de desenvolvimento (dev) ou produção (prod). Ele também inclui scripts de automação para build, testes e deploy diretamente para o GitHub Releases.

---

## Versão de Desenvolvimento 0.2.0 

---

### Features
**Cython Compilation**
- Facilita a compilação de código Python para Cython para melhorar a performance.
Inclui suporte a múltiplos arquivos e diretórios.
**Automated Directory Setup**
- Criação automática de estruturas de diretórios tanto para desenvolvimento quanto para produção.

**Build Automation**
- Scripts .sh para compilar o projeto de forma automática.
- Builds otimizados para Linux e Windows.

Used to investigate your operating system by reading all active processes on your computer.

**GitHub Integration**
- Envia os builds diretamente para o GitHub Releases, reduzindo a complexidade do deploy.

**Integrated Development Features**
- Gerenciamento de dependências utilizando Poetry.
- Scripts para iniciar e testar o projeto com facilidade.


## Usage
1. Clone o repositório.
2. Configure as dependências listadas no arquivo requirements.txt ou instale usando o Poetry.
3. Use os scripts disponíveis para rodar ou buildar o projeto.

## Get Started
1. Clone o repositório:

```bash
    git clone https://github.com/seu-repositorio.git
```

2. Instale as dependências:

```bash
    poetry install
```

3. De permissões para os arquivos .sh
```bash
    chmod +x build.sh
    chmod +x start.sh

```

4. Execute o projeto:

```bash
    ./start.sh
```

**Para criar builds:**

```bash
    ./build.sh <repo>
```
parametros que dependendo do da arvore do projeto , caso tenha mais pastas precisa passar

```bash
    ./build.sh <repo> --compile-all
```

Lembrando que repo é o caminho estatico do repositório Ex:
```bash
    eusouanderson/orange
```


Test Locally
No Linux ou Windows:
```bash
    ./start.sh
```
Build para Produção:
```bash
    ./build.sh
```
# Tools
- Linguagem: **Python**
- Compilador: **Cython**
- Gerenciador de Dependências: **Poetry**
- Scripts de Build: **.sh automatizados**
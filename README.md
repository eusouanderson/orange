# Orange Framework: Python Micro Framework for Cython Compilation

## Overview

O **Orange Framework** é um micro framework projetado para facilitar o processo de compilação de Python para Cython. Ele também automatiza a criação de diretórios em ambientes de desenvolvimento (dev) ou produção (prod). Além disso, o framework inclui scripts de automação para build, testes e deploy diretamente para o GitHub Releases.

Após ser compilado com o Cython, o projeto é convertido em um executável utilizando o **PyInstaller**, o que facilita a distribuição e execução do projeto sem a necessidade de instalar o Python (Por enquanto.).
A grande vantagem desse framework é que ele resolve o problema comum de inconsistências de diretório durante a execução. Normalmente, em alguns casos, o local onde o Python está sendo executado pode ser diferente do diretório onde o arquivo está, o que pode causar problemas ao tentar acessar ou manipular arquivos. Esse framework garante que o ambiente de execução e o caminho dos arquivos sejam sempre tratados de forma correta, evitando esse tipo de erro.

### Funcionalidades:

- **Compilação de Python para Cython**: Facilita o processo de transformar código Python em código compilado.
- **Criação automática de diretórios**: Configura os diretórios necessários para ambientes de desenvolvimento e produção.
- **Automação de Build, Testes e Deploy**: Scripts que automatizam o processo de build, execução de testes e deploy para o GitHub Releases (Precisa ter instalado o CLI GH ).
- **Geração de Executável com PyInstaller**: Depois de compilado com Cython, o projeto é transformado em um executável com PyInstaller.
- **Aplicação exemplo (PyQt6)**: Calculadora 3D profissional para desenvolvimento em FreeCAD com conversão de unidades, geometria 2D/3D e histórico de cálculos.


### Features
**Cython Compilation**
- Facilita a compilação de código Python para Cython para melhorar a performance.
Inclui suporte a múltiplos arquivos e diretórios.
**Automated Directory Setup**
- Criação automática de estruturas de diretórios tanto para desenvolvimento quanto para produção.

**Build Automation**
- Scripts .sh para compilar o projeto de forma automática.
- Builds otimizados para Linux e Windows.

**GitHub Integration**
- Envia os builds diretamente para o GitHub Releases, reduzindo a complexidade do deploy.

**Integrated Development Features**
- Gerenciamento de dependências utilizando Poetry.
- Scripts para iniciar e testar o projeto com facilidade.


## Usage
1. Clone o repositório.
2. Configure as dependências listadas no arquivo requirements.txt ou instale usando o Poetry.
3. Na pasta scripts na raiz do projeto tem um script de instalação ```"install.sh"```.
4. Após a instalação concluida, navegue para o diretório raiz e execute o script ```"start.sh"```

## Requisitos de sistema (Linux)
- Python 3.10–3.13, Poetry.
- Bibliotecas do sistema necessárias para o backend Qt (instale todas de uma vez):
    ```bash
    sudo apt-get update && sudo apt-get install -y \
        libgl1 libegl1 libfontconfig1 libglib2.0-0 libxkbcommon0 \
        libxcb-cursor0 libxcb-shape0 libxcb-icccm4 libxcb-keysyms1 \
        libxcb-xinerama0 libxkbcommon-x11-0 libxcb-render-util0
    ```

## Aplicação de exemplo (Calc3D)
- Calculadora 3D profissional para FreeCAD e engenharia.
- **Conversão de Unidades**: mm, cm, m, polegadas, pés.
- **Geometria 2D**: área retângulo, circunferência e área círculo.
- **Geometria 3D**: volume paralelepípedo, esfera, área superfície, distância entre pontos em 3D.
- **Ferramentas Extras**: raiz quadrada, potência (x^n).
- **Histórico**: tabela com data/hora de todos os cálculos realizados.
- Interface escura e responsiva com PyQt6.

Se estiver em ambiente sem display (CI/WSL/SSH), use uma sessão X/Wayland ou execute offscreen:
```bash
QT_QPA_PLATFORM=offscreen ./start.sh
```

## Get Started
1. Clone o repositório:

```bash
    git clone https://github.com/eusouanderson/orange.git
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

4. Execute o projeto com `make` ou script direto:

```bash
    # Via Makefile (recomendado)
    make start              # executa normalmente
    make watch              # watch mode: reinicia ao salvar (hot reload)

    # Via script
    ./start.sh
```

## Comandos Make

O projeto inclui um **Makefile** para simplificar operações comuns:

```bash
# Executar a aplicação (Calc3D)
make start

# Watch mode: reinicia automaticamente ao salvar arquivos Python
make watch

# Fazer build local (sem upload para GitHub)
make build

# Alias para build
make build-local

# Rodar testes
make test

# Build com customização
make build TAG=v1.2.3 PLATFORM=linux FLAGS="--compile-all"

# Build e upload para GitHub
make build FLAGS="--compile-all" REPO=seu_usuario/seu_repo
```

### Watch Mode (Hot Reload em Desenvolvimento)

Para desenvolvimento iterativo com auto-reload:

```bash
make watch
```

Este comando:
- Monitora mudanças em arquivos Python (`src/`)
- Reinicia a aplicação automaticamente ao salvar
- Ideal para desenvolvimento rápido sem parar/iniciar manualmente
- Pressione `Ctrl+C` para sair

**Dica:** Use em conjunto com seu editor (VS Code, PyCharm, etc.) para feedback imediato!


**Para criar builds (Linux, Windows, WSL):**

```bash
    # via Makefile (recomendado, sem upload por padrão)
    make build  # usa TAG do pyproject, --compile-all e --no-upload

    # build + upload (remova --no-upload)
    make build FLAGS="--compile-all" REPO=seu/repo TAG=v1.2.3

    # manual (script original)
    ./build.sh <repo>

## Testes

Execute a suíte de testes com:

```bash
    make test

    # ou manualmente
    poetry run pytest -v
```

A cobertura inclui testes para:
- Conversão de unidades (mm, cm, m, polegadas, pés)
- Geometria 2D (área retângulo, circunferência, área círculo)
- Geometria 3D (volume, área superfície, distância 3D)
- Helpers do build (Cython, PyInstaller)

**Resultado esperado:** 10 testes passando ✅

Caso o projeto tenha uma estrutura com múltiplas pastas e você precise compilar todas elas, utilize o parâmetro **--compile-all** :

```bash
    ./build.sh <repo> --compile-all
```

Onde **repo** é o caminho estático do repositório. Exemplo:

```bash
    ./build.sh eusouanderson/orange --compile-all 
```
****Atenção: A estrutura do projeto deve ser mantida intacta, pois é fundamental para a organização e o bom funcionamento do código. Inicialmente, o projeto deve conter as pastas src/core, além das pastas compile, dist, docs e reload na raiz do projeto. A estrutura deve ser preservada à medida que o projeto evolui, permitindo a adição de novos módulos ou componentes conforme necessário. Manter essa organização desde o início facilita a escalabilidade, a manutenção e a colaboração no desenvolvimento, garantindo que tudo funcione corretamente .****

## Testar Localmente

### No Linux ou Windows

Para rodar o projeto localmente, execute:

```bash
make start
```

- Executa a Calc3D (calculadora 3D para FreeCAD).
- Define automaticamente as variáveis de ambiente para Qt (XCB no Linux).

Se estiver em um ambiente sem display (SSH, WSL, CI):
```bash
QT_QPA_PLATFORM=offscreen make start
```

Build para Produção (com upload para GitHub):
```bash
    make build FLAGS="--compile-all" REPO=seu_usuario/seu_repo
```

Build Local (sem upload):
```bash
    make build  # padrão: --no-upload
```

## Cross-compilation para Windows (a partir de Linux/WSL)

Requisitos:
```bash
    sudo apt-get update && sudo apt-get install -y mingw-w64 wine patchelf
```

Build:
```bash
    PLATFORM=windows make build FLAGS="--compile-all --no-upload" TAG=v1.2.3
```


# Tools
- Linguagem: **Python**
- Compilador: **Cython**
- Gerenciador de Dependências: **Poetry**
- Scripts de Build: **.sh automatizados**

## Licença

Este projeto está licenciado sob a **GNU General Public License (GPL)**, versão 3, de 29 de junho de 2007.

Copyright (C) 2007 **Free Software Foundation, Inc.** <https://fsf.org/>

A licença permite que todos copiem e distribuam cópias verbatim deste documento de licença, mas alterações no conteúdo não são permitidas.

### Preamble

A GNU General Public License (GPL) foi criada para garantir sua liberdade de compartilhar e modificar o software, para que você possa usar e melhorar os programas que você usa. Isso significa que qualquer programa que seja distribuído sob esta licença pode ser copiado, modificado e redistribuído, desde que as mesmas liberdades sejam garantidas para os futuros usuários.

Para mais detalhes sobre a licença, consulte o [documento completo da GPL v3](https://www.gnu.org/licenses/gpl-3.0.html).

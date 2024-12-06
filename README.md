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

4. Execute o projeto:

```bash
    ./start.sh
```

**Para criar builds:**

```bash
    ./build.sh <repo>
```
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

Para rodar o projeto localmente, execute o seguinte comando:

```bash
./start.sh
```

- Ao executar o comando, será iniciado o projeto, e você verá uma calculadora que foi desenvolvida utilizando esta configuração.

Build para Produção:
```bash
    ./build.sh
```
- Na raiz do seu projeto na pasta **dist** encontrar um arquivo compactado com nome:
```bash
    Orange-v0.1.1
```

- Pretendo atualizar este projeto sempre que possível e, em breve, enviá-lo para o PyPI.
- Agradeço a todos que baixaram o projeto. Juntos, vamos construir uma comunidade Python mais forte! Tamo junto! 🚀


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

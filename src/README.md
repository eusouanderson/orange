# Calculadora Complexa em PySide6

## Descrição

Este é um projeto de uma **calculadora complexa** construída utilizando o **PySide6** (Qt para Python), com diversas funcionalidades matemáticas, incluindo operações básicas e funções trigonométricas (seno, cosseno, tangente). A calculadora também suporta a operação de raiz quadrada e permite a utilização de parênteses para agrupar expressões.

## Funcionalidades

A calculadora oferece as seguintes funcionalidades:

### Operações Básicas:
- **Adição**: Soma de dois ou mais números.
- **Subtração**: Subtração entre números.
- **Multiplicação**: Multiplicação entre números.
- **Divisão**: Divisão entre números.

### Funções Trigonométricas:
- **Seno (sin)**: Calcula o seno de um ângulo em graus.
- **Cosseno (cos)**: Calcula o cosseno de um ângulo em graus.
- **Tangente (tan)**: Calcula a tangente de um ângulo em graus.

### Outras Funções:
- **Raiz Quadrada (√)**: Calcula a raiz quadrada de um número.
- **Limpeza (C)**: Limpa a tela da calculadora.

### Suporte para Parênteses:
- Você pode utilizar parênteses `()` para agrupar expressões e controlar a ordem das operações.

## Como Usar

### Interface
- **Tela de Exibição**: Na parte superior da interface, você encontrará uma tela de exibição onde a expressão será exibida à medida que você digita.
- **Botões**: A interface contém botões para as operações matemáticas básicas, funções trigonométricas (sin, cos, tan), e outros botões úteis como a raiz quadrada e o botão de limpar (C).

### Exemplos de Uso

1. **Soma de dois números**:
    - Digite `7 + 3` e pressione o botão `=`.
    - Resultado: `10`.

2. **Funções Trigonométricas**:
    - Para calcular o **seno** de 30 graus, digite `sin(30)` e pressione `=`.
    - Resultado: `0.5`.

    - Para calcular o **cosseno** de 45 graus, digite `cos(45)` e pressione `=`.
    - Resultado: `0.7071`.

    - Para calcular a **tangente** de 45 graus, digite `tan(45)` e pressione `=`.
    - Resultado: `1`.

3. **Raiz Quadrada**:
    - Para calcular a raiz quadrada de 25, digite `√25` e pressione `=`.
    - Resultado: `5`.

4. **Uso de Parênteses**:
    - Para calcular a expressão `(2 + 3) * 4`, digite `(2 + 3) * 4` e pressione `=`.
    - Resultado: `20`.

5. **Limpeza**:
    - Para limpar a tela, pressione o botão `C`.

## Como Executar

Para executar a calculadora, siga os seguintes passos:

### Pré-requisitos
- Python 3.x instalado.
- PySide6 instalado (utilizado para a criação da interface gráfica).
- Opcional: Um ambiente virtual para gerenciar dependências do projeto.

### Instalando Dependências

Se você não tiver o PySide6 instalado, use o seguinte comando para instalá-lo:

```bash
pip install pyside6
Rodando o Projeto
Clone o repositório ou baixe o arquivo Python que contém a implementação da calculadora.
Abra o terminal ou prompt de comando e navegue até o diretório onde o arquivo está localizado.
Execute o arquivo Python:
bash
Copiar código
python nome_do_arquivo.py
Isso abrirá a janela da calculadora. Você pode começar a usá-la imediatamente.

Estrutura do Projeto
O projeto contém os seguintes arquivos e diretórios:

main.py: Contém o código principal que implementa a calculadora utilizando PySide6.
README.md: Este arquivo de documentação.
Contribuições
Se você deseja contribuir para o projeto, siga os seguintes passos:

Faça um fork do repositório.
Crie uma branch para a sua modificação (git checkout -b minha-modificacao).
Faça suas alterações e commit (git commit -am 'Adiciona nova funcionalidade').
Envie suas alterações para o repositório (git push origin minha-modificacao).
Abra um pull request.
Licença
Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE para mais detalhes.

markdown
Copiar código

---

### Explicação do Documento

- **Descrição**: Dá uma visão geral do que é a calculadora, destacando suas principais funcionalidades.
- **Funcionalidades**: Explica cada operação e função disponível na calculadora.
- **Como Usar**: Fornece exemplos de como realizar cálculos com a calculadora.
- **Como Executar**: Instruções sobre como rodar o projeto localmente.
- **Estrutura do Projeto**: Mostra os arquivos e pastas principais do projeto.
- **Contribuições**: Instruções para quem deseja contribuir com melhorias ou correções.
- **Licença**: Indica que o projeto é licenciado sob a Licença MIT, o que permite modificações e redistribuições.

Esse formato ajuda a organizar bem a documentação e facilita para qualquer pessoa entender rapidame
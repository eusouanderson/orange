# Usar imagem base do Python
FROM python:3.10-slim

# Configuração do diretório de trabalho
WORKDIR /app

# Copiar os arquivos do projeto
COPY . .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Comando de inicialização do projeto
CMD ["python", "src/main.py"]

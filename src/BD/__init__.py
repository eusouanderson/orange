import psycopg2

# Parâmetros de conexão com o banco de dados
host = "localhost"
database = "exemplo"
user = "usuario"
password = "senha"

# Estabelece a conexão com o banco de dados
conn = psycopg2.connect(
    host=host,
    database=database,
    user=user,
    password=password
)

# Cria um cursor para executar as consultas SQL
cursor = conn.cursor()

# Executa uma consulta SQL
cursor.execute("SELECT * FROM tabela_exemplo")

# Lê os resultados da consulta SQL
results = cursor.fetchall()

# Imprime os resultados na tela
for row in results:
    print(row)

# Fecha a conexão com o banco de dados
conn.close()

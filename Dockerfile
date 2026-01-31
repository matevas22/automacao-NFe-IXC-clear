# Usar uma imagem base leve do Python
FROM python:3.10-slim

# Definir o diretório de trabalho no container
WORKDIR /app

# Copiar o arquivo de requisitos e instalar as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código da aplicação
COPY . .

# Expor a porta que o Flask usa
EXPOSE 5000

# Comando para iniciar o servidor
# Usamos o módulo flask para garantir que rode escutando em todos os IPs (0.0.0.0)
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]

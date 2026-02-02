FROM python:3.13-slim

WORKDIR /app

# Adiciona compiladores e dependências de sistema necessárias
# Isso corrige erros ao instalar Pandas, NumPy, CFFI, etc.
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    musl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . .

EXPOSE 4050

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=4050"]

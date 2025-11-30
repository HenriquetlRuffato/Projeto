# Backend Dockerfile
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    FLASK_ENV=production

WORKDIR /app

# Sistema necessário para compilar dependências (se houver)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar requisitos primeiro para otimizar cache
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código do backend
COPY . .

# Garantir diretório de banco SQLite
RUN mkdir -p /app/instance

EXPOSE 5000

CMD ["python", "run.py"]
# Backend Dockerfile
FROM python:3.12-slim

# Configurações de ambiente
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    FLASK_ENV=production

# Diretório de trabalho dentro do container
WORKDIR /app

# Pacotes do sistema necessários para compilar libs Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia o requirements.txt que está em backend/ no repositório
COPY backend/requirements.txt ./requirements.txt

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia TODO o código do backend para dentro do container
COPY backend/. .

# Garante diretório para o SQLite
RUN mkdir -p /app/instance

# Expõe a porta usada pelo Flask
EXPOSE 5000

# Comando para iniciar a aplicação
CMD ["python", "run.py"]

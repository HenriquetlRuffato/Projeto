# Frontend Dockerfile
FROM node:18-alpine

WORKDIR /usr/src/app

# Instalar dependências primeiro
COPY package*.json ./
RUN npm ci

# Copiar código
COPY . .

# CRA dev server
ENV HOST=0.0.0.0
EXPOSE 3000

CMD ["npm", "start"]
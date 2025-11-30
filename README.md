# Extrator de Dados de Nota Fiscal

Sistema completo para extração automática de dados de notas fiscais em PDF usando Inteligência Artificial.

## Estrutura do Projeto

```
zParaibaZ/
├── backend/          # API Flask (Python)
│   ├── app.py
│   ├── models.py
│   ├── routes.py
│   ├── requirements.txt
│   └── README.md
├── frontend/         # Interface React
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── README.md
└── README.md
```

## Funcionalidades

- **Upload de PDFs**: Interface drag-and-drop para carregar notas fiscais
- **Extração Inteligente**: Usa IA (OpenAI) para extrair dados estruturados
- **Classificação Automática**: Categoriza despesas automaticamente
- **Visualização**: Interface moderna para visualizar dados extraídos
- **Persistência**: Salva dados em banco SQLite
- **API REST**: Comunicação entre frontend e backend

## Instalação Rápida

### Backend (Flask)
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend (React)
```bash
cd frontend
npm install
npm start
```

## Acesso

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000

## Configuração

1. Configure a chave da OpenAI no arquivo `backend/.env`:
```
OPENAI_API_KEY=sua_chave_aqui
```

2. O banco de dados SQLite será criado automaticamente na primeira execução.

## Como Usar

1. Acesse http://localhost:3000
2. Faça upload de um PDF de nota fiscal
3. Aguarde a extração automática dos dados
4. Visualize os dados extraídos
5. Salve no banco de dados

## Tecnologias

- **Backend**: Flask, SQLAlchemy, OpenAI API, PyPDF2
- **Frontend**: React, Axios, CSS3
- **Banco**: SQLite
- **IA**: OpenAI GPT para extração de dados
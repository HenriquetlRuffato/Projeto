# Backend - Extrator de Dados de Nota Fiscal

API Flask para extração e processamento de dados de notas fiscais em PDF.

## Funcionalidades

- Extração de dados de PDFs de notas fiscais usando IA
- Classificação automática de despesas
- API REST para integração com frontend
- Banco de dados SQLite para persistência

## Instalação

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Configure as variáveis de ambiente no arquivo `.env`:
```
OPENAI_API_KEY=sua_chave_aqui
```

3. Execute o servidor:
```bash
python app.py
```

O servidor estará disponível em `http://localhost:5000`

## Endpoints da API

- `GET /api/expense-categories` - Lista categorias de despesas
- `POST /api/extract-data` - Extrai dados de PDF
- `POST /api/save-invoice` - Salva dados da nota fiscal
- `GET /api/invoices` - Lista notas fiscais salvas

## Estrutura do Projeto

- `app.py` - Aplicação principal Flask
- `models.py` - Modelos do banco de dados
- `routes.py` - Rotas da API
- `crud_routes.py` - Operações CRUD
- `pdf_processor.py` - Processamento de PDFs
- `expense_classifier.py` - Classificação de despesas
- `seed_data.py` - Dados iniciais do banco

## Docker

- Build e subir API:
```
docker compose up -d --build
```
A API ficará disponível em `http://localhost:5000`.

- Parar os containers:
```
docker compose down
```

## Novo endpoint

- `POST /api/analyze-and-save`
  - Analisa e informa se FORNECEDOR, FATURADO e DESPESA existem (com IDs),
    cria os que faltam, lança a conta a pagar, parcela e classificação,
    e retorna `message: "Registro foi lançado com sucesso."` junto com `analysis_message`.

### Payload exemplo
```
{
  "fornecedor": {"razao_social": "IGUAÇU MAQUINAS LTDA", "fantasia": "IGUAÇU", "cnpj": "11.111.111/0001-00"},
  "faturado": {"nome_completo": "BELTRANO DA SILVA", "cpf": "999.999.999-99"},
  "classificacao_despesa": "MANUTENÇÃO E OPERAÇÃO",
  "numero_nota_fiscal": "NF-123",
  "data_emissao": "2024-09-20",
  "descricao_produtos": "Peças e serviços",
  "valor_total": 1234.56,
  "data_vencimento": "2024-10-20"
}
```

### Configuração com MySQL

- Variáveis de ambiente suportadas:
  - `DB_ENGINE`: `mysql` para usar MySQL (default: `sqlite`).
  - `DB_HOST`, `DB_PORT`: host e porta (ex.: `localhost` e `3306`).
  - `DB_USER`, `DB_PASSWORD`: usuário e senha (ex.: `root` e `1234`).
  - `DB_NAME`: nome do banco (ex.: `banco_paraiba`).

- Exemplo `.env` para sua instalação local (MySQL Workbench):
```
DB_ENGINE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=1234
DB_NAME=banco_paraiba
```

- Com Docker Compose (já incluso):
  - Sobe um `mysql:8` com banco `banco_paraiba` e senha `1234`.
  - Backend conecta automaticamente ao serviço `db` via envs.
  - Comando: `docker compose up -d --build`
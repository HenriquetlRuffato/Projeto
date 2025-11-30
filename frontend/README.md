# Frontend - Extrator de Dados de Nota Fiscal

Interface React para upload e visualização de dados extraídos de notas fiscais.

## Funcionalidades

- Interface drag-and-drop para upload de PDFs
- Visualização dos dados extraídos
- Integração com API do backend
- Interface responsiva e moderna

## Instalação

1. Instale as dependências:
```bash
npm install
```

2. Inicie o servidor de desenvolvimento:
```bash
npm start
```

A aplicação estará disponível em `http://localhost:3000`

## Scripts Disponíveis

- `npm start` - Inicia o servidor de desenvolvimento
- `npm run build` - Cria build de produção
- `npm test` - Executa os testes
- `npm run eject` - Ejeta a configuração do Create React App

## Configuração

O frontend está configurado para se comunicar com o backend em `http://localhost:5000`. 

Para alterar a URL da API, modifique as chamadas axios no arquivo `src/App.js`.

## Estrutura do Projeto

- `src/App.js` - Componente principal da aplicação
- `src/index.js` - Ponto de entrada da aplicação
- `src/index.css` - Estilos globais
- `public/index.html` - Template HTML
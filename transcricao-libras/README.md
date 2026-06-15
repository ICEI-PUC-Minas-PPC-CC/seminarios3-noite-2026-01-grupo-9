# Tradutor de Voz para Libras

Plataforma de acessibilidade que converte fala em texto e traduz para Língua Brasileira de Sinais (Libras) em tempo real.

## Requisitos

- Python 3.11+
- Navegador com suporte à Web Speech API (Chrome, Edge)

## Como rodar localmente

```bash
# 1. Instalar dependências
cd backend
pip install -r requirements.txt

# 2. Iniciar o servidor
uvicorn main:app --reload

# 3. Abrir no navegador
# http://localhost:8000
```

## Com Docker

```bash
docker compose up --build
# Acesse: http://localhost:8000
```

## Estrutura

```
├── backend/
│   ├── main.py            # Ponto de entrada FastAPI
│   ├── config.py           # Configurações (variáveis de ambiente)
│   ├── database.py         # Engine e sessão SQLAlchemy
│   ├── models.py           # Modelos ORM
│   ├── schemas.py          # Schemas Pydantic (validação)
│   ├── routers/
│   │   └── transcricoes.py # Endpoints CRUD
│   ├── requirements.txt    # Dependências Python
│   └── .env.example        # Template de variáveis de ambiente
├── frontend/
│   ├── index.html          # Página principal
│   ├── script.js           # Lógica de voz + integração API
│   └── style.css           # Estilos (dark mode)
├── Dockerfile              # Build para deploy
├── docker-compose.yml      # Desenvolvimento local com Docker
└── render.yaml             # Deploy no Render.com
```

## API Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/api/transcricoes` | Salvar nova transcrição |
| `GET` | `/api/transcricoes` | Listar (paginado, filtro por sessão) |
| `GET` | `/api/transcricoes/{id}` | Detalhes de uma transcrição |
| `DELETE` | `/api/transcricoes/{id}` | Excluir transcrição |
| `GET` | `/api/estatisticas` | Métricas gerais de uso |
| `GET` | `/api/health` | Health check |

## Documentação da API

Com o servidor rodando, acesse: http://localhost:8000/docs (Swagger UI)

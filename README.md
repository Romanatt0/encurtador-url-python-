# Encurtador URL API

API em FastAPI para encurtamento de URLs com suporte a:

- criação de URLs curtas públicas
- criação de URLs curtas vinculadas a usuários autenticados
- expiração por tipo de usuário
- coleta de métricas de acesso
- geração de QR Code
- autenticação com JWT
- versionamento de schema com Alembic

## Visão Geral

O projeto implementa um micro SaaS de encurtamento de URLs com duas regras principais de negócio:

- usuários não cadastrados podem gerar URLs curtas
- usuários não cadastrados não podem acessar métricas e suas URLs expiram antes

Hoje a aplicação já está organizada em camadas de rota, service, schema, auth e model.

## Stack

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- SQLite (apenas como fallback local/desenvolvimento)
- Alembic
- Pydantic
- SlowAPI
- Passlib + bcrypt
- PyJWT
- qrcode
- Docker + docker-compose

## Estrutura Do Projeto

```text
src/
  alembic/
    env.py
    versions/
  auth/
    __init__.py
    acess.py
    auth.py
  core/
    rate_limiter.py
  dependencies/
    dependencies.py
  models/
    models.py
  routes/
    metrics_routes.py
    shortener_routes.py
    user_routes.py
  schemas/
    metric_schema.py
    shortener_schema.py
    token_schema.py
    user_schema.py
  services/
    metric_service.py
    short_url_service.py
    user_service.py
  tests/
    conftest.py
    test_auth/
    test_routes/
    test_schemas/
    test_services/
    test_utils/
  utils/
    short_code.py
    url_utils.py
  main.py
requirements.txt
```

## Arquitetura

### Rotas

As rotas recebem a requisição HTTP, resolvem dependências do FastAPI e delegam a regra de negócio para os services.

- `src/routes/shortener_routes.py`
- `src/routes/user_routes.py`
- `src/routes/metrics_routes.py`

### Services

Os services concentram a regra de negócio da aplicação.

- `short_url_service.py`
  - valida URL
  - gera hash curto
  - define expiração
  - persiste URL encurtada
  - valida expiração no redirecionamento
  - registra métricas de acesso
- `metric_service.py`
  - consulta métricas por dia, mês e ano
  - restringe acesso a URLs anônimas
  - restringe acesso a usuários que não são donos da URL
- `user_service.py`
  - cria usuário
  - busca usuário por e-mail
  - autentica usuário
  - emite tokens JWT

### Models

Os models SQLAlchemy estão em `src/models/models.py`.

- `User`
- `ShortUrl`
- `UrlMetric`

### Schemas

Os schemas Pydantic definem payloads de entrada e saída da API.

### Auth

O módulo `src/auth` centraliza autenticação JWT e recuperação do usuário autenticado.

### Utils

Os utilitários concentram helpers puros reutilizáveis.

- `validate_url()`
- `generate_short_id()`

## Regras De Negócio

### URLs anônimas

- podem ser criadas sem autenticação
- ficam com `user_id = null`
- expiram em `7` dias
- não podem ter métricas consultadas

### URLs de usuários autenticados

- exigem token Bearer válido
- ficam associadas ao `user_id`
- expiram em `30` dias
- métricas só podem ser acessadas pelo dono da URL

### Expiração

A expiração é armazenada em `ShortUrl.expires_at`.

Durante o redirecionamento:

- se a URL não existir, retorna `404`
- se estiver expirada, retorna `410`
- se estiver válida, registra métrica e redireciona

### Métricas

As métricas são agregadas por dia em `UrlMetric`:

- `day`
- `month`
- `year`
- `amount`

As consultas mensal e anual somam os registros diários armazenados.

## Banco De Dados

O projeto usa **PostgreSQL** (container Docker) e **SQLite** apenas como fallback para execução local sem Docker.

A URL de conexão é lida da variável de ambiente `DATABASE_URL`:

- `postgresql+psycopg2://postgres:postgres@postgres:5432/encurtador` — dentro da rede Docker
- `postgresql+psycopg2://postgres:postgres@localhost:5433/encurtador` — acesso externo ao container (DBeaver, apps locais)

O engine SQLAlchemy é definido em `src/models/models.py`:

```python
db = create_engine(os.getenv("DATABASE_URL", "sqlite:///banco.db"))
```

As sessões são abertas via `get_session()` em `src/dependencies/dependencies.py`.

Se `DATABASE_URL` não estiver definida, o SQLite (`banco.db`) é usado para desenvolvimento local.

## Models

### User

Campos:

- `id`
- `name`
- `email`
- `password`
- `access`

Relacionamentos:

- `short_urls`

### ShortUrl

Campos:

- `id`
- `origin_url`
- `hash_url`
- `user_id`
- `expires_at`

Relacionamentos:

- `user`
- `metrics`

### UrlMetric

Campos:

- `id`
- `day`
- `month`
- `year`
- `amount`
- `short_url_id`

## Endpoints

### Público

#### `POST /short`

Cria uma URL curta anônima.

Rate limit: `10/minute`

Request:

```json
{
  "url": "https://exemplo.com"
}
```

Response:

```json
{
  "url": "https://exemplo.com",
  "short_url": "http://localhost:8000/abc123X"
}
```

#### `GET /{short_id}`

Redireciona para a URL original.

Rate limit: `5/minute`

Observações:

- possui rate limit de `5/minute`
- registra métrica diária
- retorna `410` se a URL estiver expirada

#### `GET /{short_id}/qrcode`

Gera um QR Code PNG apontando para a URL curta.

Rate limit: `5/minute`

### Usuário

Prefixo base: `/user`

#### `POST /user/create`

Cria usuário.

Rate limit: `5/minute`

Request:

```json
{
  "name": "Victor",
  "email": "victor@email.com",
  "password": "123456"
}
```

#### `POST /user/login`

Autentica usuário e retorna tokens.

Rate limit: `5/minute`

Request:

```json
{
  "email": "victor@email.com",
  "password": "123456"
}
```

Response:

```json
{
  "access_token": "...",
  "refresh_token": "..."
}
```

#### `GET /user/me`

Retorna informações do usuário autenticado.

Rate limit: `50/minute`

Headers:

```text
Authorization: Bearer <access_token>
```

Response:

```json
{
  "name": "Victor",
  "email": "victor@email.com"
}
```

#### `POST /user/refresh`

Gera um novo access token a partir de um refresh token.

Rate limit: `5/minute`

Request:

```json
{
  "access_token": "<refresh_token>"
}
```

Response:

```json
{
  "refresh_token": "...",
  "token_type": "bearer"
}
```

#### `POST /user/createUrl`

Cria uma URL curta vinculada ao usuário autenticado.

Rate limit: `5/minute`

Headers:

```text
Authorization: Bearer <access_token>
```

Request:

```json
{
  "url": "https://exemplo.com"
}
```

### Métricas

As rotas de métricas exigem autenticação e validam ownership.

#### `GET /metrics/day/{short_id}`

Retorna métricas do dia da URL do usuário.

Rate limit: `5/minute`

#### `GET /metrics/month/{short_id}`

Retorna soma das métricas do mês atual.

Rate limit: `5/minute`

#### `GET /metrics/year/{short_id}`

Retorna soma das métricas do ano atual.

Rate limit: `5/minute`

## Autenticação

A autenticação usa JWT.

Arquivo principal:

- `src/auth/auth.py`

Funções principais:

- `create_access_token()`
- `create_refresh_token()`
- `decode_token()`

O usuário autenticado é resolvido em:

- `src/auth/acess.py`

O token deve conter:

- `sub`: e-mail do usuário
- `type`: `access` ou `refresh`

## Configuração De Ambiente

O projeto lê variáveis do `.env` para configuração:

- `SECRET_KEY`
- `HASH`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `REFRESH_TOKEN_EXPIRE_MINUTES`
- `API_KEY`
- `DATABASE_URL`

## Migrations Com Alembic

Configuração principal:

- `src/alembic.ini`
- `src/alembic/env.py`

Revisões atuais:

- `ffaeb92272a5_create_initial_tables.py`
- `6f8e9b0a1c2d_add_expires_at_to_short_urls.py`

### Comandos úteis

Rodando a partir de `src/`:

```bash
alembic current
alembic heads
alembic history
alembic upgrade head
alembic revision --autogenerate -m "descricao"
```

Rodando a partir da raiz do projeto:

```bash
py -m alembic -c "src/alembic.ini" upgrade head
py -m alembic -c "src/alembic.ini" revision --autogenerate -m "descricao"
```

## Docker

A aplicação roda em containers com dois serviços:

- `api` — imagem própria definida no `Dockerfile`, porta `8000`
- `postgres` — imagem `postgres:17`, dados persistidos no volume `postgres_data`

Mapeamento de portas:

| Serviço | Host | Container |
|---|---|---|
| api | 8000 | 8000 |
| postgres | 5433 | 5432 |

> A porta do host do Postgres é `5433` para evitar conflito com um PostgreSQL
> nativo do Windows que ocupa a `5432`. Por isso o DBeaver e ferramentas externas
> usam `localhost:5433`.

### Subir os containers

```powershell
docker compose up --build -d
```

No primeiro `up`, a API executa `alembic upgrade head` automaticamente (comando do `Dockerfile`), criando as tabelas no Postgres.

### Comandos úteis

```powershell
docker ps -a                   # listar containers
docker compose logs -f api     # acompanhar logs da API
docker compose down            # parar (preserva volume de dados e imagens)
docker compose down -v         # parar e apagar o volume de dados
docker compose down --rmi all  # parar e remover as imagens
docker images                  # listar imagens
```

### Acessando o banco (DBeaver e afins)

O serviço `postgres` é criado com:

- `POSTGRES_DB=encurtador`
- `POSTGRES_USER=postgres`
- `POSTGRES_PASSWORD=postgres`

No DBeaver:

- **Host:** `localhost`
- **Porta:** `5433`
- **Database:** `encurtador`
- **User:** `postgres`
- **Password:** `postgres`

Ou pela JDBC URL:

```
jdbc:postgresql://localhost:5433/encurtador?user=postgres&password=postgres
```

## Como Executar

### 1. Com Docker (recomendado)

```powershell
docker compose up --build -d
```

API em `http://localhost:8000` / docs em `http://localhost:8000/docs`.

Os passos a seguir são apenas para execução local **sem** Docker (passam a usar SQLite, salvo se `DATABASE_URL` apontar para um Postgres acessível).

### 2. Criar e ativar ambiente virtual

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Aplicar migrations

Na pasta `src`:

```bash
alembic upgrade head
```

### 5. Subir a API

Na pasta `src`:

```bash
uvicorn main:app --reload
```

## Fluxos Principais

### Fluxo de criação de URL anônima

1. cliente chama `POST /short`
2. rota delega para `short_url_service.create_short_url(..., user_id=None)`
3. service valida a URL
4. service gera `short_id`
5. service define expiração de 7 dias
6. service persiste no banco
7. rota devolve a URL encurtada completa

### Fluxo de criação de URL autenticada

1. cliente chama `POST /user/createUrl`
2. FastAPI resolve `get_current_user`
3. rota chama `short_url_service.create_short_url(..., user_id=current_user.id)`
4. service define expiração de 30 dias
5. URL fica vinculada ao usuário

### Fluxo de redirecionamento

1. cliente acessa `GET /{short_id}`
2. service busca a URL pelo hash
3. service valida se a URL não expirou
4. service incrementa ou cria a métrica do dia
5. API responde com redirect para `origin_url`

### Fluxo de consulta de métricas

1. cliente chama rota de métricas com Bearer token
2. FastAPI resolve usuário autenticado
3. service localiza a URL pelo hash
4. service valida se a URL pertence ao usuário
5. service consulta ou agrega métricas
6. rota retorna o schema correspondente

## Limitações E Pontos De Atenção

Esta seção documenta o estado real atual do projeto.

### Dependências incompletas no `requirements.txt` (resolvido)

O `requirements.txt` agora inclui todas as bibliotecas usadas pelo código (`alembic`, `python-dotenv`, `passlib`, `bcrypt`, `PyJWT`, `qrcode`, `slowapi`) além do driver `psycopg2-binary` para PostgreSQL.

### Incompatibilidade observada entre `passlib` e `bcrypt` (resolvido)

O problema de hashing com `bcrypt==5.0.0` foi evitado fixando `bcrypt==4.3.0` no `requirements.txt`.

### `tokenUrl` diferente do endpoint real (resolvido)

`OAuth2PasswordBearer` agora aponta para `tokenUrl="/user/login"`, alinhado com a rota real.

### Engine do banco e caminho do SQLite (resolvido)

O engine agora lê `DATABASE_URL` do ambiente (PostgreSQL no Docker) com fallback para SQLite local:

```python
db = create_engine(os.getenv("DATABASE_URL", "sqlite:///banco.db"))
```

### Ausência de testes automatizados (resolvido)

Testes foram adicionados — veja seção [Testes](#testes).

### Naming inconsistente

Alguns nomes ainda podem ser melhorados futuramente:

- `acess.py` em vez de `access.py`
- `shortenerRequest` e `shortenerResponse` com inicial minúscula
- `createUrl` misturando convenções de nome

## Melhorias Naturais Futuras

1. ~~corrigir dependências do `requirements.txt`~~ (concluído)
2. ~~alinhar `tokenUrl` com `/user/login`~~ (concluído)
3. ~~padronizar caminho do banco SQLite~~ (concluído — `DATABASE_URL` com fallback)
4. ~~adicionar testes para services e rotas~~ (concluído)
5. adicionar deleção ou limpeza de URLs expiradas
6. adicionar planos de acesso com base em `AccessLevel`
7. padronizar nomes de rotas e schemas

## Estado Atual Resumido

O projeto já possui uma boa base funcional para um micro SaaS de encurtamento de URLs com:

- autenticação JWT
- diferenciação entre usuário anônimo e cadastrado
- expiração por política
- coleta de métricas
- QR Code
- migrations com Alembic
- separação de regra de negócio em services
- execução conteinerizada com Docker Compose (API + PostgreSQL)

Próximos passos naturais: deleção/limpeza de URLs expiradas e padronização de nomes de rotas e schemas.

## Testes

### Stack de testes

- **pytest** (runner)
- **httpx** (TestClient do FastAPI)
- **pytest-cov** (cobertura)
- **SQLite in-memory** (banco isolado por sessão de teste)

### Estrutura

```
src/tests/
  conftest.py              # fixtures: engine, db_session, app, client, tokens
  test_auth/
    test_auth.py           # JWT create/decode, tipos de token, expiração
  test_routes/
    test_metrics_routes.py # GET /metrics/day|month|year/{short_id}
    test_shortener_routes.py # POST /short, GET /s/{id}, DELETE, refresh, qrcode
    test_user_routes.py    # POST /user/create|login|refresh, GET /user/me
  test_schemas/
    test_metric_schema.py
    test_shortener_schema.py
    test_token_schema.py
    test_user_schema.py
  test_services/
    test_metric_service.py    # get_daily|monthly|yearly_metrics
    test_short_url_service.py # create, get, refresh, delete, register_access
    test_user_service.py      # create_user, authenticate_user
  test_utils/
    test_short_code.py    # generate_short_id
    test_url_utils.py     # validate_url
```

### Como executar

A partir da pasta `src/`:

```powershell
$env:PYTHONPATH = "D:\caminho\para\src"
..\venv\Scripts\pytest tests/ -v
```

Com relatório de cobertura:

```powershell
..\venv\Scripts\pytest tests/ --cov=. --cov-report=term
```

### Cobertura

Os testes cobrem **~91% do código da aplicação** (excluindo `main.py`):

| Camada       | Cobertura |
|--------------|-----------|
| Models       | 100%      |
| Utils        | 100%      |
| Auth         | 100%      |
| Schemas      | 100%      |
| Services     | 87-100%   |
| Routes       | 92-100%   |

### Dependências adicionais para testes

```txt
pytest>=8.0
pytest-cov>=5.0
httpx>=0.27
```
